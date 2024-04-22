from aiogram.types import Message

# from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from states.start import Start
from states.booking import Booking
from loguru import logger
from database import check_user, create_user
from keyboards import to_booking, keyboard_menu


async def command_start_handler(message: Message, state: FSMContext) -> None:
    logger.debug(f"New user with username @{message.from_user.username}")
    await state.update_data(username=message.from_user.username)
    if await check_user(message.from_user.username):
        await start_booking_handler(message, state)
        logger.debug("Check user ok")
        return

    await message.answer(
        "Привет! Это бот для бронирования ROOM616.\n\n"
        "Всем новым клиентам студии необходимо оставить свой номер телефона, чтобы наш менеджер смог связаться с тобой при необходимости.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Start.number)


async def number_handler(message: Message, state: FSMContext) -> None:
    logger.debug(f"User number: {message.text}")
    await state.update_data(number=message.text)
    await create_user(message.from_user.username, message.text)
    keyboard = await to_booking()
    await message.answer(
        "Перед бронью студии необходимо ознакомиться с <a href='https://telegra.ph/Pravila-poseshcheniya-ROOM616-02-08'>правилами бронирования и пребывания в ROOM616</a>. \n\n"
        "<i>Обрати внимание: незнание правил не освобождает от ответственности.</i> ",
        reply_markup=keyboard,
        parse_mode="html",
    )
    await state.set_state(Start.booking)


async def start_booking_handler(message: Message, state: FSMContext) -> None:
    keyboard = await keyboard_menu()
    await state.update_data(name_of_engineer="Без звукаря")
    await message.answer(
        "Информация о доступных услугах:\n\n"
        "<b>Час на студии (день):</b>\n"
        "⌛️ услуга предоставляется с 10:00 до 22:00\n"
        "💰700р\n\n"
        "<b>Час на студии (ночь):</b> \n"
        "⌛️ услуга предоставляется с 22:00 до 10:00\n"
        "💰 900р:\n\n"
        "<b>Ночь на студии:</b> \n"
        "⌛️ услуга предоставляется с 22:00 до 6:00 и только в присутствии сотрудника ROOM616\n"
        "💰 5000р\n\n"
        "<b>Аренда (час на студии без звукорежиссера):</b>\n"
        "⌛️предоставляется с 8:00 до 22:00\n"
        "💰700р\n",
        reply_markup=keyboard,
        parse_mode="html",
    )
    await state.update_data(service="аренда студии (день)")
    await state.set_state(Booking.menu)
