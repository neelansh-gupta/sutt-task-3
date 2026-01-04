from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.models import Site


def send_reply_notification(reply):
    """Send email notification when someone replies to a thread"""
    thread = reply.thread
    thread_author = thread.author
    
    # Don't send notification if replying to own thread
    if reply.author == thread_author:
        return
    
    # Get site domain
    current_site = Site.objects.get_current()
    domain = current_site.domain
    
    # Build thread URL
    thread_url = f"http://{domain}{reverse('forum:thread_detail', kwargs={'pk': thread.pk})}"
    
    subject = f"New reply to your thread: {thread.title}"
    
    context = {
        'thread': thread,
        'reply': reply,
        'thread_url': thread_url,
        'recipient': thread_author,
    }
    
    # Render email templates
    html_message = render_to_string('forum/emails/reply_notification.html', context)
    plain_message = render_to_string('forum/emails/reply_notification.txt', context)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[thread_author.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send email notification: {e}")


def send_mention_notification(user, thread, mentioning_user):
    """Send email notification when someone mentions a user"""
    
    # Don't send notification if mentioning self
    if user == mentioning_user:
        return
    
    # Get site domain
    current_site = Site.objects.get_current()
    domain = current_site.domain
    
    # Build thread URL
    thread_url = f"http://{domain}{reverse('forum:thread_detail', kwargs={'pk': thread.pk})}"
    
    subject = f"{mentioning_user.get_display_name()} mentioned you in: {thread.title}"
    
    context = {
        'thread': thread,
        'thread_url': thread_url,
        'recipient': user,
        'mentioning_user': mentioning_user,
    }
    
    # Render email templates
    html_message = render_to_string('forum/emails/mention_notification.html', context)
    plain_message = render_to_string('forum/emails/mention_notification.txt', context)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send mention notification: {e}")


def send_thread_locked_notification(thread, locked_by):
    """Send notification when a thread is locked"""
    
    # Only notify thread author
    if thread.author == locked_by:
        return
    
    # Get site domain
    current_site = Site.objects.get_current()
    domain = current_site.domain
    
    # Build thread URL
    thread_url = f"http://{domain}{reverse('forum:thread_detail', kwargs={'pk': thread.pk})}"
    
    subject = f"Your thread has been locked: {thread.title}"
    
    context = {
        'thread': thread,
        'thread_url': thread_url,
        'recipient': thread.author,
        'locked_by': locked_by,
    }
    
    # Render email templates
    html_message = render_to_string('forum/emails/thread_locked.html', context)
    plain_message = render_to_string('forum/emails/thread_locked.txt', context)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[thread.author.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send thread locked notification: {e}")
