# Render Environment Variables

Add these environment variables in your Render dashboard:

## Required Variables

```bash
# Django Secret Key (generate a new one for production)
SECRET_KEY=your-very-long-random-secret-key-here

# Database (Render provides this automatically)
# DATABASE_URL=postgresql://... (auto-configured by Render)

# Admin credentials
ADMIN_EMAIL=admin@pilani.bits-pilani.ac.in
ADMIN_PASSWORD=your-strong-admin-password

# Debug mode (set to False for production)
DEBUG=False

# Allowed hosts
ALLOWED_HOSTS=sutt-task-3.onrender.com
```

## Optional Variables

```bash
# Email backend (for production, use SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# Google OAuth (if enabling social login)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## How to Generate a Secret Key

Run this Python command to generate a secure secret key:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Or use this one-liner:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Setting Environment Variables in Render

1. Go to your Render dashboard
2. Select your web service (sutt-task-3)
3. Go to "Environment" tab
4. Add each variable as a key-value pair
5. Click "Save Changes"
6. Render will automatically redeploy with the new variables
