from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter

from states.start import Start
from . import start


def setup_handlers() -> Router:
    router = Router()
    router.message.register(start.command_start_handler, CommandStart())
    router.message.register(start.number_handler, StateFilter(Start.number))
    router.message.register(start.start_booking_handler, StateFilter(Start.booking))
    return router
