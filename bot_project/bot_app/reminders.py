"""The module contains the method for sending notifications on the slack."""
import pytz
import asyncio
import logging
import calendar
from asgiref.sync import sync_to_async
from slack_sdk.errors import SlackApiError
from datetime import datetime, timedelta
from django.conf import settings
from .utils import get_start_end_month
from .models import SlackUser

logger = logging.getLogger(__name__)
CLIENT = settings.CLIENT

penultimate_day = get_start_end_month()[1] - timedelta(days=1)


def schedule_time(delta=1):
    return (
        (
            penultimate_day.replace(day=calendar.monthrange(year, month)[1])
            - timedelta(days=delta)
        ).replace(year=year, month=month, hour=11)
        for year in range(penultimate_day.year, penultimate_day.year + 10)
        for month in range(1, 13)
    )


@sync_to_async
def get_all_users():
    return list(SlackUser.objects.all())


async def send_reminder_at_end_month():
    """Get all users from db"""
    users = await get_all_users()

    """Send reminder on the penultimate day of month."""
    end_month = schedule_time()
    post_at = next(end_month)
    while post_at <= datetime.now(tz=pytz.UTC):
        post_at = next(end_month)

    """Open file contain information about awards program."""
    with open("pw_reminder", encoding="UTF8") as file:
        reminder_text = file.read()

        """Send message to all users in db."""
        for user in users:
            try:
                response = CLIENT.chat_scheduleMessage(
                    channel=user.slack_id, text=reminder_text, post_at=int(post_at.timestamp())
                ).data
                logger.info(response)
            except SlackApiError as e:
                print(e)
            except KeyboardInterrupt:
                pass

try:
    loop_send_reminder_at_end_month = asyncio.get_event_loop()
    loop_send_reminder_at_end_month.run_until_complete(send_reminder_at_end_month())
except Exception as e:
    print(e)

"""Pierwszego dnia miesiąca podsumowanie głosów - wysłanie na główny kanał"""


# async def send_as_schedule():
#     while True:
#         time_delta = timedelta(seconds=10)
#         started = datetime.now() + timedelta(seconds=100)
#         send = started + time_delta
#         scheduled_time = started.time()
#         schedule_timestamp = datetime.combine(send, scheduled_time).strftime('%s')
#
#         channel_id = "U03BKQMSU5D"
#
#         sleep = 15
#         try:
#             result = CLIENT.chat_scheduleMessage(
#                 channel=channel_id,
#                 text=f"Looking towards the future started: {started}, sendet: {send}, ",
#                 post_at=schedule_timestamp
#             )
#             print(result)
#             await asyncio.sleep(sleep)
#             started = send
#         except SlackApiError as e:
#             print(e)
#         except KeyboardInterrupt:
#             pass
#
# loop = asyncio.get_event_loop()
# try:
#     asyncio.ensure_future(send_as_schedule())
#     loop.run_forever()
# except Exception as e:
#     print(e)
