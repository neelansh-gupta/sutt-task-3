#!/bin/bash

# StudyDeck Forum - Database Reset Script
# This will completely reset the database with fresh sample data

echo "========================================="
echo "     StudyDeck Forum - Database Reset"
echo "========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements if needed
echo "📚 Checking dependencies..."
pip install -r requirements.txt -q

echo ""
echo "🗑️  Resetting database..."

# Remove the database file
if [ -f "db.sqlite3" ]; then
    rm db.sqlite3
    echo "   ✓ Database removed"
fi

# Remove migration files (keep __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete 2>/dev/null
find . -path "*/migrations/*.pyc" -delete 2>/dev/null
echo "   ✓ Migration files cleaned"

# Create new migrations
echo ""
echo "🔨 Creating fresh migrations..."
python manage.py makemigrations accounts --noinput
python manage.py makemigrations courses --noinput
python manage.py makemigrations resources --noinput
python manage.py makemigrations forum --noinput

# Run migrations
echo ""
echo "🗄️  Creating database tables..."
python manage.py migrate --noinput

# Create superuser
echo ""
echo "👤 Creating admin user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.create_superuser(
    username='admin',
    email='admin@pilani.bits-pilani.ac.in',
    password='admin123',
    full_name='Admin User'
)
print('   ✓ Admin user created')
"

# Populate database with sample data
echo ""
echo "📝 Loading sample data..."
echo "   → Adding courses..."
python manage.py populate_courses
echo "   → Adding resources..."
python manage.py populate_resources
echo "   → Setting up forum categories..."
python manage.py setup_forum
echo "   → Creating sample threads and discussions..."
python manage.py populate_forum_content

# Collect static files
echo ""
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput > /dev/null 2>&1

echo ""
echo "========================================="
echo "✅ Database Reset Complete!"
echo "========================================="
echo ""
echo "📊 Database now contains:"
python manage.py shell -c "
from django.contrib.auth import get_user_model
from forum.models import Category, Thread, Reply
from courses.models import Course
from resources.models import Resource

User = get_user_model()
print(f'   • {User.objects.count()} users')
print(f'   • {Course.objects.count()} courses')
print(f'   • {Resource.objects.count()} resources')
print(f'   • {Category.objects.count()} forum categories')
print(f'   • {Thread.objects.count()} threads')
print(f'   • {Reply.objects.count()} replies')
"
echo ""
echo "📌 Admin Login:"
echo "   Email: admin@pilani.bits-pilani.ac.in"
echo "   Password: admin123"
echo ""
echo "🚀 Run './run.sh' to start the server"
echo "========================================="
