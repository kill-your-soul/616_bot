from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards import (
    sound_engineers,
    keyboard_available_dates,
    keyboard_available_dates_inline,
    start_time_keyboard,
    start_time_night_keyboard,
    end_time_keyboard,
    end_time_keyboard_night,
    approvement_keyboard,
    pay_inline_keyboard,
)
from states.booking import Booking
from states.night_booking import NightBooking
from states.start import Start
from loguru import logger
from handlers.start.start import start_booking_handler
from database import write_booking, get_number, find_temp
from utils.sum import count_sum
from utils.date import determine_month
from typing import Dict, Any
import os
import json


@logger.catch()
async def menu_handler(message: Message, state: FSMContext):
    logger.debug(message.text)
    await state.update_data(service=message.text)
    
    keyboard = await sound_engineers()
    await message.answer(
        "Выбери звукорежиссера:\n\n"
        "<a href='https://vk.com/music/playlist/-171812248_1_ddeed634b65ab0a356'><b>VICEYY</b></a>\n"
        "Стаж: 6 лет\n"
        "Основные жанры: hip-hop, new school rap, underground\n\n"
        "<a href='https://vk.com/music/playlist/-171812248_3_880334b157b3791d4a'><b>DIEZE</b></a>\n"
        "Стаж: 4 года\n"
        "Основные жанры: trap, r&b, techno\n\n"
        "<a href='https://vk.com/music/playlist/-171812248_2_a50dc5347aa81298cc'><b>AKSENIY</b></a>\n"
        "Стаж: 5 лет\n"
        "Основные жанры: hip-hop, rock, underground\n\n"
        "Если тебе нужна срочная запись или специалист не имеет значения, нажми кнопку <i>'Не имеет значения'</i>.",
        reply_markup=keyboard,
        parse_mode="html",
    )
    await state.set_state(Booking.engineer)


