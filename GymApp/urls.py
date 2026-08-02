from django.urls import path

from .views import *

urlpatterns = [
    path('', home, name='home'), #include gymapp URLs
    path('about/', about, name='about'),
    path('admin-login/', admin_login_view, name='admin_login'),
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('logout/', logout_view, name='logout'),
    path('admin_plans/', admin_plans_list, name='admin_plans_list'),
    path('admin_plans_add/', admin_plan_add, name='admin_plan_add'),
    path('admin_plans_edit/<int:plan_id>/', admin_plan_edit, name='admin_plan_edit'),
    path('admin_plans_delete/<int:plan_id>/', admin_plan_delete, name='admin_plan_delete'),
]