# LearnMore Reborn Demo Setup

This guide explains how to set up and use the demo data for showcasing the LearnMore platform, including the advanced quiz system and AI tutor with RAG integration.

## 🚀 Demo Setup Instructions

Follow these steps to set up a complete demo environment with sample users, courses, quizzes, and AI tutor content.

### Prerequisites

1. Make sure you have a virtual environment activated:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Apply migrations:
   ```bash
   python manage.py migrate
   ```

### Step 1: Create Test Users

Create a set of demo users with different roles (admin, instructors, students):

```bash
python manage.py shell < create_test_users.py
```

This will create the following users (all with password: `testpass123`):
- **Admin**: `admin@example.com` (username: `admin`)
- **Instructors**: 
  - `professor@example.com` (username: `professor`)
  - `teacher@example.com` (username: `teacher`)
- **Students**:
  - `student1@example.com` (username: `student1`)
  - `student2@example.com` (username: `student2`)
  - `student3@example.com` (username: `student3`)

### Step 2: Create Demo Course Content

Generate rich course content with detailed modules and quizzes:

```bash
python manage.py shell < create_demo_rag_content.py
```

This will create:
- 4 courses covering different topics
- 12 modules with detailed content
- Multiple quizzes with different question types (multiple-choice, true/false, essay)
- Automatic enrollment of test students in all courses

### Step 3: Ingest Content for AI Tutor RAG

Prepare the course content for use with the AI tutor's Retrieval Augmented Generation system:

```bash
python manage.py shell < ingest_rag_content.py
```

This will:
- Create knowledge base entries from course content
- Ingest all content into the vector database
- Enable the AI tutor to retrieve relevant information when answering questions

### Step 4: Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The demo is now ready to use! Visit http://127.0.0.1:8000/ to access the platform.

## 🧪 Demo Features to Explore

### 1. Course Catalog and Enrollment

- View the course catalog at `/courses/`
- See detailed course information including modules and quizzes
- Explore the different course types and content

### 2. Advanced Quiz System

The quiz system supports various question types and features:

- **Multiple Question Types**: 
  - Multiple-choice questions
  - True/False questions
  - Essay questions requiring manual grading

- **Quiz Features**:
  - Time limits
  - Randomization of questions and choices
  - Multiple attempts
  - Detailed feedback

- **To Try It Out**:
  1. Log in as a student (e.g., `student1`)
  2. Navigate to an enrolled course
  3. Select a module with a quiz
  4. Take a quiz and explore the different question types

### 3. AI Tutor with RAG Integration

The AI Tutor uses the course content to provide context-aware responses:

- **RAG Features**:
  - Knowledge base built from course content
  - Context-aware responses based on course materials
  - Citation of sources in responses

- **To Try It Out**:
  1. Log in as a student
  2. Navigate to the AI Tutor at `/ai_tutor/`
  3. Create a new tutor session (optionally selecting a specific course)
  4. Ask questions about course topics to see context-aware responses

### 4. Instructor Features

As an instructor, you can:

- Create and manage courses
- Create modules and quizzes
- Grade essay questions
- View student progress and analytics

- **To Try It Out**:
  1. Log in as an instructor (e.g., `professor`)
  2. Create a new course or edit existing ones
  3. Manage quizzes and view student attempts
  4. Grade essay question responses

## 📊 Analytics and Dashboards

The platform includes analytics dashboards for both students and instructors:

- **Student Analytics**: View your learning progress, quiz scores, and activity
- **Instructor Analytics**: Monitor course performance, student engagement, and quiz effectiveness

- **To Try It Out**:
  1. Log in as an instructor
  2. Navigate to the Analytics dashboard
  3. Explore the different metrics and visualizations

## 📝 Notes for Developers

- The demo uses mock embeddings for RAG integration to work without OpenAI API keys
- For production use, you would need to:
  - Configure real embedding providers
  - Set up proper API keys
  - Optimize the vector database for production use

- The LangChain integration is set up but requires API keys for full functionality
- The RAG system is ready for further enhancements like:
  - Real-time content indexing
  - More sophisticated retrieval strategies
  - Integration with other knowledge sources

## 🧹 Resetting the Demo

To reset the demo data:

1. Delete the database:
   ```bash
   rm db.sqlite3
   ```

2. Delete the vector store:
   ```bash
   rm -rf ai_tutor/vector_store
   ```

3. Apply migrations again:
   ```bash
   python manage.py migrate
   ```

4. Repeat the demo setup steps