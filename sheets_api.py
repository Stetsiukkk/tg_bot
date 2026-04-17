import os
import json
import logging
import gspread_asyncio
from google.oauth2.service_account import Credentials
from tenacity import retry, stop_after_attempt, wait_exponential
from config import SPREADSHEET_ID

# --- НАЛАШТУВАННЯ АВТЕНТИФІКАЦІЇ ---

def get_creds():
    """
    Отримує та десеріалізує ключі доступу Google із змінних оточення.
    """
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise ValueError("❌ GOOGLE_CREDENTIALS_JSON не знайдено в .env!")

    creds_info = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_info)
    
    # Додаємо необхідні права доступу (Scopes)
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
    ])
    return scoped

# Менеджер асинхронного клієнта для Google Sheets
agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)

# Налаштування повторних спроб (Retry) при збоях мережі
retry_setup = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)

# --- ФУНКЦІЇ ДЛЯ РОБОТИ З ТАБЛИЦЯМИ ---

@retry_setup
async def get_client_info(email: str) -> str:
    """
    Шукає клієнта на листі 'Clients' за Email. 
    Повертає JSON-рядок із даними або повідомлення про помилку.
    """
    try:
        client = await agcm.authorize()
        ss = await client.open_by_key(SPREADSHEET_ID)
        worksheet = await ss.worksheet("Clients")
        
        cell = await worksheet.find(email)
        if not cell:
            return f"Клієнта з email {email} не знайдено."

        row_data = await worksheet.row_values(cell.row)
        
        # Структуруємо дані (припускаємо, що колонки: Email, Name, Status, Discount)
        data = {
            "name": row_data[1] if len(row_data) > 1 else "Не вказано",
            "status": row_data[2] if len(row_data) > 2 else "Звичайний",
            "discount_available": row_data[3] if len(row_data) > 3 else "Немає"
        }
        return json.dumps(data, ensure_ascii=False)
    
    except Exception as e:
        logging.error(f"Sheets API Error (Client): {e}")
        raise e

@retry_setup
async def get_order_status(order_id: str) -> str:
    """
    Шукає замовлення на листі 'Orders' за ID.
    Повертає JSON-рядок зі статусом та датою доставки.
    """
    try:
        client = await agcm.authorize()
        ss = await client.open_by_key(SPREADSHEET_ID)
        worksheet = await ss.worksheet("Orders")

        cell = await worksheet.find(str(order_id))
        if not cell:
            return f"Замовлення №{order_id} не знайдено."

        row_data = await worksheet.row_values(cell.row)
        
        # Структуруємо дані (припускаємо: ID, Товар, Статус, Дата)
        data = {
            "order_id": row_data[0],
            "status": row_data[2] if len(row_data) > 2 else "В обробці",
            "delivery_date": row_data[3] if len(row_data) > 3 else "Уточнюється"
        }
        return json.dumps(data, ensure_ascii=False)
    
    except Exception as e:
        logging.error(f"Sheets API Error (Order): {e}")
        raise e