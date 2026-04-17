🤖 SmartHome Pro Assistant

SmartHome Pro Assistant — це інтелектуальний Telegram-бот для першої лінії підтримки інтернет-магазину. Бот використовує потужність Claude 3.5 Sonnet для гнучкого спілкування та інтегрований з Google Sheets як легкою базою даних.
✨ Основні можливості

    AI-спілкування: Розуміння природної мови та контексту клієнта.

    Інтеграція з Google Sheets: Перевірка статусу замовлень та профілів лояльності в реальному часі.

    Агентська логіка: Бот самостійно вирішує, коли викликати інструмент (Tool Use), а коли відповісти самостійно.

    Система "Thinking": Прозорість логіки через приховані роздуми в консолі для розробника.

    Надійність: Автоматичні повторні спроби (Retry logic) та захист від паралельних запитів.

🛡️ Безпека та UX

    Throttling: Обмеження кількості повідомлень для захисту від спаму.

    Input Sanitization: Очищення вводу від HTML-тегів та захист від Prompt Injection.

    Context Management: Автоматичне обмеження історії діалогу для стабільної роботи AI.

🛠 Налаштування змінних оточення

Для запуску бота створіть файл .env у кореневій папці проєкту та заповніть його за зразком нижче.

    Важливо: Весь JSON-вміст сервісного акаунта має бути в одинарних лапках, щоб уникнути помилок через внутрішні подвійні лапки.

Фрагмент коду

# --- Telegram Bot Settings ---
# Отримайте у @BotFather
TELEGRAM_BOT_TOKEN=your_bot_token_here

# --- Anthropic AI Settings ---
# Ключ доступу до Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# --- Google Sheets Settings ---
# ID можна скопіювати з посилання на вашу таблицю
SPREADSHEET_ID=your_google_spreadsheet_id_here

# --- Google Credentials (JSON string) ---
# Весь вміст файлу сервісного акаунта (.json) в один рядок
GOOGLE_CREDENTIALS_JSON='{"type": "service_account", "project_id": "...", "private_key": "..."}'

🚀 Як запустити

    Встановіть залежності: pip install -r requirements.txt

    Налаштуйте файл .env.

    Запустіть бота: python bot.py
