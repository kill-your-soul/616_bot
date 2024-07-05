from aiogram.fsm.state import State, StatesGroup


class Admin(StatesGroup):
    menu = State()
    price = State()
    set_price = State()
    get_id = State()