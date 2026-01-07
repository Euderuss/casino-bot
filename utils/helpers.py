import random
from datetime import datetime, timedelta

def format_balance(amount: float) -> str:
    """Форматирование суммы денег"""
    return f"${amount:,.2f}"

def generate_referral_code() -> str:
    """Генерация реферального кода"""
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def calculate_vip_level(experience: int) -> int:
    """Расчет уровня VIP"""
    return min(experience // 1000, 10)

def format_time_delta(delta: timedelta) -> str:
    """Форматирование временного интервала"""
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if delta.days > 0:
        return f"{delta.days}д {hours}ч"
    elif hours > 0:
        return f"{hours}ч {minutes}м"
    elif minutes > 0:
        return f"{minutes}м {seconds}с"
    else:
        return f"{seconds}с"