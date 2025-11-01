# main.py
"""
Основной файл Telegram-бота на aiogram 3.x.

Функционал:
- При команде /start сохраняет пользователя в БД.
- Два раза в день (9:00 и 18:00 UTC) отправляет мемы всем подписчикам.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import settings
from database import UserDB
from memes import get_random_meme

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация компонентов
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
user_db = UserDB()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start.
    Сохраняет пользователя в базу и приветствует.
    """
    user_id = message.from_user.id
    username = message.from_user.username
    await user_db.add_user(user_id, username)
    await message.answer(
        "✅ Вы подписаны! Теперь вы будете получать мемы дважды в день (в 9:00 и 18:00 по UTC)."
    )


async def send_daily_memes():
    """
    Отправляет случайный мем всем пользователям из базы.
    Вызывается по расписанию.
    """
    user_ids = await user_db.get_all_users()
    meme_url = get_random_meme()
    logger.info(f"Отправка мема {meme_url} {len(user_ids)} пользователям...")

    for user_id in user_ids:
        try:
            await bot.send_photo(chat_id=user_id, photo=meme_url)
        except Exception as e:
            logger.error(f"Не удалось отправить мем пользователю {user_id}: {e}")


async def main():
    """Основная асинхронная функция запуска бота."""
    # Инициализация БД
    await user_db.init_db()

    # Настройка планировщика
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(send_daily_memes, CronTrigger(hour=9, minute=0))
    scheduler.add_job(send_daily_memes, CronTrigger(hour=18, minute=0))
    scheduler.start()

    logger.info("Бот запущен. Ожидание сообщений...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
