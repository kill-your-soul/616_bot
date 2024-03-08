from database import get_prices
from loguru import logger


@logger.catch()
async def count_sum(service: str, count: int = 1) -> int:
    prices: dict[str, int] = await get_prices()
    result: int = prices[service] * count
    return result
