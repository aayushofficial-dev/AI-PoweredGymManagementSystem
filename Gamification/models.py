from django.conf import settings
from django.db import models


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
    icon = models.CharField(max_length=20, default='🏆')
    points_required = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class MemberBadge(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gamification_badges'
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE
    )
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'badge'],
                name='unique_member_badge'
            )
        ]

    def __str__(self):
        return f'{self.member.username} - {self.badge.name}'