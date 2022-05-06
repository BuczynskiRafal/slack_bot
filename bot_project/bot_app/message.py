from typing import Dict

CATEGORIES = ["Team up to win", "Act to deliver", "Disrupt to grow"]


class DialogWidow:
    """Create a message with voting form."""

    """Message header"""
    START_TEXT = {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": ":mag: Search for the user you want to vote for in fallowing category.",
            "emoji": True,
        },
    }

    """Split text / message."""
    DIVIDER = {"type": "divider"}

    """Open file contain information about awards program."""
    with open("about", encoding="UTF8") as file:
        about_text = file.read()

    """Stores information about the award program. 
    It is part of the message being sent."""
    START_ABOUT_TEXT = {"type": "section", "text": {"type": "mrkdwn", "text": about_text}}

    voting_form = [
        {
            "type": "section",
            "text": {"type": "plain_text", "text": "Team up to win.", "emoji": True},
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "users_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a user",
                        "emoji": True,
                    },
                    "action_id": "actionId-0",
                },
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Choose number of points",
                        "emoji": True,
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "0", "emoji": True},
                            "value": "value-0",
                        },
                        {
                            "text": {"type": "plain_text", "text": "1", "emoji": True},
                            "value": "value-1",
                        },
                        {
                            "text": {"type": "plain_text", "text": "2", "emoji": True},
                            "value": "value-2",
                        },
                        {
                            "text": {"type": "plain_text", "text": "3", "emoji": True},
                            "value": "value-3",
                        },
                    ],
                    "action_id": "actionId-1",
                },
            ],
        },
        {
            "type": "section",
            "text": {"type": "plain_text", "text": "Act to deliver.", "emoji": True},
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "users_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a user",
                        "emoji": True,
                    },
                    "action_id": "actionId-0",
                },
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Choose number of points",
                        "emoji": True,
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "0", "emoji": True},
                            "value": "value-0",
                        },
                        {
                            "text": {"type": "plain_text", "text": "1", "emoji": True},
                            "value": "value-1",
                        },
                        {
                            "text": {"type": "plain_text", "text": "2", "emoji": True},
                            "value": "value-2",
                        },
                        {
                            "text": {"type": "plain_text", "text": "3", "emoji": True},
                            "value": "value-3",
                        },
                    ],
                    "action_id": "actionId-1",
                },
            ],
        },
        {
            "type": "section",
            "text": {"type": "plain_text", "text": "Disrupt to grow.", "emoji": True},
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "users_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a user",
                        "emoji": True,
                    },
                    "action_id": "actionId-0",
                },
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Choose number of points",
                        "emoji": True,
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "0", "emoji": True},
                            "value": "value-0",
                        },
                        {
                            "text": {"type": "plain_text", "text": "1", "emoji": True},
                            "value": "value-1",
                        },
                        {
                            "text": {"type": "plain_text", "text": "2", "emoji": True},
                            "value": "value-2",
                        },
                        {
                            "text": {"type": "plain_text", "text": "3", "emoji": True},
                            "value": "value-3",
                        },
                    ],
                    "action_id": "actionId-1",
                },
            ],
        },
    ]

    def __init__(self, channel) -> None:
        self.channel = channel
        self.icon_emoji = ":robot_face:"
        self.completed = False
        self.timestamp = ""
        # self.callback_id = "U03BKQMSU5D"

    def get_vote_message(self) -> Dict:
        """Prepare complete message.
        @return: dict
        """
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": "Program Wyróżnień - bot",
            "icon_emoji": self.icon_emoji,
            "blocks": [
                self.DIVIDER,
                self.START_TEXT,
                self.DIVIDER,
                self.voting_form[0],
                self.voting_form[1],
                self.DIVIDER,
                self.voting_form[2],
                self.voting_form[3],
                self.DIVIDER,
                self.voting_form[4],
                self.voting_form[5],
                self.DIVIDER,
            ],
        }

    def get_about_message(self) -> Dict:
        """Prepare complete message.
        @return: dict
        """
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": "Program Wyróżnień - bot",
            "icon_emoji": self.icon_emoji,
            "blocks": [
                self.START_ABOUT_TEXT,
                self.DIVIDER,
                self._get_reaction_task()
            ],
        }

    def _get_reaction_task(self):
        checkmark = ":white_check_mark:"
        if not self.completed:
            checkmark = ":white_large_square:"

        text = f"{checkmark} *React to this message!*"

        return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


