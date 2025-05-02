from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from .models import UserProfile
from .forms import UserRegistrationForm, UserProfileForm, AvatarUploadForm
from .decorators import group_required

# Create your views here.

def register(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            profile = UserProfile.objects.create(user=user)
            # Add to Student group by default
            student_group = Group.objects.get(name='Student')
            user.groups.add(student_group)
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """
    View for user login.
    Redirects users to their appropriate dashboard based on their group membership.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                # Redirect based on user's group membership
                if user.groups.filter(name='Administrator').exists():
                    return redirect('courses:admin_dashboard')
                elif user.groups.filter(name='Course Coordinator').exists():
                    return redirect('courses:coordinator_dashboard')
                elif user.groups.filter(name='Instructor').exists():
                    return redirect('courses:instructor_dashboard')
                elif user.groups.filter(name='Student').exists():
                    return redirect('courses:student_dashboard')
                else:
                    # Default to home page if no specific group is assigned
                    return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """
    Custom view for user logout that ensures messages are cleared.
    """
    # Clear any existing messages
    storage = FallbackStorage(request)
    storage.used = True
    
    # Perform logout
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    """User profile view."""
    profile = request.user.profile
    return render(request, 'accounts/profile.html', {'profile': profile})

@login_required
def profile_edit(request):
    """Edit user profile view."""
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form})

@login_required
def avatar_upload(request):
    """Upload user avatar view."""
    profile = request.user.profile
    if request.method == 'POST':
        form = AvatarUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Avatar updated successfully!')
            return redirect('accounts:profile')
    else:
        form = AvatarUploadForm(instance=profile)
    return render(request, 'accounts/avatar_upload.html', {'form': form})

@group_required(['Administrator', 'Course Coordinator'])
def group_list(request):
    """List all groups view."""
    groups = Group.objects.all()
    return render(request, 'accounts/group_list.html', {'groups': groups})

@group_required(['Administrator', 'Course Coordinator'])
def group_detail(request, group_id):
    """Group detail view."""
    group = get_object_or_404(Group, id=group_id)
    return render(request, 'accounts/group_detail.html', {'group': group})

@group_required(['Administrator'])
def group_edit(request, group_id):
    """Edit group view."""
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        # Handle group update
        name = request.POST.get('name')
        permissions = request.POST.getlist('permissions')
        
        group.name = name
        group.permissions.set(permissions)
        group.save()
        
        messages.success(request, 'Group updated successfully!')
        return redirect('accounts:group_detail', group_id=group.id)
        
    permissions = Permission.objects.all()
    return render(request, 'accounts/group_edit.html', {
        'group': group,
        'permissions': permissions
    })

@group_required(['Administrator'])
def group_members(request, group_id):
    """Manage group members view."""
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        # Handle members update
        members = request.POST.getlist('members')
        group.user_set.set(members)
        messages.success(request, 'Group members updated successfully!')
        return redirect('accounts:group_detail', group_id=group.id)
        
    users = UserProfile.objects.all()
    return render(request, 'accounts/group_members.html', {
        'group': group,
        'users': users
    })
