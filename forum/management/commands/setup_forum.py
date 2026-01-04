from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from forum.models import Category, Tag, Thread, Reply


class Command(BaseCommand):
    help = 'Set up initial forum categories, tags, and permissions'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up forum...')
        
        # Create permission groups
        self.setup_groups()
        
        # Create initial categories
        self.create_categories()
        
        # Create initial tags
        self.create_tags()
        
        self.stdout.write(self.style.SUCCESS('Forum setup completed successfully!'))
    
    def setup_groups(self):
        """Create and configure permission groups"""
        self.stdout.write('Setting up permission groups...')
        
        # Create Student group
        student_group, created = Group.objects.get_or_create(name='Students')
        if created:
            self.stdout.write(f'Created group: Students')
            
            # Add permissions for students
            thread_ct = ContentType.objects.get_for_model(Thread)
            reply_ct = ContentType.objects.get_for_model(Reply)
            
            student_permissions = [
                Permission.objects.get(codename='add_thread', content_type=thread_ct),
                Permission.objects.get(codename='change_thread', content_type=thread_ct),
                Permission.objects.get(codename='add_reply', content_type=reply_ct),
                Permission.objects.get(codename='change_reply', content_type=reply_ct),
            ]
            
            student_group.permissions.set(student_permissions)
            self.stdout.write('Assigned permissions to Students group')
        
        # Create Moderator group
        moderator_group, created = Group.objects.get_or_create(name='Moderators')
        if created:
            self.stdout.write(f'Created group: Moderators')
            
            # Add all forum-related permissions for moderators
            thread_ct = ContentType.objects.get_for_model(Thread)
            reply_ct = ContentType.objects.get_for_model(Reply)
            
            moderator_permissions = Permission.objects.filter(
                content_type__in=[thread_ct, reply_ct]
            )
            
            moderator_group.permissions.set(moderator_permissions)
            self.stdout.write('Assigned all forum permissions to Moderators group')
    
    def create_categories(self):
        """Create initial forum categories"""
        self.stdout.write('Creating forum categories...')
        
        categories = [
            {
                'name': 'General Discussion',
                'slug': 'general',
                'description': 'General discussions about academics, campus life, and more',
                'icon': 'bi-chat-dots',
                'order': 1
            },
            {
                'name': 'Course Queries',
                'slug': 'course-queries',
                'description': 'Ask questions and discuss specific courses',
                'icon': 'bi-question-circle',
                'order': 2
            },
            {
                'name': 'Exam Preparation',
                'slug': 'exam-prep',
                'description': 'Discuss exam strategies, share tips, and find study partners',
                'icon': 'bi-journal-bookmark',
                'order': 3
            },
            {
                'name': 'Resources & Materials',
                'slug': 'resources',
                'description': 'Share and request study materials, notes, and resources',
                'icon': 'bi-file-earmark-text',
                'order': 4
            },
            {
                'name': 'Projects & Assignments',
                'slug': 'projects',
                'description': 'Collaborate on projects and get help with assignments',
                'icon': 'bi-kanban',
                'order': 5
            },
            {
                'name': 'Announcements',
                'slug': 'announcements',
                'description': 'Important announcements and updates',
                'icon': 'bi-megaphone',
                'order': 0
            },
            {
                'name': 'Feedback & Suggestions',
                'slug': 'feedback',
                'description': 'Share your feedback and suggestions for StudyDeck',
                'icon': 'bi-lightbulb',
                'order': 6
            }
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'order': cat_data['order']
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
    
    def create_tags(self):
        """Create initial tags"""
        self.stdout.write('Creating initial tags...')
        
        tags = [
            'urgent', 'solved', 'help-needed', 'discussion',
            'midsem', 'compre', 'quiz', 'assignment',
            'project', 'lab', 'tutorial', 'doubt',
            'resource-request', 'tips', 'announcement',
            'feedback', 'bug', 'feature-request'
        ]
        
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
