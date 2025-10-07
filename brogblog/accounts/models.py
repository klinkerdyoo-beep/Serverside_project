from django.db import models


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=200, unique=True, null=False)
    password = models.CharField(max_length=200, null=False)
    username = models.CharField(max_length=200, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    bio = models.CharField(max_length=200, blank=True, null=True)
    profile_path = models.TextField(blank=True, null=True)

    roles = models.ManyToManyField(Role, through='UserRole')

    def __str__(self):
        return self.username


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'role')


class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    follow = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('user', 'follow')
