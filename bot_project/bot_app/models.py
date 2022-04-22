import uuid

from django.db import models
from django.utils import timezone


class SlackProfile(models.Model):
    title = models.TextField()
    phone = models.TextField()
    skype = models.TextField()
    real_name = models.TextField()
    real_name_normalized = models.TextField()
    display_name = models.TextField()
    first_name = models.TextField()
    last_name = models.TextField()
    team = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class SlackUser(models.Model):
    slack_id = models.TextField(unique=True, blank=True, null=True)
    team_id = models.TextField(unique=True, blank=True, null=True)
    name = models.TextField(unique=True, blank=True, null=True)
    deleted = models.BooleanField(default=False)
    color = models.TextField(unique=False, blank=True, null=True)
    real_name = models.TextField(unique=False, blank=True, null=True)
    tz = models.TextField(unique=False, blank=True, null=True)
    tz_label = models.TextField(unique=False, blank=True, null=True)
    tz_offset = models.TextField(unique=False, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    is_primary_owner = models.BooleanField(default=False)
    is_restricted = models.BooleanField(default=False)
    is_ultra_restricted = models.BooleanField(default=False)
    is_bot = models.BooleanField(default=False)
    is_app_user = models.BooleanField(default=False)
    updated = models.SmallIntegerField(default=0)
    is_email_confirmed = models.BooleanField(default=False)
    who_can_share_contact_card = models.TextField(unique=False, blank=True, null=True)
    profile = models.ForeignKey(SlackProfile, on_delete=models.CASCADE, related_name="slack_profile")

    def __str__(self):
        return f"{self.slack_id}"
