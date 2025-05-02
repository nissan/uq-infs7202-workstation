I'm working on a Django-based learning management system called Enhanced LearnMore. We've made significant progress and I'd like to continue development. Here's our current state:

1. Project Structure:
- Main Django project: `djangoapps/learnmore_plus`
- Key apps: accounts, dashboard, core, courses
- Using Tailwind CSS for styling
- Dark mode support implemented
- Secure session handling in place

2. Recent Progress:
- Implemented course management system
- Created course catalog with search and filtering
- Added course models and admin interface
- Implemented file upload support
- Fixed broken avatar image with SVG icon
- Improved course card design and filter sidebar
- Enhanced quiz system with pre-requisite surveys and results page
- Combined student dashboard and learning progress
- Updated documentation (TODO.md, NOTES.md, CHECKPOINT.md)
- Improved homepage button contrast and accessibility
- Made 'Browse All Courses' a prominent button
- Fixed number circle contrast in 'How Enhanced LearnMore Works'

3. Current Focus:
- Complete quiz system implementation
  - Add quiz analytics for instructors
  - Implement quiz time tracking
  - Add support for question feedback
  - Enhance quiz navigation between questions
- Assignment submission system
- Discussion forum implementation

4. Security Considerations:
- Using Django's session framework instead of localStorage
- Secure cookie handling
- CSRF protection
- XSS prevention
- SQL injection protection
- File upload validation
- Input sanitization

5. Documentation:
- TODO.md: Updated with recent changes and next steps
- NOTES.md: Added dashboard consolidation and quiz improvements
- CHECKPOINT.md: Updated current state and achievements
- README.md: Project overview and setup instructions

6. Effective Prompting Patterns:
For UI Changes:
"Can you [improve/fix/update] the [component] in [file] to [desired outcome]?"

For Feature Implementation:
"Let's implement [feature] in [component/file]. We need:
- [requirement 1]
- [requirement 2]
- [requirement 3]"

For Troubleshooting:
"I'm seeing [issue] when [action]. Here's the error:
[error message/behavior]"

7. Testing Approach:
- Manual testing of UI changes
- Checking responsive design
- Verifying dark mode functionality
- Testing user authentication flow
- Validating course management features
- Testing file upload functionality
- Verifying search and filtering

8. Known Issues:
None currently pending - all recent issues have been resolved:
- Fixed migration order issues
- Implemented proper file upload handling
- Added search across multiple fields
- Fixed filter persistence
- Replaced broken avatar image with SVG icon

9. Next Steps:
1. Create course detail template
2. Implement course enrollment
3. Add course content preview
4. Display course modules
5. Create user dashboard

10. Environment:
- Working Directory: `/Users/nissan/code/uq-infs7202-workstation`
- Django Project: `djangoapps/learnmore_plus`
- Python Virtual Environment: Active in `djangoapps/learnmore_plus/venv`
- Database: SQLite3 (`db.sqlite3`)
- Git Branch: `main`

11. Active Files:
- `djangoapps/learnmore_plus/courses/models.py`
- `djangoapps/learnmore_plus/courses/views.py`
- `djangoapps/learnmore_plus/courses/templates/courses/student_dashboard.html`
- `djangoapps/learnmore_plus/courses/templates/courses/quiz/result.html`
- `djangoapps/learnmore_plus/templates/base.html`
- `TODO.md`
- `NOTES.md`
- `CHECKPOINT.md`
- `README.md`

12. Project Structure:
djangoapps/learnmore_plus/
├── accounts/
│ ├── views.py
│ ├── models.py
│ └── middleware.py
├── core/
│ ├── views.py
│ ├── urls.py
│ └── templates/
│     └── core/
│         └── home.html
├── courses/
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ └── templates/
│     └── courses/
│         ├── catalog.html
│         └── detail.html (to be created)
├── dashboard/
│ ├── views.py
│ ├── models.py
│ └── templates/
│     └── dashboard/
│         └── home.html
├── templates/
│ └── base.html
└── learnmore_plus/
    ├── settings.py
    └── urls.py

13. Response Patterns:
The LLM has been most effective when:
1. Explaining changes before making them
2. Breaking down complex tasks into steps
3. Providing context for security implications
4. Checking file contents before modifications
5. Verifying directory locations before commands
6. Using conventional commit formats
7. Updating documentation alongside changes

14. Git Workflow:
- Using conventional commit format
- Committing changes with descriptive messages
- Pushing to remote repository regularly
- Maintaining clean commit history

15. Security Best Practices:
- No sensitive data in version control
- Secure session handling
- Proper authentication/authorization
- Input validation
- XSS/CSRF protection
- SQL injection prevention
- File upload validation
- Input sanitization

16. Development Guidelines:
- Follow Django best practices
- Maintain clean code structure
- Document all changes
- Test thoroughly
- Consider security implications
- Keep dependencies updated

17. UI/UX Standards:
- Responsive design
- Dark mode support
- Accessibility compliance
- Consistent styling
- User-friendly interfaces
- Clear error messages
- Use SVG icons for better scaling
- Proper hover and focus states

18. Performance Considerations:
- Optimize database queries
- Minimize HTTP requests
- Use caching where appropriate
- Optimize static files
- Monitor resource usage
- Implement pagination
- Add proper indexing

19. Documentation Requirements:
- Keep TODO.md updated
- Document all changes in NOTES.md
- Maintain CHECKPOINT.md for session continuity
- Comment complex code
- Document security measures
- Update README.md

20. Testing Requirements:
- Test all new features
- Verify security measures
- Check responsive design
- Validate user flows
- Test error handling
- Test file uploads
- Verify search functionality

Tomorrow's Focus:
1. Complete quiz system implementation
   - Add quiz analytics for instructors
   - Implement quiz time tracking
   - Add support for question feedback
   - Enhance quiz navigation between questions
2. Begin assignment system implementation
3. Start discussion forum development

Please help me continue development following these guidelines and patterns. Let's start by reviewing our current state and determining the next immediate task to tackle.

## Quickstart for Demo

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Reset and seed the database:
   ```bash
   python manage.py reset_db
   ```
3. Run the development server:
   ```bash
   python manage.py runserver
   ```
4. Log in as any demo user (see output after seeding)

## Demo Data & Showcase
- The system is seeded with realistic users, courses, modules, content, quizzes, enrollments, and progress.
- All user types and workflows are demo-ready.
- Use the Showcase Script in the README to walk through all features and dashboards.
