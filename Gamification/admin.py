from django.contrib import admin

from .models import (
    Badge,
    Challenge,
    ChallengeParticipation,
    MemberBadge,
    MemberStats,
)


@admin.register(MemberStats)
class MemberStatsAdmin(admin.ModelAdmin):

    list_display = (
        'member',
        'points',
        'current_streak',
        'longest_streak',
        'total_checkins',
    )

    search_fields = (
        'member__username',
        'member__first_name',
        'member__last_name',
    )

    ordering = ('-points',)


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'icon',
        'points_required',
    )

    search_fields = (
        'name',
    )


@admin.register(MemberBadge)
class MemberBadgeAdmin(admin.ModelAdmin):

    list_display = (
        'member',
        'badge',
        'earned_at',
    )

    search_fields = (
        'member__username',
        'badge__name',
    )

    list_filter = (
        'badge',
    )


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'target',
        'points_reward',
        'start_date',
        'end_date',
        'is_active',
    )

    list_filter = (
        'is_active',
        'start_date',
        'end_date',
    )

    search_fields = (
        'name',
    )


@admin.register(ChallengeParticipation)
class ChallengeParticipationAdmin(admin.ModelAdmin):

    list_display = (
        'member',
        'challenge',
        'progress',
        'completed',
        'joined_at',
    )

    list_filter = (
        'completed',
        'challenge',
    )

    search_fields = (
        'member__username',
        'challenge__name',
    )