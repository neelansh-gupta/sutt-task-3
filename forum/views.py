from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import reverse
from django_ratelimit.decorators import ratelimit
from django.conf import settings
from django.db import connection

User = get_user_model()

# Import PostgreSQL search if available
try:
    from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

# Import fuzzy search for SQLite
try:
    from fuzzywuzzy import fuzz, process
    HAS_FUZZY = True
except ImportError:
    HAS_FUZZY = False

from .models import Category, Thread, Reply, Tag, ThreadLike, ReplyLike, Report
from .forms import ThreadForm, ReplyForm, ReportForm
from .permissions import (
    can_edit_content, can_delete_content, can_lock_thread,
    can_pin_thread, can_mark_solution, moderator_required
)
from .notifications import send_reply_notification, send_thread_locked_notification
from courses.models import Course
from resources.models import Resource


def forum_home(request):
    """Forum home page showing all categories"""
    categories = Category.objects.annotate(
        thread_count=Count('threads', filter=Q(threads__is_deleted=False))
    ).order_by('order', 'name')
    
    # Get recent threads
    recent_threads = Thread.objects.filter(
        is_deleted=False
    ).select_related('author', 'category').order_by('-last_activity')[:5]
    
    # Get popular threads (most liked)
    popular_threads = Thread.objects.filter(
        is_deleted=False
    ).annotate(
        like_count=Count('likes')
    ).select_related('author', 'category').order_by('-like_count')[:5]
    
    context = {
        'categories': categories,
        'recent_threads': recent_threads,
        'popular_threads': popular_threads,
    }
    return render(request, 'forum/home.html', context)


def all_threads(request):
    """View all threads with sorting and filtering"""
    threads = Thread.objects.filter(is_deleted=False).select_related(
        'author', 'category'
    ).prefetch_related(
        'tags',
        Prefetch('replies', queryset=Reply.objects.filter(is_deleted=False))
    ).annotate(
        reply_count=Count('replies', filter=Q(replies__is_deleted=False)),
        like_count=Count('likes')
    )
    
    # Sorting
    sort = request.GET.get('sort', 'latest')
    if sort == 'popular':
        threads = threads.order_by('-like_count', '-reply_count')
    elif sort == 'latest':
        threads = threads.order_by('-last_activity')
    elif sort == 'oldest':
        threads = threads.order_by('created_at')
    elif sort == 'most_viewed':
        threads = threads.order_by('-views')
    elif sort == 'unanswered':
        threads = threads.filter(reply_count=0).order_by('-created_at')
    
    # Category filter
    category_filter = request.GET.get('category')
    if category_filter:
        threads = threads.filter(category__slug=category_filter)
    
    # Tag filter
    tag_filter = request.GET.get('tag')
    if tag_filter:
        threads = threads.filter(tags__slug=tag_filter)
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        threads = threads.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(threads, 20)
    page = request.GET.get('page')
    threads = paginator.get_page(page)
    
    # Get all categories and tags for filtering
    categories = Category.objects.all().order_by('name')
    tags = Tag.objects.all()
    
    context = {
        'threads': threads,
        'categories': categories,
        'tags': tags,
        'current_sort': sort,
        'current_category': category_filter,
        'current_tag': tag_filter,
        'search_query': search_query,
    }
    return render(request, 'forum/all_threads.html', context)


def category_detail(request, slug):
    """Display threads in a category"""
    category = get_object_or_404(Category, slug=slug)
    
    threads = Thread.objects.filter(
        category=category,
        is_deleted=False
    ).select_related('author').prefetch_related(
        'tags',
        Prefetch('replies', queryset=Reply.objects.filter(is_deleted=False))
    ).annotate(
        reply_count=Count('replies', filter=Q(replies__is_deleted=False)),
        like_count=Count('likes')
    ).order_by('-is_pinned', '-last_activity')
    
    # Filtering
    tag_filter = request.GET.get('tag')
    if tag_filter:
        threads = threads.filter(tags__slug=tag_filter)
    
    search_query = request.GET.get('q')
    if search_query:
        threads = threads.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Sorting
    sort = request.GET.get('sort', 'latest')
    if sort == 'popular':
        threads = threads.order_by('-is_pinned', '-like_count', '-reply_count')
    elif sort == 'unanswered':
        threads = threads.filter(reply_count=0)
    
    # Pagination
    paginator = Paginator(threads, 10)
    page = request.GET.get('page')
    threads = paginator.get_page(page)
    
    # Get all tags for filtering
    tags = Tag.objects.all()
    
    context = {
        'category': category,
        'threads': threads,
        'tags': tags,
        'current_tag': tag_filter,
        'search_query': search_query,
        'current_sort': sort,
    }
    return render(request, 'forum/category_detail.html', context)


