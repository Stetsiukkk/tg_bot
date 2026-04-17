import anthropic
import re
import json
import logging
from typing import List, Dict
from sheets_api import get_client_info, get_order_status
from config import ANTHROPIC_API_KEY, SYSTEM_PROMPT, TOOLS

# Ініціалізація клієнта
client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

async def run_agentic_loop(messages_history: List[Dict]) -> str:
    """
    Основний цикл взаємодії з Claude: обробка думок, виклик інструментів 
    та формування фінальної відповіді для клієнта.
    """
    while True:
        # --- БЛОК ВІЗУАЛЬНОГО ЛОГУВАННЯ ---
        print("\n" + "═"*60)
        print("📤 ВІДПРАВЛЯЄМО ЗАПИТ ДО CLAUDE:")
        print(json.dumps(messages_history, indent=2, ensure_ascii=False, default=str))
        print("═"*60 + "\n")

        # Запит до моделі
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages_history,
            tools=TOOLS
        )

        # 1. ФОРМУЄМО ЧИСТУ ІСТОРІЮ ТА ШУКАЄМО РОЗДУМИ ОДРАЗУ
        clean_content = []
        for block in response.content:
            if block.type == "text":
                clean_content.append({"type": "text", "text": block.text})
                
                # МИТТЄВИЙ ВИВІД РОЗДУМІВ (до виклику інструментів)
                thinking_match = re.search(r'<thinking>(.*?)</thinking>', block.text, re.DOTALL)
                if thinking_match:
                    print(f"🧠 [THINKING]:\n{thinking_match.group(1).strip()}\n")
            
            elif block.type == "tool_use":
                clean_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })

        messages_history.append({"role": "assistant", "content": clean_content})

        # --- СЦЕНАРІЙ 1: МОДЕЛЬ ВИКЛИКАЄ ІНСТРУМЕНТ ---
        if response.stop_reason == "tool_use":
            tool_results = []
            
            for block in response.content:
                if block.type == "tool_use":
                    print(f"🛠 [ВИКЛИК ІНСТРУМЕНТУ]: {block.name} | Аргументи: {block.input}")
                    
                    try:
                        if block.name == "get_client_info":
                            result = await get_client_info(**block.input)
                        elif block.name == "get_order_status":
                            result = await get_order_status(**block.input)
                        else:
                            result = f"Error: Unknown tool {block.name}"
                    except Exception as e:
                        result = f"Error: Google Sheets API failure: {str(e)}"
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            messages_history.append({"role": "user", "content": tool_results})
            continue

        # --- СЦЕНАРІЙ 2: ФІНАЛЬНА ВІДПОВІДЬ ТЕКСТОМ ---
        elif response.stop_reason in ["end_turn", "stop_sequence"]:
            # Беремо текст з чистих блоків, які ми вже зібрали
            raw_text = "".join([b["text"] for b in clean_content if b["type"] == "text"])
            
            # Очищуємо текст від технічних тегів для користувача
            clean_answer = re.sub(r'<thinking>.*?</thinking>', '', raw_text, flags=re.DOTALL).strip()
            return clean_answer
            
        else:
            return "Вибачте, сталася непередбачувана помилка при генерації відповіді. 🛑"