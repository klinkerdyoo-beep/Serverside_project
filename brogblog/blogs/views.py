from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Count, Value
from django.db.models.functions import Concat

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpRequest

from django.db import transaction

from .models import *
from tags.models import *
from blogs.forms import *

class HomeView(View):
    # permission_required = ["blogs.view_blog"]
    # login_url = '/authen/login/'

    def get(self, request: HttpRequest):
        return render(request, "home.html")
class CreateBlogView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ["blogs.add_blog"]
    login_url = settings.LOGIN_URL

    def get(self, request: HttpRequest):
        blogform = BlogForm()
        imgform = BlogImageForm()
        blog_status = BlogStatus.objects.all()
        cat_list = Category.objects.all()
        context = {
            "status": blog_status,
            "category": cat_list,
            "blogform": blogform,
            "imgform": imgform,
        }
        return render(request, "create_blog.html", context)
    