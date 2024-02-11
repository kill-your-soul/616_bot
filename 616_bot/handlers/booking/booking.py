from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards import (
    sound_engineers,
    keyboard_available_dates,
    keyboard_available_dates_inline,
    start_time_keyboard,
    end_time_keyboard,
    approvement_keyboard,
    pay_inline_keyboard,
)
from states.booking import Booking
from states.night_booking import NightBooking
from states.start import Start
from loguru import logger
from handlers.start.start import start_booking_handler
from database import write_booking
from typing import Dict, Any
import os
import json


@logger.catch()
async def menu_handler(message: Message, state: FSMContext):
    logger.debug(message.text)
    await state.update_data(service=message.text)
    keyboard = await sound_engineers()
    await message.answer(
        "Выбери звукорежжисера:\n\n"

"VICEYY (ссылка на примеры работ)\n"
"Стаж: 6 лет\n"
"Основные жанры: hip-hop, new school rap, underground\n\n"

"DIEZE (ссылка на примеры работ)\n"
"Стаж: 4 года\n"
"Основные жанры: trap, r&b, techno\n\n"

"AKSENIY (ссылка на примеры работ)\n"
"Стаж: 5 лет\n"
"Основные жанры: hip-hop, rock, underground\n\n"

"Если тебе нужна срочная запись или специалист не имеет значение, нажми кнопку <i>'Не имеет значения'</i>." ,
        reply_markup=keyboard, parse_mode='html'
    )
    await state.set_state(Booking.engineer)


@logger.catch()
async def date_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    keyboard = await keyboard_available_dates()
    logger.debug(data)
    logger.debug(f"service: {data.get('service', '')}")
    await message.answer(
        "сообщ выберите дату." "+ тут будет пояснение как именно выбирается дата",
        reply_markup=keyboard,
    )
    if data.get("service", "") == "ночь на студии":
        await state.update_data(start_time="22:00")
        await state.update_data(end_time="6:00")
        await state.set_state(Booking.approvement)
        data = await state.get_data()
        logger.debug(f"night data: {data}")
        # await approvement_night_handler(message, state)
        await state.set_state(NightBooking.date)
        return
    await state.set_state(Booking.start_time)


@logger.catch()
async def engineer_handler(message: Message, state: FSMContext) -> None:
    # logger.debug(message.text)
    # await message.answer(f"Ты выбрал {message.text}")
    logger.debug(f"{message.text}")
    # state
    await state.update_data(name_of_engineer=message.text)
    await date_handler(message, state)


@logger.catch()
async def start_time_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    day: str = message.text
    await state.update_data(day=day)
    logger.debug(f"Chosen day: {day}")
    logger.debug(data)
    keyboard = await start_time_keyboard(day)
    await message.answer(
        "Выберите время начала записи, и бот сам выдаст доступные диапазоны (минимум за 12 ч до)",
        reply_markup=keyboard,
    )
    await state.set_state(Booking.end_time)


async def end_time_handler(message: Message, state: FSMContext) -> None:
    start_time = message.text
    await state.update_data(start_time=start_time)
    data = await state.get_data()
    # logger.debug(data)
    keyboard = await end_time_keyboard(data["day"], data["start_time"])
    await message.answer("выберите время окончания записи", reply_markup=keyboard)
    await state.set_state(Booking.approvement)


@logger.catch()
async def approvement_handler(message: Message, state: FSMContext) -> None:
    end_time = message.text
    await state.update_data(end_time=end_time)
    data = await state.get_data()
    # TODO: count sum
    keyboard = await approvement_keyboard()
    await state.set_state(Booking.end)
    if not data.get("name_og_engineer"):
        # TODO: изменить текст
        await message.answer(
        f"""сообщ-подтвержд 
услуга: {data['service']}  
время: {data['start_time']} - {data['end_time']}""",
        reply_markup=keyboard,
    )
    else:
        await message.answer(
        f"""сообщ-подтвержд 
услуга: {data['service']} 
звукарь: {data['name_of_engineer']} 
время: {data['start_time']} - {data['end_time']}""",
        reply_markup=keyboard,
        )


@logger.catch()
async def approvement_night_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(day=message.text)
    keyboard = await approvement_keyboard()
    data = await state.get_data()
    # TODO: count sum
    await message.answer(
        f"""сообщ-подтвержд 
услуга: {data['service']} 
звукарь: {data['name_of_engineer']} 
время: {data['start_time']} - {data['end_time']}""",
        reply_markup=keyboard,
    )
    await state.set_state(Booking.end)

@logger.catch()
async def end(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    keyboard = await pay_inline_keyboard(message.from_user.id, data["service"])
    #TODO: изменить текст
    await message.answer(
        """заебись! ты успешно записался

бронь считается действительной после получения предоплаты
*реквизиты, сумма*
после оплаты ожидай сообщения с подтверждением брони"""
    )
    await message.bot.send_message(
        chat_id=os.environ.get("CHAT_ID"), text=str(data), reply_markup=keyboard
    )
    # TODO: дополнить тут функционал 
    await state.set_state(Booking.waiting_for_pay)

@logger.catch()
async def waiting_for_pay(message: Message, state: FSMContext) -> None:
    pass


@logger.catch
async def approve_handler(callback: CallbackQuery) -> None:
    logger.debug(f"Callback: {callback}")
    logger.debug(f"data: {callback.message.text} {type(callback.message.text)}")
    text: str = callback.message.text.replace("\'", "\"")
    data: Dict[str, Any] = json.loads(text)
    logger.debug(f"dict: {data} {type(data)}")
    await write_booking(data)
    # print(callback.message.text)
    await callback.bot.send_message(
        callback.data.split(":")[0],
        f"Оплата услуги {callback.data.split(':')[1]} прошла успешно",
    )


@logger.catch()
async def back(message: Message, state: FSMContext) -> None:
    # await state.set_data({})
    await state.set_state(Start.booking)
    await start_booking_handler(message, state=state)
