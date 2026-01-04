from django.contrib import admin
from .models import Department, Course


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'department', 'credits', 'created_at']
    list_filter = ['department', 'credits']
    search_fields = ['code', 'title']
    prepopulated_fields = {'slug': ('code', 'title')}
    ordering = ['code']