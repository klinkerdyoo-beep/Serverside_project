from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.db import transaction

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest


from .forms import *
from .models import *

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

    def get(self, request: HttpRequest):
        form = RegisterForm()
        return render(request, 'edit_profile.html', {"form": form})
    
    # def post(self, request):
