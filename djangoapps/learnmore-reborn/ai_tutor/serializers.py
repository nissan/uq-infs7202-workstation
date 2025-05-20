from rest_framework import serializers
from .models import TutorSession, TutorMessage, TutorKnowledgeBase, TutorFeedback, TutorConfiguration

class TutorKnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorKnowledgeBase
        fields = ['id', 'title', 'content', 'course', 'module', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class TutorMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorMessage
        fields = ['id', 'session', 'message_type', 'content', 'metadata', 'created_at']
        read_only_fields = ['created_at']

class TutorMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorMessage
        fields = ['session', 'message_type', 'content', 'metadata']
        
class TutorSessionSerializer(serializers.ModelSerializer):
    messages = TutorMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = TutorSession
        fields = ['id', 'user', 'course', 'module', 'quiz', 'title', 'status', 
                  'session_context', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['created_at', 'updated_at']

class TutorSessionListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TutorSession
        fields = ['id', 'user', 'title', 'status', 'created_at', 'updated_at', 'message_count']
        read_only_fields = ['created_at', 'updated_at', 'message_count']
    
    def get_message_count(self, obj):
        return obj.messages.count()

class TutorSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorSession
        fields = ['user', 'course', 'module', 'quiz', 'title', 'session_context']

class TutorFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorFeedback
        fields = ['id', 'session', 'user', 'message', 'rating', 'comment', 'helpful', 'created_at']
        read_only_fields = ['created_at']

class TutorConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorConfiguration
        fields = ['id', 'name', 'model_provider', 'model_name', 'temperature', 
                  'max_tokens', 'system_prompt', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']