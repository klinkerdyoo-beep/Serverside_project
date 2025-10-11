from django.conf import settings
from django.db import models

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
    # roles = models.ManyToManyField(Role, through='UserRole')

    def __str__(self):
        return self.auth_user.username

# class UserRole(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     role = models.ForeignKey(Role, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('user', 'role')


#settings.AUTH_USER_MODEL เผื่อแก้ส่วนauth
class Following(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    follow = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('user', 'follow')
