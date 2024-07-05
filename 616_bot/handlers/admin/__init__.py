from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.filters.command import Command
from . import admin
from states.admin import Admin


def setup_handlers() -> Router:
    router = Router()
    router.message.register(admin.start, Command("admin"))
    router.message.register(admin.show_prices, F.text == "Изменить цену", StateFilter(Admin.menu))
    router.message.register(admin.change_price, StateFilter(Admin.price))
    router.message.register(admin.change_price, StateFilter(Admin.price))
    router.message.register(admin.set_price, StateFilter(Admin.set_price))
    router.message.register(admin.show_users, F.text == "Посмотреть пользователей", StateFilter(Admin.menu))
    router.message.register(admin.add_admin, F.text == "Добавить админа", StateFilter(Admin.menu))
    router.message.register(admin.get_id, StateFilter(Admin.get_id))
    return router