from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Progress
from .serializers import ProgressSerializer

class ProgressViewSet(viewsets.ModelViewSet):
    serializer_class = ProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Users can only see their own progress"""
        return Progress.objects.filter(user=self.request.user)