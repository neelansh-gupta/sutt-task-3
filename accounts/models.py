from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom User model for StudyDeck Forum"""
    
    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_moderator = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.full_name or self.email
    
    def save(self, *args, **kwargs):
        # Extract full name from email if not provided
        if not self.full_name and self.email:
            self.full_name = self.email.split('@')[0].replace('.', ' ').title()
        
        # Set username from email if not provided
        if not self.username and self.email:
            self.username = self.email.split('@')[0]
        
        super().save(*args, **kwargs)
        
        # Add to appropriate group
        if self.is_moderator:
            moderator_group, _ = Group.objects.get_or_create(name='Moderators')
            self.groups.add(moderator_group)
        else:
            student_group, _ = Group.objects.get_or_create(name='Students')
            self.groups.add(student_group)
    
    @property
    def is_student(self):
        """Check if user is a student"""
        return not self.is_moderator
    
    def can_moderate(self):
        """Check if user can moderate content"""
        return self.is_moderator or self.is_staff or self.is_superuser
    
    def get_display_name(self):
        """Get the best available display name"""
        return self.full_name or self.username or self.email.split('@')[0]