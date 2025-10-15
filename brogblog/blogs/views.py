from django.shortcuts import render, redirect,  get_object_or_404
from django.views import View
from django.views.generic import DetailView
from django.db.models import Count, Value
from django.db.models.functions import Concat
from django.http import JsonResponse
import json

from django.contrib import messages

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from rest_framework import status

from .models import *
from blogs.models import *
from tags.models import *
from accounts.models import User
from reports.models import *

from .forms import CommentForm

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

from django.utils import timezone
from datetime import timedelta

from google.cloud import translate_v2 as translate

def is_my_blog(user, author):
    if user == author:
        return True
    return False

translate_client = translate.Client()

def translate_blog(request, blog_id):
    target_lang = "en"
    try:
        blog = Blog.objects.get(pk=blog_id)
    except Blog.DoesNotExist:
        return JsonResponse({"error": "Blog not found"}, status=404)


    translated_header = translate_client.translate(
        blog.header or "", target_language=target_lang
    )["translatedText"]
    translated_body = translate_client.translate(
        blog.body or "", target_language=target_lang
    )["translatedText"]

    return JsonResponse({
        "blog_id": blog.blog_id,
        "header": translated_header,
        "body": translated_body,
    })

class HomeView(View):
    def get(self, request):
        # search_query = request.GET.get('search', '').strip()
        # categories = Category.objects.filter(name__icontains=search_query) if search_query else []
        blogs = Blog.objects.annotate(num_comments=Count("comment")).filter(blogstatus__status = "public" )
        categories = Category.objects.all()
    
        
        context = {
            'categories': categories,
            'blogs': blogs,
            # 'search_query': search_query,
        }
        return render(request, 'home.html', context)
    
class CreateBlogView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ["blogs.add_blog"]
    login_url = settings.LOGIN_URL

    def get(self, request: HttpRequest):
        blogform = BlogForm()
        imgform = BlogImageForm()
        catform = CategoryForm()

        blog_status = BlogStatus.objects.all()
        cat_list = Category.objects.all()
        context = {
            "status": blog_status,
            "category": cat_list,
            "blogform": blogform,
            "imgform": imgform,
            "catform": catform,
        }
        return render(request, "create_blog.html", context)
    
    def post(self, request):
        blogform = BlogForm(request.POST)
        catform = CategoryForm(request.POST)
        imgform = BlogImageForm(request.POST, request.FILES)
        action = request.POST.get('action')
        blog_user = User.objects.get(auth_user=request.user)
        try:
            with transaction.atomic():
                if blogform.is_valid() and imgform.is_valid() and catform.is_valid():

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

                    category = catform.cleaned_data.get('category')
                    cat_name = category.name.strip() if category else None
                    print(cat_name)

                    tag_names = blogform.cleaned_data.get('tags', [])
                    if cat_name and cat_name not in tag_names:
                        tag_names.append(cat_name)

                    for name in tag_names:
                        if not name:
                            continue
                        tag, created = Tag.objects.get_or_create(
                            name=name,
                            defaults={'category': category}
                        )
                        if tag.category is None and category:
                            tag.category = category
                            tag.save()

                        BlogTag.objects.get_or_create(blog=blog, tag=tag)
                    print("sucessfully posted")
                    return redirect('home')
                
                else:
                    print("raise error")
                    raise transaction.TransactionManagementError("Error")
        except Exception as e:
            print("exceptional", e)
            return render(request, "create_blog.html", {
                "blogform": blogform,
                "imgform": imgform,
                "catform": catform,
            })
    
    
