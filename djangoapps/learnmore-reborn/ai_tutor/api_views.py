from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TutorSession, TutorMessage, TutorKnowledgeBase, TutorFeedback, TutorConfiguration
from .serializers import (
    TutorSessionSerializer, 
    TutorSessionListSerializer,
    TutorSessionCreateSerializer,
    TutorMessageSerializer,
    TutorMessageCreateSerializer,
    TutorKnowledgeBaseSerializer,
    TutorFeedbackSerializer,
    TutorConfigurationSerializer
)

class TutorSessionViewSet(viewsets.ModelViewSet):
    queryset = TutorSession.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TutorSessionListSerializer
        elif self.action == 'create':
            return TutorSessionCreateSerializer
        return TutorSessionSerializer
    
    def get_queryset(self):
        user = self.request.user
        return TutorSession.objects.filter(user=user).order_by('-updated_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """
        Send a new message in the tutor session and get a response from the AI tutor.
        """
        session = self.get_object()
        serializer = TutorMessageCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save the user message
            user_message = serializer.save(
                session=session,
                message_type='user'
            )
            
            # Get response from LangChain service
            from .langchain_service import tutor_langchain_service
            
            # Generate response using LangChain
            response_data = tutor_langchain_service.get_tutor_response(session, user_message.content)
            
            # Create tutor response message
            tutor_response = TutorMessage.objects.create(
                session=session,
                message_type='tutor',
                content=response_data["content"],
                metadata={
                    "sources": response_data.get("sources", []),
                    **response_data.get("metadata", {})
                }
            )
            
            # Return both the user message and tutor response
            response_data = {
                'user_message': TutorMessageSerializer(user_message).data,
                'tutor_response': TutorMessageSerializer(tutor_response).data
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TutorMessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TutorMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        session_id = self.request.query_params.get('session', None)
        
        queryset = TutorMessage.objects.filter(session__user=user)
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
            
        return queryset.order_by('created_at')

class TutorKnowledgeBaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TutorKnowledgeBase.objects.all()
    serializer_class = TutorKnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.request.query_params.get('course', None)
        module_id = self.request.query_params.get('module', None)
        
        queryset = TutorKnowledgeBase.objects.all()
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
            
        if module_id:
            queryset = queryset.filter(module_id=module_id)
            
        return queryset

class TutorFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = TutorFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return TutorFeedback.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)