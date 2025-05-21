from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import TutorSession, TutorMessage, TutorFeedback, TutorConfiguration
from courses.models import Course, Module

@login_required
def ai_tutor_dashboard(request):
    """
    Display a dashboard showing all tutor sessions for the current user.
    """
    user_sessions = TutorSession.objects.filter(user=request.user).order_by('-updated_at')
    courses = Course.objects.filter(enrollments__user=request.user).distinct()
    
    context = {
        'user_sessions': user_sessions,
        'courses': courses,
    }
    
    return render(request, 'ai_tutor/dashboard.html', context)

@login_required
def create_tutor_session(request):
    """
    Create a new tutor session.
    """
    if request.method == 'POST':
        title = request.POST.get('title', 'New Session')
        course_id = request.POST.get('course')
        module_id = request.POST.get('module')
        
        # Create a new session
        session = TutorSession.objects.create(
            user=request.user,
            title=title,
            course_id=course_id if course_id else None,
            module_id=module_id if module_id else None,
            status='active'
        )
        
        # Add a welcome message from the tutor
        TutorMessage.objects.create(
            session=session,
            message_type='tutor',
            content="Hello! I'm your AI tutor. How can I help you today?"
        )
        
        return redirect('ai_tutor_session', session_id=session.id)
    
    # If GET request, redirect to dashboard
    return redirect('ai_tutor_dashboard')

@login_required
def tutor_session_view(request, session_id):
    """
    Display an active tutor session with conversation history.
    """
    session = get_object_or_404(TutorSession, id=session_id, user=request.user)
    messages = session.messages.all().order_by('created_at')
    
    # Get related courses and modules for context switch
    courses = Course.objects.filter(enrollments__user=request.user).distinct()
    
    modules = []
    if session.course:
        modules = Module.objects.filter(course=session.course)
    
    context = {
        'session': session,
        'messages': messages,
        'courses': courses,
        'modules': modules,
    }
    
    return render(request, 'ai_tutor/session.html', context)

@login_required
@require_POST
def send_message(request, session_id):
    """
    Send a message to the AI tutor and get a response.
    """
    session = get_object_or_404(TutorSession, id=session_id, user=request.user)
    message_content = request.POST.get('message', '').strip()
    
    if not message_content:
        return JsonResponse({
            'status': 'error',
            'message': 'Message cannot be empty'
        }, status=400)
    
    # Create user message
    user_message = TutorMessage.objects.create(
        session=session,
        message_type='user',
        content=message_content
    )
    
    # TODO: Process with AI (LangChain, etc)
    # This will be replaced with actual AI processing
    # For now, just create a dummy response
    
    # Get response from LangChain service
    from .langchain_service import tutor_langchain_service
    
    # Generate response using LangChain
    response_data = tutor_langchain_service.get_tutor_response(session, message_content)
    
    # Create tutor response message
    tutor_message = TutorMessage.objects.create(
        session=session,
        message_type='tutor',
        content=response_data["content"],
        metadata={
            "sources": response_data.get("sources", []),
            **response_data.get("metadata", {})
        }
    )
    
    # Update session
    session.save()  # This will update the updated_at timestamp
    
    return JsonResponse({
        'status': 'success',
        'user_message': {
            'id': user_message.id,
            'content': user_message.content,
            'created_at': user_message.created_at.isoformat(),
        },
        'tutor_message': {
            'id': tutor_message.id,
            'content': tutor_message.content,
            'created_at': tutor_message.created_at.isoformat(),
        }
    })

@login_required
@require_POST
def provide_feedback(request, message_id):
    """
    Submit feedback on a specific tutor message.
    """
    message = get_object_or_404(TutorMessage, id=message_id)
    session = message.session
    
    # Ensure the user owns the session
    if session.user != request.user:
        return JsonResponse({
            'status': 'error',
            'message': 'Not authorized'
        }, status=403)
    
    helpful = request.POST.get('helpful')
    if helpful:
        helpful = helpful.lower() == 'true'
    else:
        helpful = None
        
    rating = request.POST.get('rating')
    if rating:
        try:
            rating = int(rating)
        except ValueError:
            rating = None
    
    comment = request.POST.get('comment', '').strip()
    
    # Create or update feedback
    feedback, created = TutorFeedback.objects.update_or_create(
        session=session,
        user=request.user,
        message=message,
        defaults={
            'helpful': helpful,
            'rating': rating,
            'comment': comment
        }
    )
    
    return JsonResponse({
        'status': 'success',
        'feedback_id': feedback.id
    })

@login_required
@require_POST
def end_session(request, session_id):
    """
    End an active tutor session.
    """
    session = get_object_or_404(TutorSession, id=session_id, user=request.user)
    
    if session.status == 'active':
        session.status = 'completed'
        session.save()
        
        # Add a closing message
        TutorMessage.objects.create(
            session=session,
            message_type='system',
            content="This session has been completed. You can start a new session or review this one later."
        )
        
        messages.success(request, "Tutor session completed successfully.")
    
    return redirect('ai_tutor_dashboard')