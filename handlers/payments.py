from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiohttp
import json
import keyboards as kb
from database import get_or_create_user, update_balance
from config import config

router = Router()

class PaymentStates(StatesGroup):
    waiting_deposit_amount = State()
    waiting_withdraw_amount = State()
    waiting_withdraw_wallet = State()

@router.message(F.text == "💰 Баланс")
async def show_balance(message: Message):
    """Показать баланс"""
    user = await get_or_create_user(message.from_user.id)
    
    balance_text = f"""💰 *ВАШ БАЛАНС*

💵 *Доступно:* ${user['balance']:.2f}
🏆 *VIP уровень:* {user['vip_level']}
📊 *Статистика:*
  • Депозиты: ${user['total_deposited']:.2f}
  • Выводы: ${user['total_withdrawn']:.2f}
  • Выиграно: ${user['total_won']:.2f}

💳 *Пополнение:* от ${config.MIN_DEPOSIT}
🏦 *Вывод:* от ${config.MIN_WITHDRAW} (комиссия {config.WITHDRAW_FEE*100}%)

_Выберите действие:_"""
    
    await message.answer(
        balance_text,
        reply_markup=kb.get_balance_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "deposit")
async def start_deposit(callback: CallbackQuery):
    """Начать пополнение"""
    user = await get_or_create_user(callback.from_user.id)
    
    deposit_text = f"""💳 *ПОПОЛНЕНИЕ БАЛАНСА*

💰 *Текущий баланс:* ${user['balance']:.2f}
💎 *Минимальный депозит:* ${config.MIN_DEPOSIT}
⚡ *Мгновенное зачисление*

📊 *Текущие курсы (примерные):*
  • 1 TON ≈ $5.00
  • 1 USDT = $1.00
  • 1 USDC = $1.00

⚠️ *Внимание:* Используйте только указанные сети!

_Выберите валюту для пополнения:_"""
    
    await callback.message.edit_text(
        deposit_text,
        reply_markup=kb.get_deposit_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "deposit_ton")
