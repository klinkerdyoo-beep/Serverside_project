from django import forms
from django.forms import ModelForm, ValidationError, FileInput
from .models import *
from tags.models import Category, Tag
from django.contrib.auth.models import User as AuthUser
from utils.tailwinds import *


class BlogForm(forms.ModelForm):
    tags = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": FIELD_WIDE_INPUT_CLASSES,
            "id": "id_tags",
            "placeholder": "Enter tag(s)"
        }),
        required = True)
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={
            "class": "hidden",
            "id": "id_category_select",
            'x-ref': 'categorySelect'
        }),
        required = False
    )

    blogstatus = forms.ModelChoiceField(
        queryset=BlogStatus.objects.filter(status__in=['draft', 'public', 'private']),
        widget=forms.Select(attrs={
            "class": "hidden",
            "id": "id_status_select",
            'x-ref': 'statusSelect'
        }),
        required=False
    )

    header = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": FIELD_WIDE_INPUT_CLASSES,
            "id": "id_header",
            "placeholder": "Title*"
        }),
        required = True)
    
    body = forms.CharField(widget=forms.Textarea(attrs={
            "class": FIELD_TEXTAREA_CLASSES,
            "id": "id_body",
            "placeholder": "Body text(optional)"
        }), required = False)
    
    class Meta:
        model = Blog
        fields = ['header', 'body', 'tags', 'category', 'blogstatus']
        
    def clean_tags(self):
        tags_input = self.cleaned_data.get('tags', '')
        tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
        return tag_names
    
    def save(self, commit=True, user=None, status=None):
        blog = super().save(commit=False)
        if user:
            blog.user = user
        if status:
            blog.blogstatus = status

        blog.category = self.cleaned_data.get('category')

        if commit:
            blog.save()
        return blog


class BlogImageForm(forms.ModelForm):
    class Meta:
        model = BlogImage
        fields = ["image_path"]
        widgets = {
            # "image_path": FileInput(),
            "image_path": FileInput(attrs={"class": "hidden"}),
        }