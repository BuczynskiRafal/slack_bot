# """The module contains the method for sending notifications on the slack."""
#
# """TODO.txt
# -- Sending notifications in a private message once a month.
# -- Notification content from an external file.
# -- Determining how often notifications are to be sent.
# -- Setting a schedule for sending notifications.
# """
# import asyncio
# import logging
# from slack_sdk.errors import SlackApiError
# from datetime import datetime, timedelta, date, time
# from django.conf import settings
# from .scrap_users import get_users
#
# logger = logging.getLogger(__name__)
# CLIENT = settings.CLIENT
#
#
# SCHEDULED_MESSAGES = [
#     {
#         "text": "First message",
#         "post_at": int((datetime.now() + timedelta(seconds=15)).timestamp()),
#         "channel": "C03C25AACLD",
#     },
#     {
#         "text": "Second Message!",
#         "post_at": int((datetime.now() + timedelta(seconds=16)).timestamp()),
#         "channel": "C03C25AACLD",
#     },
# ]
#
#
# def schedule_messages(messages):
#     ids = []
#     for msg in messages:
#         response = CLIENT.chat_scheduleMessage(channel=msg["channel"], text=msg["text"], post_at=msg["post_at"]).data
#         id_ = response.get("scheduled_message_id")
#         ids.append(id_)
#     return ids
#
#
# def send_reminder_in_pw(messages):
#     """Get all users from db"""
#     users = get_users()
#
#     """Open file contain information about awards program."""
#     with open("pw_reminder", encoding="UTF8") as file:
#         reminder_text = file.read()
#
#         """Send message to all users in db."""
#         for user in users:
#
#             """Send scheduled messages."""
#             for msg in messages:
#                 response = CLIENT.chat_scheduleMessage(channel=str(user), text=reminder_text, post_at=msg["post_at"]).data
#
#
# # send_reminder_in_pw(messages=SCHEDULED_MESSAGES)
#
# """Pierwszego dnia miesiąca podsumowanie głosów - wysłanie na główny kanał"""
#
#
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
