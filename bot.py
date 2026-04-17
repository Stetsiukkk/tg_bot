import asyncio
import logging
import sys
import time
import re
from typing import Any, Awaitable, Callable, Dict

from aiogram import Bot, Dispatcher, types, BaseMiddleware, F
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.enums import ParseMode

from agent import run_agentic_loop
from config import TELEGRAM_BOT_TOKEN

# --- MIDDLEWARE ---
class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: int = 8, time_window: int = 60):
        self.users = {} 
        self.rate_limit = rate_limit
        self.time_window = time_window

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()
        if user_id not in self.users:
            self.users[user_id] = []
        
        self.users[user_id] = [ts for ts in self.users[user_id] if current_time - ts < self.time_window]

        if len(self.users[user_id]) >= self.rate_limit:
            await event.answer("⚠️ Ви відправляєте занадто багато повідомлень! Зачекайте хвилинку.")
            return 

        self.users[user_id].append(current_time)
        return await handler(event, data)

# --- UTILS ---
def sanitize_input(text: str) -> str:
    if not text: return ""
    text = text[:1000]
    forbidden = ["ignore previous", "system prompt", "forget all", "ігноруй попередні", "забудь все"]
    if any(phrase in text.lower() for phrase in forbidden):
        return "⚠️ [ЗАБЛОКОВАНО: СПРОБА ІН'ЄКЦІЇ]"
    return re.sub(r'<[^>]*>', '', text).strip()

def get_main_keyboard():
    kb = [[KeyboardButton(text="📦 Стан замовлення"), KeyboardButton(text="🏷 Дізнатися знижку")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def trim_history(history: list, max_len: int = 10) -> list:
    """
    Обрізає історію, стежачи за тим, щоб вона не починалася з 'tool_result',
    що призведе до помилки 400 у Claude.
    """
    if len(history) <= max_len:
        return history

    new_history = history[-max_len:]
    
    # Якщо перше повідомлення в обрізаній історії - це результат інструменту,
    # нам треба видалити його, бо Claude не знайде запиту (tool_use) для нього.
    while new_history and (new_history[0].get("role") == "user" and isinstance(new_history[0].get("content"), list) and "tool_result" in str(new_history[0])):
        new_history.pop(0)
        
    return new_history

# --- SETUP ---
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
dp.message.middleware(ThrottlingMiddleware(rate_limit=8, time_window=60))

user_sessions = {}
processing_users = set()

# --- HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "Вітаю! Я розумний асистент **SmartHome Pro** 🤖\n\n"
        "Допоможу перевірити замовлення, знижку або відповім на питання.\n"
        "Чим можу допомогти?"
    )
    user_sessions[message.from_user.id] = [{"role": "assistant", "content": welcome_text}]
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text == "📦 Стан замовлення")
async def handle_order_prompt(message: types.Message):
    text = "З радістю! Напишіть мені номер вашого замовлення (наприклад: *12345*)."
    user_id = message.from_user.id
    if user_id not in user_sessions: user_sessions[user_id] = []
    user_sessions[user_id].append({"role": "assistant", "content": text})
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text == "🏷 Дізнатися знижку")
async def handle_discount_prompt(message: types.Message):
    text = "Щоб перевірити вашу знижку, напишіть, будь ласка, ваш **email**."
    user_id = message.from_user.id
    if user_id not in user_sessions: user_sessions[user_id] = []
    user_sessions[user_id].append({"role": "assistant", "content": text})
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    if user_id in processing_users:
        await message.answer("⏳ Я ще обробляю вашу попередню думку...")
        return

    processing_users.add(user_id)
    session = user_sessions.get(user_id, []) # Безпечне отримання сесії

    try:
        safe_text = sanitize_input(message.text)
        session.append({"role": "user", "content": safe_text})

        session = trim_history(session, max_len=12)
        user_sessions[user_id] = session

        async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
            answer = await run_agentic_loop(session)
            await message.answer(answer, parse_mode=ParseMode.MARKDOWN)
            
    except Exception as e:
        logging.error(f"Error in handle_message: {e}")
        await message.answer("🛠 Сталася помилка. Спробуйте ще раз через хвилину.")
        if len(session) > 0: session.pop() # Видаляємо останнє повідомлення користувача, на яке не було відповіді
            
    finally:
        processing_users.discard(user_id)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())