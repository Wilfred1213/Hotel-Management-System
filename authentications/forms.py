
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django.contrib.auth.forms import AuthenticationForm
from authentications.models import CustomUser

from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms import ClearableFileInput

CustomUser = get_user_model()



class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)


    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'first_name', 'last_name',
                  'password2', 'is_customer', 
                  'is_staff','address', 'photo'
                  ]

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match. Please try again.")
        if CustomUser.objects.filter(username = username).exists():
            raise forms.ValidationError("Username already exist")
        if CustomUser.objects.filter(email = email).exists():
            raise forms.ValidationError("Email already exist")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your username',
        'class': ''
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your password',
        'class': ''
    }))

    class Meta:
        fields = ['username', 'password']
        
