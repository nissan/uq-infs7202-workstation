from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from apps.courses.models import (
    Category, Course, Module, Content, Quiz, Question, Choice,
    CourseEnrollment, ModuleProgress, QuizAttempt, Answer
)
from apps.qr_codes.models import QRCode
from django.contrib.contenttypes.models import ContentType
from apps.dashboard.models import UserActivity
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Completes seed data to ensure all demo scenarios are covered'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Completing demo data to cover all scenarios...'))
        
        try:
            with transaction.atomic():
                self.ensure_qr_codes()
                self.ensure_prerequisite_quizzes()
                self.ensure_empty_courses()
                self.ensure_draft_and_archived_courses()
                self.ensure_course_types()
                self.ensure_quiz_types()
                self.ensure_activity_data()
                
            self.stdout.write(self.style.SUCCESS('Successfully completed seed data for all demo scenarios'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error completing seed data: {str(e)}'))
    
    def ensure_qr_codes(self):
        """Ensure QR codes exist for courses and modules"""
        self.stdout.write('Ensuring QR codes for courses and modules...')
        
        # Get published courses
        courses = Course.objects.filter(status='published')
        
        course_ct = ContentType.objects.get_for_model(Course)
        module_ct = ContentType.objects.get_for_model(Module)
        
        # Create QR codes for courses
        for course in courses:
            # Check if QR code already exists
            if not QRCode.objects.filter(content_type=course_ct, object_id=course.id).exists():
                qr_code = QRCode.objects.create(
                    content_type=course_ct,
                    object_id=course.id,
                    url=f"/courses/{course.slug}/"
                )
                self.stdout.write(f'  Created QR code for course: {course.title}')
            
            # Create QR codes for modules
            for module in course.modules.all():
                if not QRCode.objects.filter(content_type=module_ct, object_id=module.id).exists():
                    qr_code = QRCode.objects.create(
                        content_type=module_ct,
                        object_id=module.id,
                        url=f"/courses/{course.slug}/modules/{module.id}/"
                    )
                    self.stdout.write(f'  Created QR code for module: {module.title}')
        
        # Generate some scan statistics
        self.stdout.write('Generating QR code scan statistics...')
        qr_codes = QRCode.objects.all()
        
        for qr_code in qr_codes:
            # Add scan count between 5-30
            scan_count = random.randint(5, 30)
            qr_code.scan_count = scan_count
            qr_code.save()
            
            # Set last_used date for some codes
            if random.random() > 0.3:  # 70% chance
                qr_code.last_used = timezone.now() - timedelta(days=random.randint(1, 14))
                qr_code.save()
                
            self.stdout.write(f'  Added {scan_count} scans to QR code for {qr_code.content_object}')
    
    def ensure_prerequisite_quizzes(self):
        """Ensure prerequisite quizzes exist"""
        self.stdout.write('Ensuring prerequisite quizzes...')
        
        # Find courses with modules and no prerequisite quizzes
        courses = Course.objects.filter(status='published').exclude(modules__isnull=True)
        
        # Check for at least one prerequisite quiz
        has_prereq = Content.objects.filter(
            content_type='quiz', 
            module__course__in=courses,
            quiz__is_prerequisite=True
        ).exists()
        
        if not has_prereq:
            # Choose a course to add a prerequisite quiz to
            course = courses.first()
            if course and course.modules.count() > 1:
                # Add prerequisite quiz to the second module
                module = course.modules.all()[1]
                
                # Create content for quiz
                content = Content.objects.create(
                    module=module,
                    title='Prerequisite Quiz',
                    content_type='quiz',
                    content='You must pass this quiz to proceed to the next module',
                    estimated_time=20,
                    order=1,
                    is_required=True
                )
                
                # Create the quiz
                quiz = Quiz.objects.create(
                    content=content,
                    title='Module Prerequisite Quiz',
                    description='You must score at least 70% to proceed to the next module',
                    passing_score=70,
                    time_limit=30,
                    attempts_allowed=3,
                    is_prerequisite=True,
                    is_pre_check=False,
                    shuffle_questions=True
                )
                
                # Create questions
                self.create_quiz_questions(quiz)
                
                self.stdout.write(f'  Created prerequisite quiz for module: {module.title}')
    
    def create_quiz_questions(self, quiz, count=3):
        """Create questions for a quiz"""
        for i in range(count):
            question = Question.objects.create(
                quiz=quiz,
                question_text=f'Question {i+1} for {quiz.title}',
                question_type='multiple_choice',
                points=5,
            )
            
            # Create choices
            Choice.objects.create(
                question=question,
                choice_text='Correct answer',
                is_correct=True,
            )
            
            for j in range(3):
                Choice.objects.create(
                    question=question,
                    choice_text=f'Wrong answer {j+1}',
                    is_correct=False,
                )
    
    def ensure_empty_courses(self):
        """Ensure there are empty courses available for enrollment"""
        self.stdout.write('Ensuring empty courses...')
        
        # Check for empty published courses
        empty_courses = Course.objects.filter(
            status='published',
            modules__isnull=True
        )
        
        if not empty_courses.exists():
            # Check for courses with empty modules
            empty_module_courses = Course.objects.filter(
                status='published',
                modules__contents__isnull=True
            ).distinct()
            
            if not empty_module_courses.exists():
                # Create a new empty course
                category = Category.objects.first()
                instructor = User.objects.filter(groups__name='Instructor').first()
                
                course = Course.objects.create(
                    title='Empty Course for Demonstration',
                    description='This course is intentionally empty to demonstrate the enrollment process for courses without content.',
                    category=category,
                    status='published',
                    max_students=50,
                    slug='empty-course-demo',
                    start_date=timezone.now().date(),
                    end_date=(timezone.now() + timedelta(days=90)).date(),
                )
                
                if instructor:
                    course.instructors.add(instructor)
                
                # Add an empty module
                module = Module.objects.create(
                    course=course,
                    title='Coming Soon',
                    description='Content for this module is coming soon. Stay tuned!',
                    order=1,
                )
                
                self.stdout.write(f'  Created empty course: {course.title}')
    
    def ensure_draft_and_archived_courses(self):
        """Ensure draft and archived courses exist"""
        self.stdout.write('Ensuring draft and archived courses...')
        
        # Check for draft courses
        draft_courses = Course.objects.filter(status='draft')
        if not draft_courses.exists():
            # Create a draft course
            category = Category.objects.first()
            instructor = User.objects.filter(groups__name='Instructor').first()
            
            course = Course.objects.create(
                title='Mobile App Development (Draft)',
                description='This course is in draft mode and will be published soon.',
                category=category,
                status='draft',
                max_students=30,
                slug='mobile-app-draft',
                start_date=timezone.now().date(),
                end_date=(timezone.now() + timedelta(days=90)).date(),
            )
            
            if instructor:
                course.instructors.add(instructor)
            
            # Add a module
            module = Module.objects.create(
                course=course,
                title='Introduction to Mobile Development',
                description='An overview of mobile app development',
                order=1,
            )
            
            self.stdout.write(f'  Created draft course: {course.title}')
        
        # Check for archived courses
        archived_courses = Course.objects.filter(status='archived')
        if not archived_courses.exists():
            # Create an archived course
            category = Category.objects.first()
            instructor = User.objects.filter(groups__name='Instructor').first()
            
            course = Course.objects.create(
                title='Legacy Web Development (Archived)',
                description='This course has been archived and is no longer available for enrollment.',
                category=category,
                status='archived',
                max_students=0,
                slug='legacy-web-archived',
                start_date=(timezone.now() - timedelta(days=180)).date(),
                end_date=(timezone.now() - timedelta(days=30)).date(),
            )
            
            if instructor:
                course.instructors.add(instructor)
            
            # Add a module
            module = Module.objects.create(
                course=course,
                title='Introduction to Legacy Web Development',
                description='An overview of legacy web development techniques',
                order=1,
            )
            
            self.stdout.write(f'  Created archived course: {course.title}')
    
    def ensure_course_types(self):
        """Ensure all course types mentioned in the demo scenarios exist"""
        self.stdout.write('Ensuring all course types exist...')
        
        # Define required course titles from demo scenarios
        required_courses = [
            'Python Programming Fundamentals',
            'Web Development with HTML, CSS, and JavaScript',
            'Cloud Computing with AWS',
            'Introduction to SQL and Database Design',
            'Mobile App Development with React Native',
            'Legacy Web Development with PHP'
        ]
        
        # Check which ones exist
        existing_courses = set(Course.objects.filter(title__in=required_courses).values_list('title', flat=True))
        missing_courses = set(required_courses) - existing_courses
        
        if missing_courses:
            self.stdout.write(f'  Missing {len(missing_courses)} required courses: {missing_courses}')
            
            # Create missing courses with basic content
            category = Category.objects.first()
            instructor = User.objects.filter(groups__name='Instructor').first()
            
            for course_title in missing_courses:
                # Determine status based on title
                if 'Legacy' in course_title:
                    status = 'archived'
                elif 'Mobile App' in course_title:
                    status = 'draft'
                else:
                    status = 'published'
                
                # Create course
                course = Course.objects.create(
                    title=course_title,
                    description=f'This course covers {course_title}.',
                    category=category,
                    status=status,
                    max_students=30 if status == 'published' else 0,
                    slug=course_title.lower().replace(' ', '-'),
                    start_date=timezone.now().date(),
                    end_date=(timezone.now() + timedelta(days=90)).date(),
                )
                
                if instructor and status != 'archived':
                    course.instructors.add(instructor)
                
                # Add at least one module
                module = Module.objects.create(
                    course=course,
                    title=f'Introduction to {course_title}',
                    description=f'An overview of {course_title}',
                    order=1,
                )
                
                # For published courses, add some content
                if status == 'published':
                    # Add text content
                    Content.objects.create(
                        module=module,
                        title='Introduction',
                        content_type='text',
                        content='This is an introduction to the course.',
                        estimated_time=30,
                        order=1,
                    )
                
                self.stdout.write(f'  Created missing course: {course.title} ({status})')
    
    def ensure_quiz_types(self):
        """Ensure all quiz types mentioned in the demo scenarios exist"""
        self.stdout.write('Ensuring all quiz types exist...')
        
        # Check for pre-check surveys
        pre_check = Content.objects.filter(
            content_type='quiz',
            quiz__is_pre_check=True
        ).exists()
        
        if not pre_check:
            # Add a pre-check survey to a course
            course = Course.objects.filter(status='published').first()
            if course and course.modules.exists():
                module = course.modules.first()
                
                # Create content for pre-check
                content = Content.objects.create(
                    module=module,
                    title='Pre-Course Survey',
                    content_type='quiz',
                    content='Please complete this survey before starting the course',
                    estimated_time=15,
                    order=1,
                )
                
                # Create the quiz
                quiz = Quiz.objects.create(
                    content=content,
                    title='Pre-Course Survey',
                    description='This survey helps us understand your background',
                    passing_score=0,
                    time_limit=15,
                    attempts_allowed=1,
                    is_prerequisite=False,
                    is_pre_check=True,
                    shuffle_questions=False
                )
                
                # Create survey questions
                for i, question_text in enumerate([
                    'How would you rate your experience with this subject?',
                    'What do you hope to gain from this course?',
                    'How much time can you dedicate to this course weekly?'
                ]):
                    question = Question.objects.create(
                        quiz=quiz,
                        question_text=question_text,
                        question_type='multiple_choice',
                        points=0,
                    )
                    
                    # Create choices - all correct for surveys
                    for j, choice_text in enumerate([
                        'Option A', 'Option B', 'Option C', 'Option D'
                    ]):
                        Choice.objects.create(
                            question=question,
                            choice_text=choice_text,
                            is_correct=True,  # All options are "correct" in a survey
                        )
                
                self.stdout.write(f'  Created pre-check survey for course: {course.title}')
        
        # Check for knowledge check quizzes
        knowledge_check = Content.objects.filter(
            content_type='quiz',
            quiz__is_pre_check=False,
            quiz__is_prerequisite=False
        ).exists()
        
        if not knowledge_check:
            # Add a knowledge check quiz to a course
            course = Course.objects.filter(status='published').first()
            if course and course.modules.exists():
                module = course.modules.first()
                
                # Create content for knowledge check
                content = Content.objects.create(
                    module=module,
                    title='Module Knowledge Check',
                    content_type='quiz',
                    content='Test your understanding of this module',
                    estimated_time=20,
                    order=999,  # Put at the end
                )
                
                # Create the quiz
                quiz = Quiz.objects.create(
                    content=content,
                    title='Module Knowledge Check',
                    description='Test your understanding of the concepts covered in this module',
                    passing_score=70,
                    time_limit=30,
                    attempts_allowed=3,
                    is_prerequisite=False,
                    is_pre_check=False,
                    shuffle_questions=True
                )
                
                # Create quiz questions
                self.create_quiz_questions(quiz)
                
                self.stdout.write(f'  Created knowledge check quiz for course: {course.title}')
    
    def ensure_activity_data(self):
        """Ensure activity data exists for all scenarios"""
        self.stdout.write('Ensuring activity data exists...')
        
        # Check for existing activities
        if UserActivity.objects.count() < 100:
            # We need more activities
            self.stdout.write('  Adding more user activities...')
            
            # Get users
            users = User.objects.all()
            
            # Activity types
            activity_types = [
                'login', 'logout', 'course_view', 'quiz_attempt',
                'content_access', 'profile_update', 'settings_change'
            ]
            
            # Create 20 activities per user
            for user in users:
                for _ in range(20):
                    # Random date in the past 30 days
                    date = timezone.now() - timedelta(days=random.randint(0, 30))
                    
                    # Random activity type
                    activity_type = random.choice(activity_types)
                    
                    # Create activity
                    UserActivity.objects.create(
                        user=user,
                        action=activity_type,
                        timestamp=date,
                        ip_address=f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}',
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        details={
                            'page': f'/{activity_type}/',
                            'item_id': random.randint(1, 100),
                            'duration': random.randint(30, 600)
                        }
                    )
            
            self.stdout.write(f'  Added {20 * users.count()} new user activities')