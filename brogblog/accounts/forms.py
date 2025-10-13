from django import forms
from .models import *

from django.contrib.auth.models import User as AuthUser, Group
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login

from django.forms import ModelForm, ValidationError, FileInput
from django.core.validators import RegexValidator

from utils.tailwinds import FIELD_INPUT_CLASSES 

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": FIELD_INPUT_CLASSES,
            "id": "id_email",
            "placeholder": "Enter your email"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": FIELD_INPUT_CLASSES,
            "id": "id_password",
            "placeholder": "Enter your password"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        print(email)
        if email and password:
            try:
                findUser = User.objects.get(auth_user__email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("No account found.")

            user = authenticate(username=findUser.auth_user.username, password=password)

            if user is None:
                raise forms.ValidationError("Incorrect password.")
            cleaned_data["user"] = user

        return cleaned_data

    def get_user(self):
        return self.cleaned_data.get("user")

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, required=True,
        widget=forms.TextInput(attrs={
            "class": FIELD_INPUT_CLASSES,
            "id": "id_username",
            "placeholder": "Enter your username"
        }))
    email = forms.EmailField(required=True, 
        widget=forms.EmailInput(attrs={
            "class": FIELD_INPUT_CLASSES,
            "id": "id_email",
            "placeholder": "Enter your email"
        }))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": FIELD_INPUT_CLASSES,
            "id": "id_password",
            "placeholder": "Enter your password"
        }),
        required=True
    )

    profile_img = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={"class": "hidden"})
    )
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))
    def save(self):
        # new auth
        auth_user = AuthUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )

        # profile for auth
        user_profile = User.objects.create(
            auth_user=auth_user,
            bio=self.cleaned_data.get('bio'),
            profile_path=self.cleaned_data.get('profile_img')
        )

        return user_profile
