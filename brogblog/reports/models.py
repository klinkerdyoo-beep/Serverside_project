from django.db import models
from accounts.models import User
from blogs.models import Blog, Comment


class ReportBlog(models.Model):
    reportblog_id = models.AutoField(primary_key=True)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_blogs')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    reported_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('resolved', 'Resolved'), ('rejected', 'Rejected')],
        default='pending'
    )
    updated_date = models.DateTimeField(auto_now=True)
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='handled_blogs')


class ReportComment(models.Model):
    reportcomment_id = models.AutoField(primary_key=True)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_comments')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    reported_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('resolved', 'Resolved'), ('rejected', 'Rejected')],
        default='pending'
    )
    updated_date = models.DateTimeField(auto_now=True)
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='handled_comments')

class LogReport(models.Model):
    log_id = models.AutoField(primary_key=True)
    blog = models.ForeignKey(Blog, on_delete=models.SET_NULL, null=True)
    blog_name = models.CharField(max_length=200)
    action_taken = models.CharField(max_length=20, choices=[('private', 'Private'), ('delete', 'Delete')])
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='logs_reported')
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='logs_handled')
    resolved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blog_name} - {self.action_taken} by {self.handled_by}"