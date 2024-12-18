import asyncio
import logging
import aiohttp
import openai
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_key = config.openai_api_key.get_secret_value()


class ChatGPTService:
    """
    Сервис для взаимодействия с ChatGPT API.

    Attributes:
        model (str): Название модели GPT для использования
        max_tokens (int): Максимальное количество токенов в ответе
        temperature (float): Параметр температуры для генерации ответа (0.0 - 1.0)

    Note:
        Использует асинхронные вызовы для взаимодействия с API
        Автоматически форматирует ответы на русском языке
    """

    def __init__(self, model="gpt-3.5-turbo", max_tokens=1000, temperature=0.7):
        """
        Инициализация сервиса ChatGPT.

        Args:
            model (str): Название модели GPT
            max_tokens (int): Максимальное количество токенов
            temperature (float): Параметр температуры
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def get_response(self, message: str) -> str:
        """
        Получает ответ от ChatGPT на сообщение пользователя.

        Args:
            message (str): Текст сообщения от пользователя

        Returns:
            str: Ответ от ChatGPT на русском языке

        Raises:
            Exception: При ошибке взаимодействия с API

        Note:
            Использует asyncio.to_thread для асинхронного вызова синхронного API
        """
        try:
            prompt = f"{message}\nПожалуйста, ответь на русском языке."
            
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Ошибка при получении ответа от ChatGPT: {str(e)}")
            return "Извините, произошла ошибка при обработке вашего запроса."


class PokeAPIService:
    """
    Сервис для взаимодействия с PokeAPI.

    Attributes:
        base_url (str): Базовый URL для API
        session (aiohttp.ClientSession): Сессия для HTTP-запросов

    Note:
        Использует aiohttp для асинхронных HTTP-запросов
        Автоматически форматирует ответы на русском языке
    """

    def __init__(self, base_url="https://pokeapi.co/api/v2"):
        """
        Инициализация сервиса PokeAPI.

        Args:
            base_url (str): Базовый URL для API
        """
        self.base_url = base_url
        self.session = None

    async def get_session(self) -> aiohttp.ClientSession:
        """
        Получает или создает сессию для HTTP-запросов.

        Returns:
            aiohttp.ClientSession: Сессия для HTTP-запросов

        Note:
            Создает новую сессию, если она еще не существует
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def get_pokemon_info(self, pokemon_name: str) -> str:
        """
        Получает информацию о покемоне по его имени.

        Args:
            pokemon_name (str): Имя покемона

        Returns:
            str: Информация о покемоне на русском языке

        Raises:
            Exception: При ошибке получения данных из API

        Note:
            Форматирует ответ с основными характеристиками покемона
        """
        try:
            session = await self.get_session()
            url = f"{self.base_url}/pokemon/{pokemon_name.lower()}"
            
            async with session.get(url) as response:
                if response.status == 404:
                    return f"Покемон с именем {pokemon_name} не найден."
                elif response.status != 200:
                    return "Произошла ошибка при получении данных о покемоне."
                
                data = await response.json()
                
                info = (
                    f"🎮 Информация о покемоне {data['name'].capitalize()}:\n\n"
                    f"📊 Базовые характеристики:\n"
                    f"• ID: {data['id']}\n"
                    f"• Рост: {data['height']/10} м\n"
                    f"• Вес: {data['weight']/10} кг\n\n"
                    f"💪 Способности:\n"
                )
                
                abilities = [ability['ability']['name'] for ability in data['abilities']]
                info += "• " + "\n• ".join(abilities) + "\n\n"
                
                types = [t['type']['name'] for t in data['types']]
                info += f"📋 Типы: {', '.join(types)}"
                
                return info
                
        except Exception as e:
            logger.error(f"Ошибка при получении информации о покемоне: {str(e)}")
            return "Извините, произошла ошибка при получении информации о покемоне."
        
        finally:
            if self.session and not self.session.closed:
                await self.session.close()
