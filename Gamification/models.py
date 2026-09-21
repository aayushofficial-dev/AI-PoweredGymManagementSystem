from django.db import models
from django.conf import settings


class MemberStats(models.Model):
    member = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gamification_stats'
    )

    points = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    total_checkins = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.member.username

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🏆')
    points_required = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class MemberBadge(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='badges'
    )

    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE
    )

    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('member', 'badge')

    def __str__(self):
        return f"{self.member.username} - {self.badge.name}"

class Challenge(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()

    target = models.PositiveIntegerField()

    start_date = models.DateField()
    end_date = models.DateField()

    points_reward = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ChallengeParticipation(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE
    )

    progress = models.PositiveIntegerField(default=0)

    joined_at = models.DateTimeField(auto_now_add=True)

    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('member', 'challenge')