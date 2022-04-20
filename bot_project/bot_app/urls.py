from django.urls import path
from .views import call, event_hook


app_name = 'bot_app'

urlpatterns = [
    path('call/', call, name='call'),
    path('event/hook/', event_hook, name='event_hook'),
]
