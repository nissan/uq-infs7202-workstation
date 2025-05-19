from django.shortcuts import render
from django.views.generic import DetailView
from .models import Module, Quiz

class ModuleDetailView(DetailView):
    model = Module
    template_name = 'courses/module_detail.html'

class QuizDetailView(DetailView):
    model = Quiz
    template_name = 'courses/quiz_detail.html'