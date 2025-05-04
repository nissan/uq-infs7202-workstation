# Seed Data Guide

This document provides detailed information about the enhanced seed data available in LearnMore Plus. The seed data is designed to showcase different aspects of the platform and provide meaningful demonstration scenarios.

## Running the Seed Command

To reset the database and seed it with enhanced demo data, run:

```bash
python manage.py reset_db
```

This will:
1. Reset the database (drop and recreate it)
2. Run all migrations
3. Seed the database with enhanced course data
4. Create demo users and groups
5. Seed AI Tutor demo data
6. Seed activity data for the dashboard

If you want to run just the enhanced seed data command (on an existing database), run:

```bash
python manage.py enhanced_seed_data
```

## Course Variety

The enhanced seed data includes different types of courses to demonstrate the full course lifecycle:

### Published Courses with Content

These courses have complete content and are available for enrollment:

1. **Python Programming Fundamentals**
   - Category: Programming
   - Features:
     - Multiple modules with various content types
     - Pre-check survey quizzes
     - Knowledge check quizzes
     - Text, video, and file content

2. **Web Development with HTML, CSS, and JavaScript**
   - Category: Web Development
   - Features:
     - Comprehensive HTML fundamentals module
     - Pre-course survey
     - Prerequisite knowledge check
     - Mix of text and video content

3. **Data Analysis with Python**
   - Category: Data Science
   - Features:
     - Multiple modules on data analysis concepts
     - NumPy and Pandas content
     - Knowledge check quizzes with scoring

### Empty Courses Available for Enrollment

These courses are published but don't yet have content, allowing students to enroll and see the "waiting for content" experience:

1. **Cloud Computing with AWS**
   - Category: Cloud Computing
   - Empty course structure waiting for content

2. **Introduction to SQL and Database Design**
   - Category: Database Management
   - Module framework without content

3. **Cybersecurity Fundamentals**
   - Category: Cybersecurity
   - Ready for content to be added

### Draft and Archived Courses

These courses show different states in the course lifecycle:

1. **Mobile App Development with React Native**
   - Status: Draft
   - Category: Mobile Development
   - Has minimal content not yet published to students

2. **Legacy Web Development with PHP**
   - Status: Archived
   - Category: Web Development
   - Historical course that is no longer active

## Quiz Types

The seed data includes different types of quizzes to showcase the assessment system:

### Pre-Check Surveys

Survey-style quizzes with no right/wrong answers, used to gauge student prior knowledge:

- All answers are considered "correct"
- Don't affect student progress
- Usually found at the beginning of courses/modules
- Focus on gathering information rather than assessment

Example: "Pre-Course Knowledge Check" in Python Programming course

### Knowledge Check Quizzes

Traditional quizzes with right and wrong answers:

- Multiple choice and true/false questions
- Scored with passing thresholds
- Multiple attempts allowed
- Detailed feedback on performance

Example: "Module 1 Quiz" in Python Programming course

### Prerequisite Quizzes

Quizzes that must be passed before proceeding to the next module:

- Block progression until successfully completed
- Usually have important foundational knowledge
- Show how content flow can be controlled

Example: "HTML Knowledge Check" in Web Development course

## Enrollment and Progress States

Each student in the seed data has varied enrollment and progress states:

1. **Active Enrollments in Different Stages**
   - Just started (0-20% complete)
   - In progress (20-80% complete)
   - Nearly finished (80-99% complete)

2. **Completed Courses**
   - Fully completed courses with 100% progress
   - All modules marked as completed
   - Quiz attempts with passing scores

3. **Dropped Courses**
   - Partially completed then abandoned
   - Some modules completed, others not started
   - Incomplete quiz attempts

## User Roles and Data

The seed data includes different user types with appropriate data:

### Admin
- Username: `admin`
- Password: `admin123`
- Has access to all courses and system functions
- Can see all student, instructor, and coordinator data

### Course Coordinator
- Username: `coordinator`
- Password: `coordinator123`
- Assigned as coordinator to several courses
- Can manage course assignments

### Instructors
- Various instructor accounts (`dr.smith`, `dr.johnson`, `prof.williams`)
- Each assigned to different courses
- Some instructors have multiple courses
- Some courses have multiple instructors

### Students
- Four student accounts with different enrollment patterns
- Students have varied progress across courses
- Some students have dropped courses
- Some students have completed courses
- Each student has different quiz attempt patterns

## Demo Scenarios

Here are some suggested demo scenarios to showcase the different types of seed data:

### Course Status Flow
1. Log in as an instructor
2. View a course in "draft" status
3. Publish the course
4. Log in as a student to enroll
5. As an admin, archive an old course

### Quiz Experience
1. Log in as a student
2. Take a pre-check survey in a course
3. Complete a module with content
4. Take a knowledge check quiz
5. Retry the quiz if you fail
6. Encounter a prerequisite quiz that blocks progress

### Enrollment Management
1. Log in as a student
2. View the course catalog
3. Enroll in an empty course
4. See the "waiting for content" experience
5. Enroll in a course with content
6. Begin the learning journey

### Progress Tracking
1. Log in as a student with varied progress
2. View your dashboard to see overall progress
3. View specific course progress
4. See module completion status
5. Review quiz scores and attempts

### Instructor Experience
1. Log in as an instructor
2. View assigned courses
3. See student enrollment data
4. Review student quiz attempts
5. Examine course analytics

## Technical Implementation

The seed data is implemented in the `enhanced_seed_data.py` management command with the following features:

1. **Consistent Data Generation**
   - User accounts with appropriate roles
   - Course categories and course data
   - Module and content structure
   - Quiz questions and choices

2. **Realistic User Activity**
   - Randomized but sensible progress tracking
   - Time-appropriate enrollment dates
   - Quiz attempts with time tracking
   - Module progress based on enrollment status

3. **Course Diversity**
   - Different course statuses (published, draft, archived)
   - Varied course content types
   - Different quiz types and configurations
   - Empty and fully populated courses

4. **Integration with Other Systems**
   - AI Tutor data integration
   - QR Code generation for courses
   - Activity tracking for dashboard

## Modifying Seed Data

If you need to modify the seed data, follow these steps:

1. Edit the `enhanced_seed_data.py` file in the `apps/courses/management/commands/` directory
2. Add or modify course data in the `course_data` list
3. Run the command to update your database:
   ```bash
   python manage.py enhanced_seed_data
   ```

You can also customize specific aspects:
- Add more courses by extending the `course_data` list
- Change the random distribution of enrollments by modifying the probability values
- Alter the quiz questions in the quiz creation methods
- Add more user accounts in the student or instructor data lists