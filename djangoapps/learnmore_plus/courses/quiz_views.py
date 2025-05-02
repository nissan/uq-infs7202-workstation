from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from .models import Course, Content, Quiz, Question, Choice, QuizAttempt, Answer
from .forms import QuizForm, QuestionForm, ChoiceFormSet

@login_required
def quiz_create(request, course_slug, content_id):
    """Create a new quiz for a course content"""
    content = get_object_or_404(Content, id=content_id, content_type='quiz')
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is the course instructor
    if not course.instructors.filter(id=request.user.id).exists():
        return HttpResponseForbidden("Only course instructors can create quizzes")
    
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.content = content
            quiz.save()
            messages.success(request, 'Quiz created successfully')
            return redirect('quiz_edit', course_slug=course_slug, quiz_id=quiz.id)
    else:
        form = QuizForm()
    
    return render(request, 'courses/quiz/create.html', {
        'form': form,
        'course': course,
        'content': content
    })

@login_required
def quiz_edit(request, course_slug, quiz_id):
    """Edit an existing quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is the course instructor
    if not course.instructors.filter(id=request.user.id).exists():
        return HttpResponseForbidden("Only course instructors can edit quizzes")
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully')
            return redirect('quiz_edit', course_slug=course_slug, quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)
    
    questions = quiz.questions.all()
    return render(request, 'courses/quiz/edit.html', {
        'form': form,
        'quiz': quiz,
        'course': course,
        'questions': questions
    })

@login_required
def question_create(request, course_slug, quiz_id):
    """Add a new question to a quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is the course instructor
    if not course.instructors.filter(id=request.user.id).exists():
        return HttpResponseForbidden("Only course instructors can add questions")
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            
            if question.question_type in ['multiple_choice', 'true_false']:
                if formset.is_valid():
                    formset.instance = question
                    formset.save()
            
            messages.success(request, 'Question added successfully')
            return redirect('quiz_edit', course_slug=course_slug, quiz_id=quiz.id)
    else:
        form = QuestionForm()
        formset = ChoiceFormSet()
    
    return render(request, 'courses/quiz/question_form.html', {
        'form': form,
        'formset': formset,
        'quiz': quiz,
        'course': course
    })

@login_required
def quiz_take(request, course_slug, quiz_id):
    """Take a quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is enrolled in the course
    if not course.enrollments.filter(student=request.user).exists():
        return HttpResponseForbidden("You must be enrolled in the course to take quizzes")
    
    # Check if user has remaining attempts
    attempts = quiz.attempts.filter(student=request.user)
    if quiz.attempts_allowed > 0 and attempts.count() >= quiz.attempts_allowed:
        return HttpResponseForbidden("You have used all your attempts for this quiz")
    
    # Create new attempt
    attempt = QuizAttempt.objects.create(
        student=request.user,
        quiz=quiz,
        status='in_progress'
    )
    
    # Get questions
    questions = quiz.questions.all()
    if quiz.shuffle_questions:
        questions = questions.order_by('?')
    
    return render(request, 'courses/quiz/take.html', {
        'quiz': quiz,
        'course': course,
        'attempt': attempt,
        'questions': questions
    })

@login_required
def quiz_submit(request, course_slug, attempt_id):
    """Submit a quiz attempt"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    course = get_object_or_404(Course, slug=course_slug)
    
    # Only check status for non-POST requests
    if request.method != 'POST' and attempt.status != 'in_progress':
        return HttpResponseForbidden("This attempt has already been submitted")
    
    if request.method == 'POST':
        # Process answers
        total_points = 0
        earned_points = 0
        is_pre_check = attempt.quiz.is_pre_check
        
        for question in attempt.quiz.questions.all():
            answer_text = request.POST.get(f'question_{question.id}')
            if answer_text:
                # Get or create the answer
                answer, created = Answer.objects.get_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={'answer_text': answer_text}
                )
                if not created:
                    answer.answer_text = answer_text
                if not is_pre_check:
                    answer.is_correct = False  # Reset correctness
                    answer.points_earned = 0   # Reset points
                    # Auto-grade if possible
                    if question.question_type in ['multiple_choice', 'true_false']:
                        correct_choice = question.choices.filter(is_correct=True).first()
                        if correct_choice and answer_text == correct_choice.choice_text:
                            answer.is_correct = True
                            answer.points_earned = question.points
                answer.save()
                if not is_pre_check:
                    total_points += question.points
                    if answer.is_correct:
                        earned_points += answer.points_earned
        # Calculate score only for non-pre-check quizzes
        if not is_pre_check and total_points > 0:
            attempt.score = (earned_points / total_points) * 100
        else:
            attempt.score = None
        attempt.status = 'submitted'
        attempt.submitted_at = timezone.now()
        attempt.save()
        messages.success(request, 'Quiz submitted successfully')
        # Redirect to the quiz result page
        return redirect('courses:quiz_result', course_slug=course_slug, attempt_id=attempt.id)
    return redirect('courses:learn', slug=course_slug)

@login_required
def quiz_result(request, course_slug, attempt_id):
    """View quiz attempt results"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    course = get_object_or_404(Course, slug=course_slug)
    
    if attempt.status == 'in_progress':
        return HttpResponseForbidden("This attempt has not been submitted yet")
    
    return render(request, 'courses/quiz/result.html', {
        'quiz': attempt.quiz,
        'course': course,
        'attempt': attempt,
        'answers': attempt.answers.all()
    }) 