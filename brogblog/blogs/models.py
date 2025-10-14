from django.db import models
# from accounts.models import User


class BlogStatus(models.Model):
    blogstatus_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=200, null=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.status


class Blog(models.Model):
    blog_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('accounts.User',on_delete=models.CASCADE,
        related_name='blogs'
    )
    blogstatus = models.ForeignKey(BlogStatus, on_delete=models.CASCADE)
    header = models.CharField(max_length=200, null=False)
    body = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    

    def __str__(self):
        return self.header


class BlogImage(models.Model):
    blogimage_id = models.AutoField(primary_key=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    image_path = models.FileField(upload_to='image_post/', blank=True, null=True)


class BlogExpiration(models.Model):
    blogexpiration_id = models.AutoField(primary_key=True)
    reporting = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    expire_in = models.DateTimeField(null=False)
    reason = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.blog.header} expires on {self.expire_in}"

class ViewingHistory(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog')


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True
    )

    comment_status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('editted', 'Editted'), ('deleted', 'Deleted')],
        default='active'
    )

    comment_text = models.TextField(null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}: {self.comment_text[:30]}"