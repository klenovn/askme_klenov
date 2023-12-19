from django import forms
from django.forms import ValidationError
from django.contrib.auth.models import User
from .models import Question


class LoginForm(forms.Form):
    username = forms.CharField(label='Enter username', min_length=4, max_length=30)
    password = forms.CharField(label='Password', min_length=4, max_length=30, widget=forms.PasswordInput)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_check = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def clean(self):
        password = self.cleaned_data['password']
        password_check = self.cleaned_data['password_check']

        if password != password_check:
            raise ValidationError('Passwords don\'t match')
        
    def save(self):
        self.cleaned_data.pop('password_check')
        return User.objects.create_user(**self.cleaned_data)
    

class AskForm(forms.ModelForm):
    tags = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter tags over space (e. g. python js frontend)'}))

    class Meta:
        model = Question
        fields = ['title', 'content']


class AnswerForm(forms.Form):
    content = forms.CharField(min_length=5)


class EditProfileForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=30, required=False)
    password = forms.CharField(label='Password', min_length=4, max_length=30, widget=forms.PasswordInput, required=False)
    email = forms.EmailField(required=False)
    old_password = forms.CharField(label='Enter old password', min_length=4, max_length=30, widget=forms.PasswordInput, required=False)
