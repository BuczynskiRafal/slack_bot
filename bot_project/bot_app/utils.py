import datetime
from typing import Dict
from django.db.models import Sum
from django.http import HttpResponse


from .models import VotingResults, ArchiveVotingResults
from .scrap_users import get_user, get_users

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

    messages = [
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
        self.callback_id = "U03BKQMSU5D"

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
                self.DIVIDER,
                self.START_TEXT,
                self.DIVIDER,
                self.messages[0],
                self.messages[1],
                self.DIVIDER,
                self.messages[2],
                self.messages[3],
                self.DIVIDER,
                self.messages[4],
                self.messages[5],
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


def total_points_current_month():
    users = get_users()
    users_points = {}
    for user in users:
        users_points[user.slack_id] = calculate_points(user.slack_id)
    return users_points


def total_points_current_day():
    users = get_users()
    users_points = {}
    for user in users:
        users_points[user.slack_id] = calculate_points_ts(user.slack_id)
    return users_points


def total_points_all_time():
    users_points = total_points_current_month()
    for user, values in users_points.items():
        for k, v in values.items():
            users_points[user][k] += calculate_archive_points(user)[k]
    return users_points


def winner_month():
    users_points = total_points_current_month()
    winner_team_up_to_win = max(
        users_points, key=lambda v: users_points[v]["points_team_up_to_win"]
    )
    points_team_up_to_win = users_points[winner_team_up_to_win]["points_team_up_to_win"]
    winner_act_to_deliver = max(
        users_points, key=lambda v: users_points[v]["points_act_to_deliver"]
    )
    points_act_to_deliver = users_points[winner_act_to_deliver]["points_act_to_deliver"]
    winner_disrupt_to_grow = max(
        users_points, key=lambda v: users_points[v]["points_disrupt_to_grow"]
    )
    points_disrupt_to_grow = users_points[winner_disrupt_to_grow][
        "points_disrupt_to_grow"
    ]

    winners = [
        (winner_team_up_to_win, points_team_up_to_win),
        (winner_act_to_deliver, points_act_to_deliver),
        (winner_disrupt_to_grow, points_disrupt_to_grow),
    ]
    text = f"Wyniki głosowania w programie wyróżnień.\n"
    for i in range(3):
        text += f"W kategorii '{CATEGORIES[i]}' wygrywa '{get_user(winners[i][0]).name}', liczba głosów {winners[i][1]}.\n"
    return text


def winner_all_time():
    users_points = total_points_all_time()
    winner_team_up_to_win = max(
        users_points, key=lambda v: users_points[v]["points_team_up_to_win"]
    )
    points_team_up_to_win = users_points[winner_team_up_to_win]["points_team_up_to_win"]
    winner_act_to_deliver = max(
        users_points, key=lambda v: users_points[v]["points_act_to_deliver"]
    )
    points_act_to_deliver = users_points[winner_act_to_deliver]["points_act_to_deliver"]
    winner_disrupt_to_grow = max(
        users_points, key=lambda v: users_points[v]["points_disrupt_to_grow"]
    )
    points_disrupt_to_grow = users_points[winner_disrupt_to_grow][
        "points_disrupt_to_grow"
    ]

    winners = [
        (winner_team_up_to_win, points_team_up_to_win),
        (winner_act_to_deliver, points_act_to_deliver),
        (winner_disrupt_to_grow, points_disrupt_to_grow),
    ]
    text = f"Wyniki głosowania w programie wyróżnień.\n"
    for i in range(3):
        text += f"W kategorii '{CATEGORIES[i]}' wygrywa '{get_user(winners[i][0]).name}', liczba głosów {winners[i][1]}.\n"
    return text


def archive_results():
    """Archive the results and drop the score table once a month."""
    data = VotingResults.objects.all()
    for obj in data:
        try:
            archive_data = ArchiveVotingResults()
            for field in obj._meta.fields:
                setattr(archive_data, field.name, getattr(obj, field.name))
            archive_data.save()
            obj.delete()
        except Exception as e:
            print(e)
    return HttpResponse(status=200)


def get_start_and_end():
    today = datetime.datetime.now()
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end = today.replace(hour=23, minute=59, second=59, microsecond=9999)
    ts_start = datetime.datetime.timestamp(start)
    ts_end = datetime.datetime.timestamp(end)
    return ts_start, ts_end


def validate_user_selection(voting_results):
    if (
        voting_results[0]["selected_user"] == voting_results[1]["selected_user"]
        or voting_results[0]["selected_user"] == voting_results[2]["selected_user"]
        or voting_results[1]["selected_user"] == voting_results[2]["selected_user"]
    ):
        return False
    return True


def validate_votes_himself(voting_results: dict, voting_user_id: str):
    """Check if the user voted for himself."""
    for i in range(3):
        if voting_results[i]["selected_user"] == voting_user_id:
            return False
    return True


def validate_points_amount(voting_results: dict):
    points = 0
    for i in range(3):
        points += voting_results[i]["points"]
    return 0 < points <= 3


def validate(voting_results: dict, voting_user_id: str):
    return all(
        [
            validate_points_amount(voting_results),
            validate_votes_himself(voting_results, voting_user_id),
            validate_user_selection(voting_results),
        ]
    )


def error_message(voting_results: dict, voting_user_id: str):
    text = ""
    if (
        validate_votes_himself(
            voting_results=voting_results, voting_user_id=voting_user_id
        )
        is False
    ):
        text += "You cannot vote for yourself.\n"
    if validate_user_selection(voting_results=voting_results) is False:
        text += "You cannot vote for the same user in two categories.\n"
    if validate_points_amount(voting_results=voting_results) is False:
        text += "You can give away a maximum of 3 points in all categories.\n"
    text += "Results were not saved."
    return text


def save_votes(voting_results: dict, voting_user: str):
    """Save votes to db."""
    desc = VotingResults.objects.filter(voting_user_id=voting_user).exists()
    if not desc:
        voting_res = VotingResults.objects.create(
            voting_user_id=voting_user,
            ts=datetime.datetime.now().timestamp(),
        )
        voting_res.save()

    if desc:
        voting_res = VotingResults.objects.get(voting_user_id=voting_user)
        try:
            voting_res.team_up_to_win = get_user(
                slack_id=voting_results[0]["selected_user"]
            )
            voting_res.points_team_up_to_win = int(voting_results[0]["points"])
        except Exception as e:
            pass
        try:
            voting_res.act_to_deliver = get_user(
                slack_id=voting_results[1]["selected_user"]
            )
            voting_res.points_act_to_deliver = int(voting_results[1]["points"])
        except Exception as e:
            pass
        try:
            voting_res.disrupt_to_grow = get_user(
                slack_id=voting_results[2]["selected_user"]
            )
            voting_res.points_disrupt_to_grow = int(voting_results[2]["points"])
        except Exception as e:
            pass

        voting_res.ts = datetime.datetime.now().timestamp()
        voting_res.save(
            update_fields=[
                "team_up_to_win",
                "act_to_deliver",
                "disrupt_to_grow",
                "points_team_up_to_win",
                "points_act_to_deliver",
                "points_disrupt_to_grow",
                "ts",
            ]
        )


def prepare_data(request):
    decode_data = request.body.decode("utf-8")

    data = {}
    params = [param for param in decode_data.split("&")]
    for attributes in params:
        item = attributes.split("=")
        data[item[0]] = item[1]
    return data


def create_text(voting_user_id: str) -> str:
    """Create a message containing information on how the user voted.
    @return: str :
    """
    voting_results = VotingResults.objects.get(
        voting_user_id=get_user(slack_id=voting_user_id)
    )

    text = f"Cześć {get_user(voting_user_id).name.split('.')[0].capitalize()}.\n"
    attributes = [
        (
            voting_results.team_up_to_win,
            voting_results.points_team_up_to_win,
            "Team up to win",
        ),
        (
            voting_results.act_to_deliver,
            voting_results.points_act_to_deliver,
            "Act to deliver",
        ),
        (
            voting_results.disrupt_to_grow,
            voting_results.points_disrupt_to_grow,
            "Disrupt to grow",
        ),
    ]
    for user, points, category in attributes:
        if user:
            text += f"W kategorii '{category}' wybrano użytkownika: '{user.name}', punkty: '{points}'.\n"
        else:
            text += f"W kategorii '{category}' nie wybrano nikogo i nie przyznano punktów.\n"
    return text


def calculate_points(voting_user_id: str):
    points = {
        "points_team_up_to_win": VotingResults.objects.filter(
            team_up_to_win=get_user(voting_user_id)
        ).aggregate(Sum("points_team_up_to_win"))["points_team_up_to_win__sum"],
        "points_act_to_deliver": VotingResults.objects.filter(
            act_to_deliver=get_user(voting_user_id)
        ).aggregate(Sum("points_act_to_deliver"))["points_act_to_deliver__sum"],
        "points_disrupt_to_grow": VotingResults.objects.filter(
            disrupt_to_grow=get_user(voting_user_id)
        ).aggregate(Sum("points_disrupt_to_grow"))["points_disrupt_to_grow__sum"],
    }
    for k, v in points.items():
        if v is None:
            points[k] = 0
    return points


def calculate_archive_points(voting_user_id: str):
    points = {
        "points_team_up_to_win": ArchiveVotingResults.objects.filter(
            team_up_to_win=get_user(voting_user_id)
        ).aggregate(Sum("points_team_up_to_win"))["points_team_up_to_win__sum"],
        "points_act_to_deliver": ArchiveVotingResults.objects.filter(
            act_to_deliver=get_user(voting_user_id)
        ).aggregate(Sum("points_act_to_deliver"))["points_act_to_deliver__sum"],
        "points_disrupt_to_grow": ArchiveVotingResults.objects.filter(
            disrupt_to_grow=get_user(voting_user_id)
        ).aggregate(Sum("points_disrupt_to_grow"))["points_disrupt_to_grow__sum"],
    }
    for k, v in points.items():
        if v is None:
            points[k] = 0
    return points


def calculate_points_ts(voting_user_id: str):
    ts_start, ts_end = get_start_and_end()
    points = {
        "points_team_up_to_win": VotingResults.objects.filter(
            team_up_to_win=get_user(voting_user_id), ts__range=(ts_start, ts_end)
        ).aggregate(Sum("points_team_up_to_win"))["points_team_up_to_win__sum"],
        "points_act_to_deliver": VotingResults.objects.filter(
            act_to_deliver=get_user(voting_user_id), ts__range=(ts_start, ts_end)
        ).aggregate(Sum("points_act_to_deliver"))["points_act_to_deliver__sum"],
        "points_disrupt_to_grow": VotingResults.objects.filter(
            disrupt_to_grow=get_user(voting_user_id), ts__range=(ts_start, ts_end)
        ).aggregate(Sum("points_disrupt_to_grow"))["points_disrupt_to_grow__sum"],
    }
    for k, v in points.items():
        if v is None:
            points[k] = 0
    return points
