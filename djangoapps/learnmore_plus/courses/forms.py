from django import forms
from django.forms import inlineformset_factory
from .models import Quiz, Question, Choice

class QuizForm(forms.ModelForm):
    """Form for creating and editing quizzes"""
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'passing_score', 'time_limit', 
                 'attempts_allowed', 'shuffle_questions', 'show_correct_answers']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'time_limit': forms.NumberInput(attrs={'min': 1}),
            'attempts_allowed': forms.NumberInput(attrs={'min': 0}),
            'passing_score': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }

class QuestionForm(forms.ModelForm):
    """Form for creating and editing questions"""
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'points', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3}),
            'points': forms.NumberInput(attrs={'min': 1}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }

class ChoiceForm(forms.ModelForm):
    """Form for creating and editing choices"""
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct', 'order']
        widgets = {
            'choice_text': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }

# Create a formset for choices
ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    form=ChoiceForm,
    extra=4,  # Number of empty forms to display
    can_delete=True,
    min_num=2,  # Minimum number of forms required
    validate_min=True,
) 