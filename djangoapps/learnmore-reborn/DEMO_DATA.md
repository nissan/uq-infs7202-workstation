# Demo Data Generator

This document provides instructions for using the comprehensive demo data generator for the LearnMore Reborn platform. The generator creates rich test data that showcases all features of the platform, making it useful for development, testing, demonstrations, and presentations.

## Features

The demo data generator creates:

- **Users**: Admin, instructors, and students with complete profiles
- **Courses**: A variety of courses with rich descriptions and metadata
- **Modules**: Learning modules with sample content organized in lessons
- **Quizzes**: Different types of quizzes including standard tests and surveys
- **Questions**: Multiple choice, true/false, and essay questions with detailed feedback
- **Rubrics**: Scoring rubrics for essay questions
- **Enrollments**: Student enrollments in various courses
- **Progress Data**: Realistic learning progress for students
- **Quiz Attempts**: Completed quiz attempts with realistic scores
- **QR Codes**: Sample QR codes for courses and modules
- **Analytics Data**: Comprehensive analytics about student performance and engagement

## Usage

Run the management command from the Django project's root directory:

```bash
python manage.py generate_demo_data
```

### Command Options

The generator supports several optional parameters:

```bash
# Generate data with custom amount of users, instructors, and courses
python manage.py generate_demo_data --users 30 --instructors 8 --courses 12

# Clean existing demo data before creating new data
python manage.py generate_demo_data --clean

# Skip generating user progress data
python manage.py generate_demo_data --no-progress

# Skip generating analytics data
python manage.py generate_demo_data --no-analytics
```

### Default Login Credentials

After generating demo data, you can use the following credentials to access the platform:

- **Admin**:
  - Username: `admin`
  - Password: `adminpassword`

- **Instructors**:
  - Username: `instructor1`, `instructor2`, etc.
  - Password: `instructorpassword`

- **Students**:
  - Username: `student1`, `student2`, etc.
  - Password: `studentpassword`

## Generated Data Details

### Users

- **Admin**: Superuser with access to all platform features
- **Instructors**: Created with instructor permissions, departments, and bios
- **Students**: Regular users with student profiles, enrolled in various courses

### Courses

Courses are created with various configurations:
- Different enrollment types (open, restricted)
- Different course types (standard, self-paced, intensive)
- Some with QR code access enabled
- A mix of published and draft courses

### Modules

Each course contains 3-6 modules with:
- Sample content with lessons
- Prerequisite relationships
- Estimated completion times
- QR access settings

### Quizzes

Quizzes include:
- Regular assessment quizzes
- Survey quizzes for feedback
- Time limits and grace periods
- Randomization options
- Detailed feedback settings
- Access codes (for some quizzes)
- Prerequisite requirements

### Questions

Various question types are generated:
- **Multiple Choice**: Single and multiple answer questions
- **True/False**: Basic boolean questions
- **Essay Questions**: Text response questions with word count requirements and rubrics

### Learning Progress

For enrolled students, the generator creates:
- Overall course progress
- Module completion records
- Time spent tracking
- Content position tracking

### Quiz Attempts

For completed modules, the generator creates:
- Quiz attempts with realistic scores
- Question responses
- Essay responses with instructor grades
- Multiple attempts for some quizzes showing improvement

### QR Codes

QR codes are generated for:
- Courses with QR enabled
- Modules with QR access
- Scan statistics and access restrictions

### Analytics

Comprehensive analytics data includes:
- Learner performance metrics
- Course engagement statistics
- Module engagement data
- Quiz performance analysis
- User activity logs

## Cleaning Demo Data

To remove all generated demo data:

```bash
python manage.py generate_demo_data --clean
```

This will remove:
- All users with demo emails
- All courses with "Demo" in the title
- Related progress, enrollments, and analytics data
- Demo QR code batches

## Customization

If you need to modify the generated content:

1. Edit the course templates in the `create_courses` method
2. Adjust question distribution in the `create_regular_questions` method
3. Modify analytics data generation in the `generate_analytics_data` method

## Troubleshooting

If you encounter issues:

1. Make sure all required apps are installed in Django settings
2. Ensure the database migrations are up to date
3. Check that all required models are properly defined
4. Consider running with `--no-analytics` if analytics generation is causing errors

## Purpose

This generator is ideal for:
- Preparing demonstration environments
- Testing platform features with realistic data
- Development and QA scenarios
- Training new users or administrators
- Showcasing the platform's capabilities to stakeholders