def thread_detail(request, pk):
    """Display a thread and its replies"""
    thread = get_object_or_404(
        Thread.objects.select_related('author', 'category').prefetch_related(
            'tags', 'courses', 'resources'
        ),
        pk=pk
    )
    
    # Check if thread is deleted
    if thread.is_deleted and not request.user.is_staff:
        messages.error(request, "This thread has been deleted.")
        return redirect('forum:home')
    
    # Increment view count
    thread.views += 1
    thread.save(update_fields=['views'])
    
    # Get replies
    replies = Reply.objects.filter(
        thread=thread,
        is_deleted=False
    ).select_related('author').order_by('created_at')
    
    # Check permissions
    can_edit = can_edit_content(request.user, thread)
    can_delete = can_delete_content(request.user, thread)
    can_lock = can_lock_thread(request.user)
    can_pin = can_pin_thread(request.user)
    
    # Check if user has liked the thread
    user_liked = False
    if request.user.is_authenticated:
        user_liked = ThreadLike.objects.filter(user=request.user, thread=thread).exists()
    
    context = {
        'thread': thread,
        'replies': replies,
        'can_edit': can_edit,
        'can_delete': can_delete,
        'can_lock': can_lock,
        'can_pin': can_pin,
        'user_liked': user_liked,
    }
    return render(request, 'forum/thread_detail.html', context)


@login_required
@ratelimit(key='user', rate='5/h', method='POST')
def create_thread(request, category_slug=None):
    """Create a new thread"""
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
    
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user
            if category:
                thread.category = category
            thread.save()
            form.save_m2m()  # Save many-to-many relationships
            
            messages.success(request, "Thread created successfully!")
            return redirect('forum:thread_detail', pk=thread.pk)
    else:
        initial = {'category': category} if category else {}
        form = ThreadForm(initial=initial)
    
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'forum/create_thread.html', context)


@login_required
def edit_thread(request, pk):
    """Edit a thread"""
    thread = get_object_or_404(Thread, pk=pk)
    
    if not can_edit_content(request.user, thread):
        messages.error(request, "You don't have permission to edit this thread.")
        return redirect('forum:thread_detail', pk=pk)
    
    if request.method == 'POST':
        form = ThreadForm(request.POST, instance=thread)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.edited_at = timezone.now()
            thread.save()
            form.save_m2m()
            
            messages.success(request, "Thread updated successfully!")
            return redirect('forum:thread_detail', pk=pk)
    else:
        form = ThreadForm(instance=thread)
    
    context = {
        'form': form,
        'thread': thread,
    }
    return render(request, 'forum/edit_thread.html', context)


@login_required
@require_POST
def delete_thread(request, pk):
    """Delete a thread"""
    thread = get_object_or_404(Thread, pk=pk)
    
    if not can_delete_content(request.user, thread):
        messages.error(request, "You don't have permission to delete this thread.")
        return redirect('forum:thread_detail', pk=pk)
    
    thread.is_deleted = True
    thread.save()
    
    messages.success(request, "Thread deleted successfully!")
    return redirect('forum:category_detail', slug=thread.category.slug)


@login_required
@require_POST
@ratelimit(key='user', rate='10/h', method='POST')
def create_reply(request, thread_pk):
    """Create a reply to a thread"""
    thread = get_object_or_404(Thread, pk=thread_pk)
    
    if thread.is_locked:
        messages.error(request, "This thread is locked and cannot be replied to.")
        return redirect('forum:thread_detail', pk=thread_pk)
    
    form = ReplyForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.author = request.user
        reply.thread = thread
        reply.save()
        
        # Send email notification to thread author
        send_reply_notification(reply)
        
        messages.success(request, "Reply posted successfully!")
    else:
        messages.error(request, "Error posting reply. Please check your input.")
    
    return redirect('forum:thread_detail', pk=thread_pk)


