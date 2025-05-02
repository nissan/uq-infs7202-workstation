from django import forms
from django.forms import inlineformset_factory
from .models import Quiz, Question, Choice, Course

class QuizForm(forms.ModelForm):
    """Form for creating and editing quizzes"""
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'passing_score', 'time_limit', 
                 'attempts_allowed', 'shuffle_questions', 'show_correct_answers', 'is_pre_check']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'time_limit': forms.NumberInput(attrs={'min': 1}),
            'attempts_allowed': forms.NumberInput(attrs={'min': 0}),
            'passing_score': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'is_pre_check': forms.CheckboxInput(),
        }

class QuestionForm(forms.ModelForm):
    """Form for creating and editing questions"""
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'points']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3}),
            'points': forms.NumberInput(attrs={'min': 1}),
        }

class ChoiceForm(forms.ModelForm):
    """Form for creating and editing choices"""
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct']
        widgets = {
            'choice_text': forms.TextInput(attrs={'class': 'form-control'}),
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

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title', 'slug', 'description', 'category', 'instructors', 'coordinator',
            'cover_image', 'start_date', 'end_date', 'max_students', 'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(),
        } 