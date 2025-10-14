from django import forms
from .models import *

from django.contrib.auth.models import User as AuthUser, Group
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login

from django.forms import ModelForm, ValidationError, FileInput
from django.core.validators import RegexValidator

from utils.tailwinds import *

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
    
class EditProfileForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": FIELD_WIDE_INPUT_CLASSES,
            "placeholder": "Enter your new username",
            "readonly": True,
            "onfocus": "this.removeAttribute('readonly');",
            })
        )
    bio = forms.CharField(widget=forms.Textarea(attrs={
            "class": FIELD_TEXTAREA_CLASSES,
            "id": "id_body",
            "placeholder": "Space for introducing yourself",
            "rows": "5",
        }), required = False)
    
    profile_path = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={"class": "hidden"})
    )

    email = forms.EmailField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": FIELD_LONG_INPUT_CLASSES,
            "readonly": True
            })
        )
    
    current_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": FIELD_INPUT_CLASSES,
            "placeholder": "Enter your current password",
            "readonly": True,
            "onfocus": "this.removeAttribute('readonly');",
        }),
        label="Current password"
    )
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": FIELD_INPUT_CLASSES,
            "placeholder": "Enter your new password"
        }),
        label="New password"
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": FIELD_INPUT_CLASSES,
            "placeholder": "Confirm your new password"
        }),
        label="Confirm new password"
    )

    class Meta:
        model = User
        fields = ['profile_path', 'bio']
        
    # for linking to auth
    def __init__(self, *args, **kwargs):
        self.auth_user_instance = kwargs.pop('auth_user_instance', None)
        super().__init__(*args, **kwargs)
        if self.auth_user_instance:
            self.fields['username'].initial = self.auth_user_instance.username
            self.fields['email'].initial = self.auth_user_instance.email

    def clean(self):
        cleaned_data = super().clean()
        current = cleaned_data.get('current_password')
        new = cleaned_data.get('new_password')
        confirm = cleaned_data.get('confirm_password')

        if new or confirm:
            if not current:
                self.add_error('current_password', "Please enter your current password.")
            elif not self.auth_user_instance.check_password(current):
                # check password input-db
                self.add_error('current_password', "Current password is incorrect.")
            if new != confirm:
                self.add_error('confirm_password', "New passwords do not match.")

        return cleaned_data

    # ลองย้ายมาทำในไฟล์นี้อ่ะ
    def save(self, commit=True):
        profile = super().save(commit=False)

        if self.auth_user_instance:
            self.auth_user_instance.username = self.cleaned_data['username']
            self.auth_user_instance.email = self.cleaned_data['email']

            new_password = self.cleaned_data.get('new_password')
            if new_password:
                self.auth_user_instance.set_password(new_password)

            self.auth_user_instance.save()

        if commit:
            profile.save()
        return profile
