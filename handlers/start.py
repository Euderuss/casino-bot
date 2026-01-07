from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
import keyboards as kb
from database import get_or_create_user
from config import config

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработка команды /start"""
    user = await get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    welcome_text = f"""🎰 *Добро пожаловать в казино!* 🎰

💰 *Ваш баланс:* ${user['balance']:.2f}
👤 *ID:* {user['id']}
🏆 *Уровень:* {user['vip_level']}

💎 *Доступные игры:*
  • 🎰 Слоты (x2-x100)
  • 🎲 Кости (x1.5-x6)
  • 🪙 Монетка (x2)

🎁 *Бонусы:*
  • Ежедневный подарок
  • Реферальная система (до 9%)
  • Промокоды

👑 *VIP программа:* повышайте уровень для увеличения лимитов!

_Для начала игры нажмите 🎰 Игры_"""
    
    await message.answer(
        welcome_text,
        reply_markup=kb.get_main_menu(),
        parse_mode="Markdown"
    )

@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message):
    """Помощь по боту"""
    help_text = """*📚 Помощь по боту*

🎰 *Игры:*
  • *Слоты* - 3 барабана, шанс выигрыша до 1:1000
  • *Кости* - угадайте число или больше/меньше
  • *Монетка* - классический орёл/решка

💰 *Финансы:*
  • *Пополнение:* от $1 через Crypto Pay
  • *Вывод:* от $0.5 с комиссией 5%
  • *Курсы:* обновляются в реальном времени

👥 *Рефералы:* приглашайте друзей и получайте до 9% с их депозитов

🎁 *Бонусы:*
  • Ежедневный бонус (растёт с каждым днём)
  • Колесо фортуны раз в 3 дня
  • Промокоды от администрации

⚠️ *Правила:*
  • Минимальный возраст: 18 лет
  • Ответственная игра
  • Одна учетная запись на человека

*Техподдержка:* @casino_support"""
    
    await message.answer(help_text, parse_mode="Markdown")

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    """Возврат в главное меню"""
    user = await get_or_create_user(callback.from_user.id)
    
    welcome_text = f"""🎰 *Главное меню* 🎰

💰 *Баланс:* ${user['balance']:.2f}
👤 *ID:* {user['id']}
🎯 *Стрик:* {user['daily_streak']} дней
👥 *Рефералы:* +${user['referral_bonus']:.2f}

_Выберите действие:_"""
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=None,
        parse_mode="Markdown"
    )
    await callback.message.answer(
        "Вы в главном меню:",
        reply_markup=kb.get_main_menu()
    )
    await callback.answer()