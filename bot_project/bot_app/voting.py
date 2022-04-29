import calendar
import datetime
import json
import time
from typing import Dict
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.db.models import Count

from .adapter_slackclient import slack_events_adapter, SLACK_VERIFICATION_TOKEN
from .scrap_users import get_user
from .models import SlackUser, VotingResults, ArchiveVotingResults


CLIENT = settings.CLIENT

BOT_ID = CLIENT.api_call("auth.test")["user_id"]


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

    # messages = [
    #     {
    #         "type": "section",
    #         "text": {
    #             "type": "mrkdwn",
    #             "text": "Select user who should receive points in the category Team up to win.",
    #         },
    #         "accessory": {
    #             "type": "users_select",
    #             "placeholder": {
    #                 "type": "plain_text",
    #                 "text": "Team up to win",
    #                 "emoji": True,
    #             },
    #             "action_id": "users_select-action",
    #         },
    #     },
    #     {
    #         "type": "section",
    #         "text": {
    #             "type": "mrkdwn",
    #             "text": "Select user who should receive points in the category Act to deliver.",
    #         },
    #         "accessory": {
    #             "type": "users_select",
    #             "placeholder": {
    #                 "type": "plain_text",
    #                 "text": "Act to deliver",
    #                 "emoji": True,
    #             },
    #             "action_id": "users_select-action",
    #         },
    #     },
    #     {
    #         "type": "section",
    #         "text": {
    #             "type": "mrkdwn",
    #             "text": "Select user who should receive points in the category Disrupt to grow.",
    #         },
    #         "accessory": {
    #             "type": "users_select",
    #             "placeholder": {
    #                 "type": "plain_text",
    #                 "text": "Disrupt to grow",
    #                 "emoji": True,
    #             },
    #             "action_id": "users_select-action",
    #         },
    #     },
    # ]

    messages = [
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "Team up to win.",
                "emoji": True
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "users_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a user",
                        "emoji": True
                    },
                    "action_id": "actionId-0"
                },
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Choose number of points",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "0",
                                "emoji": True
                            },
                            "value": "value-0"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "1",
                                "emoji": True
                            },
                            "value": "value-1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "2",
                                "emoji": True
                            },
                            "value": "value-2"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "3",
                                "emoji": True
                            },
                            "value": "value-3"
                        }
                    ],
                    "action_id": "actionId-1"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "Act to deliver.",
                "emoji": True
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "users_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a user",
                        "emoji": True
                    },
                    "action_id": "actionId-0"
                },
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Choose number of points",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "0",
                                "emoji": True
                            },
                            "value": "value-0"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "1",
                                "emoji": True
                            },
                            "value": "value-1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "2",
                                "emoji": True
                            },
                            "value": "value-2"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "3",
                                "emoji": True
                            },
                            "value": "value-3"
                        }
                    ],
                    "action_id": "actionId-1"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "Disrupt to grow.",
                "emoji": True
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "users_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a user",
                        "emoji": True
                    },
                    "action_id": "actionId-0"
                },
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Choose number of points",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "0",
                                "emoji": True
                            },
                            "value": "value-0"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "1",
                                "emoji": True
                            },
                            "value": "value-1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "2",
                                "emoji": True
                            },
                            "value": "value-2"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "3",
                                "emoji": True
                            },
                            "value": "value-3"
                        }
                    ],
                    "action_id": "actionId-1"
                }
            ]
        }
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


info_channels = {}
voting_messages = {}


def send_message(channel, user):
    if channel not in info_channels:
        info_channels[channel] = {}
    if user in info_channels[channel]:
        return

    dialog_window = DialogWidow(channel)
    message = dialog_window.get_message()
    response = CLIENT.chat_postMessage(**message, text="Zagłosuj na użytkownika.")
    dialog_window.timestamp = response["ts"]
    info_channels[channel][user] = message


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
        (voting_results.team_up_to_win, "Team up to win"),
        (voting_results.act_to_deliver, "Act to deliver"),
        (voting_results.disrupt_to_grow, "Disrupt to grow"),
    ]
    for attr, category in attributes:
        if attr:
            text += f"W kategorii '{category}' wybrano użytkownika '{attr.name}'.\n"
        else:
            text += f"W kategorii '{category}' nie wybrano nikogo.\n"
    return text


