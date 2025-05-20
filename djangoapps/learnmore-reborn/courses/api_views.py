from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Course, Enrollment
from .serializers import CourseSerializer, CourseDetailSerializer, EnrollmentSerializer

class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow instructors to create, update, or delete courses.
    Regular users can only view courses they're enrolled in.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only instructors can create courses
        if hasattr(request.user, 'profile'):
            return request.user.profile.is_instructor
        return False
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            # Check if user is enrolled in the course or is the instructor
            return (obj.instructor == request.user or
                   Enrollment.objects.filter(user=request.user, course=obj).exists())
        
        # Only the course instructor can edit or delete
        return obj.instructor == request.user

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructorOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'start_date']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if self.action == 'catalog':
            # Only show published courses in catalog
            return Course.objects.filter(status='published')
        elif hasattr(user, 'profile') and user.profile.is_instructor:
            # Instructors can see all courses
            return Course.objects.all()
        else:
            # Regular users see courses they're enrolled in
            return Course.objects.filter(
                Q(instructor=user) | Q(enrollments__user=user)
            ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer
    
    @action(detail=False, methods=['get'])
    def catalog(self, request):
        """
        Return a list of all published courses for the catalog.
        """
        queryset = self.filter_queryset(
            Course.objects.filter(status='published')
        )
        
        # Apply filters
        enrollment_type = request.query_params.get('enrollment_type')
        if enrollment_type:
            queryset = queryset.filter(enrollment_type=enrollment_type)
            
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for courses by title or description.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Query parameter 'q' is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = Course.objects.filter(
            Q(status='published') & 
            (Q(title__icontains=query) | Q(description__icontains=query))
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, slug=None):
        """
        Enroll the current user in the course.
        """
        course = self.get_object()
        user = request.user
        
        # Check if user is already enrolled
        if Enrollment.objects.filter(user=user, course=course).exists():
            return Response(
                {"error": "You are already enrolled in this course"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if course is published
        if course.status != 'published':
            return Response(
                {"error": "You cannot enroll in an unpublished course"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if course is full
        if course.is_full:
            return Response(
                {"error": "This course has reached its maximum enrollment capacity"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if enrollment is open
        if course.enrollment_type == 'restricted':
            # Here you would implement logic for checking if user is allowed
            # to enroll in a restricted course (e.g., check invitation code)
            pass
        
        # Create enrollment
        enrollment = Enrollment.objects.create(
            user=user,
            course=course,
            status='active'
        )
        
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def unenroll(self, request, slug=None):
        """
        Unenroll the current user from the course.
        """
        course = self.get_object()
        user = request.user
        
        try:
            enrollment = Enrollment.objects.get(user=user, course=course)
            enrollment.status = 'dropped'
            enrollment.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Enrollment.DoesNotExist:
            return Response(
                {"error": "You are not enrolled in this course"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.is_instructor:
            return Enrollment.objects.all()
        return Enrollment.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Return a list of the current user's active enrollments.
        """
        enrollments = Enrollment.objects.filter(
            user=request.user,
            status='active'
        )
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """
        Return a list of the current user's completed enrollments.
        """
        enrollments = Enrollment.objects.filter(
            user=request.user,
            status='completed'
        )
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)