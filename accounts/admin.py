from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'username', 'is_moderator', 'is_staff', 'created_at']
    list_filter = ['is_moderator', 'is_staff', 'is_superuser', 'is_active', 'created_at']
    search_fields = ['email', 'full_name', 'username']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('full_name', 'profile_image', 'is_moderator')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'full_name', 'is_moderator')
        }),
    )