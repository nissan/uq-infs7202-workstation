#!/bin/bash
# Script to verify demo scenarios are all functioning

echo "=== Testing Demo Scenarios ==="
echo ""

# Start Django shell
python manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Module, Content, Quiz
from apps.qr_codes.models import QRCode
from apps.dashboard.models import UserActivity
from django.contrib.contenttypes.models import ContentType
import sys

User = get_user_model()

scenarios_passed = 0
scenarios_failed = 0

def check_scenario(name, condition, details=''):
    global scenarios_passed, scenarios_failed
    print(f'Testing {name}... ', end='')
    sys.stdout.flush()
    if condition:
        scenarios_passed += 1
        print('✅ PASSED')
    else:
        scenarios_failed += 1
        print('❌ FAILED')
        if details:
            print(f'   Details: {details}')
    print()

# Check Course Variety
published_with_content = Course.objects.filter(status='published').exclude(modules__contents__isnull=True).exists()
check_scenario(
    'Published Courses with Content',
    published_with_content,
    'No published courses with content found'
)

empty_courses = Course.objects.filter(
    status='published'
).filter(
    modules__isnull=True
).exists() or Course.objects.filter(
    status='published',
    modules__contents__isnull=True
).exists()
check_scenario(
    'Empty Courses Available for Enrollment',
    empty_courses,
    'No empty courses found'
)

draft_courses = Course.objects.filter(status='draft').exists()
archived_courses = Course.objects.filter(status='archived').exists()
check_scenario(
    'Draft and Archived Courses',
    draft_courses and archived_courses,
    f'Draft courses: {draft_courses}, Archived courses: {archived_courses}'
)

# Check Quiz Types
pre_check_surveys = Quiz.objects.filter(is_pre_check=True).exists()
check_scenario(
    'Pre-Check Surveys',
    pre_check_surveys,
    'No pre-check surveys found'
)

knowledge_checks = Quiz.objects.filter(is_pre_check=False, is_prerequisite=False).exists()
check_scenario(
    'Knowledge Check Quizzes',
    knowledge_checks,
    'No knowledge check quizzes found'
)

prerequisite_quizzes = Quiz.objects.filter(is_prerequisite=True).exists()
check_scenario(
    'Prerequisite Quizzes',
    prerequisite_quizzes,
    'No prerequisite quizzes found'
)

# Check QR Code System
course_qr_codes = QRCode.objects.filter(
    content_type=ContentType.objects.get_for_model(Course)
).exists()
check_scenario(
    'Course QR Code Generation',
    course_qr_codes,
    'No course QR codes found'
)

module_qr_codes = QRCode.objects.filter(
    content_type=ContentType.objects.get_for_model(Module)
).exists()
check_scenario(
    'Module QR Code Generation',
    module_qr_codes,
    'No module QR codes found'
)

qr_codes_with_scans = QRCode.objects.filter(scan_count__gt=0).exists()
check_scenario(
    'QR Code Analytics',
    qr_codes_with_scans,
    'No QR codes with scan statistics found'
)

# Check Activity Logging
activity_logs = UserActivity.objects.count() > 100
check_scenario(
    'Activity Logging and Monitoring',
    activity_logs,
    f'Only {UserActivity.objects.count()} activity logs found'
)

# Required Course Titles
required_courses = [
    'Python Programming Fundamentals',
    'Web Development with HTML, CSS, and JavaScript',
    'Cloud Computing with AWS',
    'Introduction to SQL and Database Design',
    'Mobile App Development with React Native',
    'Legacy Web Development with PHP'
]

for course_title in required_courses:
    course_exists = Course.objects.filter(title__contains=course_title.split(' ')[0]).exists()
    check_scenario(
        f'Course: {course_title}',
        course_exists,
        f'Course with title containing {course_title.split(\" \")[0]} not found'
    )

# Summary
print(f'Scenarios passed: {scenarios_passed}')
print(f'Scenarios failed: {scenarios_failed}')
print()

if scenarios_failed > 0:
    print('Some scenarios failed. Run the following command to fix missing scenarios:')
    print('python manage.py complete_seed_data')
else:
    print('All demo scenarios are ready! Use the following user credentials:')
    print('Admin:')
    print('  Username: admin')
    print('  Password: admin123')
    print('')
    print('Coordinator:')
    print('  Username: coordinator')
    print('  Password: coordinator123')
    print('')
    print('Instructor:')
    print('  Username: dr.smith')
    print('  Password: dr.smith123')
    print('')
    print('Student:')
    print('  Username: john.doe')
    print('  Password: john.doe123')
    print('')
"

# Make the script executable
chmod +x test_demo_scenarios.sh

echo ""
echo "=== Test complete ==="