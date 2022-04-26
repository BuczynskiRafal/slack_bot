import json
import string
import slack_sdk
from datetime import datetime, timedelta
from typing import Dict
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from .adapter_slackclient import slack_events_adapter, SLACK_VERIFICATION_TOKEN

from .reminder_message import send_reminder_in_pw, SCHEDULED_MESSAGES
from .scraping_users import create_users_from_slack
from .event_message import check_if_searched_words, send_info
from .through_dialogs import send_message

CLIENT = settings.CLIENT


BOT_ID = CLIENT.api_call("auth.test")["user_id"]


# create_users_from_slack()

# send_reminder_in_pw()


@slack_events_adapter.on("message")
def message(payload: json):
    """ Respond to the phrases "program", "wyróżnień", "wyroznien".
        The bot adds a comment informing that it is
        sending a message about the highlight program in a private message.
        The bot sends a message with the content specified in the "about" file.
    @param payload: dict
    @rtype: None
    """
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    if user_id != BOT_ID:
        if check_if_searched_words(text.lower()):
            text = "Informacje o pragramie wyróżnień prześlę Ci na pw. Sprawdź swoją skrzynkę."
            ts = event.get("ts")
            CLIENT.chat_postMessage(channel=channel_id, thread_ts=ts, text=text)
            send_info(f"@{user_id}", user_id)


@csrf_exempt
def call_info(request):
    """Supports the slash method - '/program-wyroznien'."""
    if request.method == "POST":
        decode_data = request.body.decode("utf-8")

        data = {}
        params = [param for param in decode_data.split("&")]
        for attributes in params:
            item = attributes.split("=")
            data[item[0]] = item[1]

        user_id = data.get("user_id")
        channel_id = data.get("channel_id")
        text = "slash is working correctly"

        CLIENT.chat_postMessage(channel=channel_id, text=text)
        send_info(f"@{user_id}", user_id)
        return HttpResponse(status=200)


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
