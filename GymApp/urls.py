from django.urls import path

from .views import *

urlpatterns = [
    path('', home, name='home'), #include gymapp URLs
    path('about/', about, name='about')
]