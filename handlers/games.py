from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import random
import keyboards as kb
from database import get_or_create_user, update_balance, create_game_record
from config import config

router = Router()

class GameStates(StatesGroup):
    waiting_bet = State()
    playing_slots = State()
    playing_dice = State()
    playing_coin = State()

@router.message(F.text == "🎰 Игры")
async def show_games_menu(message: Message):
    """Показать меню игр"""
    await message.answer(
        "🎮 *Выберите игру:*",
        reply_markup=kb.get_games_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "game_slots")
async def start_slots(callback: CallbackQuery, state: FSMContext):
    """Начать игру в слоты"""
    user = await get_or_create_user(callback.from_user.id)
    
    if user['balance'] < 1:
        await callback.answer("❌ Минимальная ставка $1!", show_alert=True)
        return
    
    await state.set_state(GameStates.waiting_bet)
    await state.update_data(game_type="slots")
    
    await callback.message.edit_text(
        f"🎰 *ИГРА: СЛОТЫ*\n\n"
        f"💰 Ваш баланс: ${user['balance']:.2f}\n"
        f"🎯 Минимальная ставка: $1\n\n"
        f"*Символы и множители:*\n"
        f"🍒 x2    🍋 x3    🍊 x4\n"
        f"🍉 x5    💎 x10   🎰 x50\n"
        f"💰 x100 (джекпот)\n\n"
        f"*Выберите сумму ставки:*",
        reply_markup=kb.get_bet_amounts(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("bet_"))
async def place_bet(callback: CallbackQuery, state: FSMContext):
    """Сделать ставку"""
    bet_amount = float(callback.data.split("_")[1])
    user = await get_or_create_user(callback.from_user.id)
    
    if user['balance'] < bet_amount:
        await callback.answer(f"❌ Недостаточно средств!", show_alert=True)
        return
    
    data = await state.get_data()
    game_type = data.get("game_type")
    
    # Снимаем ставку
    await update_balance(callback.from_user.id, -bet_amount, "bet")
    
    if game_type == "slots":
        await play_slots(callback, bet_amount, state)
    elif game_type == "dice":
        await play_dice(callback, bet_amount, state)
    elif game_type == "coin":
        await play_coin(callback, bet_amount, state)

async def play_slots(callback: CallbackQuery, bet_amount: float, state: FSMContext):
    """Игра в слоты"""
    # Символы и их множители
    symbols = {
        "🍒": 2,
        "🍋": 3,
        "🍊": 4,
        "🍉": 5,
        "💎": 10,
        "🎰": 50,
        "💰": 100  # Джекпот
    }
    
    # Генерация барабанов
    reels = [
        random.choice(list(symbols.keys())),
        random.choice(list(symbols.keys())),
        random.choice(list(symbols.keys()))
    ]
    
    # Проверка выигрыша
    win_multiplier = 0
    result_text = ""
    
    if reels[0] == reels[1] == reels[2]:
        # 3 одинаковых символа
        win_multiplier = symbols[reels[0]]
        result_text = f"🎉 *ДЖЕКПОТ!* x{win_multiplier}"
    elif reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
        # 2 одинаковых символа
        win_multiplier = 2
        result_text = f"✅ *Выигрыш!* x2"
    else:
        result_text = "❌ *Проигрыш*"
    
    win_amount = bet_amount * win_multiplier if win_multiplier > 0 else 0
    
    if win_amount > 0:
        # Зачисляем выигрыш
        await update_balance(callback.from_user.id, win_amount, "win")
    
    # Записываем игру
    await create_game_record(
        user_id=callback.from_user.id,
        game_type="slots",
        bet_amount=bet_amount,
        win_amount=win_amount,
        result=f"{reels[0]}{reels[1]}{reels[2]}"
    )
    
    user = await get_or_create_user(callback.from_user.id)
    
    result_message = (
        f"🎰 *РЕЗУЛЬТАТ СЛОТОВ*\n\n"
        f"🌀 *Барабаны:* [{reels[0]}][{reels[1]}][{reels[2]}]\n\n"
        f"💰 *Ставка:* ${bet_amount:.2f}\n"
        f"🎯 *Результат:* {result_text}\n"
        f"🏆 *Выигрыш:* ${win_amount:.2f}\n\n"
        f"💵 *Новый баланс:* ${user['balance']:.2f}\n\n"
        f"_Для повторной игры нажмите 🎰 Игры_"
    )
    
    await callback.message.edit_text(
        result_message,
        reply_markup=kb.get_games_menu(),
        parse_mode="Markdown"
    )
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "game_dice")
async def start_dice(callback: CallbackQuery, state: FSMContext):
    """Начать игру в кости"""
    user = await get_or_create_user(callback.from_user.id)
    
    if user['balance'] < 1:
        await callback.answer("❌ Минимальная ставка $1!", show_alert=True)
        return
    
    await state.set_state(GameStates.waiting_bet)
    await state.update_data(game_type="dice")
    
    await callback.message.edit_text(
        f"🎲 *ИГРА: КОСТИ*\n\n"
        f"💰 Ваш баланс: ${user['balance']:.2f}\n"
        f"🎯 Правила:\n"
        f"• Угадайте число от 1 до 6\n"
        f"• Выигрыш x6 за точное совпадение\n"
        f"• Или выберите 'Больше/Меньше'\n\n"
        f"*Выберите сумму ставки:*",
        reply_markup=kb.get_bet_amounts(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "game_coin")
async def start_coin(callback: CallbackQuery, state: FSMContext):
    """Начать игру в орла/решку"""
    user = await get_or_create_user(callback.from_user.id)
    
    if user['balance'] < 1:
        await callback.answer("❌ Минимальная ставка $1!", show_alert=True)
        return
    
    await state.set_state(GameStates.waiting_bet)
    await state.update_data(game_type="coin")
    
    await callback.message.edit_text(
        f"🪙 *ИГРА: МОНЕТКА*\n\n"
        f"💰 Ваш баланс: ${user['balance']:.2f}\n"
        f"🎯 Правила:\n"
        f"• Угадайте сторону монеты\n"
        f"• Выигрыш x2 за правильный выбор\n"
        f"• Шанс 50/50\n\n"
        f"*Выберите сумму ставки:*",
        reply_markup=kb.get_bet_amounts(),
        parse_mode="Markdown"
    )
    await callback.answer()