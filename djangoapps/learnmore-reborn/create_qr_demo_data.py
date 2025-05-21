#!/usr/bin/env python
"""
Script to create demonstration QR code data for the LearnMore platform.
This script generates QR codes for existing courses, modules, and quizzes,
and sets up sample scan data to showcase the QR code tracking functionality.

Usage:
    python create_qr_demo_data.py
"""

import os
import django
import random
import uuid
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmore.settings')
django.setup()

from django.contrib.auth import get_user_model
from courses.models import Course, Module, Quiz, Enrollment
from progress.models import Progress
from qr_codes.models import QRCode, QRCodeScan, QRCodeBatch
from qr_codes.services import QRCodeService

User = get_user_model()

def create_qr_demo_data():
    """Create comprehensive QR code demo data."""
    print("Creating QR code demonstration data...")
    
    try:
        # Get or create admin user
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
        
        # Get or create instructor and student users
        try:
            instructor = User.objects.get(username='instructor')
        except User.DoesNotExist:
            instructor = User.objects.create_user(
                username='instructor',
                email='instructor@example.com',
                password='instructor123'
            )
            instructor.is_staff = True
            instructor.save()
        
        try:
            student = User.objects.get(username='student')
        except User.DoesNotExist:
            student = User.objects.create_user(
                username='student',
                email='student@example.com',
                password='student123'
            )
        
        # Use transaction to ensure atomicity
        with transaction.atomic():
            # 1. Create QR codes for existing courses
            print("Creating QR codes for courses...")
            course_content_type = ContentType.objects.get_for_model(Course)
            courses = Course.objects.all()
            
            if not courses.exists():
                print("No courses found. Please run create_test_data.py or create_demo_rag_content.py first.")
                return
            
            # Enable QR codes for all courses
            for course in courses:
                course.qr_enabled = True
                course.save()
                
                # Create QR code for this course
                qr_code, created = QRCode.objects.get_or_create(
                    content_type=course_content_type,
                    object_id=course.id,
                    defaults={
                        'is_active': True,
                        'access_level': 'public',
                        'payload': {
                            'title': course.title,
                            'description': course.description[:100] if course.description else ''
                        }
                    }
                )
                
                if created or not qr_code.image_data:
                    QRCodeService.generate_qr_image(qr_code)
                    print(f"Created QR code for course: {course.title}")
            
            # 2. Create QR codes for modules with different access levels
            print("Creating QR codes for modules...")
            module_content_type = ContentType.objects.get_for_model(Module)
            modules = Module.objects.all()
            
            access_levels = ['public', 'enrolled', 'instructor']
            for i, module in enumerate(modules):
                # Set QR access for the module
                access_level = access_levels[i % len(access_levels)]
                module.qr_access = 'disabled' if access_level == 'instructor' and i % 5 == 0 else access_level
                module.save()
                
                # Create QR code if access is not disabled
                if module.qr_access != 'disabled':
                    qr_code, created = QRCode.objects.get_or_create(
                        content_type=module_content_type,
                        object_id=module.id,
                        defaults={
                            'is_active': True,
                            'access_level': access_level,
                            'payload': {
                                'title': module.title,
                                'course': module.course.title,
                                'description': module.description[:100] if module.description else ''
                            }
                        }
                    )
                    
                    if created or not qr_code.image_data:
                        QRCodeService.generate_qr_image(qr_code)
                        print(f"Created QR code for module: {module.title} (Access: {access_level})")
            
            # 3. Create QR codes for selected quizzes
            print("Creating QR codes for quizzes...")
            quiz_content_type = ContentType.objects.get_for_model(Quiz)
            quizzes = Quiz.objects.all()
            
            for i, quiz in enumerate(quizzes):
                # Enable QR tracking for every other quiz
                quiz.qr_tracking = (i % 2 == 0)
                quiz.save()
                
                if quiz.qr_tracking:
                    qr_code, created = QRCode.objects.get_or_create(
                        content_type=quiz_content_type,
                        object_id=quiz.id,
                        defaults={
                            'is_active': True,
                            'access_level': 'enrolled',
                            'max_scans': 10 if i % 3 == 0 else None,  # Add scan limits to some quizzes
                            'payload': {
                                'title': quiz.title,
                                'module': quiz.module.title,
                                'time_limit_minutes': quiz.time_limit_minutes
                            }
                        }
                    )
                    
                    if created or not qr_code.image_data:
                        QRCodeService.generate_qr_image(qr_code)
                        print(f"Created QR code for quiz: {quiz.title}")
            
            # 4. Create QR code batches
            print("Creating QR code batches...")
            
            # Batch for course access
            course_batch = QRCodeBatch.objects.create(
                name='Course Access QR Codes',
                description='Batch of QR codes for accessing all courses',
                created_by=admin_user,
                content_type=course_content_type,
                target_type='course',
                is_active=True,
                access_level='public'
            )
            
            # Add courses to the batch
            for course in courses:
                qr_code = QRCode.objects.get(content_type=course_content_type, object_id=course.id)
                qr_code.batch = course_batch
                qr_code.save()
            
            # Update batch statistics
            course_batch.codes_count = QRCode.objects.filter(batch=course_batch).count()
            course_batch.save()
            
            # Batch for module access (only for public modules)
            public_modules = Module.objects.filter(qr_access='public')
            if public_modules.exists():
                module_batch = QRCodeBatch.objects.create(
                    name='Public Module QR Codes',
                    description='Batch of QR codes for accessing public modules',
                    created_by=instructor,
                    content_type=module_content_type,
                    target_type='module',
                    is_active=True,
                    access_level='public'
                )
                
                # Add public modules to the batch
                for module in public_modules:
                    try:
                        qr_code = QRCode.objects.get(content_type=module_content_type, object_id=module.id)
                        qr_code.batch = module_batch
                        qr_code.save()
                    except QRCode.DoesNotExist:
                        pass
                
                # Update batch statistics
                module_batch.codes_count = QRCode.objects.filter(batch=module_batch).count()
                module_batch.save()
            
            # 5. Simulate QR code scans for demo data
            print("Creating sample QR code scan data...")
            
            # Get enrollments and progress records
            enrollments = Enrollment.objects.filter(status='active')
            
            # If we have enrollments, create scan data
            if enrollments.exists():
                for enrollment in enrollments[:5]:  # Limit to first 5 enrollments
                    user = enrollment.user
                    course = enrollment.course
                    
                    # Get progress record or create one
                    progress, created = Progress.objects.get_or_create(
                        user=user,
                        course=course,
                        defaults={'qr_scans': {}}
                    )
                    
                    # Get QR codes for this course and its modules
                    course_qr = QRCode.objects.filter(content_type=course_content_type, object_id=course.id).first()
                    module_qrs = QRCode.objects.filter(
                        content_type=module_content_type, 
                        object_id__in=course.modules.values_list('id', flat=True)
                    )
                    
                    # Create scan records for the course QR code
                    if course_qr:
                        # Create multiple scans with different timestamps
                        for i in range(3):
                            scan_time = timezone.now() - timedelta(days=i*2)
                            scan = QRCodeScan.objects.create(
                                qr_code=course_qr,
                                user=user,
                                scanned_at=scan_time,
                                ip_address='127.0.0.1',
                                user_agent=f'Demo Browser {i+1}',
                                status='success'
                            )
                        
                        # Update scan count
                        course_qr.current_scans = QRCodeScan.objects.filter(qr_code=course_qr).count()
                        course_qr.save()
                        
                        # Add to user's progress tracking
                        last_scan = QRCodeScan.objects.filter(qr_code=course_qr, user=user).order_by('-scanned_at').first()
                        first_scan = QRCodeScan.objects.filter(qr_code=course_qr, user=user).order_by('scanned_at').first()
                        
                        if last_scan and first_scan:
                            scans = progress.qr_scans or {}
                            scans[str(course_qr.id)] = {
                                'first_scan': str(first_scan.id),
                                'last_scan': str(last_scan.id),
                                'count': QRCodeScan.objects.filter(qr_code=course_qr, user=user).count(),
                                'last_scan_time': last_scan.scanned_at.isoformat()
                            }
                            progress.qr_scans = scans
                            progress.save()
                    
                    # Create scan records for module QR codes (randomly select 2)
                    if module_qrs.exists():
                        for module_qr in random.sample(list(module_qrs), min(2, module_qrs.count())):
                            # Create a scan record
                            scan_time = timezone.now() - timedelta(hours=random.randint(1, 48))
                            scan = QRCodeScan.objects.create(
                                qr_code=module_qr,
                                user=user,
                                scanned_at=scan_time,
                                ip_address='127.0.0.1',
                                user_agent=f'Demo Mobile {random.randint(1, 3)}',
                                latitude=random.uniform(-90, 90) if random.random() > 0.5 else None,
                                longitude=random.uniform(-180, 180) if random.random() > 0.5 else None,
                                status='success'
                            )
                            
                            # Update scan count
                            module_qr.current_scans = QRCodeScan.objects.filter(qr_code=module_qr).count()
                            module_qr.save()
                            
                            # Add to user's progress tracking
                            scans = progress.qr_scans or {}
                            scans[str(module_qr.id)] = {
                                'first_scan': str(scan.id),
                                'last_scan': str(scan.id),
                                'count': 1,
                                'last_scan_time': scan.scanned_at.isoformat()
                            }
                            progress.qr_scans = scans
                            progress.save()
            
            # 6. Update batch scan counts
            for batch in QRCodeBatch.objects.all():
                total_scans = 0
                for qr_code in QRCode.objects.filter(batch=batch):
                    total_scans += QRCodeScan.objects.filter(qr_code=qr_code).count()
                batch.scans_count = total_scans
                batch.save()
                print(f"Batch '{batch.name}' has {batch.codes_count} codes and {batch.scans_count} scans")
                
        print("QR code demonstration data created successfully!")
    
    except Exception as e:
        print(f"Error creating QR code demonstration data: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_qr_demo_data()