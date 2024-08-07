from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    ReplyKeyboardBuilder,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from loguru import logger
from database import (
    get_available_dates,
    get_available_start_time,
    get_available_end_time,
    get_available_night_start_time,
    get_available_end_time_night,
    get_prices_from_db,
    insert_temp,
)


async def keyboard_available_dates() -> ReplyKeyboardMarkup:
    dates = await get_available_dates()
    builder = ReplyKeyboardBuilder()
    for date in dates:
        builder.button(text=f"{date}")
    builder.button(text="Назад")
    builder.adjust(5, 5, 4, 1)
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)


async def keyboard_available_dates_inline() -> InlineKeyboardMarkup:
    dates = await get_available_dates()
    builder = InlineKeyboardBuilder()
    for date in dates:
        builder.button(text=f"{date}", callback_data=f"date:{date}")
    builder.button(text="Назад", callback_data="back")
    builder.adjust(5, 5, 4, 1)
    logger.debug(builder)
    return builder.as_markup()


async def to_booking() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Начать бронирование")
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)


async def keyboard_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="час на студии (день)").button(text="час на студии (ночь)")
    builder.button(text="аренда студии (день)").button(text="ночь на студии")
    builder.adjust(2, 2)
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)


async def keyboard_menu_with_back() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="час на студии (день)").button(text="час на студии (ночь)")
    builder.button(text="аренда студии (день)").button(text="ночь на студии")
    builder.button(text="Назад")
    builder.adjust(2, 2, 1)
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)


async def sound_engineers() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="VICEYY").button(text="dieze").button(text="akseniy").button(
        text="не имеет значения"
    ).button(text="Назад")
    builder.adjust(2, 2, 1)
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)


async def start_time_night_keyboard(day) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    start_times = await get_available_night_start_time(int(day))
    logger.debug(start_times)
    for time in start_times:
        builder.button(text=f"{time}")
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)


async def start_time_keyboard(day) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    start_times = await get_available_start_time(int(day))
    logger.debug(start_times)
    for time in start_times:
        builder.button(text=f"{time}")
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)


async def end_time_keyboard(day, start_time) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    end_times = await get_available_end_time(int(day), start_time)
    # logger.debug(end_time)
    for time in end_times:
        builder.button(text=f"{time}")
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)


async def end_time_keyboard_night(day, start_time) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    end_times: list[dict[str, str]] = await get_available_end_time_night(
        int(day), start_time
    )
    logger.debug(end_times)
    for time in end_times:
        builder.button(text=f"{time}")
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)


async def approvement_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Записаться")
    builder.row()
    builder.button(text="Назад")
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)


async def pay_inline_keyboard(chat_id: int, data: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    _id = await insert_temp(data=data)
    builder.button(text="Оплатил", callback_data=str(chat_id) + ";" + _id)
    # logger.debug(str(service).replace(' ', ''))
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)


async def get_admins_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Изменить цену").button(text="Посмотреть пользователей").button(
        text="Добавить админа"
    )
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)

async def get_prices_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for item in get_prices_from_db():
        builder.button(text=item["title"])
        logger.debug(f"{item['title']} {item['price']}")
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)