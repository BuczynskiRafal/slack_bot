from django.urls import path
from .views import slack_events, call_info
from .voting import vote, interactive, check_votes, check_points, check_winner_month


app_name = 'bot_app'

urlpatterns = [
    path('event/hook/', slack_events, name='slack_events'),
    path('program-wyroznien', call_info, name='call_info'),
    path('vote', vote, name='vote'),
    path('interactive', interactive, name='interactive'),
    path('check-votes', check_votes, name='check_votes'),
    path('check-winner-month', check_winner_month, name='check_winner_month'),
]
