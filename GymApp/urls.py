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

    path('admin_trainers/', admin_trainers_list, name='admin_trainers_list'),
    path('admin_trainers_add/', admin_trainer_add, name='admin_trainer_add'),
    path('admin_trainers_edit/<int:trainer_id>/', admin_trainer_edit, name='admin_trainer_edit'),
    path('admin_trainers_delete/<int:trainer_id>/', admin_trainer_delete, name='admin_trainer_delete'),

    path('admin_members/', admin_members_list, name='admin_members_list'),
    path('admin_members_add/', admin_member_add, name='admin_member_add'),
    path('admin_members_edit/<int:member_id>/', admin_member_edit, name='admin_member_edit'),
    path('admin_members_delete/<int:member_id>/', admin_member_delete, name='admin_member_delete'),

]