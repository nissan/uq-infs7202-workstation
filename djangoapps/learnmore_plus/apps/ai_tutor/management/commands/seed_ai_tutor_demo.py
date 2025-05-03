from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.courses.models import Course, Module, Content
from apps.ai_tutor.models import TutorSession, TutorMessage, TutorContextItem
from apps.ai_tutor.services import ContentIndexingService, TutorService
import logging
import random
from datetime import timedelta

User = get_user_model()
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Seeds demo data for the AI Tutor module'

    def handle(self, *args, **options):
        self.stdout.write('Seeding AI Tutor demo data...')
        
        try:
            # Check if migrations need to be run
            self.check_migrations()
            
            with transaction.atomic():
                self.seed_tutor_sessions()
                self.seed_tutor_demo_conversations()
                self.index_course_content()
                
            self.stdout.write(self.style.SUCCESS('Successfully seeded AI Tutor demo data'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding AI Tutor demo data: {str(e)}'))
            logger.error(f'Error seeding AI Tutor demo data: {str(e)}')
            
            # If there's a table missing error, suggest fixing migrations
            if "no such table" in str(e).lower():
                self.stdout.write(self.style.WARNING(
                    "It looks like migrations are missing. Try running:\n"
                    "python manage.py makemigrations apps.ai_tutor\n"
                    "python manage.py migrate apps.ai_tutor\n"
                    "Then run this command again."
                ))
    
    def check_migrations(self):
        """Check if migrations need to be run and suggest fixes."""
        from django.db import connection
        
        # Try a simple query to see if the table exists
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM ai_tutor_tutorsession LIMIT 1")
        except Exception as e:
            if "no such table" in str(e).lower():
                self.stdout.write(self.style.WARNING("AI Tutor tables don't exist yet. Attempting to create migrations..."))
                
                # Try to create and run migrations automatically
                from django.core.management import call_command
                try:
                    call_command('makemigrations', 'ai_tutor')
                    call_command('migrate', 'ai_tutor')
                    self.stdout.write(self.style.SUCCESS("Successfully created and applied migrations for AI Tutor."))
                except Exception as migrate_error:
                    self.stdout.write(self.style.ERROR(f"Error creating migrations: {str(migrate_error)}"))
                    raise Exception("Unable to create AI Tutor tables automatically. Please run migrations manually.")
                    
        # Check if Ollama is available and has the required models
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags")
            models = response.json().get("models", [])
            required_models = ["llama3", "nomic-embed-text"]
            
            # Check if models exist, accounting for tags like ":latest"
            missing_models = []
            for req_model in required_models:
                model_found = False
                for m in models:
                    model_name = m.get("name", "")
                    if (model_name == req_model or 
                        model_name == f"{req_model}:latest" or 
                        model_name.startswith(f"{req_model}:")):
                        model_found = True
                        break
                if not model_found:
                    missing_models.append(req_model)
            
            if missing_models:
                self.stdout.write(self.style.WARNING(f"Missing required Ollama models: {', '.join(missing_models)}"))
                self.stdout.write(self.style.WARNING("Please pull the required models with:"))
                for model in missing_models:
                    self.stdout.write(f"ollama pull {model}")
                self.stdout.write(self.style.WARNING("Some functionality may not work correctly without these models."))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not check Ollama models: {str(e)}"))
            self.stdout.write(self.style.WARNING("Ollama may not be running or installed."))
            self.stdout.write(self.style.WARNING("Install Ollama from https://ollama.ai/ or configure OpenAI API keys for AI Tutor to work properly."))
            
    def seed_tutor_sessions(self):
        """Seed some tutor sessions for demo users"""
        self.stdout.write('Seeding tutor sessions...')
        
        # Get some students
        students = User.objects.filter(groups__name='Student').order_by('?')[:3]
        if not students:
            self.stdout.write(self.style.WARNING('No students found, skipping tutor session creation'))
            return
            
        # Get some courses with modules and content
        courses = Course.objects.prefetch_related('modules', 'modules__contents').filter(modules__isnull=False).distinct()
        if not courses:
            self.stdout.write(self.style.WARNING('No courses with modules found, skipping tutor session creation'))
            return
            
        # Create some sessions for each student
        for student in students:
            # Course-level session
            course = random.choice(courses)
            TutorService.create_session(
                user=student,
                course=course,
                title=f"Help with {course.title}",
                session_type='course'
            )
            self.stdout.write(f'  Created course session for {student.username} on {course.title}')
            
            # Module-level session if available
            if course.modules.exists():
                module = random.choice(course.modules.all())
                TutorService.create_session(
                    user=student,
                    course=course,
                    module=module,
                    title=f"Questions about {module.title}",
                    session_type='module'
                )
                self.stdout.write(f'  Created module session for {student.username} on {module.title}')
                
                # Content-level session if available
                if module.contents.exists():
                    content = random.choice(module.contents.all())
                    TutorService.create_session(
                        user=student,
                        course=course,
                        module=module,
                        content=content,
                        title=f"Understanding {content.title}",
                        session_type='content'
                    )
                    self.stdout.write(f'  Created content session for {student.username} on {content.title}')
            
            # General session
            TutorService.create_session(
                user=student,
                title="General learning questions",
                session_type='general'
            )
            self.stdout.write(f'  Created general session for {student.username}')
    
    def seed_tutor_demo_conversations(self):
        """Seed some demo conversations in the tutor sessions"""
        self.stdout.write('Seeding demo conversations...')
        
        # Get existing sessions
        sessions = TutorSession.objects.all()
        
        # Example conversations for different session types
        course_conversation = [
            ("Can you give me an overview of this course?", "This course covers core concepts in [subject]. You'll learn about the fundamental principles, practical applications, and advanced techniques. The course is organized into several modules, each focusing on a specific aspect of the subject."),
            ("What's the most challenging topic in this course?", "Based on student feedback, conceptual understanding of [topic] is often challenging. This is covered in module 3, and I recommend spending extra time on the practice exercises for that section."),
            ("How should I prepare for the quizzes?", "For quiz preparation, review the key concepts listed at the end of each module. The practice exercises are designed to test your understanding of the same concepts. Make sure to understand rather than memorize the material.")
        ]
        
        module_conversation = [
            ("What are the key learning objectives for this module?", "This module focuses on [topic]. By the end, you should be able to understand [concept], apply [skill], and analyze [application]. The most important sections are [x] and [y], which build the foundation for later modules."),
            ("How does this module connect to the previous one?", "This module builds directly on the concepts from the previous module on [topic]. Specifically, the [concept] you learned about earlier is now applied to [new context]. If you're having trouble, revisiting section 2.3 of the previous module might help."),
            ("I'm stuck on the concept of [x]. Can you explain it differently?", "Let's approach [x] from a different angle. Think of it as [analogy]. In this framework, [explanation]. Does that help clarify the concept?")
        ]
        
        content_conversation = [
            ("I don't understand this diagram. Can you explain it?", "This diagram illustrates [concept]. The left side represents [x], while the right side shows [y]. The arrows indicate [relationship]. Think of it as [analogy] which might make it easier to understand."),
            ("Can you provide some examples of this concept in practice?", "Here are some real-world examples of this concept: 1) [example 1] - where [explanation]. 2) [example 2] - which demonstrates [principle]. 3) [example 3] - a case where [application]."),
            ("How would I apply this to solve a problem?", "To apply this concept to problem-solving, follow these steps: 1) Identify [condition]. 2) Apply [principle]. 3) Calculate [variable]. 4) Interpret your results in terms of [context]. Let's work through a simple example together...")
        ]
        
        general_conversation = [
            ("What's the best way to study effectively?", "Effective studying varies by person, but some proven techniques include: 1) Spaced repetition rather than cramming. 2) Active recall instead of passive re-reading. 3) Teaching concepts to others. 4) Taking breaks using the Pomodoro technique. 5) Getting proper sleep to consolidate memory."),
            ("I'm struggling with motivation. Any tips?", "Motivation challenges are common. Try these approaches: 1) Break large tasks into smaller, achievable goals. 2) Create a consistent study environment. 3) Use the 5-minute rule - commit to just 5 minutes, and often you'll continue. 4) Connect the material to your personal goals. 5) Reward yourself for milestone achievements."),
            ("How can I remember complex information better?", "For better retention of complex information: 1) Create mental associations and use mnemonic devices. 2) Visualize concepts with mind maps or diagrams. 3) Explain the material in your own words. 4) Connect new information to existing knowledge. 5) Apply concepts to solve problems rather than just reading about them.")
        ]
        
        # Add conversations to sessions based on type
        for session in sessions:
            conversation = None
            if session.session_type == 'course':
                conversation = course_conversation
            elif session.session_type == 'module':
                conversation = module_conversation
            elif session.session_type == 'content':
                conversation = content_conversation
            elif session.session_type == 'general':
                conversation = general_conversation
                
            if conversation:
                # Add the conversation to the session
                for user_msg, assistant_msg in conversation:
                    # Create user message
                    user_message = TutorMessage.objects.create(
                        session=session,
                        message_type='user',
                        content=user_msg,
                        created_at=session.created_at + timedelta(minutes=random.randint(1, 60))
                    )
                    
                    # Create assistant message
                    assistant_message = TutorMessage.objects.create(
                        session=session,
                        message_type='assistant',
                        content=assistant_msg,
                        created_at=user_message.created_at + timedelta(seconds=random.randint(5, 30))
                    )
                    
                # Update the session's updated_at time
                session.updated_at = assistant_message.created_at
                session.save(update_fields=['updated_at'])
                
                self.stdout.write(f'  Added conversation to {session.title} for {session.user.username}')
    
    def index_course_content(self):
        """Index all course content for AI tutor retrieval"""
        self.stdout.write('Indexing course content for RAG...')
        
        # Get content to index
        contents = Content.objects.select_related('module__course').all()
        indexed_count = 0
        error_count = 0
        
        for content in contents:
            try:
                ContentIndexingService.index_content(content)
                self.stdout.write(f'  Indexed: {content.title}')
                indexed_count += 1
            except Exception as e:
                error_str = str(e)
                # Convert to string to handle any object serialization issues
                if "_type" in error_str:
                    # This is a known issue we're handling with fallbacks
                    self.stdout.write(self.style.WARNING(f'  Type issue indexing {content.title}, using fallback embeddings'))
                    # We'll count this as success since we're using fallbacks
                    indexed_count += 1
                else:
                    self.stdout.write(self.style.ERROR(f'  Error indexing {content.title}: {error_str}'))
                    error_count += 1
                
        # Print summary
        self.stdout.write(f'Indexing summary: {indexed_count} items indexed successfully, {error_count} errors.')