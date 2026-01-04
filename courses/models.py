from django.db import models
from django.utils.text import slugify


class Department(models.Model):
    """Department model for organizing courses"""
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Department"
        verbose_name_plural = "Departments"
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Course(models.Model):
    """Course model representing academic courses"""
    
    code = models.CharField(max_length=20, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    description = models.TextField(blank=True)
    credits = models.IntegerField(default=3)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['slug']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.code}-{self.title}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('courses:detail', kwargs={'slug': self.slug})