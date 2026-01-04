from django.contrib import admin
from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'course', 'views', 'created_at']
    list_filter = ['type', 'course__department', 'created_at']
    search_fields = ['title', 'course__code', 'course__title']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'type', 'link', 'course')
        }),
        ('Details', {
            'fields': ('description', 'uploaded_by', 'views')
        }),
    )