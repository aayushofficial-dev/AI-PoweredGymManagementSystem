from django.urls import path

from . import views


urlpatterns = [
    path(
        '',views.gamification_dashboard,
        name='gamification_dashboard'
    ),

    path(
        'challenge/<int:challenge_id>/join/',
        views.join_challenge,
        name='join_challenge'
    ),
]