from rest_framework import serializers
from .models import Progress

class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Progress.objects.all(),
                fields=['user', 'course'],
                message="A progress record for this user and course already exists."
            )
        ]
        
    def validate_completed_lessons(self, value):
        if value < 0:
            raise serializers.ValidationError("Completed lessons cannot be negative.")
        return value
        
    def validate_total_lessons(self, value):
        if value < 0:
            raise serializers.ValidationError("Total lessons cannot be negative.")
        return value