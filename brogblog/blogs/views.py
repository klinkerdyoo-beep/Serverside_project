from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Count, Value
from django.db.models.functions import Concat
from .models import *

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpRequest

from django.db import transaction

class HomeView(View):
    # permission_required = ["blogs.view_blog"]
    # login_url = '/authen/login/'

    def get(self, request: HttpRequest):
        return render(request, "home.html")
    