from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.db import transaction

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
        try:
            with transaction.atomic():
                if form.is_valid():
                    user_profile = form.save()
                    auth_user = user_profile.auth_user

                    #add member role
                    try:
                        member_group = Group.objects.get(name="member")
                    except Group.DoesNotExist:
                        member_group = Group.objects.create(name="member")
                    auth_user.groups.add(member_group)

                    login(request, auth_user)
                    return redirect('home')
                else:
                    raise transaction.TransactionManagementError("Error")
        except Exception:
            return render(request, 'register.html', {"form": form})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')