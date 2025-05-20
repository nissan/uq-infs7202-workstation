from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Course
from .serializers import CourseSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter courses based on user role"""
        user = self.request.user
        if user.profile.is_instructor:
            # Instructors can see all courses
            return Course.objects.all()
        # Students can only see courses they're enrolled in
        return Course.objects.filter(progress_records__user=user).distinct()