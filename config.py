import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    BOT_TOKEN: str = "8480371822:AAETYBC_6D-3VVsl7UwjhfZDlI73ljSTfvU"
    ADMIN_ID: int = 8148320466
    CRYPTO_PAY_TOKEN: str = "512203:AABKidRae0kvraQEMUKljxew9XPySslZyEj"
    WALLET_ADDRESS: str = "UQCvg_jVSaC44BNtDX4Wm9uRWIcyZXF8tS6jwl6PHPEpuAPw"
    
    # Настройки
    WITHDRAW_FEE: float = 0.05  # 5%
    MIN_DEPOSIT: float = 1.0
    MIN_WITHDRAW: float = 0.5
    DAILY_BONUS: list = None
    REFERRAL_PERCENTS: list = None
    
    # База данных
    DB_PATH: str = "database/casino.db"
    
    def __post_init__(self):
        self.DAILY_BONUS = [10, 15, 20, 25, 30, 40, 50]  # Бонусы за 7 дней
        self.REFERRAL_PERCENTS = [5, 3, 1]  # 3 уровня рефералов

config = Config()