@login_required
def edit_reply(request, pk):
    """Edit a reply"""
    reply = get_object_or_404(Reply, pk=pk)
    
    if not can_edit_content(request.user, reply):
        messages.error(request, "You don't have permission to edit this reply.")
        return redirect('forum:thread_detail', pk=reply.thread.pk)
    
    if request.method == 'POST':
        form = ReplyForm(request.POST, instance=reply)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.edited_at = timezone.now()
            reply.save()
            
            messages.success(request, "Reply updated successfully!")
            return redirect('forum:thread_detail', pk=reply.thread.pk)
    else:
        form = ReplyForm(instance=reply)
    
    context = {
        'form': form,
        'reply': reply,
    }
    return render(request, 'forum/edit_reply.html', context)


@login_required
@require_POST
def delete_reply(request, pk):
    """Delete a reply"""
    reply = get_object_or_404(Reply, pk=pk)
    thread_pk = reply.thread.pk
    
    if not can_delete_content(request.user, reply):
        messages.error(request, "You don't have permission to delete this reply.")
        return redirect('forum:thread_detail', pk=thread_pk)
    
    reply.is_deleted = True
    reply.save()
    
    messages.success(request, "Reply deleted successfully!")
    return redirect('forum:thread_detail', pk=thread_pk)


@login_required
@require_POST
def toggle_thread_like(request, pk):
    """Toggle like on a thread"""
    thread = get_object_or_404(Thread, pk=pk)
    
    like, created = ThreadLike.objects.get_or_create(
        user=request.user,
        thread=thread
    )
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': thread.likes.count()
        })
    
    return redirect('forum:thread_detail', pk=pk)


@login_required
@require_POST
def toggle_reply_like(request, pk):
    """Toggle like on a reply"""
    reply = get_object_or_404(Reply, pk=pk)
    
    like, created = ReplyLike.objects.get_or_create(
        user=request.user,
        reply=reply
    )
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': reply.likes.count()
        })
    
    return redirect('forum:thread_detail', pk=reply.thread.pk)


@login_required
@require_POST
def toggle_thread_lock(request, pk):
    """Lock/unlock a thread (moderator only)"""
    if not can_lock_thread(request.user):
        return HttpResponseForbidden("You don't have permission to lock threads.")
    
    thread = get_object_or_404(Thread, pk=pk)
    thread.is_locked = not thread.is_locked
    thread.save()
    
    # Send notification if thread was locked
    if thread.is_locked:
        send_thread_locked_notification(thread, request.user)
    
    status = "locked" if thread.is_locked else "unlocked"
    messages.success(request, f"Thread {status} successfully!")
    return redirect('forum:thread_detail', pk=pk)


@login_required
@require_POST
def toggle_thread_pin(request, pk):
    """Pin/unpin a thread (moderator only)"""
    if not can_pin_thread(request.user):
        return HttpResponseForbidden("You don't have permission to pin threads.")
    
    thread = get_object_or_404(Thread, pk=pk)
    thread.is_pinned = not thread.is_pinned
    thread.save()
    
    status = "pinned" if thread.is_pinned else "unpinned"
    messages.success(request, f"Thread {status} successfully!")
    return redirect('forum:thread_detail', pk=pk)


@login_required
@require_POST
def mark_reply_solution(request, pk):
    """Mark a reply as the solution (thread author only)"""
    reply = get_object_or_404(Reply, pk=pk)
    thread = reply.thread
    
    if not can_mark_solution(request.user, thread):
        return HttpResponseForbidden("Only the thread author can mark solutions.")
    
    # Unmark previous solution if exists
    Reply.objects.filter(thread=thread, is_solution=True).update(is_solution=False)
    
    # Mark this reply as solution
    reply.is_solution = True
    reply.save()
    
    messages.success(request, "Reply marked as solution!")
    return redirect('forum:thread_detail', pk=thread.pk)


@login_required
@ratelimit(key='user', rate='3/h', method='POST')
def report_content(request):
    """Report inappropriate content"""
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reported_by = request.user
            
            # Determine content type
            content_type = request.POST.get('content_type')
            content_id = request.POST.get('content_id')
            
            if content_type == 'thread':
                report.thread = get_object_or_404(Thread, pk=content_id)
            elif content_type == 'reply':
                report.reply = get_object_or_404(Reply, pk=content_id)
            
            report.save()
            messages.success(request, "Report submitted successfully. Moderators will review it soon.")
            
            # Redirect back to the content
            if report.thread:
                return redirect('forum:thread_detail', pk=report.thread.pk)
            elif report.reply:
                return redirect('forum:thread_detail', pk=report.reply.thread.pk)
    
    return redirect('forum:home')


