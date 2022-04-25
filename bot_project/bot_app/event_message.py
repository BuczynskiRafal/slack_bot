import string
from typing import Dict
from django.conf import settings
from .adapter_slackclient import slack_events_adapter, SLACK_VERIFICATION_TOKEN

CLIENT = settings.CLIENT

BOT_ID = CLIENT.api_call("auth.test")["user_id"]

WORDS_SEARCHED = ["program", "wyróżnień", "wyroznien"]


info_channels = {}


class InfoMessage:
    """The class handles information about the award program."""

    """Open file contain information about awards program."""
    with open("about", encoding="UTF8") as file:
        text = file.read()

    """Stores information about the award program. 
    It is part of the message being sent."""
    START_TEXT = {"type": "section", "text": {"type": "mrkdwn", "text": text}}

    """Split text / message."""
    DIVIDER = {"type": "divider"}

    def __init__(self, channel) -> None:
        self.channel = channel
        self.icon_emoji = ":robot_face:"  # set a bot avatar
        self.timestamp = ""
        self.completed = False

    def get_message(self) -> Dict:
        """Prepare complete message.
        @return: dict
        """
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": "Program Wyróżnień - bot",
            "icon_emoji": self.icon_emoji,
            "blocks": [
                self.START_TEXT,
                self.DIVIDER,
                # self._get_reaction_task()
            ],
        }

    # def _get_reaction_task(self):
    #     checkmark = ':white_check_mark:'
    #     if not self.completed:
    #         checkmark = ':white_large_square:'
    #
    #     text = f'{checkmark} *React to this message!*'
    #
    #     return {'type': 'section', 'text': {'type': 'mrkdwn', 'text': text}}


def send_info(channel, user):
    """Send info about awards program."""
    if channel not in info_channels:
        info_channels[channel] = {}
    if user in info_channels[channel]:
        return

    info = InfoMessage(channel)
    message = info.get_message()
    response = CLIENT.chat_postMessage(**message)
    info.timestamp = response["ts"]
    info_channels[channel][user] = info


def check_if_searched_words(message):
    msg = message.lower()
    msg = msg.translate(str.maketrans("", "", string.punctuation))
    return any(word in msg for word in WORDS_SEARCHED)


