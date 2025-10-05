from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Count, Value
from django.db.models.functions import Concat
from .models import *

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.db import transaction

class StudentView(View):

    def get(self, request):
        
        return render(request, "neoy_havepic.html")
    