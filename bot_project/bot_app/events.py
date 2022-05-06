import string
from typing import Dict
from django.conf import settings
from .adapter_slackclient import slack_events_adapter, SLACK_VERIFICATION_TOKEN
from .message import DialogWidow

CLIENT = settings.CLIENT
BOT_ID = CLIENT.api_call("auth.test")["user_id"]
WORDS_SEARCHED = ["program", "wyróżnień", "wyroznien"]

info_channels = {}


def send_info(channel, user):
    """Send info about awards program."""
    if channel not in info_channels:
        info_channels[channel] = {}
    if user in info_channels[channel]:
        return

    info = DialogWidow(channel)
    message = info.get_about_message()
    response = CLIENT.chat_postMessage(**message, text='pw_bot')
    info.timestamp = response["ts"]
    info_channels[channel][user] = info


def check_if_searched_words(message):
    msg = message.lower()
    msg = msg.translate(str.maketrans("", "", string.punctuation))
    return any(word in msg for word in WORDS_SEARCHED)


