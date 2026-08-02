from django.urls import path

from .views import *

urlpatterns = [
    path('', home, name='home'), #include gymapp URLs
    path('about/', about, name='about'),
    path('admin_login/', admin_login_view, name='admin_login'),
    path('admin_dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('logout/', logout_view, name='logout'),
]