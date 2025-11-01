# memes.py
"""
Модуль для получения мемов из Reddit.

Использует публичный API Reddit (через JSON-эндпоинты).
Поддерживает фолбэк на локальные мемы, если API недоступен.
"""

# import asyncio
import logging
import random
from typing import List

import aiohttp

logger = logging.getLogger(__name__)

# Список резервных мемов на случай ошибки Reddit
FALLBACK_MEMES: List[str] = [
    "https://i.imgur.com/Juq4xJv.jpg",
    "https://i.imgur.com/6rNv1Za.jpg",
    "https://i.imgur.com/9bRvzQl.jpg",
    "https://i.imgur.com/8x5NkQj.jpg",
]

# Список популярных сабреддитов с мемами
SUBREDDITS: List[str] = [
    "memes",
    "dankmemes",
    "funny",
    "wholesomememes",
]


async def fetch_reddit_memes(subreddit: str, limit: int = 20) -> List[str]:
    """
    Получает список URL изображений из указанного сабреддита.

    :param subreddit: Название сабреддита (без r/).
    :param limit: Количество постов для загрузки.
    :return: Список URL изображений (.jpg, .png, .gif).
    """
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    headers = {
        "User-Agent": "MemeBot/1.0 by YourTelegramUsername"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    logger.warning(f"Reddit вернул статус {response.status} для {subreddit}")
                    return []

                data = await response.json()
                memes = []

                for post in data["data"]["children"]:
                    post_data = post["data"]
                    image_url = post_data.get("url")

                    # Фильтруем только изображения
                    if image_url and (
                        image_url.endswith((".jpg", ".jpeg", ".png", ".gif"))
                        and not image_url.endswith(".gifv")
                    ):
                        memes.append(image_url)

                logger.info(f"Получено {len(memes)} мемов из r/{subreddit}")
                return memes

    except Exception as e:
        logger.error(f"Ошибка при загрузке мемов из r/{subreddit}: {e}")
        return []


async def get_random_meme() -> str:
    """
    Возвращает случайный мем из Reddit или резервного списка.

    Пытается получить мемы из случайного сабреддита.
    Если не удаётся — возвращает резервный мем.
    """
    subreddit = random.choice(SUBREDDITS)
    memes = await fetch_reddit_memes(subreddit, limit=25)

    if memes:
        return random.choice(memes)

    # Фолбэк
    logger.warning("Reddit недоступен или нет изображений. Используется резервный мем.")
    return random.choice(FALLBACK_MEMES)
