from aiogram import types
from aiogram.fsm.context import FSMContext
from loguru import logger
from database import get_admins


def admin_only(handler):
    async def wrapper(message: types.Message, state: FSMContext, *args, **kwargs):
        if message.from_user.id not in get_admins():
            logger.info(f"Not admin {message.from_user.username}")
            await message.answer("Вы не администратор")
            return
        return await handler(message, state, *args, **kwargs)
    return wrapper
