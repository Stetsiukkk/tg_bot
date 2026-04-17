🤖 SmartHome Pro Assistant

SmartHome Pro Assistant — це інтелектуальний Telegram-бот для першої лінії підтримки інтернет-магазину. Бот використовує потужність Claude AI (Anthropic) для гнучкого спілкування з клієнтами та інтегрований з Google Sheets як легкою базою даних.
✨ Основні можливості

    AI-спілкування: Використання моделі Claude 3.5 Sonnet для розуміння природної мови.

    Інтеграція з Google Sheets: Перевірка статусу замовлень та профілів лояльності в реальному часі.

    Агентська логіка: Бот сам вирішує, коли йому потрібно викликати інструмент (Tool Use), а коли відповісти самостійно.

    Система "Thinking": Прозорість логіки бота через приховані роздуми в консолі.

    Надійність: Автоматичні повторні спроби запитів (Retry logic) та захист від паралельних запитів одного користувача.

🛡️ Безпека та UX

    Throttling: Захист від спаму (обмеження кількості повідомлень за хвилину).

    Input Sanitization: Очищення вводу користувача від HTML-тегів та спроб Prompt Injection.

    Context Management: Автоматичне очищення та обмеження історії діалогу для стабільної роботи AI.


🛠 Налаштування змінних оточення

Для роботи бота необхідно створити файл .env у кореневій папці проєкту та заповнити його за наступним шаблоном:
Plaintext

# --- Telegram Bot Settings ---
# Токен вашого бота від @BotFather
TELEGRAM_BOT_TOKEN=your_bot_token_here

# --- Anthropic AI Settings ---
# Ваш API ключ від Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# --- Google Sheets Settings ---
# ID вашої Google таблиці (можна взяти з URL таблиці)
SPREADSHEET_ID=your_google_spreadsheet_id_here

# --- Google Credentials (JSON string) ---
# Весь вміст файлу сервісного акаунта (.json) в один рядок.
# ВАЖЛИВО: Обов'язково використовуйте ОДИНАРНІ лапки навколо JSON-рядка.
GOOGLE_CREDENTIALS_JSON='{"type": "service_account", "project_id": "...", ...}'
