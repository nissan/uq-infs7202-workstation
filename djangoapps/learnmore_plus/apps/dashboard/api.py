from rest_framework import viewsets, permissions
from .models import UserActivity
from .serializers import UserActivitySerializer

class UserActivityViewSet(viewsets.ModelViewSet):
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserActivity.objects.all()
        return UserActivity.objects.filter(user=user) 