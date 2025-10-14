from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth import logout, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.db import transaction
from django.http import JsonResponse

from .forms import *
from .models import *
from blogs.models import *
from tags.models import *
from accounts.models import User

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {"form": form})
    
    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request,user)
            return redirect('home')  

        return render(request,'login.html', {"form":form})
    
class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'register.html', {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user_profile = form.save()
                    auth_user = user_profile.auth_user

                    # Add member role
                    member_group, _ = Group.objects.get_or_create(name="member")
                    auth_user.groups.add(member_group)

                    login(request, auth_user)
                    return redirect('home')

            except Exception as e:
                # fix exception: duplicate key value violates unique constraint "auth_user_pkey"
                if "duplicate key value" in str(e):
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT setval(
                                pg_get_serial_sequence('auth_user','id'),
                                COALESCE((SELECT MAX(id) FROM auth_user), 1) + 1,
                                false
                            );
                        """)
                    # retry register
                    try:
                        user_profile = form.save()
                        auth_user = user_profile.auth_user
                        member_group, _ = Group.objects.get_or_create(name="member")
                        auth_user.groups.add(member_group)
                        login(request, auth_user)
                        return redirect('home')
                    except Exception as e2:
                        print("retry failed:", e2)
                        return render(request, 'register.html', {"form": form})
                else:
                    print("exception:", e)
                    return render(request, 'register.html', {"form": form})
        else:
            print("form not valid")
            return render(request, 'register.html', {"form": form})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    
class MyAccountView(LoginRequiredMixin, View):
    def get(self, request):
        # ดึง user ปัจจุบัน (custom user)
        user = request.user.user  

        # Blog ที่ user สร้างเอง
        user_blogs = Blog.objects.filter(user=user).order_by('-created_date')

        # Blog ที่ user bookmark ไว้
        bookmarked_blogs = user.bookmarked_posts.all().order_by('-created_date')

        # ความคิดเห็นทั้งหมดที่ user เคยเขียน
        user_comments = Comment.objects.filter(user=user).select_related('blog').order_by('-created_date')

        # Blog ที่ user เคยดู (ถ้ามีการเก็บใน model เช่น BlogViewHistory)
        # ถ้ายังไม่มี model นั้น สามารถละส่วนนี้ไว้ก่อนได้
        try:
            from blogs.models import BlogViewHistory
            viewed_blogs = BlogViewHistory.objects.filter(user=user).select_related('blog').order_by('-viewed_at')
        except:
            viewed_blogs = []

        context = {
            'user': user,
            'user_blogs': user_blogs,
            'bookmarked_blogs': bookmarked_blogs,
            'user_comments': user_comments,
            'viewed_blogs': viewed_blogs,
        }

        return render(request, "my_account.html", context)