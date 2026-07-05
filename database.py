import aiosqlite
from config import DB_NAME


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price TEXT,
                payment_link TEXT,
                channel_link TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category_id INTEGER,
                screenshot_file_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


# ---------- FOYDALANUVCHILAR ----------

async def add_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name)
        )
        await db.commit()


async def users_count() -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0]


# ---------- KATEGORIYALAR ----------

async def add_category(name: str, price: str, payment_link: str, channel_link: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """INSERT INTO categories (name, price, payment_link, channel_link)
               VALUES (?, ?, ?, ?)""",
            (name, price, payment_link, channel_link)
        )
        await db.commit()
        return cursor.lastrowid


async def get_categories():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id, name, price, payment_link, channel_link FROM categories"
        )
        return await cursor.fetchall()


async def get_category(category_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id, name, price, payment_link, channel_link FROM categories WHERE id = ?",
            (category_id,)
        )
        return await cursor.fetchone()


async def remove_category(category_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        await db.commit()


# ---------- SO'ROVLAR (TO'LOV TEKSHIRUVI) ----------

async def create_request(user_id: int, category_id: int, screenshot_file_id: str) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """INSERT INTO requests (user_id, category_id, screenshot_file_id, status)
               VALUES (?, ?, ?, 'pending')""",
            (user_id, category_id, screenshot_file_id)
        )
        await db.commit()
        return cursor.lastrowid


async def get_request(request_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id, user_id, category_id, screenshot_file_id, status FROM requests WHERE id = ?",
            (request_id,)
        )
        return await cursor.fetchone()


async def update_request_status(request_id: int, status: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE requests SET status = ? WHERE id = ?", (status, request_id))
        await db.commit()
