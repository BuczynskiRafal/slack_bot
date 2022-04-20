import os
import string
import slack
from datetime import datetime, timedelta
from django.shortcuts import render
from slackeventsapi import SlackEventAdapter

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from django.http import HttpResponse, JsonResponse


# slack_events_adapter = SlackEventAdapter(os.environ[settings.SIGNING_SECRET], "/slack/events", 'bot_app')

# client = slack.WebClient(token=os.environ[settings.SLACK_TOKEN])

client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
# check bot id
# BOT_ID = client.api_call("auth.test")["user_id"]

# client.chat_postMessage(channel='#test', text='Hello from test script')


def call(request):
    pass


@csrf_exempt
def event_hook(request):
    return HttpResponse(status=200)
    # json_dict = json.loads(request.body.decode('utf-8'))
    #
    # if json_dict['token'] != settings.VERIFICATION_TOKEN:
    #     return HttpResponse(status=403)

    #return the challenge code here
    # if 'type' in json_dict:
    #     if json_dict['type'] == 'url_verification':
    #         response_dict = {"challenge": json_dict['challenge']}
    #         return JsonResponse(response_dict, safe=False)
    # return HttpResponse(status=500)
