from datetime import datetime, timedelta

from loguru import logger


# def determine_month(day: int) -> int:
#     today = datetime.now()
#     selected_date = today.replace(day=day)
#     logger.debug(f"May be day: {selected_date}")
#     # if selected_date <= today:
#     #     return today.month
#     if today >= selected_date:
#         return today.month
#     return (today + timedelta(days=30)).month


def determine_month(day: int) -> int:
    # Получаем текущую дату
    current_date = datetime.now()

    # Проверяем, может ли дата быть в текущем месяце
    if current_date.day <= day:
        relative_month = current_date.month
    else:
        # Иначе, возвращаем следующий месяц
        relative_month = (
            current_date + timedelta(days=30)
        ).month  # Предполагаем, что следующий месяц не более чем через 30 дней

    return relative_month
