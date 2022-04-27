from django.urls import path
from .views import slack_events, call_info
from .voting import vote, interactive


app_name = 'bot_app'

urlpatterns = [
    path('event/hook/', slack_events, name='slack_events'),
    path('program-wyroznien', call_info, name='call_info'),
    path('vote', vote, name='vote'),
    path('interactive', interactive, name='interactive'),
]
