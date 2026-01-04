from django.core.management.base import BaseCommand
from courses.models import Course
from resources.models import Resource, ResourceType
import random


class Command(BaseCommand):
    help = 'Populate database with sample resources'
    
    def handle(self, *args, **options):
        self.stdout.write('Populating resources...')
        
        # Get all courses
        courses = Course.objects.all()
        if not courses:
            self.stdout.write(
                self.style.ERROR(
                    'No courses found. Please run populate_courses command first.'
                )
            )
            return
        
        # Sample resource data templates
        resource_templates = [
            # PDFs
            {'title': 'Lecture Notes - Unit 1', 'type': ResourceType.PDF, 'link': 'https://drive.google.com/file/lecture1.pdf'},
            {'title': 'Lecture Notes - Unit 2', 'type': ResourceType.PDF, 'link': 'https://drive.google.com/file/lecture2.pdf'},
            {'title': 'Lecture Notes - Unit 3', 'type': ResourceType.PDF, 'link': 'https://drive.google.com/file/lecture3.pdf'},
            {'title': 'Tutorial Sheet 1', 'type': ResourceType.PDF, 'link': 'https://drive.google.com/file/tutorial1.pdf'},
            {'title': 'Tutorial Sheet 2', 'type': ResourceType.PDF, 'link': 'https://drive.google.com/file/tutorial2.pdf'},
            
            # Videos
            {'title': 'Introduction Lecture', 'type': ResourceType.VIDEO, 'link': 'https://youtube.com/watch?v=intro'},
            {'title': 'Mid-Semester Review', 'type': ResourceType.VIDEO, 'link': 'https://youtube.com/watch?v=midsem'},
            {'title': 'Problem Solving Session', 'type': ResourceType.VIDEO, 'link': 'https://youtube.com/watch?v=problems'},
            
            # Links
            {'title': 'Course Website', 'type': ResourceType.LINK, 'link': 'https://coursepage.bits-pilani.ac.in/'},
            {'title': 'Reference Book Online', 'type': ResourceType.LINK, 'link': 'https://onlinelibrary.com/book'},
            {'title': 'MIT OCW Similar Course', 'type': ResourceType.LINK, 'link': 'https://ocw.mit.edu/course'},
            
            # Previous Year Questions
            {'title': 'Midsem 2023', 'type': ResourceType.PYQ, 'link': 'https://drive.google.com/file/midsem2023.pdf'},
            {'title': 'Compre 2023', 'type': ResourceType.PYQ, 'link': 'https://drive.google.com/file/compre2023.pdf'},
            {'title': 'Midsem 2022', 'type': ResourceType.PYQ, 'link': 'https://drive.google.com/file/midsem2022.pdf'},
            {'title': 'Compre 2022', 'type': ResourceType.PYQ, 'link': 'https://drive.google.com/file/compre2022.pdf'},
            
            # Handouts
            {'title': 'Course Handout', 'type': ResourceType.HANDOUT, 'link': 'https://drive.google.com/file/handout.pdf'},
            {'title': 'Lab Manual', 'type': ResourceType.HANDOUT, 'link': 'https://drive.google.com/file/labmanual.pdf'},
            
            # Notes
            {'title': 'Important Formulas', 'type': ResourceType.NOTES, 'link': 'https://drive.google.com/file/formulas.pdf'},
            {'title': 'Quick Revision Notes', 'type': ResourceType.NOTES, 'link': 'https://drive.google.com/file/revision.pdf'},
            {'title': 'Solved Examples', 'type': ResourceType.NOTES, 'link': 'https://drive.google.com/file/examples.pdf'},
        ]
        
        created_count = 0
        
        # Create resources for each course (randomly select 5-10 resources per course)
        for course in courses:
            num_resources = random.randint(5, 10)
            selected_templates = random.sample(
                resource_templates, 
                min(num_resources, len(resource_templates))
            )
            
            for template in selected_templates:
                resource, created = Resource.objects.get_or_create(
                    title=f"{template['title']} - {course.code}",
                    course=course,
                    type=template['type'],
                    defaults={
                        'link': template['link'],
                        'description': f"This is a {template['type']} resource for {course.title}",
                        'views': random.randint(0, 500)
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f"Created resource: {resource.title}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} resources'
            )
        )
