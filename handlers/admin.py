from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import keyboards as kb
from database import get_all_users, get_total_stats, update_balance, get_user_stats
from config import config

router = Router()

class AdminStates(StatesGroup):
    waiting_user_id = State()
    waiting_balance_change = State()
    waiting_promocode = State()
    waiting_broadcast = State()

@router.message(F.from_user.id == config.ADMIN_ID, F.text == "/admin")
async def admin_panel(message: Message):
    """Панель администратора"""
    stats = await get_total_stats()
    
    admin_text = f"""👑 *ПАНЕЛЬ АДМИНИСТРАТОРА*

📊 *Общая статистика:*
  👥 Пользователей: {stats['total_users']}
  💰 Общий баланс: ${stats['total_balance']:.2f}
  📈 Депозиты: ${stats['total_deposits']:.2f}
  📉 Выводы: ${stats['total_withdrawals']:.2f}
  💸 Касса: ${stats['total_deposits'] - stats['total_withdrawals']:.2f}

⚡ *Быстрые действия:*
  • Управление пользователями
  • Изменение балансов
  • Создание промокодов
  • Рассылка сообщений

_Выберите действие:_"""
    
    await message.answer(
        admin_text,
        reply_markup=kb.get_admin_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.from_user.id == config.ADMIN_ID, F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """Общая статистика"""
    stats = await get_total_stats()
    
    stats_text = f"""📈 *ДЕТАЛЬНАЯ СТАТИСТИКА*

👥 *Пользователи:*
  • Всего: {stats['total_users']}
  • Онлайн: 0 (в разработке)
  • Новых сегодня: 0

💰 *Финансы:*
  • Общий баланс: ${stats['total_balance']:.2f}
  • Всего депозитов: ${stats['total_deposits']:.2f}
  • Всего выводов: ${stats['total_withdrawals']:.2f}
  • Чистая прибыль: ${stats['total_deposits'] - stats['total_withdrawals']:.2f}

🎮 *Игры:*
  • Всего игр: 0
  • Общий оборот: $0
  • RTP: 0%

📅 *За сегодня:*
  • Регистраций: 0
  • Депозитов: $0
  • Выводов: $0"""
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=kb.get_admin_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.from_user.id == config.ADMIN_ID, F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    """Список пользователей"""
    users = await get_all_users()
    
    users_list = "👥 *СПИСОК ПОЛЬЗОВАТЕЛЕЙ*\n\n"
    
    for i, user in enumerate(users[:10], 1):  # Показываем первые 10
        users_list += (
            f"{i}. ID: {user['user_id']}\n"
            f"   👤 {user['first_name']} (@{user['username'] or 'нет'})\n"
            f"   💰 ${user['balance']:.2f}\n"
            f"   🎮 Игр: {user['games_played']}\n\n"
        )
    
    if len(users) > 10:
        users_list += f"... и еще {len(users) - 10} пользователей"
    
    await callback.message.edit_text(
        users_list,
        reply_markup=kb.get_admin_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.from_user.id == config.ADMIN_ID, F.data == "admin_balance")
async def admin_balance(callback: CallbackQuery, state: FSMContext):
    """Изменение баланса пользователя"""
    await state.set_state(AdminStates.waiting_user_id)
    
    await callback.message.edit_text(
        "👤 *ИЗМЕНЕНИЕ БАЛАНСА*\n\n"
        "Введите ID пользователя:",
        reply_markup=kb.get_back_button(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(F.from_user.id == config.ADMIN_ID, AdminStates.waiting_user_id)
async def process_user_id(message: Message, state: FSMContext):
    """Обработка ID пользователя"""
    try:
        user_id = int(message.text)
        await state.update_data(target_user_id=user_id)
        await state.set_state(AdminStates.waiting_balance_change)
        
        await message.answer(
            f"✅ Пользователь найден: {user_id}\n\n"
            f"Введите сумму для изменения (используйте + для пополнения, - для списания):\n"
            f"Пример: +100 или -50",
            reply_markup=kb.get_back_button()
        )
    except ValueError:
        await message.answer("❌ Неверный ID! Введите числовой ID:")

@router.message(F.from_user.id == config.ADMIN_ID, AdminStates.waiting_balance_change)
async def process_balance_change(message: Message, state: FSMContext):
    """Обработка изменения баланса"""
    try:
        amount_str = message.text.strip()
        operation = amount_str[0]
        amount = float(amount_str[1:])
        
        if operation not in ['+', '-']:
            raise ValueError
        
        data = await state.get_data()
        user_id = data['target_user_id']
        
        # Изменяем баланс
        await update_balance(user_id, amount if operation == '+' else -amount, "admin")
        
        user = await get_user_stats(user_id)
        
        await message.answer(
            f"✅ Баланс пользователя {user_id} изменен!\n\n"
            f"📊 *Новая статистика:*\n"
            f"• Баланс: ${user['balance']:.2f}\n"
            f"• Всего депозитов: ${user['total_deposited']:.2f}\n"
            f"• Выигрыши: ${user['total_won']:.2f}\n"
            f"• Проигрыши: ${user['total_lost']:.2f}",
            parse_mode="Markdown"
        )
        
        await state.clear()
        
    except (ValueError, IndexError):
        await message.answer(
            "❌ Неверный формат! Используйте:\n"
            "+100 для пополнения\n"
            "-50 для списания"
        )