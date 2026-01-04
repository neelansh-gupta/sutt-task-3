#!/bin/bash

# StudyDeck Forum - Quick Start Script
# Just run: ./run.sh

echo "========================================="
echo "     StudyDeck Forum - Quick Setup"
echo "========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt -q

# Ask user if they want to reset the database
echo ""
echo "⚠️  Do you want to reset the database with fresh data?"
echo "   This will delete all existing data and create new sample data."
echo ""
read -p "   Reset database? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
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
    echo "🔨 Creating fresh migrations..."
    python manage.py makemigrations accounts --noinput
    python manage.py makemigrations courses --noinput
    python manage.py makemigrations resources --noinput
    python manage.py makemigrations forum --noinput
    
    # Run migrations
    echo "🗄️ Creating database tables..."
    python manage.py migrate --noinput
    
    # Create superuser
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
    echo "📝 Loading sample data..."
    python manage.py populate_courses
    python manage.py populate_resources  
    python manage.py setup_forum
    python manage.py populate_forum_content
    
    echo ""
    echo "✅ Database reset complete with fresh sample data!"
    
else
    echo ""
    echo "📌 Keeping existing database..."
    
    # Run migrations (in case there are new ones)
    echo "🗄️ Checking database..."
    python manage.py migrate --noinput
    
    # Create superuser if doesn't exist
    echo "👤 Checking admin user..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@pilani.bits-pilani.ac.in').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@pilani.bits-pilani.ac.in',
        password='admin123',
        full_name='Admin User'
    )
    print('   ✓ Admin user created')
else:
    print('   ✓ Admin user already exists')
"
    
    # Check if forum data exists, if not populate it
    python manage.py shell -c "
from forum.models import Category, Thread
if Category.objects.count() == 0:
    print('   ! No forum categories found, running setup...')
    import subprocess
    subprocess.run(['python', 'manage.py', 'populate_courses'])
    subprocess.run(['python', 'manage.py', 'populate_resources'])
    subprocess.run(['python', 'manage.py', 'setup_forum'])
    subprocess.run(['python', 'manage.py', 'populate_forum_content'])
    print('   ✓ Sample data loaded')
else:
    print('   ✓ Forum data exists')
"
fi

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput > /dev/null 2>&1

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "📌 Admin Login:"
echo "   Email: admin@pilani.bits-pilani.ac.in"
echo "   Password: admin123"
echo ""
echo "🚀 Starting server at http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo "========================================="
echo ""

# Start the server
python manage.py runserver