from aiogram.types import Message

# from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from states.start import Start
from states.booking import Booking
from loguru import logger
from keyboards import to_booking, keyboard_menu


async def command_start_handler(message: Message, state: FSMContext) -> None:
    logger.debug(f"New user with username @{message.from_user.username}")
    await state.update_data(username=message.from_user.username)
    await message.answer(
        "Привет! Это бот для бронирования ROOM616.\n\n"
        "Всем новым клиентам студии необходимо оставить свой номер телефона, чтобы наш менеджер смог связаться с тобой при необходимости.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Start.number)


async def number_handler(message: Message, state: FSMContext) -> None:
    logger.debug(f"User number: {message.text}")
    await state.update_data(number=message.text)
    keyboard = await to_booking()
    await message.answer(
        "Перед бронью студии необходимо ознакомиться с правилами бронирования и пребывания в ROOM616(ссылка). \n\n"
        "<i>Обрати внимание: незнание правил не освобождает от ответственности.</i> ",
        reply_markup=keyboard,
        parse_mode="html",
    )
    await state.set_state(Start.booking)


async def start_booking_handler(message: Message, state: FSMContext) -> None:
    keyboard = await keyboard_menu()
    await message.answer(
        "Информация о доступных услугах:\n\n"
        "<b>Час на студии день</b>: услуга предоставляется с 8:00 до 22:00\n\n"
        "<b>Час на студии ночь</b>: услуга предоставляется с 22:00 до 6:00\n\n"
        "<b>Ночь на студии</b>: услуга предоставляется с 22:00 до 6:00 и только в присутствии сотрудника ROOM616\n\n"
        "<b>Аренда</b>: час на студии без звукорежиссера, предоставляется с 8:00 до 22:00\n\n"
        "Выбери услугу: ",
        reply_markup=keyboard,
        parse_mode="html",
    )
    await state.update_data(service="аренда студии (день)")
    await state.set_state(Booking.menu)
