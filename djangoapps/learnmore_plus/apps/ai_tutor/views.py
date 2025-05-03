from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
from django.urls import reverse

import json
import logging

from apps.courses.models import Course, Module, Content
from .models import TutorSession, TutorMessage, TutorContextItem
from .services import TutorService, ContentIndexingService

logger = logging.getLogger(__name__)

@login_required
def session_list(request):
    """View to display all tutor sessions for the current user."""
    sessions = TutorSession.objects.filter(user=request.user).order_by('-updated_at')
    
    # Exclude system messages for display
    for session in sessions:
        session.last_message = session.messages.exclude(message_type='system').order_by('-created_at').first()
    
    context = {
        'sessions': sessions,
        'active_sessions': sessions.filter(is_active=True).count(),
    }
    
    return render(request, 'ai_tutor/session_list.html', context)

@login_required
def create_session(request):
    """View to create a new tutor session."""
    if request.method == 'POST':
        session_type = request.POST.get('session_type', 'general')
        title = request.POST.get('title', '')
        
        # Get related objects if specified
        course_id = request.POST.get('course_id')
        module_id = request.POST.get('module_id')
        content_id = request.POST.get('content_id')
        
        course = None
        module = None
        content = None
        
        if content_id:
            content = get_object_or_404(Content, id=content_id)
            module = content.module
            course = module.course
        elif module_id:
            module = get_object_or_404(Module, id=module_id)
            course = module.course
        elif course_id:
            course = get_object_or_404(Course, id=course_id)
        
        # Create the session
        session = TutorService.create_session(
            user=request.user,
            course=course,
            module=module,
            content=content,
            title=title,
            session_type=session_type
        )
        
        return redirect('ai_tutor:chat', session_id=session.id)
    
    # Get courses the user has access to
    courses = Course.objects.filter(enrollments__student=request.user, enrollments__status='active')
    
    context = {
        'courses': courses
    }
    
    return render(request, 'ai_tutor/create_session.html', context)

@login_required
def session_detail(request, session_id):
    """View details of a tutor session."""
    session = get_object_or_404(TutorSession, id=session_id, user=request.user)
    messages = session.messages.order_by('created_at')
    context_items = session.get_context_items()
    
    context = {
        'session': session,
        'messages': messages,
        'context_items': context_items,
    }
    
    return render(request, 'ai_tutor/session_detail.html', context)

@login_required
def delete_session(request, session_id):
    """Delete a tutor session."""
    session = get_object_or_404(TutorSession, id=session_id, user=request.user)
    
    if request.method == 'POST':
        session.delete()
        return redirect('ai_tutor:session_list')
    
    return render(request, 'ai_tutor/delete_session.html', {'session': session})

@login_required
def chat_view(request, session_id):
    """Main chat interface for interacting with the AI tutor."""
    session = get_object_or_404(TutorSession, id=session_id, user=request.user)
    
    # Get chat messages excluding system messages
    messages = session.messages.exclude(message_type='system').order_by('created_at')
    
    # Get context items
    context_items = session.get_context_items()
    
    # Get related course objects for navigation
    course = session.course
    module = session.module
    content = session.content
    
    # If the session is associated with a course, get related content
    if course:
        modules = course.modules.all().order_by('order')
        course_name = course.title
    else:
        modules = []
        course_name = "General Session"
    
    # If in a module, get its contents
    if module:
        contents = module.contents.all().order_by('order')
        module_name = module.title
    else:
        contents = []
        module_name = ""
    
    context = {
        'session': session,
        'messages': messages,
        'context_items': context_items,
        'course': course,
        'module': module,
        'content': content,
        'modules': modules,
        'contents': contents,
        'course_name': course_name,
        'module_name': module_name,
        'content_name': content.title if content else "",
    }
    
    return render(request, 'ai_tutor/chat.html', context)

@login_required
@require_POST
def send_message(request, session_id):
    """Handle sending a message to the AI tutor and getting a response."""
    session = get_object_or_404(TutorSession, id=session_id, user=request.user)
    
    message = request.POST.get('message', '').strip()
    if not message:
        return HttpResponseBadRequest("Message cannot be empty")
    
    try:
        with transaction.atomic():
            # Generate assistant response
            assistant_message = TutorService.generate_assistant_response(session, message)
            
            # Return both messages formatted for display
            return JsonResponse({
                'success': True,
                'user_message': {
                    'content': message,
                    'timestamp': assistant_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                },
                'assistant_message': {
                    'content': assistant_message.content,
                    'timestamp': assistant_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
            })
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': "An error occurred while processing your message."
        }, status=500)

