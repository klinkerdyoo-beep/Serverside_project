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

from .models import *
from blogs.models import *
from accounts.models import *

class ReportBlogListView(View):
    def get(self, request):
        reports = ReportBlog.objects.select_related('blog', 'reporter', 'handled_by').order_by('-reported_date')
        
        context = {
            'reports': reports
        }
        return render(request, "report_list.html", context)

class HandleReportBlogView(View):
    def post(self, request, report_id):
        report = get_object_or_404(ReportBlog, reportblog_id=report_id)
        action = request.POST.get('action')  #'resolve' 'reject'
        resolve_type = request.POST.get('resolve_type')  #'private' 'delete'

        if action == 'resolve':

            if resolve_type == 'private':
                private_status, _ = BlogStatus.objects.get_or_create(status='private')
                report.blog.blogstatus = private_status
                report.blog.save()
                
            elif resolve_type == 'delete':
                report.blog.delete()

            report.status = 'resolved'
            report.handled_by = request.user.user 

        elif action == 'reject':
            report.status = 'rejected'
            report.handled_by = request.user.user

        report.save()
        return redirect('report-list')