@csrf_exempt
def vote(request):
    """Supports the slash method - '/vote'."""
    if request.method == "POST":
        data = prepare_data(request=request)

        user_id = data.get("user_id")
        channel_id = data.get("channel_id")
        text = "working"
        CLIENT.chat_postMessage(channel=channel_id, text=text)
        send_message(f"{user_id}", user_id)
        return HttpResponse(status=200)


@csrf_exempt
def interactive(request):
    """Endpoint for receiving interactivity requests from Slack"""
    if request.method == "POST":
        data = json.loads(request.POST["payload"])
        voting_user_id = data["user"].get("id")

        voting_results = {}
        counter = 0
        for idx in data["message"]["blocks"]:
            if idx["type"] == "section":
                voting_results[counter] = {
                    "block_id": idx["block_id"],
                    "block_name": idx["accessory"]["placeholder"]["text"],
                }
                counter += 1

        for counter, (block, values) in enumerate(data["state"]["values"].items()):
            if voting_results[counter]["block_id"] == block:
                try:
                    voting_results[counter]["selected_user"] = values[
                        "users_select-action"
                    ]["selected_user"]
                    voting_results[counter]["selected_user_name"] = get_user(
                        slack_id=voting_results[counter]["selected_user"]
                    ).name
                except Exception as e:
                    voting_results[counter]["selected_user_name"] = None
                    print(e)

        voting_user = get_user(slack_id=voting_user_id)
        """Save votes to db."""
        if not VotingResults.objects.filter(voting_user_id=voting_user).exists():
            voting_res = VotingResults.objects.create(
                voting_user_id=voting_user,
                ts=datetime.datetime.now().timestamp(),
            )
            voting_res.save()
        if VotingResults.objects.filter(voting_user_id=voting_user).exists():
            voting_res = VotingResults.objects.get(voting_user_id=voting_user)
            try:
                voting_res.team_up_to_win = get_user(
                    slack_id=voting_results[0]["selected_user"]
                )
            except Exception as e:
                print(e)
            try:
                voting_res.act_to_deliver = get_user(
                    slack_id=voting_results[1]["selected_user"]
                )
            except Exception as e:
                print(e)
            try:
                voting_res.disrupt_to_grow = get_user(
                    slack_id=voting_results[2]["selected_user"]
                )
            except Exception as e:
                print(e)
            voting_res.ts = datetime.datetime.now().timestamp()
            voting_res.save()

        text = create_text(voting_user_id=voting_user_id)
        CLIENT.chat_postMessage(channel=voting_user_id, text=text)
        return HttpResponse({"success": True}, status=200)


@csrf_exempt
def check_votes(request):
    """Check user votes.
    @param request
    @return:
    """
    if request.method == "POST":
        data = prepare_data(request=request)

        voting_user_id = data.get("user_id")
        text = create_text(voting_user_id=voting_user_id)

        CLIENT.chat_postMessage(channel=voting_user_id, text=text)
        return HttpResponse(status=200)


@csrf_exempt
def check_points(request):
    """Check the points you get."""
    if request.method == "POST":
        data = prepare_data(request=request)
        voting_user_id = data.get("user_id")

        point_team_up_to_win = len(VotingResults.objects.filter(team_up_to_win=get_user(voting_user_id)))
        point_act_to_deliver = len(VotingResults.objects.filter(act_to_deliver=get_user(voting_user_id)))
        point_disrupt_to_grow = len(VotingResults.objects.filter(disrupt_to_grow=get_user(voting_user_id)))

        text = f"Cześć {get_user(voting_user_id).name.split('.')[0].capitalize()}.\n" \
               f"Twoje punkty w kategorii 'Team up to win' to {point_team_up_to_win}.\n" \
               f"Twoje punkty w kategorii 'Act to deliver' to {point_act_to_deliver}.\n" \
               f"Twoje punkty w kategorii 'Disrupt to grow' to {point_disrupt_to_grow}."

        CLIENT.chat_postMessage(channel=voting_user_id, text=text)
        return HttpResponse(status=200)


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


