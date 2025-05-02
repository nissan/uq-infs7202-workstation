from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from .models import (
    Category, Course, Module, Content, Quiz, Question, Choice,
    CourseEnrollment, ModuleProgress, QuizAttempt
)
from .serializers import (
    CategorySerializer, CourseSerializer, ModuleSerializer, ContentSerializer,
    QuizSerializer, QuestionSerializer, ChoiceSerializer, CourseEnrollmentSerializer,
    ModuleProgressSerializer, QuizAttemptSerializer, UserSerializer
)
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_400_BAD_REQUEST

User = get_user_model()

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            # Generate slug from name if not provided
            name = request.data.get('name')
            if not name:
                return Response({'detail': 'Name is required'}, status=HTTP_400_BAD_REQUEST)
                
            slug = request.data.get('slug', slugify(name))
            
            # Check for existing categories within transaction
            if Category.objects.filter(name__iexact=name).exists():
                return Response({'detail': f'Category with name "{name}" already exists'}, status=HTTP_400_BAD_REQUEST)
            
            if Category.objects.filter(slug=slug).exists():
                return Response({'detail': f'Category with slug "{slug}" already exists'}, status=HTTP_400_BAD_REQUEST)
            
            # Add slug to request data
            request.data['slug'] = slug
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'detail': str(e)}, status=HTTP_400_BAD_REQUEST)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Course.objects.all()
        return Course.objects.filter(
            Q(instructors=user) |
            Q(coordinator=user) |
            Q(enrollments__student=user)
        ).distinct()

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.request.query_params.get('course_id')
        if course_id:
            return Module.objects.filter(course_id=course_id)
        return Module.objects.none()

class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        module_id = self.request.query_params.get('module_id')
        if module_id:
            return Content.objects.filter(module_id=module_id)
        return Content.objects.none()

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        content_id = self.request.query_params.get('content_id')
        if content_id:
            return Quiz.objects.filter(content_id=content_id)
        return Quiz.objects.none()

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        quiz_id = self.request.query_params.get('quiz_id')
        if quiz_id:
            return Question.objects.filter(quiz_id=quiz_id)
        return Question.objects.none()

class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        question_id = self.request.query_params.get('question_id')
        if question_id:
            return Choice.objects.filter(question_id=question_id)
        return Choice.objects.none()

class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = CourseEnrollment.objects.all()
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CourseEnrollment.objects.all()
        return CourseEnrollment.objects.filter(student=user)

class ModuleProgressViewSet(viewsets.ModelViewSet):
    queryset = ModuleProgress.objects.all()
    serializer_class = ModuleProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        enrollment_id = self.request.query_params.get('enrollment_id')
        if enrollment_id:
            return ModuleProgress.objects.filter(enrollment_id=enrollment_id)
        return ModuleProgress.objects.none()

class QuizAttemptViewSet(viewsets.ModelViewSet):
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return QuizAttempt.objects.all()
        return QuizAttempt.objects.filter(student=user)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [permissions.IsAdminUser()] 