async def deposit_ton(callback: CallbackQuery, state: FSMContext):
    """Пополнение TON"""
    await state.set_state(PaymentStates.waiting_deposit_amount)
    await state.update_data(currency="TON")
    
    await callback.message.edit_text(
        "💎 *ПОПОЛНЕНИЕ TON*\n\n"
        "Введите сумму в долларах (USD):\n"
        f"Минимум: ${config.MIN_DEPOSIT}",
        reply_markup=kb.get_back_button(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "deposit_usdt")
async def deposit_usdt(callback: CallbackQuery, state: FSMContext):
    """Пополнение USDT"""
    await state.set_state(PaymentStates.waiting_deposit_amount)
    await state.update_data(currency="USDT")
    
    await callback.message.edit_text(
        "💵 *ПОПОЛНЕНИЕ USDT (TRC20)*\n\n"
        "Введите сумму в долларах (USD):\n"
        f"Минимум: ${config.MIN_DEPOSIT}",
        reply_markup=kb.get_back_button(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(PaymentStates.waiting_deposit_amount)
async def process_deposit_amount(message: Message, state: FSMContext):
    """Обработка суммы депозита"""
    try:
        amount = float(message.text)
        
        if amount < config.MIN_DEPOSIT:
            await message.answer(
                f"❌ Минимальная сумма депозита ${config.MIN_DEPOSIT}!"
            )
            return
        
        data = await state.get_data()
        currency = data['currency']
        
        # Здесь должна быть интеграция с Crypto Pay
        # Для примера просто зачисляем средства
        await update_balance(message.from_user.id, amount, "deposit")
        
        user = await get_or_create_user(message.from_user.id)
        
        await message.answer(
            f"✅ *Депозит успешно зачислен!*\n\n"
            f"💵 *Сумма:* ${amount:.2f}\n"
            f"💰 *Новый баланс:* ${user['balance']:.2f}\n"
            f"📅 *Дата:* {message.date.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"_Теперь вы можете начать играть!_ 🎰",
            parse_mode="Markdown"
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Введите корректную сумму!")

@router.callback_query(F.data == "withdraw")
async def start_withdraw(callback: CallbackQuery, state: FSMContext):
    """Начать вывод"""
    user = await get_or_create_user(callback.from_user.id)
    
    if user['balance'] < config.MIN_WITHDRAW:
        await callback.answer(
            f"❌ Минимальная сумма вывода ${config.MIN_WITHDRAW}!",
            show_alert=True
        )
        return
    
    withdraw_text = f"""🏦 *ВЫВОД СРЕДСТВ*

💰 *Доступно:* ${user['balance']:.2f}
💸 *Минимальный вывод:* ${config.MIN_WITHDRAW}
⚠️ *Комиссия:* {config.WITHDRAW_FEE*100}%
⏱️ *Время обработки:* 5-30 минут

📋 *Доступные сети:*
  • TON (The Open Network)
  • TRC20 (USDT/USDC)

_Введите сумму для вывода:_"""
    
    await state.set_state(PaymentStates.waiting_withdraw_amount)
    
    await callback.message.edit_text(
        withdraw_text,
        reply_markup=kb.get_back_button(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(PaymentStates.waiting_withdraw_amount)
async def process_withdraw_amount(message: Message, state: FSMContext):
    """Обработка суммы вывода"""
    try:
        amount = float(message.text)
        user = await get_or_create_user(message.from_user.id)
        
        if amount < config.MIN_WITHDRAW:
            await message.answer(
                f"❌ Минимальная сумма вывода ${config.MIN_WITHDRAW}!"
            )
            return
        
        if amount > user['balance']:
            await message.answer(
                f"❌ Недостаточно средств! Доступно: ${user['balance']:.2f}"
            )
            return
        
        # Рассчитываем сумму с учетом комиссии
        fee = amount * config.WITHDRAW_FEE
        received = amount - fee
        
        await state.update_data(
            withdraw_amount=amount,
            withdraw_fee=fee,
            withdraw_received=received
        )
        await state.set_state(PaymentStates.waiting_withdraw_wallet)
        
        await message.answer(
            f"📋 *ПОДТВЕРЖДЕНИЕ ВЫВОДА*\n\n"
            f"💵 *Сумма вывода:* ${amount:.2f}\n"
            f"💸 *Комиссия ({config.WITHDRAW_FEE*100}%):* ${fee:.2f}\n"
            f"💰 *К получению:* ${received:.2f}\n\n"
            f"Введите адрес кошелька для получения средств:",
            reply_markup=kb.get_back_button(),
            parse_mode="Markdown"
        )
        
    except ValueError:
        await message.answer("❌ Введите корректную сумму!")

@router.message(PaymentStates.waiting_withdraw_wallet)
async def process_withdraw_wallet(message: Message, state: FSMContext):
    """Обработка кошелька для вывода"""
    wallet = message.text.strip()
    
    # Простая валидация кошелька
    if len(wallet) < 10:
        await message.answer("❌ Неверный адрес кошелька!")
        return
    
    data = await state.get_data()
    amount = data['withdraw_amount']
    fee = data['withdraw_fee']
    received = data['withdraw_received']
    
    # Списываем средства
    await update_balance(message.from_user.id, -amount, "withdraw")
    
    user = await get_or_create_user(message.from_user.id)
    
    await message.answer(
        f"✅ *Заявка на вывод создана!*\n\n"
        f"📊 *Детали заявки:*\n"
        f"• Сумма: ${amount:.2f}\n"
        f"• Комиссия: ${fee:.2f}\n"
        f"• К получению: ${received:.2f}\n"
        f"• Кошелек: `{wallet[:10]}...{wallet[-10:]}`\n"
        f"• Статус: ⏳ Обработка\n\n"
        f"💰 *Новый баланс:* ${user['balance']:.2f}\n\n"
        f"_Заявка будет обработана в течение 30 минут._",
        parse_mode="Markdown",
        reply_markup=kb.get_back_button()
    )
    
    # Здесь должна быть логика отправки средств
    # Например, через Crypto Pay API
    
    await state.clear()