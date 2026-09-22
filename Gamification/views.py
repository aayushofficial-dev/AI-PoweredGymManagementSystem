from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from django.contrib.auth.decorators import login_required

from .models import (
    Badge,
    Challenge,
    ChallengeParticipation,
    MemberBadge,
    MemberStats,
)


@login_required
def gamification_dashboard(request):
    member = request.user

    # Create statistics automatically for members who do not have them yet.
    stats, _ = MemberStats.objects.get_or_create(
        member=member
    )

    # Badges earned by the current member.
    badges = (
        MemberBadge.objects
        .filter(member=member)
        .select_related('badge')
        .order_by('-earned_at')
    )

    today = timezone.localdate()

    # Currently active challenges.
    challenges = (
        Challenge.objects
        .filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )
        .order_by('end_date')
    )

    # Current member's challenge participation.
    participations = (
        ChallengeParticipation.objects
        .filter(
            member=member,
            challenge__in=challenges,
        )
        .select_related('challenge')
    )

    participation_map = {
        participation.challenge_id: participation
        for participation in participations
    }

    # Prepare challenge data for the template.
    challenge_data = []

    for challenge in challenges:
        participation = participation_map.get(challenge.id)

        progress_percent = 0

        if participation and challenge.target > 0:
            progress_percent = min(
                int(
                    (participation.progress / challenge.target) * 100
                ),
                100
            )

        challenge_data.append({
            'challenge': challenge,
            'participation': participation,
            'progress_percent': progress_percent,
        })

    # Top 10 members by points.
    leaderboard = (
        MemberStats.objects
        .select_related('member')
        .order_by(
            '-points',
            '-current_streak',
            '-total_checkins',
        )[:10]
    )

    context = {
        'stats': stats,
        'badges': badges,
        'challenge_data': challenge_data,
        'leaderboard': leaderboard,
    }

    return render(
        request,
        'gamification/dashboard.html',
        context
    )


@login_required
def join_challenge(request, challenge_id):

    if request.method != 'POST':
        return redirect('gamification_dashboard')

    challenge = get_object_or_404(
        Challenge,
        id=challenge_id,
        is_active=True,
    )

    today = timezone.localdate()

    # Make sure the challenge is currently active.
    if challenge.start_date > today or challenge.end_date < today:
        messages.error(
            request,
            'This challenge is not currently active.'
        )

        return redirect('gamification_dashboard')

    participation, created = (
        ChallengeParticipation.objects.get_or_create(
            member=request.user,
            challenge=challenge,
        )
    )

    if created:
        messages.success(
            request,
            f'You joined "{challenge.name}"!'
        )
    else:
        messages.info(
            request,
            'You have already joined this challenge.'
        )

    return redirect('gamification_dashboard')