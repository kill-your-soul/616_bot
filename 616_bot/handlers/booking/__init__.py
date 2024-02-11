from aiogram import F, Router
from aiogram.filters import StateFilter

from states.booking import Booking
from states.night_booking import NightBooking
from . import booking


def setup_handlers() -> Router:
    router = Router()
    router.message.register(booking.back, F.text == "Назад")
    router.message.register(
        booking.menu_handler,
        F.text == "час на студии (ночь)",
        StateFilter(Booking.menu),
    )
    router.message.register(
        booking.menu_handler,
        F.text == "час на студии (день)",
        StateFilter(Booking.menu),
    )
    router.message.register(
        booking.menu_handler,
        F.text == "ночь на студии",
        StateFilter(Booking.menu),
    )
    router.message.register(
        booking.date_handler,
        F.text == "аренда студии (день)",
        StateFilter(Booking.menu),
    )
    router.message.register(
        booking.engineer_handler,
        StateFilter(Booking.engineer),
    )
    router.message.register(booking.start_time_handler, StateFilter(Booking.start_time))
    router.message.register(booking.end_time_handler, StateFilter(Booking.end_time))
    router.message.register(
        booking.approvement_handler, StateFilter(Booking.approvement)
    )
    router.message.register(booking.end, StateFilter(Booking.end))
    router.message.register(
        booking.approvement_night_handler, StateFilter(NightBooking.date)
    )
    router.callback_query.register(booking.approve_handler)
    return router
