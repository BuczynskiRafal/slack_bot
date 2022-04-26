import json
from typing import Dict
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


CLIENT = settings.CLIENT

BOT_ID = CLIENT.api_call("auth.test")["user_id"]


class DialogWidow:
    """Create a message with voting form."""

    """Message header"""
    START_TEXT = {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": ":mag: Search for the user you want to vote for.",
            "emoji": True,
        },
    }

    """Split text / message."""
    DIVIDER = {"type": "divider"}

    message_team_up_to_win = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Team up to win."},
            "accessory": {
                "type": "users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a user",
                    "emoji": True,
                },
                "action_id": "users_select-action",
            },
        }]
    message_act_to_deliver = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Act to deliver."},
            "accessory": {
                "type": "users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a user",
                    "emoji": True,
                },
                "action_id": "users_select-action",
            },
        }]
    message_disrupt_to_grow = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Disrupt to grow."},
            "accessory": {
                "type": "users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a user",
                    "emoji": True,
                },
                "action_id": "users_select-action",
            },
        },
    ]

    # MESSAGES = [message_team_up_to_win + message_act_to_deliver + message_disrupt_to_grow]

    # messages = [
    #     {
    #         "type": "section",
    #         "text": {"type": "mrkdwn", "text": "Team up to win."},
    #         "accessory": {
    #             "type": "users_select",
    #             "placeholder": {
    #                 "type": "plain_text",
    #                 "text": "Select a user",
    #                 "emoji": True,
    #             },
    #             "action_id": "users_select-action",
    #         },
    #     },
    #     {
    #         "type": "section",
    #         "text": {"type": "mrkdwn", "text": "Act to deliver."},
    #         "accessory": {
    #             "type": "users_select",
    #             "placeholder": {
    #                 "type": "plain_text",
    #                 "text": "Select a user",
    #                 "emoji": True,
    #             },
    #             "action_id": "users_select-action",
    #         },
    #     },
    #     {
    #         "type": "section",
    #         "text": {"type": "mrkdwn", "text": "Disrupt to grow."},
    #         "accessory": {
    #             "type": "users_select",
    #             "placeholder": {
    #                 "type": "plain_text",
    #                 "text": "Select a user",
    #                 "emoji": True,
    #             },
    #             "action_id": "users_select-action",
    #         },
    #     },
    # ]

    def __init__(self, channel) -> None:
        self.channel = channel
        self.icon_emoji = ":robot_face:"
        self.completed = False
        self.timestamp = ""
        self.callback_id = 'U03BKQMSU5D'

    def get_message(self, message) -> Dict:
        """Prepare complete message.
        @return: dict
        """
        self.message = message
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": "Program Wyróżnień - bot",
            "icon_emoji": self.icon_emoji,
            "blocks": [
                self.DIVIDER,
                self.START_TEXT,
                self.DIVIDER,
                self.message[0],
                self.DIVIDER,
                # self._get_reaction_task(),
            ],
        }

    def _get_reaction_task(self):
        checkmark = ":white_check_mark:"
        if not self.completed:
            checkmark = ":white_large_square:"

        text = f"{checkmark} *React to this message!*"

        return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


info_channels = {}
voting_messages = {}


def send_message(channel, user):
    if channel not in info_channels:
        info_channels[channel] = {}
    if user in info_channels[channel]:
        return

    dialog_window = DialogWidow(channel)
    message = dialog_window.get_message()
    response = CLIENT.chat_postMessage(**message, text='message from class')
    dialog_window.timestamp = response['ts']
    voting_messages[channel][user] = message


@csrf_exempt
def send_voting_form(request):
    """Supports the slash method - '/vote'."""
    if request.method == 'POST':
        decode_data = request.body.decode('utf-8')

        data = {}
        params = [param for param in decode_data.split('&')]
        for attributes in params:
            item = attributes.split('=')
            data[item[0]] = item[1]

        user_id = data.get('user_id')
        channel_id = data.get('channel_id')
        text = 'working'


        CLIENT.chat_postMessage(channel=channel_id, text=text)
        send_message(f"{user_id}", user_id)


@csrf_exempt
def interactive(request):
    """ endpoint for receiving all interactivity requests from Slack """
    if request.method == 'POST':
        data = json.loads(request.POST['payload'])

        voting_user = data.get('user')
        print(data)
        # print(data['actions'])
        # try:
        #     category = data['message']['blocks']['text'].get('text')
        #     print(category)
        # except Exception as  e:
        #     category = 'l'

        for _ in data['message']:
            print(_)


