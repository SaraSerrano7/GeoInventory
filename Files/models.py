"""
These model classes represents Files and Users relations.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


# Create your models here.

class ManagementInfo(models.Model):
    """
    Historic data about data manipulation
    """
    creator = models.ForeignKey(
        User,
        default='deleted user',
        on_delete=models.SET_DEFAULT,
        related_name='creator_info'
    )
    created_at = models.DateTimeField(now())
    editor = models.ForeignKey(
        User,
        default='deleted user',
        on_delete=models.SET_DEFAULT,
        related_name='editor_info'
    )
    edited_at = models.DateTimeField(now())
    deleted = models.BooleanField()
    deleted_at = models.DateTimeField(now())


class Team(models.Model):
    """
    Users can be grouped into work teams
    """
    name = models.CharField(primary_key=True, max_length=50)
    info = models.ManyToManyField(ManagementInfo, related_name='team_info')


ROLES_CHOICES = [
    ('GUEST', 'G'),  # user can log in the app
    ('VIEWER', 'V'),  # user can view files
    ('CREATOR', 'C'),  # user can create and edit files
    ('OWNER', 'O'),  # user can delete files
    ('ADMIN', 'A'),  # user can create, edit and delete teams and projects
]


class Role(models.Model):
    """
    Each role gives a user different capabilities when interacting with the app
    """
    role_name = models.CharField(max_length=20)
    info = models.ManyToManyField(ManagementInfo, related_name='role_info')


class Membership(models.Model):
    """
    Represents the role a user can be given at a certain team
    """
    member = models.ForeignKey(User, default='deleted user', on_delete=models.CASCADE)
    user_team = models.ForeignKey(Team, default='deleted team', on_delete=models.SET_DEFAULT)
    user_role = models.ForeignKey(Role, default=ROLES_CHOICES[0], on_delete=models.SET_DEFAULT)
    info = models.ManyToManyField(ManagementInfo, related_name='membership_info')
