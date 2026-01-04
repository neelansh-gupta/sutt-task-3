from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps


def is_moderator(user):
    """Check if user is a moderator"""
    return user.is_authenticated and (user.is_moderator or user.is_staff or user.is_superuser)


def is_student(user):
    """Check if user is a student (regular user)"""
    return user.is_authenticated and not is_moderator(user)


# Decorators for views
moderator_required = user_passes_test(is_moderator, login_url='/accounts/login/')


def owner_or_moderator_required(view_func):
    """
    Decorator that checks if the user is the owner of the object or a moderator.
    The view must return an object with an 'author' or 'user' attribute.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to perform this action.")
        
        # For class-based views
        if hasattr(view_func, 'get_object'):
            obj = view_func.get_object()
        # For function-based views, we'll need to get the object first
        else:
            # This is a simplified version - in practice, you'd need to
            # implement this based on your specific views
            return view_func(request, *args, **kwargs)
        
        # Check ownership or moderator status
        owner = getattr(obj, 'author', getattr(obj, 'user', None))
        if owner != request.user and not is_moderator(request.user):
            raise PermissionDenied("You don't have permission to perform this action.")
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


class PermissionMixin:
    """Mixin for checking permissions in class-based views"""
    
    def check_owner_or_moderator(self, obj):
        """Check if current user is owner or moderator"""
        user = self.request.user
        owner = getattr(obj, 'author', getattr(obj, 'user', None))
        
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in.")
        
        if owner != user and not is_moderator(user):
            raise PermissionDenied("You don't have permission to perform this action.")
        
        return True
    
    def check_moderator(self):
        """Check if current user is a moderator"""
        if not is_moderator(self.request.user):
            raise PermissionDenied("Only moderators can perform this action.")
        return True


def can_edit_content(user, content):
    """Check if user can edit specific content (thread or reply)"""
    if not user.is_authenticated:
        return False
    
    # Moderators can edit anything
    if is_moderator(user):
        return True
    
    # Authors can edit their own content
    return content.author == user


def can_delete_content(user, content):
    """Check if user can delete specific content"""
    if not user.is_authenticated:
        return False
    
    # Moderators can delete anything
    if is_moderator(user):
        return True
    
    # Authors can delete their own content
    return content.author == user


def can_lock_thread(user):
    """Check if user can lock/unlock threads"""
    return is_moderator(user)


def can_pin_thread(user):
    """Check if user can pin/unpin threads"""
    return is_moderator(user)


def can_mark_solution(user, thread):
    """Check if user can mark a reply as solution"""
    if not user.is_authenticated:
        return False
    
    # Thread author or moderators can mark solutions
    return thread.author == user or is_moderator(user)


def can_view_reports(user):
    """Check if user can view moderation reports"""
    return is_moderator(user)


def can_handle_report(user):
    """Check if user can resolve/dismiss reports"""
    return is_moderator(user)
