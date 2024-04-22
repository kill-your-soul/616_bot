from pymongo import MongoClient
from pymongo.collection import Collection
from datetime import datetime, timedelta, time
from loguru import logger
import pandas as pd
from utils.date import determine_month
from typing import Dict
from bson.objectid import ObjectId


async def get_available_dates():
    client = MongoClient("mongodb://mongodb:27017")
    db = client["room_616"]
    booking_collection: Collection = db["bookings"]
    today = datetime.now()

    # Рассчитываем время, оставшееся до конца текущего дня
    remaining_hours = (
        datetime.combine(today.date(), datetime.min.time()) + timedelta(days=1) - today
    ).seconds // 3600

    # Если до конца текущего дня остается менее 12 часов, увеличиваем сегодняшнюю дату на один день
    if remaining_hours < 12:
        today += timedelta(days=1)

    end_date = today + timedelta(days=13)

    query = {
        "date": {
            "$gte": today.strftime("%Y-%m-%d"),
            "$lte": end_date.strftime("%Y-%m-%d"),
        }
    }
    result = booking_collection.find(query)
    logger.debug("Available dates")
    for booking in result:
        logger.debug(booking)

    date_range = pd.date_range(start=today, end=end_date)
    occupied_dates = pd.to_datetime(
        [f"{item['date']} {item['item']}" for item in result]
    )
    free_dates = list(set(date_range) - set(occupied_dates))
    free_dates_str = [date.strftime("%d") for date in free_dates]
    logger.debug(f"free_dates_str: {free_dates_str}")

    client.close()
    return free_dates_str


