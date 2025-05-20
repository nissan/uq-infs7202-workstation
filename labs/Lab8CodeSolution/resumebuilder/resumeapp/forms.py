
from django import forms
from django.contrib.auth.models import User
from .models import UserDetail

class UserDetailFullForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserDetail
        fields = ['firstname', 'surname', 'mobileno']
        widgets = {
            'firstname': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'mobileno': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        # Extract the user-related fields
        username = self.cleaned_data.pop("username")
        password = self.cleaned_data.pop("password")
        email = self.cleaned_data.pop("email")

        # Create the user
        user = User.objects.create_user(username=username, password=password, email=email)

        # Create the user detail object
        user_detail = super().save(commit=False)
        user_detail.user = user

        if commit:
            user_detail.save()

        return user_detail
"""
from allauth.socialaccount.forms import SignupForm  # SOCIAL signup form

class CustomSocialSignupForm(SignupForm):
    firstname = forms.CharField(max_length=100, label='First Name', required=True)
    surname = forms.CharField(max_length=100, label='Surname', required=True)
    mobileno = forms.CharField(max_length=15, label='Mobile Number', required=False)
    bio = forms.CharField(widget=forms.Textarea, label='Bio', required=False, initial="Enter the bio for your Resume")

    def __init__(self, *args, **kwargs):
        print("✅ CustomSocialSignupForm __init__ called")
        self.sociallogin = kwargs['sociallogin']
        super().__init__(*args, **kwargs)

        extra_data = self.sociallogin.account.extra_data
        self.fields['firstname'].initial = extra_data.get('given_name', '')
        self.fields['surname'].initial = extra_data.get('family_name', '')
        self.fields['bio'].initial = "Welcome to my resume!"

    def save(self, request):
        print("✅ CustomSocialSignupForm save() called")
        user = super().save(request)

        user_detail = UserDetail.objects.create(
            user=user,
            firstname=self.cleaned_data['firstname'],
            surname=self.cleaned_data['surname'],
            mobileno=self.cleaned_data.get('mobileno'),
            bio=self.cleaned_data.get('bio', "Novice Django Developer"),
        )

        return user
"""