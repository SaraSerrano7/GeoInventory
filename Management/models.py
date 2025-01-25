"""
These model classes control user permissions for
creating/updating/deleting other admin users.
"""

from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.

GLOBAL_ROLES_CHOICES = [
    ('regular', 'regular'),
    ('superadmin', 'superadmin'),
]


class GlobalRole(models.Model):
    """
    Represents the role a user can have for app usage.
    """
    name = models.CharField(choices=GLOBAL_ROLES_CHOICES, max_length=50)

    def __str__(self):
        return str(self.name)


class GlobalMembership(models.Model):
    """
    Relation between a user and a global role.
    """

    user_type = models.ForeignKey(
        GlobalRole,
        default=GLOBAL_ROLES_CHOICES[0][0],
        on_delete=models.SET_DEFAULT)

    related_user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.related_user} - {self.user_type}"
