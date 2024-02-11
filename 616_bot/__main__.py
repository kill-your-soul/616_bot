import asyncio
import logging
import os
from pathlib import Path

# from pymongo import MongoClient

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis
import handlers
from loguru import logger

# from database import mongo


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_router(handlers.start.setup_handlers())
    dp.include_router(handlers.booking.setup_handlers())


class InterceptHandler(logging.Handler):
    def emit(self, record):
        level = logger.level(record.levelname).name
        logger.log(level, record.getMessage())


@logger.catch
async def main() -> None:
    logging.getLogger("aiogram").setLevel(logging.DEBUG)
    logging.getLogger("aiogram").addHandler(InterceptHandler())
    logging.getLogger("asyncio").setLevel(logging.DEBUG)
    logging.getLogger("asyncio").addHandler(InterceptHandler())
    base_dir = Path(__file__).resolve().parent.parent
    logger.add(base_dir / "logs.log", level="DEBUG")

    # client = MongoClient("mongodb://mongodb:27017")

    # logger.add(client.room_616.logs, level="INFO")
    bot = Bot(os.environ.get("TOKEN"))
    redis = Redis(host="redis")
    storage = RedisStorage(redis)
    dp = Dispatcher(storage=storage)
    logger.info("Setup handlers")
    setup_handlers(dp)
    logger.info("Bot started")
    await dp.start_polling(bot)
    logger.info("Bot stoped")


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    with logger.catch():
        asyncio.run(main())
