from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_menu():
    """Главное меню"""
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="🎰 Игры"))
    builder.add(KeyboardButton(text="💰 Баланс"))
    builder.add(KeyboardButton(text="📊 Профиль"))
    builder.add(KeyboardButton(text="🎁 Бонусы"))
    builder.add(KeyboardButton(text="👥 Рефералы"))
    builder.add(KeyboardButton(text="ℹ️ Помощь"))
    
    builder.adjust(2, 2, 2)
    return builder.as_markup(resize_keyboard=True)

def get_games_menu():
    """Меню игр"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="🎰 Слоты (x2-x100)",
        callback_data="game_slots"
    ))
    builder.add(InlineKeyboardButton(
        text="🎲 Кости (x1.5-x6)",
        callback_data="game_dice"
    ))
    builder.add(InlineKeyboardButton(
        text="🪙 Монетка (x2)",
        callback_data="game_coin"
    ))
    builder.add(InlineKeyboardButton(
        text="🏆 Турниры",
        callback_data="game_tournaments"
    ))
    builder.add(InlineKeyboardButton(
        text="↩️ Назад",
        callback_data="back_to_main"
    ))
    
    builder.adjust(1)
    return builder.as_markup()

def get_balance_menu():
    """Меню баланса"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="💳 Пополнить",
        callback_data="deposit"
    ))
    builder.add(InlineKeyboardButton(
        text="🏦 Вывести",
        callback_data="withdraw"
    ))
    builder.add(InlineKeyboardButton(
        text="📈 История",
        callback_data="transactions"
    ))
    builder.add(InlineKeyboardButton(
        text="↩️ Назад",
        callback_data="back_to_main"
    ))
    
    builder.adjust(2)
    return builder.as_markup()

def get_bonus_menu():
    """Меню бонусов"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="🎁 Ежедневный бонус",
        callback_data="daily_bonus"
    ))
    builder.add(InlineKeyboardButton(
        text="🎡 Колесо фортуны",
        callback_data="wheel_of_fortune"
    ))
    builder.add(InlineKeyboardButton(
        text="🎫 Промокод",
        callback_data="enter_promocode"
    ))
    builder.add(InlineKeyboardButton(
        text="📋 Задания",
        callback_data="quests"
    ))
    builder.add(InlineKeyboardButton(
        text="↩️ Назад",
        callback_data="back_to_main"
    ))
    
    builder.adjust(2)
    return builder.as_markup()

def get_deposit_menu():
    """Меню пополнения"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="💎 TON (TON)",
        callback_data="deposit_ton"
    ))
    builder.add(InlineKeyboardButton(
        text="💵 USDT (TRC20)",
        callback_data="deposit_usdt"
    ))
    builder.add(InlineKeyboardButton(
        text="💶 USDC (TRC20)",
        callback_data="deposit_usdc"
    ))
    builder.add(InlineKeyboardButton(
        text="↩️ Назад",
        callback_data="back_to_balance"
    ))
    
    builder.adjust(2)
    return builder.as_markup()

def get_admin_menu():
    """Меню администратора"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="📊 Общая статистика",
        callback_data="admin_stats"
    ))
    builder.add(InlineKeyboardButton(
        text="👤 Управление пользователями",
        callback_data="admin_users"
    ))
    builder.add(InlineKeyboardButton(
        text="💰 Изменить баланс",
        callback_data="admin_balance"
    ))
    builder.add(InlineKeyboardButton(
        text="🎫 Промокоды",
        callback_data="admin_promocodes"
    ))
    builder.add(InlineKeyboardButton(
        text="📢 Рассылка",
        callback_data="admin_broadcast"
    ))
    builder.add(InlineKeyboardButton(
        text="⚙️ Настройки",
        callback_data="admin_settings"
    ))
    
    builder.adjust(2)
    return builder.as_markup()

def get_back_button():
    """Кнопка назад"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="↩️ Назад", callback_data="back"))
    return builder.as_markup()

def get_bet_amounts():
    """Кнопки для выбора ставки"""
    builder = InlineKeyboardBuilder()
    
    amounts = [1, 5, 10, 25, 50, 100]
    for amount in amounts:
        builder.add(InlineKeyboardButton(
            text=f"${amount}",
            callback_data=f"bet_{amount}"
        ))
    
    builder.add(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_games"))
    builder.adjust(3)
    return builder.as_markup()

def get_confirm_withdraw():
    """Подтверждение вывода"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="✅ Подтвердить",
        callback_data="confirm_withdraw"
    ))
    builder.add(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_withdraw"
    ))
    
    return builder.as_markup()