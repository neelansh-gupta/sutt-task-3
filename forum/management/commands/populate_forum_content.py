from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from forum.models import Category, Thread, Reply, Tag, ThreadLike, ReplyLike
from courses.models import Course
from resources.models import Resource
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate forum with sample threads and replies'
    
    def handle(self, *args, **options):
        self.stdout.write('Populating forum with sample content...')
        
        # Get or create sample users
        users = self.create_sample_users()
        
        # Get existing data
        categories = Category.objects.all()
        tags = Tag.objects.all()
        courses = Course.objects.all()[:10]  # Get first 10 courses
        
        if not categories:
            self.stdout.write(self.style.ERROR('No categories found. Run setup_forum first.'))
            return
        
        # Create threads for each category
        for category in categories:
            self.create_threads_for_category(category, users, tags, courses)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated forum with sample content!'))
    
    def create_sample_users(self):
        """Create sample student users"""
        self.stdout.write('Creating sample users...')
        
        users = []
        sample_users = [
            {'email': 'student1@pilani.bits-pilani.ac.in', 'name': 'Rahul Sharma'},
            {'email': 'student2@goa.bits-pilani.ac.in', 'name': 'Priya Patel'},
            {'email': 'student3@hyderabad.bits-pilani.ac.in', 'name': 'Arjun Kumar'},
            {'email': 'student4@pilani.bits-pilani.ac.in', 'name': 'Sneha Gupta'},
            {'email': 'student5@dubai.bits-pilani.ac.in', 'name': 'Ahmed Khan'},
        ]
        
        for user_data in sample_users:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['email'].split('@')[0],
                    'full_name': user_data['name'],
                    'is_active': True
                }
            )
            if created:
                user.set_password('student123')
                user.save()
                self.stdout.write(f'Created user: {user.email}')
            users.append(user)
        
        # Include admin user if exists
        try:
            admin = User.objects.get(email='admin@pilani.bits-pilani.ac.in')
            users.append(admin)
        except User.DoesNotExist:
            pass
        
        return users
    
    def create_threads_for_category(self, category, users, tags, courses):
        """Create sample threads for a category"""
        
        thread_templates = {
            'General Discussion': [
                {
                    'title': 'Tips for managing academic workload',
                    'content': '''Hey everyone! 👋
                    
I'm a second-year student and struggling to balance multiple courses this semester. 
I have CS F213, MATH F211, and PHY F212, along with some electives.

What strategies do you use to manage your time effectively? 
Any apps or tools that you find helpful?

Would love to hear your experiences!''',
                    'tags': ['tips', 'discussion', 'help-needed'],
                    'replies': 5
                },
                {
                    'title': 'Best places to study on campus?',
                    'content': '''Looking for quiet study spots on campus. 
                    
The library gets too crowded during exam time. Any hidden gems where you like to study?

I prefer places with:
- Good WiFi
- Power outlets
- Not too noisy
- Open late hours

Share your favorite spots!''',
                    'tags': ['discussion'],
                    'replies': 8
                },
                {
                    'title': 'Study group for Data Structures',
                    'content': '''Anyone interested in forming a study group for Data Structures?

Planning to meet twice a week to:
- Discuss problem sets
- Practice coding problems
- Share notes
- Prepare for exams together

Comment if interested!''',
                    'tags': ['discussion', 'help-needed'],
                    'replies': 6
                }
            ],
            'Course Queries': [
                {
                    'title': 'CS F111 - Doubt in recursion problems',
                    'content': '''I'm having trouble understanding recursive solutions for tree problems.

Specifically, how do we determine:
1. Base cases
2. What to return at each step
3. How to combine results from left and right subtrees

Can someone explain with a simple example?''',
                    'tags': ['doubt', 'help-needed'],
                    'replies': 4
                },
                {
                    'title': 'MATH F113 - Probability distributions confusion',
                    'content': '''Can someone explain the difference between:
- Binomial distribution
- Poisson distribution
- Normal distribution

When do we use each one? The textbook explanation is too theoretical.
Need practical examples!''',
                    'tags': ['doubt', 'help-needed'],
                    'replies': 3
                },
                {
                    'title': 'CS F213 OOP - Interface vs Abstract Class',
                    'content': '''What's the practical difference between interfaces and abstract classes in Java?

I understand the syntax difference, but when should I use one over the other in real projects?

Any good examples would be helpful!''',
                    'tags': ['doubt', 'discussion'],
                    'replies': 5
                }
            ],
            'Exam Preparation': [
                {
                    'title': 'CS F111 Midsem preparation strategy',
                    'content': '''Midsem is in 2 weeks! Here's my prep strategy:

Week 1:
- Review all lecture slides
- Solve tutorial sheets
- Practice previous year questions

Week 2:
- Focus on weak topics
- Group study sessions
- Mock tests

What's your strategy? Any topics I should focus more on?''',
                    'tags': ['midsem', 'tips'],
                    'replies': 7
                },
                {
                    'title': 'Important topics for MATH F111 compre',
                    'content': '''Based on previous years, these topics are most important:

1. Differential equations (30%)
2. Linear algebra (25%)
3. Vector calculus (25%)
4. Complex numbers (20%)

Can seniors confirm if this is still accurate?''',
                    'tags': ['compre', 'tips'],
                    'replies': 4
                },
                {
                    'title': 'Last minute tips for PHY F111',
                    'content': '''Exam tomorrow! Quick revision checklist:

✅ All formulas memorized
✅ Previous year papers solved
✅ Important derivations practiced
✅ Numerical problems from tutorials

Any last-minute tips from those who've taken it?''',
                    'tags': ['urgent', 'tips'],
                    'replies': 6
                }
            ],
            'Resources & Materials': [
                {
                    'title': 'Best YouTube channels for CS subjects',
                    'content': '''Here are my favorite YouTube channels for CS:

1. **Abdul Bari** - Algorithms and DS
2. **Neso Academy** - Digital Design, OS
3. **Gate Smashers** - DBMS, Networks
4. **CodeWithHarry** - Programming tutorials

Any other recommendations?''',
                    'tags': ['resource-request', 'tips'],
                    'replies': 5
                },
                {
                    'title': 'Request: CS F364 DAA notes',
                    'content': '''Does anyone have comprehensive notes for Design and Analysis of Algorithms?

Topics needed:
- Dynamic Programming
- Greedy Algorithms
- Graph Algorithms
- NP-Completeness

Would really appreciate if someone could share!''',
                    'tags': ['resource-request', 'help-needed'],
                    'replies': 3
                },
                {
                    'title': 'Sharing: Compiled notes for all first-year courses',
                    'content': '''I've compiled notes for all first-year courses:

- CS F111 - Computer Programming
- MATH F111 - Mathematics I
- PHY F111 - Mechanics
- CHEM F111 - General Chemistry
- EEE F111 - Electrical Sciences

Drive link: [would be shared here]

Hope this helps juniors!''',
                    'tags': ['tips'],
                    'replies': 10
                }
            ],
            'Projects & Assignments': [
                {
                    'title': 'CS F213 OOP Project - Library Management System',
                    'content': '''Working on library management system for OOP project.

Implemented features:
- User authentication ✅
- Book CRUD operations ✅
- Issue/Return books ✅

Stuck on:
- Late fee calculation
- Email notifications
- Report generation

Any suggestions for these features?''',
                    'tags': ['project', 'help-needed'],
                    'replies': 4
                },
                {
                    'title': 'Looking for team members for DBMS project',
                    'content': '''Need 2 more members for DBMS project (Hospital Management System).

Requirements:
- Good knowledge of SQL
- Basic frontend skills (HTML/CSS/JS)
- Can commit 5-6 hours per week

DM if interested!''',
                    'tags': ['project', 'help-needed'],
                    'replies': 3
                },
                {
                    'title': 'Assignment 3 - Digital Design doubt',
                    'content': '''In question 5, we need to design a sequential circuit.

My approach:
1. State diagram ✅
2. State table ✅
3. K-maps ❓

Getting different results with K-maps. Can someone verify the correct minimization?''',
                    'tags': ['assignment', 'doubt'],
                    'replies': 2
                }
            ],
            'Announcements': [
                {
                    'title': 'IMPORTANT: Midsem datesheet released',
                    'content': '''Midsem exams starting from next Monday!

Key dates:
- 15th March: CS F111
- 17th March: MATH F111
- 19th March: PHY F111
- 21st March: EEE F111

Check ERP for complete schedule and exam venues.

All the best everyone! 📚''',
                    'tags': ['announcement', 'midsem', 'urgent'],
                    'replies': 2
                },
                {
                    'title': 'Library extended hours during exams',
                    'content': '''Good news! Library will remain open 24x7 during exam period.

Additional facilities:
- Extra reading rooms open
- Coffee vending machines installed
- Group study rooms available (book in advance)

Make good use of these facilities!''',
                    'tags': ['announcement', 'tips'],
                    'replies': 1
                }
            ],
            'Feedback & Suggestions': [
                {
                    'title': 'Suggestion: Add dark mode to StudyDeck',
                    'content': '''It would be great if StudyDeck had a dark mode option.

Benefits:
- Easier on eyes during late night study
- Saves battery on OLED screens
- Looks cooler 😎

Please consider adding this feature!''',
                    'tags': ['feedback', 'feature-request'],
                    'replies': 3
                },
                {
                    'title': 'Bug report: Video player not working properly',
                    'content': '''Facing issues with video player:

1. Videos buffer too much even on good internet
2. Can't skip to specific timestamps
3. No speed control options

Device: MacBook Pro
Browser: Chrome latest

Anyone else facing similar issues?''',
                    'tags': ['bug', 'feedback'],
                    'replies': 2
                }
            ]
        }
        
        # Get threads for this category
        category_threads = thread_templates.get(category.name, [])
        
        if not category_threads:
            # Create generic threads for categories not in template
            category_threads = [
                {
                    'title': f'Welcome to {category.name}!',
                    'content': f'This is the first thread in {category.name}. Feel free to start discussions here!',
                    'tags': ['discussion'],
                    'replies': 2
                }
            ]
        
        for thread_data in category_threads:
            # Check if thread already exists
            if Thread.objects.filter(title=thread_data['title'], category=category).exists():
                continue
                
            # Create thread
            thread = Thread.objects.create(
                title=thread_data['title'],
                content=thread_data['content'],
                author=random.choice(users),
                category=category,
                created_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )
            
            # Add tags
            thread_tags = [tag for tag in tags if tag.name in thread_data.get('tags', [])]
            thread.tags.set(thread_tags)
            
            # Add related courses randomly
            if courses and random.random() > 0.5:
                thread.courses.set(random.sample(list(courses), min(2, len(courses))))
            
            # Update last activity
            thread.last_activity = thread.created_at
            thread.save()
            
            self.stdout.write(f'Created thread: {thread.title}')
            
            # Create replies
            self.create_replies_for_thread(thread, users, thread_data.get('replies', 3))
            
            # Add likes
            self.add_likes_to_thread(thread, users)
    
    def create_replies_for_thread(self, thread, users, num_replies):
        """Create sample replies for a thread"""
        
        reply_templates = [
            "Great question! Here's my take on this...",
            "I had the same doubt. What worked for me was...",
            "Thanks for sharing! This is really helpful.",
            "Following this thread. Need the same information.",
            "Here's what I learned from my experience...",
            "Adding to what others have said...",
            "I disagree slightly. In my opinion...",
            "Can confirm this works! Tested it myself.",
            "Thanks OP! This solved my problem.",
            "Anyone tried this approach? Seems interesting.",
            "This is exactly what I was looking for!",
            "Pro tip: Also consider this aspect...",
            "From a senior's perspective, I'd suggest...",
            "Had similar experience last semester...",
            "+1 to this. Very well explained!",
        ]
        
        for i in range(min(num_replies, len(reply_templates))):
            reply = Reply.objects.create(
                content=reply_templates[i] + "\n\nHope this helps! Feel free to ask if you need more clarification.",
                author=random.choice([u for u in users if u != thread.author]),
                thread=thread,
                created_at=thread.created_at + timedelta(hours=random.randint(1, 72))
            )
            
            # Randomly add likes to replies
            if random.random() > 0.3:
                num_likes = random.randint(1, min(3, len(users)))
                for user in random.sample(users, num_likes):
                    ReplyLike.objects.get_or_create(user=user, reply=reply)
            
            # Update thread's last activity
            thread.last_activity = reply.created_at
            thread.save()
    
    def add_likes_to_thread(self, thread, users):
        """Add random likes to thread"""
        if random.random() > 0.4:  # 60% chance of having likes
            num_likes = random.randint(1, min(5, len(users)))
            for user in random.sample(users, num_likes):
                ThreadLike.objects.get_or_create(user=user, thread=thread)
