from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


# Create your models here.

class Management_info(models.Model):
    creator = models.ForeignKey(User, default='deleted user', on_delete=models.SET_DEFAULT)
    created_at = models.DateTimeField(default=now())
    deleted = models.BooleanField()
    deleted_at = models.DateTimeField(default=now())


class Team(models.Model):
    name = models.CharField(primary_key=True, max_length=50)
    info = models.ManyToManyField(Management_info, related_name='info')


ROLES_CHOICES = [
    ('GUEST', 'G'),  # user can log in the app
    ('VIEWER', 'V'),  # user can view files
    ('CREATOR', 'C'),  # user can create and edit files
    ('OWNER', 'O'),  # user can delete files
    ('ADMIN', 'A'),  # user can create, edit and delete teams and projects
]


class Role(models.Model):
    role_name = models.CharField()
    info = models.ManyToManyField(Management_info, related_name='info')


class Membership(models.Model):
    member = models.ForeignKey(User, default='deleted user', on_delete=models.CASCADE())
    user_team = models.ForeignKey(User, default='deleted team', on_delete=models.SET_DEFAULT)
    user_role = models.ForeignKey(Role, default=ROLES_CHOICES[0], on_delete=models.SET_DEFAULT)
    info = models.ManyToManyField(Management_info, related_name='info')
