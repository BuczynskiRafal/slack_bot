"""Module contain methods for scraping users and save this data in db"""
import json
from django.conf import settings

from .models import SlackProfile, SlackUser
from .forms import SlackProfileForm, SlackUserForm

CLIENT = settings.CLIENT

# You probably want to use a database to store any user information ;)
users_store = {}

# Put users into the dict
def save_users(users_array):
    for user in users_array:
        # Key user info on their unique user ID
        user_id = user["id"]
        # Store the entire user object (you may not need all of the info)
        users_store[user_id] = user


def save_users_to_json_file():
    """Create json file and save users data."""
    try:
        result = CLIENT.users_list()
        save_users(result["members"])
        json_users = json.dumps(users_store)
        with open('json_data.json', 'w') as outfile:
            outfile.write(json_users)
    except Exception as e:
        print(e)

from django.core import serializers


def save_users_to_db():
    try:
        result = CLIENT.users_list()
        save_users(result["members"])
        for user, attributes in users_store.items():

            slack_profile = SlackProfile.objects.create(
                title=attributes['profile']['title'],
                phone=attributes['profile']['phone'],
                skype=attributes['profile']['skype'],
                real_name=attributes['profile']['real_name'],
                real_name_normalized=attributes['profile']['real_name_normalized'],
                display_name=attributes['profile']['display_name'],
                first_name=attributes['profile']['first_name'],
                last_name=attributes['profile']['last_name'],
                team=attributes['profile']['team'],
            )
            slack_profile.save()

            slack_user = SlackUser.objects.create(
                slack_id=attributes['id'],
                team_id=attributes['team_id'],
                name=attributes['name'],
                deleted=attributes['deleted'],
                color=attributes['color'],
                real_name=attributes['real_name'],
                tz=attributes['tz'],
                tz_label=attributes['tz_label'],
                tz_offset=attributes['tz_offset'],
                is_admin=attributes['is_admin'],
                is_owner=attributes['is_owner'],
                is_primary_owner=attributes['is_primary_owner'],
                is_restricted=attributes['is_restricted'],
                is_ultra_restricted=attributes['is_ultra_restricted'],
                is_bot=attributes['is_bot'],
                is_app_user=attributes['is_app_user'],
                updated=attributes['updated'],
                is_email_confirmed=attributes['is_email_confirmed'],
                who_can_share_contact_card=attributes['who_can_share_contact_card'],
                profile=slack_profile
            )
            print('slack_user')
            slack_user.save()

            print('finish')

    except Exception as e:
        print(e)

save_users_to_db()

