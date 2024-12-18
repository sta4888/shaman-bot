from datetime import datetime
import logging
from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time

from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class UserMessage(Base):
    """
    Модель для хранения сообщений пользователей и ответов бота.

    Attributes:
        id (int): Уникальный идентификатор сообщения
        user_id (int): ID пользователя в Telegram
        user_message (str): Текст сообщения от пользователя
        bot_response (str): Ответ бота
        api_source (str): Источник ответа ('chatgpt' или 'pokeapi')
        created_at (datetime): Время создания записи
    """

    __tablename__ = 'user_messages'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    user_message = Column(Text)
    bot_response = Column(Text)
    api_source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


def create_database_connection(retries=5, delay=5):
    """
    Создает подключение к базе данных с механизмом повторных попыток.

    Args:
        retries (int): Количество попыток подключения
        delay (int): Задержка между попытками в секундах

    Returns:
        Engine: Объект SQLAlchemy Engine для работы с базой данных

    Raises:
        Exception: Если не удалось подключиться после всех попыток

    Note:
        Использует параметры подключения из конфигурации приложения
    """
    logger.info(f"Попытка подключения к базе данных: {config.database_url}")
    
    for attempt in range(retries):
        try:
            engine = create_engine(config.database_url)
            with engine.connect() as connection:
                logger.info("Успешное подключение к базе данных")
                return engine
        except Exception as e:
            if attempt == retries - 1:
                logger.error(f"Не удалось подключиться к базе данных после {retries} попыток")
                raise
            logger.warning(f"Попытка {attempt + 1} не удалась: {str(e)}")
            time.sleep(delay)


engine = create_database_connection()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Инициализирует базу данных, создавая все необходимые таблицы.

    Raises:
        Exception: Если произошла ошибка при создании таблиц

    Note:
        Использует глобальный объект engine для подключения к базе данных
        Создает все таблицы, определенные в моделях SQLAlchemy
    """
    try:
        logger.info("Начало создания таблиц базы данных")
        Base.metadata.create_all(bind=engine)
        logger.info("Таблицы базы данных успешно созданы")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц базы данных: {str(e)}")
        raise
