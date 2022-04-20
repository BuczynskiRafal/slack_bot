import os
import string
import slack
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter


env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(
    os.environ["SIGNING_SECRET"], "/slack/events", app
)

client = slack.WebClient(token=os.environ["SLACK_TOKEN"])

# check bot id
BOT_ID = client.api_call("auth.test")["user_id"]

# client.chat_postMessage(channel='#test', text='Hello from test script')

message_counts = {}
welcome_messages = {}

BAD_WORDS = ['hmm', 'no', 'tim']

SCHEDULED_MESSAGES = [
    {'text': 'First message', 'post_at': (
        datetime.now() + timedelta(seconds=20)).timestamp(), 'channel': 'C01BXQNT598'},
    {'text': 'Second Message!', 'post_at': (
        datetime.now() + timedelta(seconds=30)).timestamp(), 'channel': 'C01BXQNT598'}
]


class WelcomeMessage:
    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                'Welcome to this awesome channel! \n\n'
                '*Get started by completing the tasks!*'
            )
        }
    }

    DIVIDER = {"type": "divider"}

    def __init__(self, channel):
        self.channel = channel
        self.icon_emoji = ':robot_face:'
        self.timestamp = ''
        self.completed = False

    def get_message(self):
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'username': 'Welcome Robot!',
            'icon_emoji': self.icon_emoji,
            'blocks': [
                self.START_TEXT,
                self.DIVIDER,
                self._get_reaction_task()
            ]
        }

    def _get_reaction_task(self):
        checkmark = ':white_check_mark:'
        if not self.completed:
            checkmark = ':white_large_square:'

        text = f'{checkmark} *React to this message!*'

        return {'type': 'section', 'text': {'type': 'mrkdwn', 'text': text}}


def send_welcome_message(channel, user):
    if channel not in welcome_messages:
        welcome_messages[channel] = {}

    if user in welcome_messages[channel]:
        return

    welcome = WelcomeMessage(channel)
    message = welcome.get_message()
    response = client.chat_postMessage(**message)
    welcome.timestamp = response['ts']

    welcome_messages[channel][user] = welcome


def check_if_bad_words(message):
    msg = message.lower()
    msg = msg.translate(str.maketrans('', '', string.punctuation))

    return any(word in msg for word in BAD_WORDS)


@slack_events_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if user_id is not None and user_id != BOT_ID:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1

        if text.lower() == 'start':
            # client.chat_postMessage(channel='#test', text='working')
            send_welcome_message(channel_id, user_id)
            send_welcome_message(f'@{user_id}', user_id)
        elif check_if_bad_words(text):
            ts = event.get('ts')
            client.chat_postMessage(
                channel=channel_id, thread_ts=ts, text="THAT IS A BAD WORD!")


@app.route("/message-count", methods=["POST"])
def message_count():
    data = request.form
    user_id = data.get("user_id")
    channel_id = data.get("channel_id")
    message_count = message_counts.get(user_id, 0)
    client.chat_postMessage(channel=channel_id, text=f"Message: {message_count}")
    return Response(), 200


def send_menu_in_message(channel, user):
    if channel not in welcome_messages:
        welcome_messages[channel] = {}

    if user in welcome_messages[channel]:
        return

    welcome = WelcomeMessage(channel)
    message = welcome.get_message()
    response = client.chat_postMessage(**message)
    welcome.timestamp = response['ts']

    welcome_messages[channel][user] = welcome


@app.route("/call", method=["POST"])
def call():
    """
    Call the robot to show you what it can do. It should send private message with menu.
    :return:
    """
    data = request.form
    user_id = data.get("user_id")
    channel_id = data.get("channel_id")
    menu = ''

    client.chat_postMessage(channel=channel_id, text=f"Menu: {menu}.")

    send_welcome_message(f'@{user_id}', user_id)

    return Response(), 200


if __name__ == "__main__":
    app.run(debug=True)
