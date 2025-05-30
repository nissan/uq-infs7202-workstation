from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, LoginSerializer, UserProfileSerializer, GoogleAuthSerializer
from .models import UserProfile
from .forms import UserRegistrationForm, UserProfileForm

# Template-based views

@csrf_exempt
def register_view(request):
    """User registration view with form handling."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Profile is auto-created via signal
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to LearnMore.')
            return redirect('course-catalog')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

@csrf_exempt
def login_view(request):
    """User login view with form handling."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            
            # Redirect based on user role
            if user.profile.is_instructor:
                return redirect('admin:index')
            else:
                return redirect('course-catalog')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'users/login.html')

@csrf_exempt
def logout_view(request):
    """User logout view."""
    # Clear any existing messages
    storage = FallbackStorage(request)
    storage.used = True
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('course-catalog')

@csrf_exempt
@login_required
def profile_view(request):
    """View for displaying user profile."""
    return render(request, 'users/profile.html')

@csrf_exempt
@login_required
def profile_edit_view(request):
    """View for editing user profile."""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'users/profile_edit.html', {'form': form})

@csrf_exempt
def social_login_view(request, provider):
    """Redirects to the appropriate social auth provider login page."""
    if provider == 'google':
        return redirect(reverse('google_login'))
    else:
        messages.error(request, f"Login with {provider} is not supported.")
        return redirect('users:login')

# API Views

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user.profile

class GoogleAuthView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Try to find user by google_id
                profile = UserProfile.objects.get(google_id=serializer.validated_data['google_id'])
                user = profile.user
            except UserProfile.DoesNotExist:
                # Try to find user by email
                try:
                    user = User.objects.get(email=serializer.validated_data['email'])
                    # Update google_id if user exists
                    profile = user.profile
                    profile.google_id = serializer.validated_data['google_id']
                    profile.save()
                except User.DoesNotExist:
                    # Create new user
                    user = User.objects.create_user(
                        username=serializer.validated_data['email'],
                        email=serializer.validated_data['email'],
                        first_name=serializer.validated_data['first_name'],
                        last_name=serializer.validated_data['last_name']
                    )
                    profile = user.profile
                    profile.google_id = serializer.validated_data['google_id']
                    profile.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
