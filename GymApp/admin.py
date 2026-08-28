from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin    
# Register your models here.
from .models import *

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']

class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'mobile', 'plan', 'join_date']
    search_fields = ['full_name', 'user__username', 'mobile']
    list_filter = ['plan', 'join_date']

class EnquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'mobile', 'created_at']
    search_fields = ['name', 'email', 'mobile' ]
    list_filter = ['status', 'created_at']

admin.site.register(User, UserAdmin)
admin.site.register(MembershipPlan)
admin.site.register(Trainer)
admin.site.register(MemberProfile, MemberProfileAdmin)
admin.site.register(WorkoutPlan)
admin.site.register(Enquiry, EnquiryAdmin)
admin.site.register(Equipment)
admin.site.register(Attendance)
admin.site.register(Payment)
admin.site.register(Feedback)
# admin.site.register(FoodAnalysis)