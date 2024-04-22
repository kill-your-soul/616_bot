from database import get_prices
from loguru import logger


@logger.catch()
async def count_sum(service: str, start_time: str, end_time: str) -> int:
    prices: dict[str, int] = await get_prices()

    start_hour = int(start_time.split(":")[0])
    end_hour = int(end_time.split(":")[0])

    if end_hour < start_hour:
        total_hours = 24 - start_hour + end_hour
    else:
        total_hours = end_hour - start_hour
    if service == "ночь на студии":
        total_hours = 1

    price = prices[service] * total_hours
    return price
