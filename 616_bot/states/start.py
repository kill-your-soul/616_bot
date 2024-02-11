from aiogram.fsm.state import State, StatesGroup


class Start(StatesGroup):
    number = State()
    booking = State()
