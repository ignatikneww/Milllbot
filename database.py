import aiosqlite
import time

DB_NAME = "millbot.db"


async def init_db():
    """Создаёт таблицы"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Пользователи
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER,
                chat_id INTEGER,
                username TEXT,
                first_name TEXT,
                rank INTEGER DEFAULT 1,
                messages_count INTEGER DEFAULT 0,
                warnings INTEGER DEFAULT 0,
                first_seen INTEGER,
                last_seen INTEGER,
                PRIMARY KEY (user_id, chat_id)
            )
        ''')
        
        # Админы бота
        await db.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER,
                chat_id INTEGER,
                added_by INTEGER,
                added_at INTEGER,
                PRIMARY KEY (user_id, chat_id)
            )
        ''')
        
        # Создатели
        await db.execute('''
            CREATE TABLE IF NOT EXISTS owners (
                user_id INTEGER,
                chat_id INTEGER,
                PRIMARY KEY (user_id, chat_id)
            )
        ''')
        
        # Статистика чатов
        await db.execute('''
            CREATE TABLE IF NOT EXISTS chat_stats (
                chat_id INTEGER PRIMARY KEY,
                total_messages INTEGER DEFAULT 0
            )
        ''')
        
        await db.commit()
        print("✅ База данных готова!")


# ==================== ПОЛЬЗОВАТЕЛИ ====================

async def get_user(user_id: int, chat_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id)
        )
        return await cursor.fetchone()


async def add_user(user_id: int, chat_id: int, username: str, first_name: str):
    now = int(time.time())
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO users (user_id, chat_id, username, first_name, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, chat_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_seen = ?
        ''', (user_id, chat_id, username, first_name, now, now, now))
        await db.commit()


async def add_message(user_id: int, chat_id: int):
    now = int(time.time())
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            UPDATE users 
            SET messages_count = messages_count + 1, last_seen = ?
            WHERE user_id = ? AND chat_id = ?
        ''', (now, user_id, chat_id))
        
        await db.execute('''
            INSERT INTO chat_stats (chat_id, total_messages)
            VALUES (?, 1)
            ON CONFLICT(chat_id) DO UPDATE SET total_messages = total_messages + 1
        ''', (chat_id,))
        
        await db.commit()


async def set_rank(user_id: int, chat_id: int, rank: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET rank = ? WHERE user_id = ? AND chat_id = ?",
            (rank, user_id, chat_id)
        )
        await db.commit()


async def add_warning(user_id: int, chat_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET warnings = warnings + 1 WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id)
        )
        await db.commit()
        
        cursor = await db.execute(
            "SELECT warnings FROM users WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id)
        )
        row = await cursor.fetchone()
        return row[0] if row else 0


async def reset_warnings(user_id: int, chat_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET warnings = 0 WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id)
        )
        await db.commit()


async def get_top_users(chat_id: int, limit: int = 10):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT * FROM users WHERE chat_id = ?
            ORDER BY messages_count DESC LIMIT ?
        ''', (chat_id, limit))
        return await cursor.fetchall()


# ==================== ВЛАДЕЛЬЦЫ И АДМИНЫ ====================

async def is_owner(user_id: int, chat_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT 1 FROM owners WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id)
        )
        return await cursor.fetchone() is not None


async def add_owner(user_id: int, chat_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO owners (user_id, chat_id) VALUES (?, ?)",
            (user_id, chat_id)
        )
        await db.commit()


async def has_owner(chat_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT 1 FROM owners WHERE chat_id = ?", (chat_id,)
        )
        return await cursor.fetchone() is not None


async def is_admin(user_id: int, chat_id: int) -> bool:
    if await is_owner(user_id, chat_id):
        return True
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT 1 FROM admins WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id)
        )
        return await cursor.fetchone() is not None


async def add_admin(user_id: int, chat_id: int, added_by: int):
    now = int(time.time())
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO admins (user_id, chat_id, added_by, added_at) VALUES (?, ?, ?, ?)",
            (user_id, chat_id, added_by, now)
        )
        await db.commit()


async def remove_admin(user_id: int, chat_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM admins WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id)
        )
        await db.commit()


async def get_admins(chat_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM admins WHERE chat_id = ?", (chat_id,)
        )
        return await cursor.fetchall()


async def count_admins(chat_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM admins WHERE chat_id = ?", (chat_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else 0


# ==================== СТАТИСТИКА ====================

async def get_chat_stats(chat_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM chat_stats WHERE chat_id = ?", (chat_id,)
        )
        return await cursor.fetchone()


async def get_total_users(chat_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM users WHERE chat_id = ?", (chat_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else 0