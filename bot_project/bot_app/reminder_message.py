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
from .scraping_users import get_users


CLIENT = settings.CLIENT


SCHEDULED_MESSAGES = [
    {
        "text": "First message",
        "post_at": int((datetime.now() + timedelta(seconds=15)).timestamp()),
        "channel": "C03C25AACLD",
    },
    {
        "text": "Second Message!",
        "post_at": int((datetime.now() + timedelta(seconds=16)).timestamp()),
        "channel": "C03C25AACLD",
    },
]


def schedule_messages(messages):
    ids = []
    for msg in messages:
        response = CLIENT.chat_scheduleMessage(channel=msg["channel"], text=msg["text"], post_at=msg["post_at"]).data
        id_ = response.get("scheduled_message_id")
        ids.append(id_)
    return ids


def send_reminder_in_pw(messages):
    """Get all users from db"""
    users = get_users()

    """Open file contain information about awards program."""
    with open("pw_reminder", encoding="UTF8") as file:
        reminder_text = file.read()

        """Send message to all users in db."""
        for user in users:

            """Send scheduled messages."""
            for msg in messages:
                response = CLIENT.chat_scheduleMessage(channel=str(user), text=reminder_text, post_at=msg["post_at"]).data


# send_reminder_in_pw(messages=SCHEDULED_MESSAGES)
