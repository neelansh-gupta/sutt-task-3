from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import get_user_model
from courses.models import Course
from resources.models import Resource
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

User = get_user_model()


class Category(models.Model):
    """Forum category for organizing discussions"""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-folder', help_text='Bootstrap icon class')
    order = models.IntegerField(default=0, help_text='Display order')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_thread_count(self):
        return self.threads.filter(is_deleted=False).count()
    
    def get_latest_thread(self):
        return self.threads.filter(is_deleted=False).order_by('-created_at').first()


class Tag(models.Model):
    """Tags for threads"""
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Thread(models.Model):
    """Discussion thread"""
    
    title = models.CharField(max_length=200)
    content = MarkdownxField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='threads'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='threads'
    )
    courses = models.ManyToManyField(
        Course,
        blank=True,
        related_name='threads'
    )
    resources = models.ManyToManyField(
        Resource,
        blank=True,
        related_name='threads'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='threads'
    )
    
    # Status fields
    is_locked = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    
    # Tracking fields
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_pinned', '-last_activity']
        indexes = [
            models.Index(fields=['-last_activity']),
            models.Index(fields=['category', '-last_activity']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def formatted_content(self):
        """Return content as HTML"""
        return markdownify(self.content)
    
    def get_reply_count(self):
        """Get count of non-deleted replies"""
        return self.replies.filter(is_deleted=False).count()
    
    def get_latest_reply(self):
        """Get the most recent non-deleted reply"""
        return self.replies.filter(is_deleted=False).order_by('-created_at').first()
    
    def update_last_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def can_edit(self, user):
        """Check if user can edit this thread"""
        return user == self.author or user.can_moderate()
    
    def can_delete(self, user):
        """Check if user can delete this thread"""
        return user == self.author or user.can_moderate()


class Reply(models.Model):
    """Reply to a thread"""
    
    content = MarkdownxField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    
    # For nested replies (optional)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )
    
    # Status
    is_deleted = models.BooleanField(default=False)  # Soft delete
    is_solution = models.BooleanField(default=False)  # Mark as solution
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Reply"
        verbose_name_plural = "Replies"
    
    def __str__(self):
        return f"Reply by {self.author} on {self.thread.title[:30]}"
    
    @property
    def formatted_content(self):
        """Return content as HTML"""
        if self.is_deleted:
            return "<p><em>[This reply has been deleted]</em></p>"
        return markdownify(self.content)
    
    def save(self, *args, **kwargs):
        # Update thread's last activity on new reply
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.is_deleted:
            self.thread.update_last_activity()
    
    def soft_delete(self):
        """Soft delete the reply"""
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])
    
    def can_edit(self, user):
        """Check if user can edit this reply"""
        return user == self.author or user.can_moderate()
    
    def can_delete(self, user):
        """Check if user can delete this reply"""
        return user == self.author or user.can_moderate()


class ThreadLike(models.Model):
    """Like/Upvote for threads"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='thread_likes'
    )
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'thread']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} likes {self.thread.title[:30]}"


class ReplyLike(models.Model):
    """Like/Upvote for replies"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reply_likes'
    )
    reply = models.ForeignKey(
        Reply,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'reply']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} likes reply by {self.reply.author}"


class Report(models.Model):
    """Report system for inappropriate content"""
    
    class ReportStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        REVIEWED = 'REVIEWED', 'Reviewed'
        RESOLVED = 'RESOLVED', 'Resolved'
        DISMISSED = 'DISMISSED', 'Dismissed'
    
    class ReportReason(models.TextChoices):
        SPAM = 'SPAM', 'Spam or Advertisement'
        INAPPROPRIATE = 'INAPPROPRIATE', 'Inappropriate Content'
        HARASSMENT = 'HARASSMENT', 'Harassment or Bullying'
        OFFTOPIC = 'OFFTOPIC', 'Off-topic'
        OTHER = 'OTHER', 'Other'
    
    # Content being reported (either thread or reply)
    thread = models.ForeignKey(
        Thread,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    reply = models.ForeignKey(
        Reply,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    
    # Report details
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports_made'
    )
    reason = models.CharField(
        max_length=20,
        choices=ReportReason.choices,
        default=ReportReason.OTHER
    )
    description = models.TextField(help_text="Please explain why you're reporting this content")
    
    # Status tracking
    status = models.CharField(
        max_length=10,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING
    )
    moderator = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reports_handled'
    )
    moderator_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        content_type = "Thread" if self.thread else "Reply"
        return f"Report: {content_type} - {self.get_reason_display()} - {self.get_status_display()}"
    
    def resolve(self, moderator, notes=''):
        """Mark report as resolved"""
        self.status = self.ReportStatus.RESOLVED
        self.moderator = moderator
        self.moderator_notes = notes
        self.resolved_at = timezone.now()
        self.save()
    
    def dismiss(self, moderator, notes=''):
        """Dismiss the report"""
        self.status = self.ReportStatus.DISMISSED
        self.moderator = moderator
        self.moderator_notes = notes
        self.resolved_at = timezone.now()
        self.save()
    
    def get_reported_content(self):
        """Get the content being reported"""
        return self.thread or self.reply
    
    def get_content_author(self):
        """Get the author of reported content"""
        content = self.get_reported_content()
        return content.author if content else None