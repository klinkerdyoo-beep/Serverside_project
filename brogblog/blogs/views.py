from django.shortcuts import render, redirect,  get_object_or_404
from django.views import View
from django.views.generic import DetailView
from django.db.models import Count, Value
from django.db.models.functions import Concat
from django.http import JsonResponse
import json

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import *
from blogs.models import *
from tags.models import *
from accounts.models import User

from .forms import CommentForm

from django.contrib.auth import get_user_model


from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpRequest

from django.db import transaction

from brogblog.settings import LOGIN_URL

class HomeView(View):
    def get(self, request):
        # search_query = request.GET.get('search', '').strip()
        # categories = Category.objects.filter(name__icontains=search_query) if search_query else []
        # blogs = Blog.objects.filter(header__icontains=search_query) if search_query else []
        categories = Category.objects.all()

        
        context = {
            'categories': categories,
            # 'blogs': blogs,
            # 'search_query': search_query,
        }
        return render(request, 'home.html', context)
    
class CreateBlogView(View):
    permission_required = ["blogs.add_blog"]
    login_url = LOGIN_URL

    def get(self, request: HttpRequest):
        return render(request, "create_blog.html")
    
    
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
        # ส่ง blog เข้า template
        context = {
            'blog': blog,
            'user': blog.user,
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
         # ดึง blog ที่กำลังดูอยู่
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
        
        # อัปเดต likes
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

# class CategoryDetailView(View):

#     def get(self, request, name):  # ต้องมี self
#         category = get_object_or_404(Category, name=name)
#         # ดึง post ที่เกี่ยวข้องกับ category
#         posts = category.blog_set.all()  # สมมติ relation เป็น blog_set
#         return render(request, 'category_detail.html', {'category': category, 'posts': posts})