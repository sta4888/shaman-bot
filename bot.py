import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from sqlalchemy.orm import Session
import time

from config import config
from models import SessionLocal, UserMessage, init_db
from services import ChatGPTService, PokeAPIService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

chatgpt_service = ChatGPTService()
pokeapi_service = PokeAPIService()


def get_db() -> Session:
    """
    Создает новую сессию базы данных.

    Returns:
        Session: Объект сессии SQLAlchemy

    Note:
        Использует контекстный менеджер для автоматического закрытия сессии
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    """
    Обработчик команды /start.
    
    Отправляет приветственное сообщение с описанием возможностей бота.

    Args:
        message (types.Message): Объект сообщения Telegram
    """
    welcome_text = (
        "👋 Добро пожаловать в ChatGPT & Pokemon Бота!\n\n"
        "Вы можете:\n"
        "🤖 Общаться с GPT: Начните сообщение с '/gpt'\n"
        "🎮 Получить информацию о покемоне: Начните с '/pokemon'\n"
        "❓ Используйте /help для просмотра всех команд"
    )
    await message.reply(welcome_text)


@dp.message(Command("help"))
async def send_help(message: types.Message):
    """
    Обработчик команды /help.
    
    Отправляет справочное сообщение со списком доступных команд.

    Args:
        message (types.Message): Объект сообщения Telegram
    """
    help_text = (
        "🤖 Команды бота:\n\n"
        "/start - Запустить бота\n"
        "/help - Показать это сообщение помощи\n"
        "/gpt <сообщение> - Общаться с ChatGPT\n"
        "/pokemon <имя> - Получить информацию о покемоне\n\n"
        "Примеры:\n"
        "/gpt Что такое Python?\n"
        "/pokemon pikachu"
    )
    await message.reply(help_text)


@dp.message(Command("gpt"))
async def handle_gpt(message: types.Message):
    """
    Обработчик команды /gpt.
    
    Отправляет запрос к ChatGPT и сохраняет взаимодействие в базе данных.

    Args:
        message (types.Message): Объект сообщения Telegram

    Note:
        Извлекает текст после команды /gpt и отправляет его в ChatGPT
        Сохраняет запрос и ответ в базе данных
    """
    user_text = message.text.replace("/gpt", "").strip()
    if not user_text:
        await message.reply("Пожалуйста, добавьте сообщение после /gpt")
        return

    response = await chatgpt_service.get_response(user_text)
    
    db = get_db()
    db_message = UserMessage(
        user_id=message.from_user.id,
        user_message=user_text,
        bot_response=response,
        api_source='chatgpt'
    )
    db.add(db_message)
    db.commit()

    await message.reply(response)


@dp.message(Command("pokemon"))
async def handle_pokemon(message: types.Message):
    """
    Обработчик команды /pokemon.
    
    Получает информацию о покемоне и сохраняет взаимодействие в базе данных.

    Args:
        message (types.Message): Объект сообщения Telegram

    Note:
        Извлекает имя покемона после команды /pokemon
        Запрашивает информацию через PokeAPI
        Сохраняет запрос и ответ в базе данных
    """
    pokemon_name = message.text.replace("/pokemon", "").strip()
    if not pokemon_name:
        await message.reply("Пожалуйста, укажите имя покемона после /pokemon")
        return

    response = await pokeapi_service.get_pokemon_info(pokemon_name)
    
    db = get_db()
    db_message = UserMessage(
        user_id=message.from_user.id,
        user_message=pokemon_name,
        bot_response=response,
        api_source='pokeapi'
    )
    db.add(db_message)
    db.commit()

    await message.reply(response)


async def main():
    """
    Основная функция запуска бота.
    
    Инициализирует базу данных и запускает бота.

    Note:
        Пытается подключиться к базе данных несколько раз перед запуском
        Если не удается подключиться к базе данных, завершает работу с ошибкой
    """
    retries = 5
    while retries > 0:
        try:
            init_db()
            logger.info("База данных успешно инициализирована")
            break
        except Exception as e:
            logger.warning(f"Ошибка подключения к базе данных: {str(e)}")
            retries -= 1
            if retries == 0:
                logger.error("Не удалось подключиться к базе данных")
                raise
            time.sleep(5)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
