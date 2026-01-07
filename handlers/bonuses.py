from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
import random
import keyboards as kb
from database import get_or_create_user, update_balance
from config import config

router = Router()

class BonusStates(StatesGroup):
    waiting_promocode = State()

@router.message(F.text == "🎁 Бонусы")
async def show_bonuses(message: Message):
    """Показать меню бонусов"""
    user = await get_or_create_user(message.from_user.id)
    
    bonuses_text = f"""🎁 *БОНУСНАЯ СИСТЕМА*

💰 *Доступные бонусы:*
  • 🎁 Ежедневный подарок (стрик: {user['daily_streak']})
  • 🎡 Колесо фортуны (раз в 3 дня)
  • 🎫 Промокоды от админов
  • 📋 Еженедельные задания

👥 *Реферальные бонусы:*
  • 1 уровень: 5% от депозитов
  • 2 уровень: 3% от депозитов
  • 3 уровень: 1% от депозитов
  • Бонус за 10 активных рефералов: $50

🏆 *VIP программа:*
  • Уровень 1: +5% к ежедневному бонусу
  • Уровень 2: +10% и увеличенные лимиты
  • Уровень 3: +20% и персональный менеджер

_Выберите бонус:_"""
    
    await message.answer(
        bonuses_text,
        reply_markup=kb.get_bonus_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "daily_bonus")
async def claim_daily_bonus(callback: CallbackQuery):
    """Получить ежедневный бонус"""
    user = await get_or_create_user(callback.from_user.id)
    
    today = datetime.now().date()
    last_daily = None
    
    if user['last_daily']:
        last_daily = datetime.strptime(user['last_daily'], '%Y-%m-%d %H:%M:%S').date()
    
    # Проверяем, можно ли получить бонус сегодня
    if last_daily == today:
        await callback.answer(
            "❌ Вы уже получали бонус сегодня! Приходите завтра.",
            show_alert=True
        )
        return
    
    # Рассчитываем бонус
    streak = user['daily_streak']
    if last_daily and today - last_daily == timedelta(days=1):
        streak += 1
    else:
        streak = 1
    
    # Ограничиваем стрик 7 днями
    streak = min(streak, 7)
    bonus_amount = config.DAILY_BONUS[streak - 1]
    
    # VIP множитель
    vip_multiplier = 1 + (user['vip_level'] * 0.05)
    bonus_amount *= vip_multiplier
    
    # Зачисляем бонус
    await update_balance(callback.from_user.id, bonus_amount, "daily_bonus")
    
    # Обновляем данные пользователя
    from database import aiosqlite
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute("""
            UPDATE users 
            SET daily_streak = ?, last_daily = ?
            WHERE user_id = ?
        """, (streak, today, callback.from_user.id))
        await db.commit()
    
    bonus_text = f"""🎁 *ЕЖЕДНЕВНЫЙ БОНУС ПОЛУЧЕН!*

💰 *Сумма бонуса:* ${bonus_amount:.2f}
📅 *Текущий стрик:* {streak} дней
👑 *VIP бонус:* +{user['vip_level'] * 5}%

📊 *Прогресс бонусов:*
"""
    
    for day in range(7):
        day_bonus = config.DAILY_BONUS[day]
        if day + 1 <= streak:
            bonus_text += f"  ✅ День {day+1}: ${day_bonus:.2f}\n"
        else:
            bonus_text += f"  ◻️ День {day+1}: ${day_bonus:.2f}\n"
    
    bonus_text += f"\n💰 *Новый баланс:* ${user['balance'] + bonus_amount:.2f}"
    
    await callback.message.edit_text(
        bonus_text,
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "wheel_of_fortune")
async def spin_wheel(callback: CallbackQuery):
    """Колесо фортуны"""
    user = await get_or_create_user(callback.from_user.id)
    
    # Проверяем, когда последний раз крутили колесо
    # Для упрощения пропустим эту проверку
    
    prizes = [
        ("💰", "x2 Депозита", 50),
        ("🎰", "Фриспины x10", 30),
        ("💎", "$100", 15),
        ("🏆", "VIP 1 месяц", 10),
        ("🎁", "$20", 25),
        ("✨", "Удвоение бонуса", 20)
    ]
    
    # Вращаем колесо
    result = random.choices(
        prizes,
        weights=[p[2] for p in prizes]
    )[0]
    
    prize_text = f"""🎡 *КОЛЕСО ФОРТУНЫ*

🎯 *Результат:* {result[0]} {result[1]}
🎉 *Поздравляем!*

💰 *Описание приза:*
"""
    
    if "Депозита" in result[1]:
        prize_text += "Следующий депозит будет удвоен!"
        # Здесь должна быть логика применения бонуса
    elif "Фриспины" in result[1]:
        prize_text += "10 бесплатных спинов в слотах!"
    elif "$100" in result[1]:
        await update_balance(callback.from_user.id, 100, "wheel_bonus")
        prize_text += "$100 зачислены на ваш баланс!"
    elif "VIP" in result[1]:
        prize_text += "VIP статус на 1 месяц!"
    elif "$20" in result[1]:
        await update_balance(callback.from_user.id, 20, "wheel_bonus")
        prize_text += "$20 зачислены на ваш баланс!"
    else:
        prize_text += "Удвоение следующего ежедневного бонуса!"
    
    prize_text += f"\n\n🎡 *Следующее вращение:* через 3 дня"
    
    await callback.message.edit_text(
        prize_text,
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "enter_promocode")
async def enter_promocode(callback: CallbackQuery, state: FSMContext):
    """Ввод промокода"""
    await state.set_state(BonusStates.waiting_promocode)
    
    await callback.message.edit_text(
        "🎫 *АКТИВАЦИЯ ПРОМОКОДА*\n\n"
        "Введите промокод для получения бонуса:",
        reply_markup=kb.get_back_button(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(BonusStates.waiting_promocode)
async def process_promocode(message: Message, state: FSMContext):
    """Обработка промокода"""
    promocode = message.text.strip().upper()
    
    # Здесь должна быть проверка промокода в БД
    # Для примепа просто выдадим фиксированный бонус
    
    # Простая проверка (в реальном проекте проверять в БД)
    valid_promocodes = {
        "WELCOME100": 100,
        "BONUS50": 50,
        "FREESPINS": 0  # Фриспины
    }
    
    if promocode in valid_promocodes:
        bonus = valid_promocodes[promocode]
        
        if bonus > 0:
            await update_balance(message.from_user.id, bonus, "promocode")
            user = await get_or_create_user(message.from_user.id)
            
            await message.answer(
                f"✅ *ПРОМОКОД АКТИВИРОВАН!*\n\n"
                f"🎫 *Код:* {promocode}\n"
                f"💰 *Бонус:* ${bonus:.2f}\n"
                f"💵 *Новый баланс:* ${user['balance']:.2f}\n\n"
                f"_Спасибо, что вы с нами!_ 🎰",
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                "✅ *ПРОМОКОД АКТИВИРОВАН!*\n\n"
                "🎫 *Код:* FREESPINS\n"
                "🎰 *Бонус:* 20 Фриспинов\n\n"
                "_Используйте их в слотах!_ 🎰",
                parse_mode="Markdown"
            )
    else:
        await message.answer(
            "❌ *ПРОМОКОД НЕ НАЙДЕН*\n\n"
            "Проверьте правильность ввода или "
            "запросите актуальные промокоды у поддержки.",
            parse_mode="Markdown"
        )
    
    await state.clear()