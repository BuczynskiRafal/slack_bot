import uuid

from django.db import models
from django.utils import timezone


class AbstractModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(null=True, default=timezone.now)
    updated_at = models.DateTimeField(null=True, default=timezone.now)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at'])
        ]


class User(AbstractModel):
    slack_id = models.TextField(unique=True)
    channel_id = models.TextField(unique=True, null=True, blank=True)
    is_active = models.BooleanField()
    name = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.slack_id

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['slack_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