@login_required
def manage_context(request, session_id):
    """Manage context items for a session."""
    session = get_object_or_404(TutorSession, id=session_id, user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            # Add a new context item
            title = request.POST.get('title')
            content = request.POST.get('content')
            
            if title and content:
                TutorContextItem.objects.create(
                    session=session,
                    context_type='custom',
                    title=title,
                    content=content,
                    order=session.context_items.count()
                )
        
        elif action == 'remove':
            # Remove a context item
            item_id = request.POST.get('item_id')
            if item_id:
                item = get_object_or_404(TutorContextItem, id=item_id, session=session)
                item.delete()
        
        elif action == 'reorder':
            # Reorder context items
            order_data = request.POST.get('order_data')
            if order_data:
                try:
                    order_dict = json.loads(order_data)
                    for item_id, new_order in order_dict.items():
                        TutorContextItem.objects.filter(id=item_id, session=session).update(order=new_order)
                except json.JSONDecodeError:
                    pass
    
    context_items = session.get_context_items()
    
    return render(request, 'ai_tutor/manage_context.html', {
        'session': session,
        'context_items': context_items,
    })

@login_required
def course_tutor(request, course_slug):
    """Start a tutor session for a specific course."""
    course = get_object_or_404(Course, slug=course_slug)
    
    # Create a new session or get existing one
    session = TutorSession.objects.filter(
        user=request.user,
        course=course,
        module=None,
        content=None,
        is_active=True
    ).first()
    
    if not session:
        session = TutorService.create_session(
            user=request.user,
            course=course,
            session_type='course'
        )
    
    return redirect('ai_tutor:chat', session_id=session.id)

@login_required
def module_tutor(request, course_slug, module_order):
    """Start a tutor session for a specific module."""
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, course=course, order=module_order)
    
    # Create a new session or get existing one
    session = TutorSession.objects.filter(
        user=request.user,
        course=course,
        module=module,
        content=None,
        is_active=True
    ).first()
    
    if not session:
        session = TutorService.create_session(
            user=request.user,
            course=course,
            module=module,
            session_type='module'
        )
    
    return redirect('ai_tutor:chat', session_id=session.id)

@login_required
def content_tutor(request, course_slug, module_order, content_order):
    """Start a tutor session for specific content."""
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, course=course, order=module_order)
    content = get_object_or_404(Content, module=module, order=content_order)
    
    # Create a new session or get existing one
    session = TutorSession.objects.filter(
        user=request.user,
        course=course,
        module=module,
        content=content,
        is_active=True
    ).first()
    
    if not session:
        session = TutorService.create_session(
            user=request.user,
            course=course,
            module=module,
            content=content,
            session_type='content'
        )
    
    return redirect('ai_tutor:chat', session_id=session.id)

# API Endpoints

@login_required
@csrf_exempt
def api_sessions(request):
    """API endpoint for session management."""
    if request.method == 'GET':
        # List sessions
        sessions = TutorSession.objects.filter(user=request.user).order_by('-updated_at')
        return JsonResponse({
            'sessions': [
                {
                    'id': session.id,
                    'title': session.title,
                    'type': session.session_type,
                    'is_active': session.is_active,
                    'updated_at': session.updated_at.isoformat(),
                    'course': session.course.title if session.course else None,
                    'module': session.module.title if session.module else None,
                    'content': session.content.title if session.content else None,
                }
                for session in sessions
            ]
        })
    
    elif request.method == 'POST':
        # Create new session
        try:
            data = json.loads(request.body)
            
            course_id = data.get('course_id')
            module_id = data.get('module_id')
            content_id = data.get('content_id')
            title = data.get('title', '')
            session_type = data.get('session_type', 'general')
            
            course = None
            module = None
            content = None
            
            if content_id:
                content = get_object_or_404(Content, id=content_id)
                module = content.module
                course = module.course
            elif module_id:
                module = get_object_or_404(Module, id=module_id)
                course = module.course
            elif course_id:
                course = get_object_or_404(Course, id=course_id)
            
            session = TutorService.create_session(
                user=request.user,
                course=course,
                module=module,
                content=content,
                title=title,
                session_type=session_type
            )
            
            return JsonResponse({
                'id': session.id,
                'title': session.title,
                'chat_url': reverse('ai_tutor:chat', args=[session.id])
            })
        
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
@csrf_exempt
def api_chat(request, session_id):
    """API endpoint for chat functionality."""
    session = get_object_or_404(TutorSession, id=session_id, user=request.user)
    
    if request.method == 'GET':
        # Get chat history
        messages = session.messages.exclude(message_type='system').order_by('created_at')
        return JsonResponse({
            'messages': [
                {
                    'id': message.id,
                    'type': message.message_type,
                    'content': message.content,
                    'timestamp': message.created_at.isoformat(),
                }
                for message in messages
            ]
        })
    
    elif request.method == 'POST':
        # Send a message
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
            # Generate assistant response
            assistant_message = TutorService.generate_assistant_response(session, message)
            
            return JsonResponse({
                'id': assistant_message.id,
                'content': assistant_message.content,
                'timestamp': assistant_message.created_at.isoformat(),
            })
        
        except Exception as e:
            logger.error(f"Error in API chat: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)