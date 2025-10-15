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
from accounts.models import *

class ReportBlogListView(View, PermissionRequiredMixin):
    permission_required = ["reports.add_blogexpiration", "reports.change_blogexpiration", "reports.delete_blogexpiration", "reports.view_blogexpiration",
                           "reports.view_reportblog", "reports.change_reportblog", "reports.delete_reportblog",
                           "reports.view_reportcomment", "reports.change_reportcomment", "reports.delete_reportcomment",
                           "blogs.change_blogstatus", "blogs.delete_blog", ]
    def get(self, request):
        reports = ReportBlog.objects.select_related('blog', 'reporter', 'handled_by').order_by('-reported_date')
        comment_reports = ReportComment.objects.select_related('comment', 'reporter', 'handled_by').order_by('-reported_date')
        logs = LogReport.objects.select_related('blog', 'reported_by', 'handled_by').order_by('-resolved_at')

        context = {
            'reports': reports,
            'comment_reports': comment_reports,
            'logs': logs
        }
        return render(request, "report_list.html", context)

class HandleReportBlogView(View, PermissionRequiredMixin):
    def post(self, request, report_id):
        report = get_object_or_404(ReportBlog, reportblog_id=report_id)
        action = request.POST.get('action')  # 'resolve' or 'reject'

        try:
            with transaction.atomic():
                if action == 'resolve':
                    form = HandleReportBlogForm(
                        request.POST, instance=report, request_user=request.user
                    )
                    if form.is_valid():
                        form.save()
                    else:
                        print("form is not valid", form.errors)
                        reports = ReportBlog.objects.select_related('blog', 'reporter', 'handled_by').all()
                        return render(request, "report_list.html", {"reports": reports, "form_errors": form.errors})
                elif action == 'reject':
                    report.status = 'rejected'
                    report.handled_by = User.objects.get(auth_user=request.user)
                    report.save()
                    
        except Exception as e:
            print('exception: ', e)
            reports = ReportBlog.objects.select_related('blog', 'reporter', 'handled_by').all()
            return render(request, "report_list.html", {
                "reports": reports,
                "error": "Failed to process the report"
            })

        return redirect('report-list')
