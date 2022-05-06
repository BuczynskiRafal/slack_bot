"""
The module contains a collection of methods that
support voting in the award program.
"""
import calendar
import datetime
import json
import time
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied

from .adapter_slackclient import slack_events_adapter, SLACK_VERIFICATION_TOKEN
from .message import DialogWidow
from .scrap_users import get_user
from .utils import (
    calculate_points,
    create_text,
    prepare_data,
    validate,
    error_message,
    save_votes,
    get_start_end_month,
    winner,
)


CLIENT = settings.CLIENT
BOT_ID = CLIENT.api_call("auth.test")["user_id"]
CATEGORIES = ["Team up to win", "Act to deliver", "Disrupt to grow"]
info_channels = {}


def send_message(channel, user):
    """Prepare message contain voting form.
    @return: None
    """
    if channel not in info_channels:
        info_channels[channel] = {}
    if user in info_channels[channel]:
        return
    dialog_window = DialogWidow(channel)
    message = dialog_window.get_vote_message()
    response = CLIENT.chat_postMessage(**message, text="Zagłosuj na użytkownika.")
    dialog_window.timestamp = response["ts"]
    info_channels[channel][user] = message


@csrf_exempt
def vote(request):
    """Supports the slash method - '/vote'."""
    if request.method == "POST":
        data = prepare_data(request=request)
        user_id = data.get("user_id")
        send_message(user_id, user_id)
        return HttpResponse(status=200)


@csrf_exempt
def interactive(request):
    """Endpoint for receiving interactivity requests from Slack"""
    if request.method == "POST":
        data = json.loads(request.POST["payload"])
        voting_user_id = data["user"].get("id")

        """Prepare data (voting results) for saving in database. """
        voting_results = {}
        counter = 0
        for idx in data["message"]["blocks"]:
            if idx["type"] == "actions":
                voting_results[counter] = {"block_id": idx["block_id"]}
                counter += 1

        for counter, (block, values) in enumerate(data["state"]["values"].items()):
            if block == voting_results[counter]["block_id"]:
                try:
                    voting_results[counter]["block_name"] = CATEGORIES[counter]
                    voting_results[counter]["selected_user"] = values["actionId-0"][
                        "selected_user"
                    ]
                    voting_results[counter]["points"] = int(
                        values["actionId-1"]["selected_option"]["text"]["text"]
                    )
                    voting_results[counter]["selected_user_name"] = get_user(
                        slack_id=voting_results[counter]["selected_user"]
                    ).name
                except TypeError as e:
                    print(e)

        """Check if data is validate. If not send message contain errors."""
        voting_user = get_user(slack_id=voting_user_id)
        if not validate(voting_results=voting_results, voting_user_id=voting_user_id):
            CLIENT.chat_postMessage(
                channel=voting_user_id,
                text=error_message(voting_results, voting_user_id),
            )
        else:
            """Save voting results in database and send message with voting results."""
            save_votes(voting_results=voting_results, voting_user=voting_user)
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
    """Check the points you get in current month.
    @param: request
    @return:
    """
    data = prepare_data(request=request)
    voting_user_id = data.get("user_id")
    current_month = get_start_end_month()
    data = calculate_points(voting_user_id, ts_start=current_month[0], ts_end=current_month[1])

    text = (
        f"Cześć {get_user(voting_user_id).name.split('.')[0].capitalize()}.\n"
        f"Twoje punkty w kategorii 'Team up to win' to {data['points_team_up_to_win']}.\n"
        f"Twoje punkty w kategorii 'Act to deliver' to {data['points_act_to_deliver']}.\n"
        f"Twoje punkty w kategorii 'Disrupt to grow' to {data['points_disrupt_to_grow']}."
    )

    CLIENT.chat_postMessage(channel=voting_user_id, text=text)
    return HttpResponse(status=200)


@csrf_exempt
def check_winner_month(request):
    """Check winner of current month.
    @param: request
    @return:
    """
    data = prepare_data(request=request)
    voting_user_id = data.get("user_id")
    current_month = get_start_end_month()
    text = winner(ts_start=current_month[0], ts_end=current_month[1])
    CLIENT.chat_postMessage(channel=voting_user_id, text=text)
    return HttpResponse(status=200)


def send_reminder():
    pass


# def run_once_a_month():
#     """Run the following method once a month.
#         archive_results() -> Archive voting results.
#
#     @rtype: object
#     """
#     while True:
#         today = datetime.datetime.today()
#         print(today)
#         if today.date() == calendar.monthrange(today.year, today.month):
#             archive_results()
#         time.sleep(28800)


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
