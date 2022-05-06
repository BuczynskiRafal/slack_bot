from django.urls import path
from .events import slack_events
from .slash import vote, interactive, check_votes, check_points, check_winner_month, call_info

app_name = 'bot_app'

urlpatterns = [
    path('event/hook/', slack_events, name='slack_events'),
    path('program-wyroznien', call_info, name='call_info'),
    path('vote', vote, name='vote'),
    path('interactive', interactive, name='interactive'),
    path('check-votes', check_votes, name='check_votes'),
    path('check-points', check_points, name='check_points'),
    path('check-winner-month', check_winner_month, name='check_winner_month'),
]
