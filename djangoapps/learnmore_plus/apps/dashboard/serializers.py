from rest_framework import serializers
from .models import UserActivity

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ['id', 'user', 'action', 'timestamp', 'ip_address', 'user_agent', 'details']
        read_only_fields = ['id', 'timestamp'] 