@logger.catch()
async def date_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    keyboard = await keyboard_available_dates()
    logger.debug(data)
    logger.debug(f"service: {data.get('service', '')}")
    if data.get("service").lower() == "аренда студии (день)":
        await message.answer("Выбери дату:")
        await message.answer(
            "<i>В клавиатуре отображаются все доступные даты на ближайшие 2 недели.</i>",
            reply_markup=keyboard,
            parse_mode="html",
            disable_notification=True
        )
    else:
        await message.answer("Выбери дату:")
        await message.answer(
            "<i>В клавиатуре отображаются все доступные даты у данного звукорежиссера на ближайшие 2 недели.</i>",
            reply_markup=keyboard,
            parse_mode="html",
            disable_notification=True
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
    if data["service"].lower() == "час на студии (ночь)":
        keyboard = await start_time_night_keyboard(day)
    await message.answer("Выбери время начала записи:")
    await message.answer(
        "<i>Время указано в 24-часовом формате. В следующем шаге бот предложит выбрать доступное время окончания записи.</i>",
        reply_markup=keyboard,
        parse_mode="html",
        disable_notification=True
    )
    await state.set_state(Booking.end_time)


async def end_time_handler(message: Message, state: FSMContext) -> None:
    start_time = message.text
    await state.update_data(start_time=start_time)
    data = await state.get_data()
    # logger.debug(data)
    keyboard = await end_time_keyboard(data["day"], data["start_time"])
    if data["service"].lower() == "час на студии (ночь)":
        keyboard = await end_time_keyboard_night(data["day"], data["start_time"])
    await message.answer("Выбери время окончания записи:\n\n")
    await message.answer(
        "<i>Если ты хочешь записаться на время, которое включает и дневной и ночной диапазон, необходимо отдельно записаться на каждый временной промежуток.</i>",
        reply_markup=keyboard,
        parse_mode="html",
        disable_notification=True
    )
    await state.set_state(Booking.approvement)


@logger.catch()
async def approvement_handler(message: Message, state: FSMContext) -> None:
    end_time = message.text
    await state.update_data(end_time=end_time)
    data = await state.get_data()
    keyboard = await approvement_keyboard()
    await state.set_state(Booking.end)
    # times: int = int(data["end_time"].split(":")[0]) - int(
    #     data["start_time"].split(":")[0]
    # )
    price = await count_sum(data["service"], data["start_time"], data["end_time"])
    await state.update_data(price=price)
    if data.get("service").lower() == "аренда студии (день)":
        await message.answer(
            f"Подтверждение бронирования:\n\n"
            f"<b>Услуга:</b> {data['service']}\n"
            f"<b>Время:</b> {data['start_time']} - {data['end_time']}\n"
            f"<b>Дата:</b> {data['day']}.{str(determine_month(int(data['day']))).zfill(2)}\n"
            f"<b>Общая стоимость услуг:</b> {price}\n\n"
            f'Если всё верно, жми "<i>Записаться</i>"',
            reply_markup=keyboard,
            parse_mode="html",
        )
        return
    if not data.get("name_of_engineer"):
        await message.answer(
            f"<b>Подтверждение бронирования:</b>\n\n"
            f"<b>Услуга:</b> {data['service']}\n"
            f"<b>Время:</b> {data['start_time']} - {data['end_time']}\n"
            f"<b>Дата:</b> {data['day']}.{str(determine_month(int(data['day']))).zfill(2)}\n"
            f"<b>Общая стоимость услуг:</b> {price}\n\n"
            f'Если всё верно, жми "<i>Записаться</i>"',
            reply_markup=keyboard,
            parse_mode="html",
        )
        return
    else:
        await message.answer(
            f"<b>Подтверждение бронирования:</b>\n\n"
            f"<b>Услуга:</b> {data['service']}\n"
            f"<b>Звукорежиссёр:</b> {data['name_of_engineer']}\n"
            f"<b>Время:</b> {data['start_time']} - {data['end_time']}\n"
            f"<b>Дата:</b> {data['day']}.{str(determine_month(int(data['day']))).zfill(2)}\n"
            f"<b>Общая стоимость услуг:</b> {price}\n\n"
            f'Если всё верно, жми "<i>Записаться</i>"',
            reply_markup=keyboard,
            parse_mode="html",
        )
        return


@logger.catch()
async def approvement_night_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(day=message.text)
    keyboard = await approvement_keyboard()
    data = await state.get_data()
    price = await count_sum(data["service"], data["start_time"], data["end_time"])
    await message.answer(
        f"Подтверждение бронирования:\n\n"
        f"<b>Услуга:</b> {data['service']}\n"
        f"<b>Звукорежиссёр:</b> {data['name_of_engineer']}\n"
        f"<b>Время:</b> {data['start_time']} - {data['end_time']}\n"
        f"<b>Дата:</b> {data['day']}.{str(determine_month(int(data['day']))).zfill(2)}\n"
        f"<b>Общая стоимость услуг:</b> {price}\n\n"
        f'Если всё верно, жми "<i>Записаться</i>"',
        reply_markup=keyboard,
        parse_mode="html",
    )
    await state.update_data(price=price)
    await state.set_state(Booking.end)


@logger.catch()
async def end(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    # logger.debug(str(data))
    # logger.debug(data)
    # logger.debug(type(data))
    keyboard = await pay_inline_keyboard(message.from_user.id, data)
    await message.answer(
        f"Остался последний шаг! Бронь считается действительной после внесения предоплаты:\n\n"
        f"💳 {os.environ.get('DETAILS')}\n"
        f"💴 {int(int(data['price']) / 2)}₽\n"
        f"📆  {data['day']}.{str(determine_month(int(data['day']))).zfill(2)}\n\n"
        f"После оплаты ожидай сообщение о подтверждении брони. Оплатить бронь необходимо в течение 30 минут, иначе она будет автоматически отменена.\n"
    )
    number = await get_number(data["username"])
    await message.bot.send_message(
        chat_id=os.environ.get("CHAT_ID"),
        text=f"Клиент: @{data['username']}\nНомер: {number}\nУслуга: {data['service']}\nЗвукорежиссер: {data['name_of_engineer']}\nДата: {data['day']}.{str(determine_month(int(data['day']))).zfill(2)}\nВремя: {data['start_time']}-{data['end_time']}\nСтоимость: {data['price']}",
        reply_markup=keyboard,
    )
    await state.set_state(Booking.waiting_for_pay)


@logger.catch()
async def waiting_for_pay(message: Message, state: FSMContext) -> None:
    pass


@logger.catch()
async def approve_handler(callback: CallbackQuery) -> None:
    logger.debug(f"Callback: {callback}")
    logger.debug(f"data: {callback.message.text} {type(callback.message.text)}")
    # text: str = callback.message.text.replace("'", '"')
    text: str = callback.data.split(";")[1]
    logger.debug(text)
    data = await find_temp(text)
    # data: Dict[str, Any] = json.loads(text)
    logger.debug(f"dict: {data} {type(data)}")
    await write_booking(data)
    logger.warning(f"data: {data.keys()}")
    # print(callback.message.text)
    await callback.answer(text="Ты подтвердил бронь")
    await callback.bot.send_message(
        callback.data.split(";")[0],
        f"Бронь подтверждена!\n\n"
        f"Дата: {data['date']}\n"
        f"Время: {data['start_time']} - {data['end_time']}\n"
        f"Звукорежиссер: {data['name_of_engineer']}\n"
        f"Адрес:  ул. Казанская 7В, БЦ Казанский, пом. 616\n"
        f"Обрати внимание: отменить бронь без потери средств можно не менее, чем за 12 часов до сеанса. Для отмены писать @room616\n\n"
        f"До встречи в ROOM616!",
    )


@logger.catch()
async def back(message: Message, state: FSMContext) -> None:
    # await state.set_data({})
    await state.set_state(Start.booking)
    await start_booking_handler(message, state=state)
