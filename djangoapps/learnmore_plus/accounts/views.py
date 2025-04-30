from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.backends import ModelBackend

# Create your views here.

def register(request):
    """
    View for user registration.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Authenticate the user with the default backend
            user = authenticate(
                request,
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password1'),
                backend='django.contrib.auth.backends.ModelBackend'
            )
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, 'Registration successful!')
                return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """
    View for user login.
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