def send_reminder():
    pass


# def winners():
#     """Check the winners of award program."""
#     winner_team_up_to_win = VotingResults.objects.values('team_up_to_win').annotate(count=Count('team_up_to_win')).order_by('-count')
#     winner_act_to_deliver = VotingResults.objects.values('act_to_deliver').annotate(count=Count('act_to_deliver')).order_by('-count')
#     winner_disrupt_to_grow = VotingResults.objects.values('disrupt_to_grow').annotate(count=Count('disrupt_to_grow')).order_by('-count')
#
#
#
#     # text = f"Wyniki głosowania w programie wyróżnień w miesiący " \
#     #        f"W kategorii 'Team up to win' wygrywa {get_user(slack_id=winner_team_up_to_win)}, liczba głosów {winner_team_up_to_win['count']}.\n" \
#     #        f"W kategorii 'Act to deliver' wygrywa {get_user(slack_id=winner_act_to_deliver)}, liczba głosów {winner_act_to_deliver['count']}.\n" \
#     #        f"W kategorii 'Disrupt to grow' wygrywa {get_user(slack_id=winner_disrupt_to_grow)}, liczba głosów {winner_disrupt_to_grow['count']}.\n"
#
#     current_month = datetime.datetime.now().month
#     print(current_month)
#     # CLIENT.chat_postMessage(channel=voting_user_id, text=text)
#     return HttpResponse(status=200)
#
# winners()


def run_once_a_month():
    """Run the following method once a month.
        archive_results() -> Archive voting results.

    @rtype: object
    """
    while True:
        today = datetime.datetime.today()
        print(today)
        if today.date() == calendar.monthrange(today.year, today.month):
            archive_results()
        time.sleep(28800)


# run_once_a_month()


def render_json_response(request, data, status=None, support_jsonp=False):
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    callback = request.GET.get("callback")
    if not callback:
        callback = request.POST.get("callback")  # in case of POST and JSONP

    if callback and support_jsonp:
        json_str = "%s(%s)" % (callback, json_str)
        response = HttpResponse(
            json_str,
            content_type="application/javascript; charset=UTF-8",
            status=status,
        )
    else:
        response = HttpResponse(
            json_str, content_type="application/json; charset=UTF-8", status=status
        )
    return response


@csrf_exempt
def slack_events(
    request, *args, **kwargs
):  # cf. https://api.slack.com/events/url_verification
    # logging.info(request.method)
    if request.method == "GET":
        raise Http404("These are not the slackbots you're looking for.")

    try:
        # https://stackoverflow.com/questions/29780060/trying-to-parse-request-body-from-post-in-django
        event_data = json.loads(request.body.decode("utf-8"))
    except ValueError as e:  # https://stackoverflow.com/questions/4097461/python-valueerror-error-message
        return HttpResponse("")

    # Echo the URL verification challenge code
    if "challenge" in event_data:
        return render_json_response(request, {"challenge": event_data["challenge"]})

    # Parse the Event payload and emit the event to the event listener
    if "event" in event_data:
        # Verify the request token
        request_token = event_data["token"]
        if request_token != SLACK_VERIFICATION_TOKEN:
            slack_events_adapter.emit("error", "invalid verification token")
            message = (
                "Request contains invalid Slack verification token: %s\n"
                "Slack adapter has: %s" % (request_token, SLACK_VERIFICATION_TOKEN)
            )
            raise PermissionDenied(message)

        event_type = event_data["event"]["type"]
        slack_events_adapter.emit(event_type, event_data)
        return HttpResponse("")

    # default case
    return HttpResponse("")
