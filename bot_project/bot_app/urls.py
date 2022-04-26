from django.urls import path
from .views import slack_events, call_info
from .through_dialogs import send_voting_form, interactive


app_name = 'bot_app'

urlpatterns = [
    path('event/hook/', slack_events, name='slack_events'),
    path('program-wyroznien', call_info, name='call_info'),
    path('vote', send_voting_form, name='send_voting_form'),
    path('interactive', interactive, name='interactive'),
]