@login_required
@moderator_required
def manage_users(request):
    """Manage users and moderators (admins only)"""
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Base queryset with annotations
    users = User.objects.annotate(
        thread_count=Count('threads', distinct=True),
        reply_count=Count('replies', distinct=True)
    )
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(username__icontains=search_query)
        )
    
    # Apply role filter
    if role_filter == 'admin':
        users = users.filter(is_superuser=True)
    elif role_filter == 'moderator':
        users = users.filter(
            is_moderator=True, is_superuser=False
        )
    elif role_filter == 'regular':
        users = users.filter(
            is_moderator=False, is_staff=False, is_superuser=False
        )
    
    # Apply sorting
    if sort_by:
        users = users.order_by(sort_by)
    
    # Calculate statistics
    total_users = User.objects.count()
    total_admins = User.objects.filter(is_superuser=True).count()
    total_moderators = User.objects.filter(
        is_moderator=True, is_superuser=False
    ).count()
    total_regular = User.objects.filter(
        is_moderator=False, is_staff=False, is_superuser=False
    ).count()
    active_today = User.objects.filter(
        last_login__gte=timezone.now() - timedelta(days=1)
    ).count()
    new_this_week = User.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(users, 20)  # 20 users per page
    page = request.GET.get('page', 1)
    
    try:
        users_page = paginator.page(page)
    except:
        users_page = paginator.page(1)
    
    context = {
        'users': users_page,
        'page_obj': users_page,
        'is_paginated': paginator.num_pages > 1,
        'total_users': total_users,
        'total_admins': total_admins,
        'total_moderators': total_moderators,
        'total_regular': total_regular,
        'active_today': active_today,
        'new_this_week': new_this_week,
    }
    
    return render(request, 'forum/manage_users.html', context)


@login_required
@moderator_required
def toggle_moderator(request, pk):
    """Toggle moderator status for a user"""
    if request.method != 'POST':
        return redirect('forum:manage_users')
    
    user = get_object_or_404(User, pk=pk)
    
    # Don't allow changing your own status
    if user == request.user:
        messages.error(request, "You cannot change your own moderator status.")
        return redirect('forum:manage_users')
    
    # Toggle moderator status
    user.is_moderator = not user.is_moderator
    user.save()
    
    if user.is_moderator:
        messages.success(request, f"✅ {user.get_display_name()} is now a moderator!")
    else:
        messages.success(request, f"❌ {user.get_display_name()} is no longer a moderator.")
    
    return redirect('forum:manage_users')


@login_required
def toggle_admin(request, pk):
    """Toggle admin status for a user (superusers only)"""
    # Only superusers can make other admins
    if not request.user.is_superuser:
        messages.error(request, "Only admins can grant admin privileges.")
        return redirect('forum:manage_users')
    
    if request.method != 'POST':
        return redirect('forum:manage_users')
    
    user = get_object_or_404(User, pk=pk)
    
    # Don't allow changing your own status
    if user == request.user:
        messages.error(request, "You cannot change your own admin status.")
        return redirect('forum:manage_users')
    
    # Toggle admin status (superuser + staff)
    if user.is_superuser:
        # Remove admin privileges
        user.is_superuser = False
        user.is_staff = False
        messages.success(request, f"👑 {user.get_display_name()} is no longer an admin.")
    else:
        # Grant admin privileges
        user.is_superuser = True
        user.is_staff = True  # Staff is needed to access Django admin
        user.is_moderator = True  # Admins should also be moderators
        messages.success(request, f"👑 {user.get_display_name()} is now an ADMIN with full privileges!")
    
    user.save()
    return redirect('forum:manage_users')


@login_required
@moderator_required
def moderation_queue(request):
    """View pending reports (moderators only)"""
    reports = Report.objects.filter(
        status='pending'
    ).select_related(
        'thread', 'reply', 'reporter'
    ).order_by('-created_at')
    
    context = {
        'reports': reports,
    }
    return render(request, 'forum/moderation_queue.html', context)


