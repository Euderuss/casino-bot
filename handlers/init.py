from aiogram import Dispatcher
from .start import router as start_router
from .games import router as games_router
from .admin import router as admin_router
from .payments import router as payments_router
from .profile import router as profile_router
from .bonuses import router as bonuses_router

def register_handlers(dp: Dispatcher):
    """Регистрация всех роутеров"""
    dp.include_router(start_router)
    dp.include_router(games_router)
    dp.include_router(admin_router)
    dp.include_router(payments_router)
    dp.include_router(profile_router)
    dp.include_router(bonuses_router)