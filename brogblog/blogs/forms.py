from django.forms import ModelForm, SplitDateTimeField
from django.forms.widgets import Textarea, TextInput, SplitDateTimeWidget
from django.core.exceptions import ValidationError
from django import forms
from .models import *

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = [
            "comment_text",
        ]