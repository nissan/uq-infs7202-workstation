from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Module, Quiz, Course
from .serializers import ModuleSerializer, QuizSerializer

class ModuleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing course modules.
    Instructors can perform all operations.
    Students can only view modules for courses they're enrolled in.
    """
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.is_instructor:
            # Instructors can see all modules
            return Module.objects.all()
        else:
            # Students can only see modules for courses they're enrolled in
            return Module.objects.filter(course__enrollments__user=user, course__status='published')
    
    def perform_create(self, serializer):
        # Ensure the user is an instructor and the course belongs to them
        course_id = self.request.data.get('course')
        if course_id:
            course = Course.objects.get(id=course_id)
            if course.instructor != self.request.user:
                raise PermissionDenied("You can only create modules for your own courses")
        serializer.save(course_id=course_id)

class QuizViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing quizzes.
    Instructors can perform all operations.
    Students can only view quizzes for modules they have access to.
    """
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.is_instructor:
            # Instructors can see all quizzes
            return Quiz.objects.all()
        else:
            # Students can only see quizzes for modules in courses they're enrolled in
            return Quiz.objects.filter(module__course__enrollments__user=user, module__course__status='published')
    
    def perform_create(self, serializer):
        # Ensure the user is an instructor and the module belongs to their course
        module_id = self.request.data.get('module')
        if module_id:
            module = Module.objects.get(id=module_id)
            if module.course.instructor != self.request.user:
                raise PermissionDenied("You can only create quizzes for your own courses")
        serializer.save()