from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth import logout, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.db import transaction
from django.http import JsonResponse

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest


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
    
class EditProfileView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL

    def get(self, request):
        auth_user = request.user
        try:
            profile = User.objects.get(auth_user=auth_user)
        except User.DoesNotExist:
            print("not found user")
            profile = None
        form = EditProfileForm(instance=profile, auth_user_instance=auth_user)
        return render(request, 'edit_profile.html', {"form": form})

    def post(self, request):
        auth_user = request.user
        profile = User.objects.get(auth_user=auth_user)
        form = EditProfileForm(request.POST, request.FILES, instance=profile, auth_user_instance=auth_user)
        if form.is_valid():
            form.save()
            print("successfully editted")
            
            login(request, auth_user)
            return redirect('home')
        print("form not valid:", form.errors)
        return render(request, 'edit_profile.html', {"form": form})
    
class MyAccountView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL
    def get(self, request):
        user = request.user.user  
        user_blogs = Blog.objects.filter(user=user).order_by('-created_date')

        bookmarked_blogs = user.bookmarked_posts.all().order_by('-created_date')

        user_comments = Comment.objects.filter(user=user).select_related('blog').order_by('-created_date')
        history = ViewingHistory.objects.filter(user=user).order_by('-viewed_at')[:10]
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
            'history':history
        }

        return render(request, "my_account.html", context)

class OthersAccountView(View):
    def get(self, request, user_id):
        user = User.objects.get(auth_user__id=user_id)
        myself = request.user.user  

        user_blogs = Blog.objects.filter(user = user, blogstatus__status = "public")
        # รับ query param สำหรับ filter
        sort_by = request.GET.get("sort")  # 'latest' หรือ 'popular'

        if sort_by == 'latest':
            user_blogs = user_blogs.order_by("-created_date")
        elif sort_by == 'popular':
            user_blogs = user_blogs.order_by("-likes")
        else:
            user_blogs = user_blogs.order_by("-created_date")  # default

        following_ids = list(myself.auth_user.following.values_list('follow_id', flat=True))

            
        context = {
            'user': user,
            'myself': myself,
            'user_blogs': user_blogs,
            'following_ids': following_ids,
        }

        return render(request, "others_account.html", context)
    
def follow(request, user_id):
    try:
        target_user = User.objects.get(auth_user__id=user_id)
        myself = request.user.user
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    if target_user == myself:
        return JsonResponse({"error": "Cannot follow yourself"}, status=400)

    existing_follow = Following.objects.filter(user=myself.auth_user, follow=target_user.auth_user)
    if existing_follow.exists():
        existing_follow.delete()
        action = "unfollowed"
    else:
        Following.objects.create(user=myself.auth_user, follow=target_user.auth_user)
        action = "followed"

    return redirect('others-account', user_id=user_id)