@logger.catch()
async def get_available_start_time(day: int) -> list[str]:
    client = MongoClient("mongodb://mongodb:27017")
    db = client["room_616"]
    booking_collection = db["bookings"]
    month = determine_month(day)
    logger.debug(f"Month {month}")
    current_year = datetime.now().year
    now = datetime.now()
    # Сборка строки с выбранной датой в формате "год-месяц-день"
    selected_date_str = f"{current_year}-{str(month).zfill(2)}-{str(day).zfill(2)}"

    # Получение занятых временных интервалов из базы данных
    logger.debug(f"Date: {selected_date_str}")
    occupied_intervals = list(booking_collection.find({"date": selected_date_str}))

    logger.debug(f"Occupied intervals: {occupied_intervals}")

    # Генерация временных интервалов от 8:00 до 22:00 с шагом в один час
    start_time = datetime.strptime("08:00", "%H:%M")
    end_time = datetime.strptime("22:00", "%H:%M")
    time_intervals = [
        (start_time + timedelta(hours=i), start_time + timedelta(hours=i + 1))
        for i in range((end_time - start_time).seconds // 3600)
    ]

    # Если выбран сегодняшний день, отфильтровать временные интервалы, оставив только те, которые еще могут быть
    if day == now.day and month == now.month:
        time_intervals = [
            (start, end)
            for start, end in time_intervals
            if (now.hour, now.minute) < (start.hour, start.minute)
        ]

    # Фильтрация свободных временных интервалов
    free_intervals = [
        {"start_time": start.strftime("%H:%M"), "end_time": end.strftime("%H:%M")}
        for start, end in time_intervals
        if not any(
            start < datetime.strptime(occupied["end_time"], "%H:%M")
            and end > datetime.strptime(occupied["start_time"], "%H:%M")
            for occupied in occupied_intervals
        )
    ]

    free_start_times = [interval["start_time"] for interval in free_intervals]

    # Закрытие соединения с MongoDB
    client.close()

    return free_start_times


@logger.catch()
async def get_available_night_start_time(day: int) -> list[str]:
    client = MongoClient("mongodb://mongodb:27017")
    db = client["room_616"]
    booking_collection = db["bookings"]
    month = determine_month(day)
    logger.debug(f"Month {month}")
    current_year = datetime.now().year
    now = datetime.now()
    # Сборка строки с выбранной датой в формате "год-месяц-день"
    selected_date_str = f"{current_year}-{str(month).zfill(2)}-{str(day).zfill(2)}"

    # Получение занятых временных интервалов из базы данных
    logger.debug(f"Date: {selected_date_str}")
    occupied_intervals = list(booking_collection.find({"date": selected_date_str}))

    logger.debug(f"Occupied intervals: {occupied_intervals}")

    # Генерация временных интервалов от 22:00 до 8:00 с шагом в один час
    start_time = datetime.strptime("22:00", "%H:%M")
    end_time = datetime.strptime("08:00", "%H:%M") + timedelta(
        days=1
    )  # Следующий день, 08:00
    time_intervals = [
        (start_time + timedelta(hours=i), start_time + timedelta(hours=i + 1))
        for i in range((end_time - start_time).seconds // 3600)
    ]

    # Если выбран сегодняшний день, отфильтровать временные интервалы, оставив только те, которые еще могут быть
    if day == now.day and month == now.month:
        time_intervals = [
            (start, end)
            for start, end in time_intervals
            if (now.hour, now.minute) < (start.hour, start.minute)
        ]

    # Фильтрация свободных временных интервалов
    free_intervals = [
        {"start_time": start.strftime("%H:%M"), "end_time": end.strftime("%H:%M")}
        for start, end in time_intervals
        if not any(
            start < datetime.strptime(occupied["end_time"], "%H:%M")
            and end > datetime.strptime(occupied["start_time"], "%H:%M")
            for occupied in occupied_intervals
        )
    ]

    free_start_times = [interval["start_time"] for interval in free_intervals]

    # Закрытие соединения с MongoDB
    client.close()

    return free_start_times


@logger.catch()
async def get_available_end_time_night(
    day: int, start_time: str
) -> list[dict[str, str]]:
    client = MongoClient("mongodb://mongodb:27017")
    db = client["room_616"]
    booking_collection = db["bookings"]
    month = determine_month(day)

    current_year = datetime.now().year

    # Сборка строки с выбранной датой и временем начала в формате "год-месяц-день час:минута"
    start_datetime_str = (
        f"{current_year}-{str(month).zfill(2)}-{str(day).zfill(2)} {start_time}"
    )

    # Преобразование строки в объект datetime
    start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")

    # Получение занятых временных интервалов из базы данных
    occupied_intervals = list(
        booking_collection.find({"date": start_datetime.date().strftime("%Y-%m-%d")})
    )
    logger.debug(f"occupied intervals: {occupied_intervals}")

    # Формирование списка свободных временных промежутков
    free_end_times = []

    for occupied_interval in occupied_intervals:
        end_datetime = datetime.strptime(occupied_interval["start_time"], "%H:%M")
        if end_datetime > start_datetime:
            free_end_times.append(end_datetime.strftime("%H:%M"))

    if not free_end_times:  # Если нет свободного времени в тот же день
        # Добавляем времена до 08:00 следующего дня
        end_time = datetime.strptime("08:00", "%H:%M") + timedelta(
            days=1
        )  # Следующий день, 08:00
        end_time_intervals = [
            (start_datetime + timedelta(hours=i)).strftime("%H:%M")
            for i in range(
                1, (end_time - start_datetime).seconds // 3600 + 1
            )  # Интервалы по 1 часу
        ]
        free_end_times.extend(end_time_intervals)

    # Закрытие соединения с MongoDB
    client.close()

    return free_end_times


@logger.catch()
async def get_available_end_time(day: int, start_time: str) -> list[dict[str, str]]:
    client = MongoClient("mongodb://mongodb:27017")
    db = client["room_616"]
    booking_collection = db["bookings"]
    month = determine_month(day)

    current_year = datetime.now().year

    # Сборка строки с выбранной датой и временем начала в формате "год-месяц-день час:минута"
    start_datetime_str = (
        f"{current_year}-{str(month).zfill(2)}-{str(day).zfill(2)} {start_time}"
    )

    # Преобразование строки в объект datetime
    start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")

    # Получение занятых временных интервалов из базы данных
    occupied_intervals = list(
        booking_collection.find({"date": start_datetime.date().strftime("%Y-%m-%d")})
    )
    logger.debug(f"occupied intervals: {occupied_intervals}")

    # Сортировка занятых интервалов по времени начала
    occupied_intervals.sort(key=lambda x: datetime.strptime(x["start_time"], "%H:%M"))

    # Поиск ближайшей записи после времени начала
    next_booking_index = next(
        (
            i
            for i, occupied in enumerate(occupied_intervals)
            if datetime.strptime(occupied["start_time"], "%H:%M").hour
            > start_datetime.hour
        ),
        None,
    )
    if next_booking_index is not None:
        # Если есть ближайшая запись, формируем список временных промежутков до времени ближайшей записи
        next_booking = occupied_intervals[next_booking_index]
        logger.debug(f"Next booking: {next_booking}")
        end_datetime = datetime.strptime(next_booking["start_time"], "%H:%M")
        end_time_intervals = [
            (start_datetime + timedelta(hours=i)).strftime("%H:%M")
            for i in range(
                1, (end_datetime - start_datetime).seconds // 3600 + 1
            )  # Интервалы по 1 часу
        ]
    else:
        # Если ближайшая запись только на следующий день, формируем список временных промежутков до 21:00
        end_time_intervals = [
            (start_datetime + timedelta(hours=i)).strftime("%H:%M")
            for i in range(
                1,
                (datetime.strptime("23:00", "%H:%M") - start_datetime).seconds // 3600,
            )
        ]
    logger.debug(f"end time intervals: {end_time_intervals}")

    # Закрытие соединения с MongoDB
    client.close()

    return end_time_intervals


@logger.catch()
async def write_booking(dict: Dict):
    client = MongoClient("mongodb://mongodb:27017")
    db = client["room_616"]
    booking_collection = db["bookings"]
    users_collection = db["users"]
    dict[
        "date"
    ] = f"2024-{str(determine_month(int(dict['day']))).zfill(2)}-{str(dict['day']).zfill(2)}"
    dict.pop("day")
    booking_collection.insert_one(dict)


@logger.catch()
async def get_prices() -> dict[str, int]:
    client = MongoClient("mongodb://mongodb:27017")
    db = client["room_616"]
    prices_collection: Collection = db["prices"]
    prices = {}
    for doc in prices_collection.find():
        title: str = doc.get("title")
        price: int = doc.get("price")
        prices[title] = price
    return prices


@logger.catch()
async def check_user(username: str) -> bool:
    client = MongoClient("mongodb://mongodb:27017")
    db = client["room_616"]
    users_collection: Collection = db["users"]
    if users_collection.find_one({"username": username}):
        return True
    return False


@logger.catch()
async def create_user(username: str, number: str) -> None:
    client = MongoClient("mongodb://mongodb:27017")
    db = client["room_616"]
    users_collection: Collection = db["users"]
    users_collection.insert_one({"username": username, "number": number})


@logger.catch()
async def get_number(username: str) -> str:
    client = MongoClient("mongodb://mongodb:27017")
    db = client["room_616"]
    users_collection: Collection = db["users"]
    user = users_collection.find_one({"username": username})
    return user["number"]


@logger.catch()
async def insert_temp(data) -> str:
    client = MongoClient("mongodb://mongodb:27017")
    db = client["room_616"]
    temp: Collection = db["temp"]
    _id = temp.insert_one(data).inserted_id
    return str(_id)


@logger.catch()
async def find_temp(_id: str):
    client = MongoClient("mongodb://mongodb:27017")
    db = client["room_616"]
    temp: Collection = db["temp"]
    return temp.find_one(ObjectId(_id))
