from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import (
    Badge,
    ChallengeParticipation,
    MemberBadge,
    MemberStats,
)


CHECKIN_POINTS = 10


@transaction.atomic
def process_checkin(member_profile):
    """
    Process all gamification rewards after a member checks in.
    """

    user = member_profile.user

    # Get or create the member's gamification statistics.
    stats, _ = MemberStats.objects.get_or_create(
        member=user
    )

    # Add points for the check-in.
    stats.points += CHECKIN_POINTS
    stats.total_checkins += 1

    # Update attendance streak.
    stats.current_streak = calculate_current_streak(
        member_profile
    )

    # Update longest streak.
    if stats.current_streak > stats.longest_streak:
        stats.longest_streak = stats.current_streak

    stats.save(
        update_fields=[
            'points',
            'total_checkins',
            'current_streak',
            'longest_streak',
        ]
    )

    # Check and award badges.
    award_badges(stats)

    # Update active challenges.
    update_challenges(user)


def calculate_current_streak(member_profile):
    """
    Calculate the number of consecutive attendance days
    ending today.
    """

    attendance_dates = set(
        member_profile.attendances.values_list(
            'date',
            flat=True
        )
    )

    today = timezone.localdate()

    # No attendance today means the current streak is zero.
    if today not in attendance_dates:
        return 0

    streak = 0
    current_date = today

    while current_date in attendance_dates:
        streak += 1
        current_date -= timedelta(days=1)

    return streak


def award_badges(stats):
    """
    Award every badge the member has reached.
    """

    available_badges = Badge.objects.filter(
        points_required__lte=stats.points
    )

    for badge in available_badges:
        MemberBadge.objects.get_or_create(
            member=stats.member,
            badge=badge,
        )


def update_challenges(user):
    """
    Increase progress for challenges the member has joined.
    """

    today = timezone.localdate()

    participations = (
        ChallengeParticipation.objects
        .select_related('challenge')
        .filter(
            member=user,
            challenge__is_active=True,
            challenge__start_date__lte=today,
            challenge__end_date__gte=today,
            completed=False,
        )
    )

    for participation in participations:
        challenge = participation.challenge

        participation.progress += 1

        if participation.progress >= challenge.target:
            participation.progress = challenge.target
            participation.completed = True

            # Give the challenge reward.
            stats, _ = MemberStats.objects.get_or_create(
                member=user
            )

            stats.points += challenge.points_reward
            stats.save(update_fields=['points'])

            # Check if the new points unlock badges.
            award_badges(stats)

        participation.save(
            update_fields=[
                'progress',
                'completed',
            ]
        )