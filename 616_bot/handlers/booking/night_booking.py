from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards import (
    sound_engineers,
    keyboard_available_dates,
    keyboard_available_dates_inline,
    start_time_keyboard,
    end_time_keyboard,
    approvement_keyboard,
)
from states.booking import Booking
from states.start import Start
from loguru import logger
from handlers.start.start import start_booking_handler
import os


@logger.catch()
async def night_date_handler(message: Message, state: FSMContext) -> None:
    pass
