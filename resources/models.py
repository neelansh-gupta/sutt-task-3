from django.db import models
from django.utils.text import slugify
from courses.models import Course


class ResourceType(models.TextChoices):
    """Choices for resource types"""
    PDF = 'PDF', 'PDF Document'
    VIDEO = 'VIDEO', 'Video'
    LINK = 'LINK', 'External Link'
    NOTES = 'NOTES', 'Lecture Notes'
    PYQ = 'PYQ', 'Previous Year Questions'
    HANDOUT = 'HANDOUT', 'Course Handout'


class Resource(models.Model):
    """Resource model for course materials"""
    
    title = models.CharField(max_length=200)
    type = models.CharField(
        max_length=10,
        choices=ResourceType.choices,
        default=ResourceType.PDF
    )
    link = models.URLField(max_length=500, help_text="URL to the resource")
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='resources'
    )
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_resources'
    )
    slug = models.SlugField(max_length=250, blank=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Resource"
        verbose_name_plural = "Resources"
        indexes = [
            models.Index(fields=['course', 'type']),
            models.Index(fields=['-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.course.code}-{self.title}")[:250]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} ({self.get_type_display()}) - {self.course.code}"
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def get_icon(self):
        """Return appropriate icon class for resource type"""
        icons = {
            ResourceType.PDF: 'bi-file-pdf',
            ResourceType.VIDEO: 'bi-play-circle',
            ResourceType.LINK: 'bi-link-45deg',
            ResourceType.NOTES: 'bi-journal-text',
            ResourceType.PYQ: 'bi-question-circle',
            ResourceType.HANDOUT: 'bi-file-text',
        }
        return icons.get(self.type, 'bi-file')