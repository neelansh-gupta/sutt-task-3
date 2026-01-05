#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

echo "=== Starting Render Build Process ==="

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate --no-input

# Create superuser if it doesn't exist (optional)
python manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()
admin_email = os.environ.get('ADMIN_EMAIL', 'admin@pilani.bits-pilani.ac.in')
admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')

if not User.objects.filter(email=admin_email).exists():
    User.objects.create_superuser(
        username='admin',
        email=admin_email,
        password=admin_password,
        full_name='Admin User'
    )
    print('Superuser created')
else:
    print('Superuser already exists')
END

# ALWAYS populate initial data - REQUIRED for the forum to work
echo "Populating database with initial data..."
python manage.py populate_courses
python manage.py populate_resources
python manage.py setup_forum
python manage.py populate_forum_content
echo "Data population complete!"