@login_required
@moderator_required
@require_POST
def resolve_report(request, pk):
    """Resolve a report (moderators only)"""
    report = get_object_or_404(Report, pk=pk)
    
    action = request.POST.get('action')
    notes = request.POST.get('notes', '')
    
    if action == 'resolve':
        report.resolve(request.user, notes)
        messages.success(request, "Report resolved successfully!")
    elif action == 'dismiss':
        report.dismiss(request.user, notes)
        messages.success(request, "Report dismissed.")
    
    return redirect('forum:moderation_queue')


def search(request):
    """Search threads and replies with fuzzy matching for both PostgreSQL and SQLite"""
    query = request.GET.get('q', '')
    threads = []
    replies = []
    
    if query:
        # Detect database type
        db_vendor = connection.vendor
        
        if db_vendor == 'postgresql' and HAS_POSTGRES:
            # Use PostgreSQL full-text search and trigram similarity
            try:
                # Search threads with fuzzy matching
                threads = Thread.objects.filter(is_deleted=False).annotate(
                    similarity=TrigramSimilarity('title', query) + TrigramSimilarity('content', query),
                    search=SearchVector('title', weight='A') + SearchVector('content', weight='B'),
                ).filter(
                    Q(similarity__gt=0.1) | Q(search=SearchQuery(query))
                ).order_by('-similarity').select_related('author', 'category')[:20]
                
                # Search replies with fuzzy matching
                replies = Reply.objects.filter(is_deleted=False).annotate(
                    similarity=TrigramSimilarity('content', query),
                ).filter(
                    similarity__gt=0.1
                ).order_by('-similarity').select_related('author', 'thread')[:20]
            except Exception as e:
                # Fallback if PostgreSQL extensions not installed
                threads, replies = _simple_search(query)
                
        elif db_vendor == 'sqlite' and HAS_FUZZY:
            # Use fuzzy search for SQLite
            threads, replies = _fuzzy_search_sqlite(query)
            
        else:
            # Fallback to simple search
            threads, replies = _simple_search(query)
    
    context = {
        'query': query,
        'threads': threads,
        'replies': replies,
        'result_count': len(threads) + len(replies),
        'search_method': _get_search_method(connection.vendor)
    }
    return render(request, 'forum/search.html', context)


def _fuzzy_search_sqlite(query, threshold=60):
    """
    Fuzzy search implementation for SQLite using fuzzywuzzy
    threshold: minimum similarity score (0-100)
    """
    from fuzzywuzzy import fuzz
    
    # Get all threads and calculate similarity scores
    all_threads = Thread.objects.filter(is_deleted=False).select_related('author', 'category')
    thread_results = []
    
    for thread in all_threads:
        # Calculate similarity for title and content
        title_score = fuzz.partial_ratio(query.lower(), thread.title.lower())
        content_score = fuzz.partial_ratio(query.lower(), thread.content.lower())
        
        # Use the higher score, with title weighted slightly more
        max_score = max(title_score * 1.2, content_score)
        
        if max_score >= threshold:
            thread.similarity_score = max_score
            thread_results.append((max_score, thread))
    
    # Sort by similarity score and get top 20
    thread_results.sort(key=lambda x: x[0], reverse=True)
    threads = [thread for score, thread in thread_results[:20]]
    
    # Get all replies and calculate similarity scores
    all_replies = Reply.objects.filter(is_deleted=False).select_related('author', 'thread')
    reply_results = []
    
    for reply in all_replies:
        # Calculate similarity for content
        score = fuzz.partial_ratio(query.lower(), reply.content.lower())
        
        if score >= threshold:
            reply.similarity_score = score
            reply_results.append((score, reply))
    
    # Sort by similarity score and get top 20
    reply_results.sort(key=lambda x: x[0], reverse=True)
    replies = [reply for score, reply in reply_results[:20]]
    
    return threads, replies


def _simple_search(query):
    """
    Simple fallback search using icontains
    """
    threads = Thread.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query),
        is_deleted=False
    ).select_related('author', 'category')[:20]
    
    replies = Reply.objects.filter(
        content__icontains=query,
        is_deleted=False
    ).select_related('author', 'thread')[:20]
    
    return threads, replies


def _get_search_method(db_vendor):
    """
    Return a description of the search method being used
    """
    if db_vendor == 'postgresql' and HAS_POSTGRES:
        return "PostgreSQL Full-Text Search with Trigram Similarity"
    elif db_vendor == 'sqlite' and HAS_FUZZY:
        return "SQLite Fuzzy Search with Levenshtein Distance"
    else:
        return "Simple Substring Search"