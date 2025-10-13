from django.conf import settings
from django.db import models

# from blogs.models import Blog
from django.contrib.auth.models import User as AuthUser

# class Role(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.name

class User(models.Model):
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    bio = models.CharField(max_length=200, blank=True, null=True)
    profile_path = models.FileField(upload_to='image_profile/', blank=True, null=True)
    bookmarked_posts = models.ManyToManyField('blogs.Blog', blank=True, related_name='bookmarked_by')
    # roles = models.ManyToManyField(Role, blank=True)

    def __str__(self):
        return self.auth_user.username

#settings.AUTH_USER_MODEL เผื่อแก้ส่วนauth
class Following(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    follow = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('user', 'follow')
