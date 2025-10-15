from django import forms
from reports.models import *
from blogs.models import BlogStatus
from accounts.models import User
from django.db import transaction

class HandleReportBlogForm(forms.ModelForm):
    resolve_type = forms.ChoiceField(
        choices=[('private', 'Make Private'), ('delete', 'Delete Blog')],
        required=True
    )

    class Meta:
        model = ReportBlog
        fields = []

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        with transaction.atomic():
            report = super().save(commit=False)
            action = self.cleaned_data.get('resolve_type')
            blog = report.blog

            # for log
            blog_name = blog.header if blog else ''
            blog_pk = blog.pk if blog else None

            # handle blog status
            if blog:
                if action == 'private':
                    private_status, _ = BlogStatus.objects.get_or_create(status='private')
                    blog.blogstatus = private_status
                    blog.save()
                elif action == 'delete':
                    blog.delete()
                    blog = None

            report.status = 'resolved'
            if self.request_user:
                report.handled_by = User.objects.get(auth_user=self.request_user)
            if commit:
                report.save()

            # Create log
            LogReport.objects.create(
                blog=blog if blog else None,
                blog_name=blog_name,
                action_taken=action,
                reported_by=report.reporter,
                handled_by=report.handled_by
            )

        return report