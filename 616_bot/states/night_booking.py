from aiogram.fsm.state import State, StatesGroup


class NightBooking(StatesGroup):
    date = State()
