import aiosqlite
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from config import config

async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                balance REAL DEFAULT 0,
                total_deposited REAL DEFAULT 0,
                total_withdrawn REAL DEFAULT 0,
                total_won REAL DEFAULT 0,
                total_lost REAL DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                referral_code TEXT UNIQUE,
                referred_by INTEGER,
                referral_bonus REAL DEFAULT 0,
                daily_streak INTEGER DEFAULT 0,
                last_daily DATE,
                vip_level INTEGER DEFAULT 0,
                experience INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE,
                is_banned BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Таблица транзакций
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT, -- deposit/withdraw/win/lose/bonus
                amount REAL,
                currency TEXT DEFAULT 'USD',
                status TEXT, -- pending/completed/failed
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица игр
        await db.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                game_type TEXT, -- slots/dice/coin
                bet_amount REAL,
                win_amount REAL,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица промокодов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS promocodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                bonus_amount REAL,
                bonus_percent REAL,
                max_uses INTEGER,
                used_count INTEGER DEFAULT 0,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица использованных промокодов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS used_promocodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                promocode_id INTEGER,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица рефералов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER UNIQUE,
                level INTEGER DEFAULT 1,
                earned REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.commit()

async def get_or_create_user(user_id: int, username: str = None, 
                            first_name: str = None, last_name: str = None):
    """Получить или создать пользователя"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        user = await cursor.fetchone()
        
        if not user:
            # Генерация реферального кода
            import random
            import string
            referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            await db.execute("""
                INSERT INTO users (user_id, username, first_name, last_name, referral_code, is_admin)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, first_name, last_name, referral_code, 
                  True if user_id == config.ADMIN_ID else False))
            await db.commit()
            
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )
            user = await cursor.fetchone()
        
        return dict(user) if user else None

async def update_balance(user_id: int, amount: float, transaction_type: str = "deposit"):
    """Обновить баланс пользователя"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        # Обновляем баланс
        if amount > 0:
            await db.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (amount, user_id)
            )
            
            # Обновляем статистику депозитов
            if transaction_type == "deposit":
                await db.execute(
                    "UPDATE users SET total_deposited = total_deposited + ? WHERE user_id = ?",
                    (amount, user_id)
                )
        else:
            await db.execute(
                "UPDATE users SET balance = balance - ? WHERE user_id = ?",
                (abs(amount), user_id)
            )
        
        # Записываем транзакцию
        await db.execute("""
            INSERT INTO transactions (user_id, type, amount, status, details)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, transaction_type, amount, "completed", 
              f"{transaction_type.capitalize()} через систему"))
        
        await db.commit()

async def create_game_record(user_id: int, game_type: str, bet_amount: float, 
                           win_amount: float, result: str):
    """Запись игры в историю"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute("""
            INSERT INTO games (user_id, game_type, bet_amount, win_amount, result)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, game_type, bet_amount, win_amount, result))
        
        # Обновляем статистику пользователя
        if win_amount > 0:
            await db.execute(
                "UPDATE users SET total_won = total_won + ?, games_played = games_played + 1 WHERE user_id = ?",
                (win_amount, user_id)
            )
        else:
            await db.execute(
                "UPDATE users SET total_lost = total_lost + ?, games_played = games_played + 1 WHERE user_id = ?",
                (bet_amount, user_id)
            )
        
        await db.commit()

async def get_user_stats(user_id: int):
    """Получить статистику пользователя"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        user = await cursor.fetchone()
        
        # Получаем историю игр
        cursor = await db.execute(
            "SELECT COUNT(*) as total, SUM(bet_amount) as total_bet FROM games WHERE user_id = ?",
            (user_id,)
        )
        games_stats = await cursor.fetchone()
        
        return {
            **dict(user),
            "games_count": games_stats["total"] if games_stats["total"] else 0,
            "total_bet": games_stats["total_bet"] if games_stats["total_bet"] else 0
        }

async def get_all_users():
    """Получить всех пользователей"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users ORDER BY balance DESC")
        users = await cursor.fetchall()
        return [dict(user) for user in users]

async def get_total_stats():
    """Получить общую статистику"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Общее количество пользователей
        cursor = await db.execute("SELECT COUNT(*) as total FROM users")
        total_users = await cursor.fetchone()
        
        # Общий баланс
        cursor = await db.execute("SELECT SUM(balance) as total_balance FROM users")
        total_balance = await cursor.fetchone()
        
        # Общие депозиты и выводы
        cursor = await db.execute("SELECT SUM(total_deposited) as deposits, SUM(total_withdrawn) as withdrawals FROM users")
        money_stats = await cursor.fetchone()
        
        return {
            "total_users": total_users["total"],
            "total_balance": total_balance["total_balance"] or 0,
            "total_deposits": money_stats["deposits"] or 0,
            "total_withdrawals": money_stats["withdrawals"] or 0
        }