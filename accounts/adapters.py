from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.forms import ValidationError
from django.contrib import messages


class BITSEmailAdapter(DefaultAccountAdapter):
    """Custom adapter to restrict registration to BITS email addresses"""
    
    def clean_email(self, email):
        """Validate that email belongs to BITS domain"""
        email = super().clean_email(email)
        
        # List of allowed BITS domains
        allowed_domains = [
            'pilani.bits-pilani.ac.in',
            'goa.bits-pilani.ac.in',
            'hyderabad.bits-pilani.ac.in',
            'dubai.bits-pilani.ac.in',
            'bits-pilani.ac.in'
        ]
        
        domain = email.split('@')[-1].lower()
        
        if not any(domain.endswith(allowed) for allowed in allowed_domains):
            raise ValidationError(
                "Registration is restricted to BITS Pilani email addresses only."
            )
        
        return email
    
    def save_user(self, request, user, form, commit=True):
        """Save user with additional processing"""
        user = super().save_user(request, user, form, commit=False)
        
        # Extract full name from email if not provided
        if not user.full_name and user.email:
            # Try to extract name from email (e.g., firstname.lastname@bits...)
            email_prefix = user.email.split('@')[0]
            user.full_name = email_prefix.replace('.', ' ').replace('_', ' ').title()
        
        if commit:
            user.save()
        
        return user


class BITSSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter for Google OAuth with BITS email restriction"""
    
    def pre_social_login(self, request, sociallogin):
        """Validate social login email domain"""
        email = sociallogin.account.extra_data.get('email', '').lower()
        
        # List of allowed BITS domains
        allowed_domains = [
            'pilani.bits-pilani.ac.in',
            'goa.bits-pilani.ac.in',
            'hyderabad.bits-pilani.ac.in',
            'dubai.bits-pilani.ac.in',
            'bits-pilani.ac.in'
        ]
        
        domain = email.split('@')[-1] if email else ''
        
        if not any(domain.endswith(allowed) for allowed in allowed_domains):
            messages.error(
                request,
                "Login is restricted to BITS Pilani email addresses only."
            )
            raise ValidationError(
                "Login is restricted to BITS Pilani email addresses only."
            )
    
    def populate_user(self, request, sociallogin, data):
        """Populate user instance with data from social provider"""
        user = super().populate_user(request, sociallogin, data)
        
        # Get additional data from Google
        extra_data = sociallogin.account.extra_data
        
        # Set full name from Google account
        if extra_data.get('name'):
            user.full_name = extra_data['name']
        elif extra_data.get('given_name') or extra_data.get('family_name'):
            given_name = extra_data.get('given_name', '')
            family_name = extra_data.get('family_name', '')
            user.full_name = f"{given_name} {family_name}".strip()
        
        # Set email
        if extra_data.get('email'):
            user.email = extra_data['email'].lower()
            user.username = user.email.split('@')[0]
        
        # Note: Profile image URL from Google can be saved later
        # if we want to download and store it locally
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """Save user after social login"""
        user = super().save_user(request, sociallogin, form)
        
        # Save Google profile picture URL if available
        picture_url = sociallogin.account.extra_data.get('picture')
        if picture_url and not user.profile_image:
            # For now, we'll just store the URL
            # In production, you might want to download and save the image
            pass
        
        return user
