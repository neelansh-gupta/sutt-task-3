from django.core.management.base import BaseCommand
from courses.models import Department, Course


class Command(BaseCommand):
    help = 'Populate database with sample courses and departments'
    
    def handle(self, *args, **options):
        self.stdout.write('Populating departments and courses...')
        
        # Create departments
        departments_data = [
            {'code': 'CS', 'name': 'Computer Science', 'description': 'Department of Computer Science and Information Systems'},
            {'code': 'EEE', 'name': 'Electrical & Electronics', 'description': 'Department of Electrical and Electronics Engineering'},
            {'code': 'MECH', 'name': 'Mechanical', 'description': 'Department of Mechanical Engineering'},
            {'code': 'PHY', 'name': 'Physics', 'description': 'Department of Physics'},
            {'code': 'CHEM', 'name': 'Chemistry', 'description': 'Department of Chemistry'},
            {'code': 'MATH', 'name': 'Mathematics', 'description': 'Department of Mathematics'},
            {'code': 'BIO', 'name': 'Biology', 'description': 'Department of Biological Sciences'},
            {'code': 'ECO', 'name': 'Economics', 'description': 'Department of Economics and Finance'},
        ]
        
        departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults={
                    'name': dept_data['name'],
                    'description': dept_data['description']
                }
            )
            departments[dept.code] = dept
            if created:
                self.stdout.write(f'Created department: {dept}')
        
        # Create courses
        courses_data = [
            # Computer Science courses
            {'code': 'CS F111', 'title': 'Computer Programming', 'department': 'CS', 'credits': 4},
            {'code': 'CS F213', 'title': 'Object Oriented Programming', 'department': 'CS', 'credits': 4},
            {'code': 'CS F214', 'title': 'Logic in Computer Science', 'department': 'CS', 'credits': 3},
            {'code': 'CS F215', 'title': 'Digital Design', 'department': 'CS', 'credits': 4},
            {'code': 'CS F222', 'title': 'Discrete Structures for Computer Science', 'department': 'CS', 'credits': 3},
            {'code': 'CS F241', 'title': 'Microprocessors and Interfacing', 'department': 'CS', 'credits': 4},
            {'code': 'CS F301', 'title': 'Principles of Programming Languages', 'department': 'CS', 'credits': 3},
            {'code': 'CS F303', 'title': 'Computer Networks', 'department': 'CS', 'credits': 4},
            {'code': 'CS F342', 'title': 'Computer Architecture', 'department': 'CS', 'credits': 3},
            {'code': 'CS F351', 'title': 'Theory of Computation', 'department': 'CS', 'credits': 3},
            {'code': 'CS F363', 'title': 'Compiler Construction', 'department': 'CS', 'credits': 3},
            {'code': 'CS F364', 'title': 'Design and Analysis of Algorithms', 'department': 'CS', 'credits': 3},
            {'code': 'CS F372', 'title': 'Operating Systems', 'department': 'CS', 'credits': 3},
            
            # EEE courses
            {'code': 'EEE F111', 'title': 'Electrical Sciences', 'department': 'EEE', 'credits': 3},
            {'code': 'EEE F241', 'title': 'Microprocessors and Interfacing', 'department': 'EEE', 'credits': 4},
            {'code': 'EEE F242', 'title': 'Control Systems', 'department': 'EEE', 'credits': 3},
            {'code': 'EEE F243', 'title': 'Signals and Systems', 'department': 'EEE', 'credits': 3},
            {'code': 'EEE F244', 'title': 'Microelectronic Circuits', 'department': 'EEE', 'credits': 3},
            
            # Mathematics courses
            {'code': 'MATH F111', 'title': 'Mathematics I', 'department': 'MATH', 'credits': 3},
            {'code': 'MATH F112', 'title': 'Mathematics II', 'department': 'MATH', 'credits': 3},
            {'code': 'MATH F113', 'title': 'Probability and Statistics', 'department': 'MATH', 'credits': 3},
            {'code': 'MATH F211', 'title': 'Mathematics III', 'department': 'MATH', 'credits': 3},
            {'code': 'MATH F213', 'title': 'Discrete Mathematics', 'department': 'MATH', 'credits': 3},
            
            # Physics courses
            {'code': 'PHY F111', 'title': 'Mechanics Oscillations and Waves', 'department': 'PHY', 'credits': 3},
            {'code': 'PHY F110', 'title': 'Physics Laboratory', 'department': 'PHY', 'credits': 1},
            {'code': 'PHY F212', 'title': 'Electromagnetic Theory I', 'department': 'PHY', 'credits': 3},
            {'code': 'PHY F213', 'title': 'Optics', 'department': 'PHY', 'credits': 3},
            
            # Chemistry courses
            {'code': 'CHEM F111', 'title': 'General Chemistry', 'department': 'CHEM', 'credits': 3},
            {'code': 'CHEM F110', 'title': 'Chemistry Laboratory', 'department': 'CHEM', 'credits': 1},
            
            # Biology courses
            {'code': 'BIO F111', 'title': 'General Biology', 'department': 'BIO', 'credits': 3},
            {'code': 'BIO F110', 'title': 'Biology Laboratory', 'department': 'BIO', 'credits': 1},
            
            # Economics courses
            {'code': 'ECON F211', 'title': 'Principles of Economics', 'department': 'ECO', 'credits': 3},
            {'code': 'ECON F311', 'title': 'International Economics', 'department': 'ECO', 'credits': 3},
        ]
        
        created_count = 0
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults={
                    'title': course_data['title'],
                    'department': departments[course_data['department']],
                    'credits': course_data['credits'],
                    'description': f"This is the course description for {course_data['title']}."
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created course: {course}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated {len(departments)} departments and {created_count} new courses'
            )
        )
