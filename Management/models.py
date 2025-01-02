from django.contrib.auth.models import User
from django.db import models

# Create your models here.

GLOBAL_ROLES_CHOICES = [
    ('superadmin', 'superadmin'),
    ('regular', 'regular'),
]


class Global_role(models.Model):
    name = models.CharField(choices=GLOBAL_ROLES_CHOICES)


class Global_membership(models.Model):
    user_type = models.ForeignKey(Global_role, default='regular', on_delete=models.SET_DEFAULT)
    related_user = models.ForeignKey(User, on_delete=models.CASCADE)
