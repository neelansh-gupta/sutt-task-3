from django.contrib import admin
from .models import Category, Tag, Thread, Reply, ThreadLike, ReplyLike, Report


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_locked', 'is_pinned', 'is_deleted', 'views', 'created_at']
    list_filter = ['category', 'is_locked', 'is_pinned', 'is_deleted', 'created_at']
    search_fields = ['title', 'content', 'author__email', 'author__full_name']
    filter_horizontal = ['courses', 'resources', 'tags']
    ordering = ['-created_at']
    
    actions = ['lock_threads', 'unlock_threads', 'pin_threads', 'unpin_threads']
    
    def lock_threads(self, request, queryset):
        queryset.update(is_locked=True)
    lock_threads.short_description = "Lock selected threads"
    
    def unlock_threads(self, request, queryset):
        queryset.update(is_locked=False)
    unlock_threads.short_description = "Unlock selected threads"
    
    def pin_threads(self, request, queryset):
        queryset.update(is_pinned=True)
    pin_threads.short_description = "Pin selected threads"
    
    def unpin_threads(self, request, queryset):
        queryset.update(is_pinned=False)
    unpin_threads.short_description = "Unpin selected threads"


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ['get_short_content', 'author', 'thread', 'is_deleted', 'is_solution', 'created_at']
    list_filter = ['is_deleted', 'is_solution', 'created_at']
    search_fields = ['content', 'author__email', 'thread__title']
    ordering = ['-created_at']
    
    def get_short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    get_short_content.short_description = 'Content'


@admin.register(ThreadLike)
class ThreadLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'thread', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'thread__title']


@admin.register(ReplyLike)
class ReplyLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'reply', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['get_content_type', 'reporter', 'reason', 'status', 'moderator', 'created_at']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['reporter__email', 'description']
    ordering = ['status', '-created_at']
    
    def get_content_type(self, obj):
        return "Thread" if obj.thread else "Reply"
    get_content_type.short_description = 'Content Type'
    
    actions = ['mark_resolved', 'mark_dismissed']
    
    def mark_resolved(self, request, queryset):
        for report in queryset:
            report.resolve(request.user, 'Resolved via admin action')
    mark_resolved.short_description = "Mark as resolved"
    
    def mark_dismissed(self, request, queryset):
        for report in queryset:
            report.dismiss(request.user, 'Dismissed via admin action')
    mark_dismissed.short_description = "Dismiss reports"