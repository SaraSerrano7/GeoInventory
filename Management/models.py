from django.contrib.auth.models import User
from django.db import models

# Create your models here.

GLOBAL_ROLES_CHOICES = [
    ('regular', 'regular'),
    ('superadmin', 'superadmin'),
]


class Global_role(models.Model):
    name = models.CharField(choices=GLOBAL_ROLES_CHOICES)


class Global_membership(models.Model):
    user_type = models.ForeignKey(Global_role, default=GLOBAL_ROLES_CHOICES[0], on_delete=models.SET_DEFAULT)
    related_user = models.ForeignKey(User, default='deleted user', on_delete=models.SET_DEFAULT)
