from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    """Form for user registration."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile."""
    class Meta:
        model = UserProfile
        fields = ('bio', 'location', 'birth_date')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class AvatarUploadForm(forms.ModelForm):
    """Form for uploading user avatar."""
    class Meta:
        model = UserProfile
        fields = ('avatar',)
        widgets = {
            'avatar': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Check file size (limit to 5MB)
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file too large (> 5MB)')
            # Check file type
            if not avatar.content_type.startswith('image/'):
                raise forms.ValidationError('File type not supported')
        return avatar 