class BlogDetailView(View):
    
    def get(self, request, blog_id):
        # ดึง Blog ตาม ID หรือ 404 ถ้าไม่มี
        blog = get_object_or_404(Blog, pk=blog_id)
        categories = Category.objects.all()
        tags2 = Tag.objects.filter(blogtag__blog=blog)
        categories2 = Category.objects.filter(tag__in=tags2).distinct()


        bookmarked = False
        if request.user.is_authenticated:
            user = request.user.user  # custom User
            bookmarked = blog in user.bookmarked_posts.all()

        # รับ query param สำหรับ filter
        sort_by = request.GET.get("sort")  # 'latest' หรือ 'popular'
        comments = Comment.objects.filter(blog=blog, parent__isnull=True)

        if sort_by == 'latest':
            comments = comments.order_by("-created_date")
        elif sort_by == 'popular':
            comments = comments.order_by("-likes")
        else:
            comments = comments.order_by("-created_date")  # default

         # ฟอร์มคอมเมนต์เปล่า (สำหรับแสดงในหน้า)
        comment_form = CommentForm()

        context = {
            'blog': blog,
            'users': blog.user,
            'comments' : comments,
            'categories' : categories,
            'tags2' : tags2,
            'categories2' : categories2,
            'comment_form' : comment_form ,
            "sort_by": sort_by,
            'bookmark_count': blog.bookmarked_by.count(),
            'bookmarked': bookmarked,
        }
        return render(request, "blog-detail.html", context)
    
    def post(self, request, blog_id):

        blog = get_object_or_404(Blog, pk=blog_id)
        parent_id = request.POST.get("parent_id")

        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            # สร้าง comment object แต่ยังไม่ save
            new_comment = comment_form.save(commit=False)

            if request.user.is_authenticated:
                new_comment.user = request.user.user  # <--- custom User instance
            else:
                return redirect('login')
            
            new_comment.blog = blog           # ผูกกับ blog ปัจจุบัน

            if parent_id:
                parent_comment = Comment.objects.filter(pk=parent_id).first()
                if parent_comment:
                    new_comment.parent = parent_comment

            new_comment.save()                # บันทึกลงฐานข้อมูล
            return redirect('blog-detail', blog_id=blog.blog_id)
        
        if not comment_form.is_valid():
            print(comment_form.errors)  # ดูว่ามี error ออกมารึเปล่า   
    
class BlogLikeView(View):

    def post(self, request, blog_id):
        blog = get_object_or_404(Blog, pk=blog_id)
        data = json.loads(request.body.decode('utf-8'))
        action = data.get('action')
        
        
        if action == 'like':
            blog.likes += 1
        elif action == 'unlike' and blog.likes > 0:
            blog.likes -= 1

        blog.save()
        
        return JsonResponse({"likes": blog.likes})
    

@method_decorator(csrf_exempt, name='dispatch')
class CommentLikeView(View):
    def post(self, request, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Comment not found'}, status=404)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        action = data.get('action')
        if action == 'like':
            comment.likes += 1
        elif action == 'unlike' and comment.likes > 0:
            comment.likes -= 1
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

        comment.save()
        return JsonResponse({'likes': comment.likes})

class BlogBookmarkToggleView(View):
    def post(self, request, blog_id):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=403)

        blog = get_object_or_404(Blog, pk=blog_id)
        user = request.user.user  # custom User model

        if blog in user.bookmarked_posts.all():
            user.bookmarked_posts.remove(blog)
            bookmarked = False
        else:
            user.bookmarked_posts.add(blog)
            bookmarked = True

        return JsonResponse({
            'bookmarked': bookmarked,
            'bookmark_count': blog.bookmarked_by.count()
        })
    
class ReportBlogView(View):
    def post(self, request, blog_id):
        # ตรวจว่า blog มีอยู่จริง
        blog = get_object_or_404(Blog, pk=blog_id)

        # ดึงค่าจาก POST
        reason = request.POST.get('reason', '').strip()
        if not reason:
            return JsonResponse({'error': 'Please provide a reason.'}, status=400)

        # แปลง request.user เป็น accounts.User instance
        reporter = User.objects.get(auth_user=request.user)

        # สร้าง ReportBlog
        ReportBlog.objects.create(
            reporter=reporter,
            blog=blog,
            reason=reason,
            # status เป็น default 'pending', handled_by เป็น null
        )

        return JsonResponse({'success': 'Reported successfully'})

class DeleteBlogView(LoginRequiredMixin, View):
    
    login_url = '/authen/login/'
    
    def get(self, request: HttpRequest, blog_id):
        blog = get_object_or_404(Blog, pk=blog_id)

        print("Logged-in user:", request.user)
        print("Blog owner auth_user:", blog.user.auth_user)
        
        if blog.user.auth_user != request.user:
            raise PermissionDenied("Only for the blog owner.")
        

        blog.delete()
        return redirect('home')
    

class CategoryDetailView(View):

    def get(self, request, name, tag_id=None):
        category = get_object_or_404(Category, name=name)
        tags = Tag.objects.filter(category = category)
        if tag_id:
            # ถ้าเลือก tag เฉพาะ
            blogtags = BlogTag.objects.filter(tag_id=tag_id)
            blogs = [bt.blog for bt in blogtags]
        else:
            # แสดงทุก blog ของ category
            blogtags = BlogTag.objects.filter(tag__category=category)
            blogs = list({bt.blog for bt in blogtags})  # set เพื่อไม่ให้ซ้ำ

        return render(request, 'category_detail.html', {
            'category': category,
            'tags': tags,
            'blogs': blogs,
            'selected_tag_id': tag_id
        })