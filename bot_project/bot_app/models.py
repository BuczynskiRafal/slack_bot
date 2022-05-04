from django.db import models


class SlackProfile(models.Model):
    title = models.TextField()
    phone = models.TextField()
    skype = models.TextField()
    real_name = models.TextField(unique=True)
    real_name_normalized = models.TextField()
    display_name = models.TextField()
    first_name = models.TextField()
    last_name = models.TextField()
    team = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TotalPoints(models.Model):
    points_team_up_to_win = models.IntegerField(default=0)
    points_act_to_deliver = models.IntegerField(default=0)
    points_disrupt_to_grow = models.IntegerField(default=0)
    ts = models.DateTimeField(auto_now=True)


class SlackUser(models.Model):
    slack_id = models.TextField(unique=True, blank=True, null=True)
    team_id = models.TextField(blank=True, null=True)
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
    profile = models.OneToOneField(
        SlackProfile, on_delete=models.CASCADE, related_name="slack_profile"
    )
    points = models.OneToOneField(TotalPoints, on_delete=models.CASCADE, related_name="user_points", null=True)

    def __str__(self):
        return f"{self.slack_id} -> {self.name}"


class AbstractVotingResults(models.Model):
    team_up_to_win = models.OneToOneField(
        SlackUser, on_delete=models.RESTRICT, null=True
    )
    points_team_up_to_win = models.IntegerField(default=0)
    act_to_deliver = models.OneToOneField(
        SlackUser, on_delete=models.RESTRICT, null=True
    )
    points_act_to_deliver = models.IntegerField(default=0)
    disrupt_to_grow = models.OneToOneField(
        SlackUser, on_delete=models.RESTRICT, null=True
    )
    points_disrupt_to_grow = models.IntegerField(default=0)
    voting_user_id = models.OneToOneField(
        SlackUser, on_delete=models.RESTRICT, null=True
    )
    ts = models.FloatField(null=True)

    class Meta:
        abstract = True


class VotingResults(AbstractVotingResults):
    team_up_to_win = models.OneToOneField(
        SlackUser, on_delete=models.RESTRICT, related_name="team_up_to_win", null=True
    )
    act_to_deliver = models.OneToOneField(
        SlackUser, on_delete=models.RESTRICT, related_name="act_to_deliver", null=True
    )
    disrupt_to_grow = models.OneToOneField(
        SlackUser, on_delete=models.RESTRICT, related_name="disrupt_to_grow", null=True
    )
    voting_user_id = models.OneToOneField(
        SlackUser, on_delete=models.RESTRICT, related_name="voting_user_id", null=True
    )
    ts = models.FloatField(null=True)

    def __str__(self):
        return f"Class: {self.__class__.__name__}, user: {self.voting_user_id}."


class ArchiveVotingResults(AbstractVotingResults):
    team_up_to_win = models.ForeignKey(
        SlackUser,
        on_delete=models.RESTRICT,
        related_name="archive_team_up_to_win",
        null=True,
        unique=False,
    )
    act_to_deliver = models.ForeignKey(
        SlackUser,
        on_delete=models.RESTRICT,
        related_name="archive_act_to_deliver",
        null=True,
        unique=False,
    )
    disrupt_to_grow = models.ForeignKey(
        SlackUser,
        on_delete=models.RESTRICT,
        related_name="archive_disrupt_to_grow",
        null=True,
        unique=False,
    )
    voting_user_id = models.ForeignKey(
        SlackUser,
        on_delete=models.RESTRICT,
        related_name="archive_voting_user_id",
        null=True,
        unique=False,
    )
    ts = models.FloatField(null=True)

    def __str__(self):
        return f"Class: {self.__class__.__name__}, user: {self.voting_user_id}."
