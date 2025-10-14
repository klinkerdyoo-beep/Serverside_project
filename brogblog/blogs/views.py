from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Count, Value
from django.db.models.functions import Concat

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# from django.contrib.auth import get_user_model
# User = get_user_model()

from django.db import transaction

from .models import *
from tags.models import *
from blogs.forms import *
from accounts.models import *


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
    
    def post(self, request):
        blogform = BlogForm(request.POST)
        imgform = BlogImageForm(request.POST, request.FILES)
        action = request.POST.get('action')
        blog_user = User.objects.get(auth_user=request.user)
        try:
            with transaction.atomic():
                if blogform.is_valid() and imgform.is_valid():

                    blog = blogform.save(commit=False)
                    blog.user = blog_user

                    if action == 'draft':
                        blog.blogstatus = BlogStatus.objects.get(status='draft')
                    else:
                        blog.blogstatus = BlogStatus.objects.get(status='public')

                    blog.save()

                    blogimg = imgform.save(commit=False)
                    blogimg.blog = blog
                    blogimg.save()

                    tag_names = blogform.cleaned_data['tags']
                    if blog.category:
                        cat_name = blog.category.name.strip()
                        if cat_name not in tag_names:
                            tag_names.append(cat_name)

                    for name in tag_names:
                        tag, created = Tag.objects.get_or_create(
                            name=name,
                            defaults={'category': blog.category}
                        )
                        BlogTag.objects.get_or_create(blog=blog, tag=tag)
                    return redirect('home')
                
                else:
                    raise transaction.TransactionManagementError("Error")
        except Exception as e:
            print("exceptional", e)
            return render(request, "create_blog.html", {
                "blogform": blogform,
                "imgform": imgform,
            })
    