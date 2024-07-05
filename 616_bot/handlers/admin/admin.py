from loguru import logger
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.decorators import admin_only
from states.admin import Admin

from keyboards import get_admins_keyboard, get_prices_keyboard
from database import add_admin_in_db, get_users, update_price

@logger.catch()
@admin_only
async def start(message: Message, state: FSMContext, **kwargs):
    keyboard = await get_admins_keyboard()
    await message.answer("Welcome to admin page", reply_markup=keyboard)

    await state.set_state(Admin.menu)


@logger.catch()
@admin_only
async def show_prices(message: Message, state: FSMContext, **kwargs):
    keyboard = await get_prices_keyboard()
    await message.answer("Какую цену вы хотите заменить", reply_markup=keyboard)
    # await state.update_data(title=message.text)
    await state.set_state(Admin.price)

@logger.catch()
@admin_only
async def change_price(message: Message, state: FSMContext, **kwargs):
    await message.answer("Напишите новую цену")
    await state.update_data(title=message.text)
    await state.set_state(Admin.set_price)


@logger.catch()
@admin_only
async def set_price(message: Message, state: FSMContext, **kwargs):
    data = await state.get_data()
    update_price(data["title"], message.text)
    await message.answer("Новая цена успешно поставлена")
    await message.answer("Чтобы продолжить или начать нажмите /start или /admin")
    await state.clear()

@logger.catch()
@admin_only
async def show_users(message: Message, state: FSMContext, **kwargs):
    text = ""
    users = get_users()
    for user in users:
        text += f"username: {user['username']} -- номер телефона: {user['number']}\n\n"
    await message.answer(text=text)


@logger.catch()
@admin_only
async def add_admin(message: Message, state: FSMContext, **kwargs):
    await message.answer("Отправь id на нового админа в формате 412163627\n\nполучить его можно тут @username_to_id_bot")
    await state.set_state(Admin.get_id)

@logger.catch()
@admin_only
async def get_id(message: Message, state: FSMContext, **kwargs):
    await message.answer("Админ успешно добавлен")
    add_admin_in_db(message.text)

