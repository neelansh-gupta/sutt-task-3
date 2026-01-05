from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    # Home and search
    path('', views.forum_home, name='home'),
    path('threads/', views.all_threads, name='all_threads'),
    path('search/', views.search, name='search'),
    
    # Categories
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Threads
    path('thread/<int:pk>/', views.thread_detail, name='thread_detail'),
    path('thread/create/', views.create_thread, name='create_thread'),
    path('thread/create/<slug:category_slug>/', views.create_thread, name='create_thread_in_category'),
    path('thread/<int:pk>/edit/', views.edit_thread, name='edit_thread'),
    path('thread/<int:pk>/delete/', views.delete_thread, name='delete_thread'),
    path('thread/<int:pk>/lock/', views.toggle_thread_lock, name='toggle_thread_lock'),
    path('thread/<int:pk>/pin/', views.toggle_thread_pin, name='toggle_thread_pin'),
    path('thread/<int:pk>/like/', views.toggle_thread_like, name='toggle_thread_like'),
    
    # Replies
    path('thread/<int:thread_pk>/reply/', views.create_reply, name='create_reply'),
    path('reply/<int:pk>/edit/', views.edit_reply, name='edit_reply'),
    path('reply/<int:pk>/delete/', views.delete_reply, name='delete_reply'),
    path('reply/<int:pk>/like/', views.toggle_reply_like, name='toggle_reply_like'),
    path('reply/<int:pk>/solution/', views.mark_reply_solution, name='mark_solution'),
    
    # Reporting
    path('report/', views.report_content, name='report_content'),
    
    # Moderation
    path('moderation/', views.moderation_queue, name='moderation_queue'),
    path('moderation/users/', views.manage_users, name='manage_users'),
    path('moderation/toggle/<int:pk>/', views.toggle_moderator, name='toggle_moderator'),
    path('moderation/toggle-admin/<int:pk>/', views.toggle_admin, name='toggle_admin'),
    path('moderation/report/<int:pk>/', views.resolve_report, name='handle_report'),
]
