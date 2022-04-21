import json
import string
import slack_sdk
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from .adapter_slackclient import slack_events_adapter, SLACK_VERIFICATION_TOKEN


CLIENT = slack_sdk.WebClient(token=settings.SLACK_BOT_TOKEN)
BOT_ID = CLIENT.api_call("auth.test")["user_id"]

WORDS_SEARCHED = ["program", "wyróżnień", "wyroznien"]

message_counts = {}
info_channels = {}


class InfoMessage:
    with open('about_program_wyroznien', encoding='UTF8') as file:
        text = file.read()

    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': text
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
            'username': 'Program Wyróżnień - bot',
            'icon_emoji': self.icon_emoji,
            'blocks': [
                self.START_TEXT,
                self.DIVIDER,
                # self._get_reaction_task()
            ]
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
    """Send info about program wyróżnień"""
    if channel not in info_channels:
        info_channels[channel] = {}
    if user in info_channels[channel]:
        return 'abc'
    info = InfoMessage(channel)
    message = info.get_message()
    response = CLIENT.chat_postMessage(**message)
    info.timestamp = response['ts']
    info_channels[channel][user] = info


def check_if_searched_words(message):
    msg = message.lower()
    msg = msg.translate(str.maketrans('', '', string.punctuation))
    return any(word in msg for word in WORDS_SEARCHED)


@slack_events_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if user_id != BOT_ID:
        if check_if_searched_words(text.lower()):
            text = 'Informacje o pragramie wyróżnień prześlę Ci na pw. Sprawdź swoją skrzynkę.'
            ts = event.get('ts')
            CLIENT.chat_postMessage(channel=channel_id, thread_ts=ts, text=text)
            send_info(f'@{user_id}', user_id)



def call_info(request):
    data = request.POST
    print(dir(data))

    # print(request)
    # print(request.post('user'))
    # print(request.POST.get('channel'))
    # request.method = ['POST']
    # data = request.POST
    # user_id = data.get('user')
    # channel_id = data.get('channel')
    # text = 'Some text.'
    # # CLIENT.users_list()
    # # CLIENT.chat_postMessage(channel=channel_id, text=text)
    # send_info(f'@{user_id}', user_id)
    return HttpResponse(), 200

# def profile(request, pk):
#     profile = Profile.objects.get(pk=pk)
#     if request.method == "POST":
#         current_user_profile = request.user.profile
#         data = request.POST
#         action = data.get("follow")
#         if action == "follow":
#             current_user_profile.follows.add(profile)
#         elif action == "unfollow":
#             current_user_profile.follows.remove(profile)
#         current_user_profile.save()
#     return render(request, "dwitter/profile.html", {"profile": profile})



def render_json_response(request, data, status=None, support_jsonp=False):
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    callback = request.GET.get("callback")
    if not callback:
        callback = request.POST.get("callback")  # in case of POST and JSONP

    if callback and support_jsonp:
        json_str = "%s(%s)" % (callback, json_str)
        response = HttpResponse(json_str, content_type="application/javascript; charset=UTF-8", status=status)
    else:
        response = HttpResponse(json_str, content_type="application/json; charset=UTF-8", status=status)
    return response


@csrf_exempt
def slack_events(request, *args, **kwargs):  # cf. https://api.slack.com/events/url_verification
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
        return render_json_response(request, {
            "challenge": event_data["challenge"]
        })

    # Parse the Event payload and emit the event to the event listener
    if "event" in event_data:
        # Verify the request token
        request_token = event_data["token"]
        if request_token != SLACK_VERIFICATION_TOKEN:
            slack_events_adapter.emit('error', 'invalid verification token')
            message = "Request contains invalid Slack verification token: %s\n" \
                      "Slack adapter has: %s" % (request_token, SLACK_VERIFICATION_TOKEN)
            raise PermissionDenied(message)

        event_type = event_data["event"]["type"]
        slack_events_adapter.emit(event_type, event_data)
        return HttpResponse("")

    # default case
    return HttpResponse("")