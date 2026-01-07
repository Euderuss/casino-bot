from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import keyboards as kb
from database import get_or_create_user

router = Router()

@router.message(F.text == "📊 Профиль")
async def show_profile(message: Message):
    """Показать профиль пользователя"""
    user = await get_or_create_user(message.from_user.id)
    
    # Рассчитываем прогресс до следующего уровня VIP
    exp_needed = (user['vip_level'] + 1) * 1000
    exp_progress = min(user['experience'] / exp_needed * 100, 100)
    
    profile_text = f"""📊 *ВАШ ПРОФИЛЬ*

👤 *Основное:*
  • ID: {user['id']}
  • Имя: {user['first_name']}
  • Юзернейм: @{user['username'] or 'не указан'}
  • Дата регистрации: {user['created_at'][:10]}

💰 *Финансы:*
  • Баланс: ${user['balance']:.2f}
  • Всего депозитов: ${user['total_deposited']:.2f}
  • Всего выводов: ${user['total_withdrawn']:.2f}
  • Реферальные: ${user['referral_bonus']:.2f}

🎮 *Игровая статистика:*
  • Сыграно игр: {user['games_played']}
  • Выиграно: ${user['total_won']:.2f}
  • Проиграно: ${user['total_lost']:.2f}
  • Прибыль: ${user['total_won'] - user['total_lost']:.2f}

🏆 *Достижения:*
  • VIP уровень: {user['vip_level']}
  • Опыт: {user['experience']}/{exp_needed}
  • Ежедневный стрик: {user['daily_streak']} дней
  • Рефералов: 0

👥 *Реферальная ссылка:*
  `https://t.me/your_bot?start={user['referral_code']}`
  
  Приводи друзей и получай до 9%!
  1 уровень: 5%
  2 уровень: 3%
  3 уровень: 1%"""
    
    await message.answer(
        profile_text,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "transactions")
async def show_transactions(callback: CallbackQuery):
    """Показать историю транзакций"""
    # Здесь должна быть логика получения истории транзакций из БД
    # Для примепа просто покажем заглушку
    
    transactions_text = """📋 *ИСТОРИЯ ТРАНЗАКЦИЙ*

⏳ *За сегодня:*
  • 12:30 Пополнение +$100 ✅
  • 14:45 Слоты -$10 ✅
  • 15:20 Выигрыш +$50 ✅
  • 16:10 Вывод -$20 ⏳

📅 *За неделю:*
  • Всего операций: 24
  • Пополнений: $500
  • Выводов: $200
  • Игровых операций: 22

💾 *Полная история:* доступна в веб-версии"""
    
    await callback.message.edit_text(
        transactions_text,
        parse_mode="Markdown"
    )
    await callback.answer()