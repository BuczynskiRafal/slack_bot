"""The module contains the method for sending notifications on the slack."""

"""TODO
-- Sending notifications in a private message once a month.
-- Notification content from an external file.
-- Determining how often notifications are to be sent.
-- Setting a schedule for sending notifications.
"""

import slack_sdk
from datetime import datetime, timedelta
from django.conf import settings


CLIENT = settings.CLIENT


SCHEDULED_MESSAGES = [
    {
        "text": "First message",
        "post_at": int((datetime.now() + timedelta(seconds=10)).timestamp()),
        "channel": "C03C25AACLD",
    },
    {
        "text": "Second Message!",
        "post_at": int((datetime.now() + timedelta(seconds=11)).timestamp()),
        "channel": "C03C25AACLD",
    },
]

"""Use orm to take users from db -- is incorrect at this moment"""
users = {'rafal.buczynski': 'U03BKQMSU5D'}

def schedule_messages(messages):
    ids = []
    for msg in messages:
        response = CLIENT.chat_scheduleMessage(channel=msg["channel"], text=msg["text"], post_at=msg["post_at"]).data
        id_ = response.get("scheduled_message_id")
        ids.append(id_)
    return ids





def send_reminder_in_pw(messages, users):
    """Open file contain information about awards program."""
    users = users
    with open("pw_reminder", encoding="UTF8") as file:
        reminder_text = file.read()

        for user in users.values():
            for msg in messages:
                response = CLIENT.chat_scheduleMessage(channel=user, text=reminder_text, post_at=msg["post_at"]).data

# send_reminder_in_pw(messages=SCHEDULED_MESSAGES, users=users)
