from aiogram.fsm.state import State, StatesGroup


class Booking(StatesGroup):
    menu = State()
    choose = State()
    engineer = State()
    date = State()
    start_time = State()
    end_time = State()
    approvement = State()
    end = State()
    waiting_for_pay = State()
