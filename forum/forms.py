from django import forms
from django.core.exceptions import ValidationError
from markdownx.fields import MarkdownxFormField
from .models import Thread, Reply, Report, Category, Tag
from courses.models import Course
from resources.models import Resource


class ThreadForm(forms.ModelForm):
    """Form for creating/editing threads"""
    
    content = MarkdownxFormField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Write your content here... (Markdown supported)'
        })
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'data-placeholder': 'Select tags...'
        })
    )
    
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'data-placeholder': 'Select related courses...'
        })
    )
    
    resources = forms.ModelMultipleChoiceField(
        queryset=Resource.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'data-placeholder': 'Select related resources...'
        })
    )
    
    class Meta:
        model = Thread
        fields = ['title', 'category', 'content', 'tags', 'courses', 'resources']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter thread title...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError("Title must be at least 5 characters long.")
        return title
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 20:
            raise ValidationError("Content must be at least 20 characters long.")
        return content


class ReplyForm(forms.ModelForm):
    """Form for creating/editing replies"""
    
    content = MarkdownxFormField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Write your reply... (Markdown supported)'
        })
    )
    
    class Meta:
        model = Reply
        fields = ['content']
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 10:
            raise ValidationError("Reply must be at least 10 characters long.")
        return content


class ReportForm(forms.ModelForm):
    """Form for reporting content"""
    
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please provide details about why you are reporting this content...'
            }),
        }
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 20:
            raise ValidationError("Please provide more details (at least 20 characters).")
        return description


class SearchForm(forms.Form):
    """Form for searching forum content"""
    
    q = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search threads and replies...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    sort = forms.ChoiceField(
        choices=[
            ('relevance', 'Most Relevant'),
            ('latest', 'Latest'),
            ('popular', 'Most Popular'),
        ],
        required=False,
        initial='relevance',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
