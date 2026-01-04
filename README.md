# StudyDeck Forum Module

A community-driven forum module for StudyDeck, built with Django. This platform allows students to discuss courses, ask questions, share resources, and collaborate effectively.

## Features

### Core Functionality
- **User Authentication**: Google OAuth integration restricted to BITS Pilani email addresses
- **Role-based Permissions**: Student and Moderator roles with different access levels
- **Discussion Threads**: Create, edit, and manage discussion threads
- **Replies System**: Threaded discussions with reply functionality
- **Categories**: Organized discussion categories for different topics
- **Tags**: Flexible tagging system for better content organization

### Interactive Features
- **Like System**: Upvote threads and replies
- **Search Functionality**: Search across threads and replies
- **Reporting System**: Report inappropriate content with moderation queue
- **Markdown Support**: Rich text formatting for posts
- **Pagination**: Efficient browsing of large discussion lists
- **Soft Delete**: Content preservation with deletion marking

### Moderation Tools
- **Thread Locking**: Prevent new replies on sensitive topics
- **Thread Pinning**: Keep important discussions at the top
- **Solution Marking**: Mark replies as solutions to questions
- **Report Management**: Review and handle user reports

## Technology Stack

- **Backend**: Django 5.0.1
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Authentication**: django-allauth with Google OAuth
- **Frontend**: Bootstrap 5, Django Templates
- **Markdown**: django-markdownx
- **Rate Limiting**: django-ratelimit

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd sutt-task-3
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# For Google OAuth (optional for local development)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create a superuser**
```bash
python manage.py createsuperuser
```

7. **Populate initial data**
```bash
python manage.py populate_courses
python manage.py populate_resources
python manage.py setup_forum
```

8. **Run the development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the forum.

## Google OAuth Setup

To enable Google OAuth authentication:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/` (development)
   - `https://yourdomain.com/accounts/google/login/callback/` (production)
6. Update `.env` with your credentials

## Usage Guide

### For Students

1. **Login**: Use your BITS Pilani email to login via Google OAuth
2. **Browse Categories**: Navigate through different discussion categories
3. **Create Threads**: Start new discussions in relevant categories
4. **Reply to Threads**: Participate in ongoing discussions
5. **Like Content**: Upvote helpful threads and replies
6. **Tag Content**: Use tags to categorize your posts
7. **Report Issues**: Flag inappropriate content for moderation

### For Moderators

Moderators have additional privileges:
- Lock/unlock threads
- Pin/unpin important discussions
- Delete any content
- Mark replies as solutions
- Access moderation queue
- Handle user reports

### Admin Panel

Access the Django admin panel at `/admin/` with superuser credentials to:
- Manage users and permissions
- Create/edit categories
- Manage courses and resources
- View all forum content
- Handle reports

## Project Structure

```
sutt-task-3/
├── studydeck_forum/      # Main project settings
├── accounts/             # User authentication app
├── courses/              # Course management app
├── resources/            # Resource management app
├── forum/                # Main forum app
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── forms.py         # Form definitions
│   ├── urls.py          # URL routing
│   └── permissions.py   # Permission handlers
├── templates/            # HTML templates
├── static/              # CSS, JS, images
├── requirements.txt     # Python dependencies
└── manage.py           # Django management script
```

## Database Schema

### Key Models
- **User**: Custom user model with BITS email validation
- **Category**: Forum categories for organization
- **Thread**: Discussion threads
- **Reply**: Replies to threads
- **Tag**: Tags for content categorization
- **ThreadLike/ReplyLike**: Like system
- **Report**: Content reporting system

## Deployment

### Using PythonAnywhere

1. Create account on [PythonAnywhere](https://www.pythonanywhere.com/)
2. Upload code or clone from GitHub
3. Create virtual environment
4. Install dependencies
5. Configure WSGI file
6. Set environment variables
7. Collect static files: `python manage.py collectstatic`
8. Reload web app

### Using Render

1. Create account on [Render](https://render.com/)
2. Connect GitHub repository
3. Create new Web Service
4. Configure build and start commands
5. Add environment variables
6. Deploy

### Environment Variables for Production

```env
SECRET_KEY=strong-random-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@host:port/dbname
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret
```

## API Endpoints

### Forum URLs
- `/` - Redirects to forum home
- `/forum/` - Forum home page
- `/forum/category/<slug>/` - Category view
- `/forum/thread/<id>/` - Thread detail
- `/forum/thread/create/` - Create new thread
- `/forum/search/` - Search functionality
- `/forum/moderation/` - Moderation queue (moderators only)

## Testing

Run tests with:
```bash
python manage.py test
```

## Performance Optimizations

- Database queries optimized with `select_related()` and `prefetch_related()`
- Pagination implemented for thread and reply lists
- Static file caching with WhiteNoise
- Database indexing on frequently queried fields

## Security Features

- CSRF protection enabled
- XSS protection through Django templates
- SQL injection prevention via ORM
- Restricted to BITS email domains
- Rate limiting on forms
- Secure password storage

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## Design Decisions

1. **Custom User Model**: Extended Django's AbstractUser for additional fields
2. **Soft Delete**: Implemented to preserve content integrity
3. **Markdown Support**: Added for rich text formatting
4. **Role-based Permissions**: Used Django groups for scalability
5. **Google OAuth Only**: Simplified authentication for BITS students

## Future Enhancements

- Real-time notifications
- Private messaging system
- Advanced search with filters
- User reputation system
- Mobile app integration
- Email digest subscriptions
- File attachments support
- Analytics dashboard

## Troubleshooting

### Common Issues

1. **Migration errors**: Delete migration files (except `__init__.py`) and re-run `makemigrations`
2. **Static files not loading**: Run `python manage.py collectstatic`
3. **Google OAuth not working**: Verify redirect URIs and credentials
4. **Database connection issues**: Check DATABASE_URL format

## License

This project is developed for SUTT recruitment purposes.

## Contact

For issues or questions, please open an issue on GitHub or contact the development team.

---

**Developed for Students' Union Technical Team - BITS Pilani**
