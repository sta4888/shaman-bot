
# Telegram Бот с интеграцией ChatGPT и PokeAPI

Этот Telegram бот интегрируется с ChatGPT и PokeAPI, позволяя пользователям взаимодействовать с обоими сервисами через простой интерфейс. Бот сохраняет все взаимодействия в базе данных PostgreSQL.

## Возможности

- Интеграция с ChatGPT для общения с ИИ
- Интеграция с PokeAPI для получения информации о покемонах
- PostgreSQL база данных для хранения взаимодействий с пользователем
- Контейнеризация с помощью Docker
- Система команд (/start, /help, /gpt, /pokemon)

## Предварительные требования

- Docker и Docker Compose
- Telegram Bot Token (от @BotFather)
- OpenAI API Key

## Установка

1. Клонируйте репозиторий
2. Скопируйте `example.env` в `.env` и заполните свои учетные данные:
   ```
   BOT_TOKEN=ваш_токен_телеграм_бота
   OPENAI_API_KEY=ваш_ключ_openai
   DATABASE_URL=postgresql://postgres:postgres@db:5432/bot_db
   ```

## Запуск бота

Использование Docker Compose:
```bash
docker-compose up --build
```

## Структура базы данных

Бот использует базу данных PostgreSQL со следующей схемой:

### Таблица: user_messages
- id (Первичный ключ)
- user_id (Integer): ID пользователя Telegram
- user_message (Text): Сообщение пользователя
- bot_response (Text): Ответ бота
- api_source (String): Источник ответа ('chatgpt' или 'pokeapi')
- created_at (DateTime): Временная метка взаимодействия

## Команды бота

- `/start` - Запуск бота
- `/help` - Показать справку
- `/gpt <сообщение>` - Общение с ChatGPT
- `/pokemon <имя>` - Получить информацию о покемоне

## Разработка

Для локального запуска бота без Docker:

1. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Запустите бота:
   ```bash
   python bot.py
   ```
