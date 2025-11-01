# database.py
"""
Модуль для работы с базой данных пользователей.

Используется SQLite для хранения ID пользователей Telegram,
которые подписались на рассылку мемов.
"""

import aiosqlite
from typing import List


class UserDB:
    """Класс для управления базой данных пользователей."""

    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path

    async def init_db(self) -> None:
        """Создаёт таблицу users, если она не существует."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT
                )
                """
            )
            await db.commit()

    async def add_user(self, user_id: int, username: str | None) -> None:
        """Добавляет пользователя в базу данных."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                (user_id, username or "unknown"),
            )
            await db.commit()

    async def get_all_users(self) -> List[int]:
        """Возвращает список всех user_id из базы."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT user_id FROM users")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
