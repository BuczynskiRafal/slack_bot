import datetime
import json
from typing import Dict
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from .adapter_slackclient import slack_events_adapter, SLACK_VERIFICATION_TOKEN

from .scrap_users import get_user
from .models import SlackUser, VotingResults


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

    messages = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Select user who should receive points in the category Team up to win.",
            },
            "accessory": {
                "type": "users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Team up to win",
                    "emoji": True,
                },
                "action_id": "users_select-action",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Select user who should receive points in the category Act to deliver.",
            },
            "accessory": {
                "type": "users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Act to deliver",
                    "emoji": True,
                },
                "action_id": "users_select-action",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Select user who should receive points in the category Disrupt to grow.",
            },
            "accessory": {
                "type": "users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Disrupt to grow",
                    "emoji": True,
                },
                "action_id": "users_select-action",
            },
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
                self.DIVIDER,
                self.messages[1],
                self.DIVIDER,
                self.messages[2],
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
    """Endpoint for receiving all interactivity requests from Slack"""
    if request.method == "POST":
        data = json.loads(request.POST["payload"])
        print(data)

        voting_results = {}
        counter = 0
        for idx in data["message"]["blocks"]:
            if idx["type"] == "section":
                voting_results[counter] = {
                    "block_id": idx["block_id"],
                    "block_name": idx["accessory"]["placeholder"]["text"],
                }
                counter += 1
        print(voting_results)

        for counter, (block, values) in enumerate(data["state"]["values"].items()):
            if voting_results[counter]["block_id"] == block:
                voting_results[counter]["selected_user"] = values[
                    "users_select-action"
                ]["selected_user"]
                voting_results[counter]["selected_user_name"] = get_user(
                    slack_id=voting_results[counter]["selected_user"]
                ).name

        voting_user = data["user"].get("username")
        voting_user_id = data["user"].get("id")

        if VotingResults.objects.filter(voting_user_id=get_user(slack_id=voting_user_id)).exists():
            voting_res = VotingResults.objects.get(voting_user_id=get_user(slack_id=voting_user_id))
            voting_res.team_up_to_win = get_user(slack_id=voting_results[0]["selected_user"])
            voting_res.act_to_deliver = get_user(slack_id=voting_results[1]["selected_user"])
            voting_res.disrupt_to_grow = get_user(slack_id=voting_results[2]["selected_user"])
            voting_res.ts = datetime.datetime.now().timestamp()
            voting_res.save()
        else:
            print('else')
            voting_res = VotingResults.objects.create(
                team_up_to_win=get_user(slack_id=voting_results[0]["selected_user"]),
                # team_up_to_win=voting_results[0]["selected_user"],
                act_to_deliver=get_user(slack_id=voting_results[1]["selected_user"]),
                # act_to_deliver=voting_results[1]["selected_user"],
                disrupt_to_grow=get_user(slack_id=voting_results[2]["selected_user"]),
                # disrupt_to_grow=voting_results[2]["selected_user"],
                # voting_user=voting_user,
                voting_user_id=get_user(slack_id=voting_user_id),
                # voting_user_id=voting_user_id,
                ts=datetime.datetime.now().timestamp()
            )
            voting_res.save()

        calling_user = get_user(voting_user_id).name.split('.')[0].capitalize()
        text = f"Cześć {calling_user}.\n"
        for values in voting_results.values():
            t = f"Wybrano użytkownika '{values['selected_user_name']}' w kategorii '{values['block_name']}'.\n"
            text += t
        CLIENT.chat_postMessage(channel=voting_user_id, text=text)
        return HttpResponse({"success": True}, status=200)

"""Dodanie timestamp aby obsłużyć dodawanie głosów w poszczególnych miesiącahc."""
"""Archiwizowanie tabeli z wynikami w odrębnej tabeli i zerowanie głównej"""


@csrf_exempt
def check_votes(request):
    """Check user votes.
    @param request: json
    @return:
    """
    if request.method == 'POST':
        data = prepare_data(request=request)

        user_id = data.get("user_id")
        votes = VotingResults.objects.get(voting_user_id=user_id)
        calling_user = get_user(user_id).name.split('.')[0].capitalize()
        text = f"Cześć {calling_user}.\n" \
               f"W kategorii 'Team up to win' wybrano {get_user(votes.team_up_to_win).name}.\n" \
               f"W kategorii 'Act to deliver' wybrano {get_user(votes.act_to_deliver).name}.\n" \
               f"W kategorii 'Disrupt to grow' wybrano {get_user(votes.disrupt_to_grow).name}.\n"

        CLIENT.chat_postMessage(channel=user_id, text=text)
        return HttpResponse(status=200)


def archive_results():
    """Zarchiwizuj wyniki i wyczyść bazę danych."""
    pass


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

