from django.shortcuts import render
from django.views.generic import DetailView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Module, Quiz, Course
from .serializers import CourseSerializer

class ModuleDetailView(DetailView):
    model = Module
    template_name = 'courses/module_detail.html'

class QuizDetailView(DetailView):
    model = Quiz
    template_name = 'courses/quiz_detail.html'

class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]