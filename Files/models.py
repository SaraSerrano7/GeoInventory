"""
These model classes represents Files and Users relations.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.contrib.gis.db import models

# Create your models here.

class DigitalResource(models.Model):
    """
    Historic info about data manipulation
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
    edited_at = models.DateTimeField()

    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField()

    def __str__(self):
        return self.pk


###############

class Team(DigitalResource):
    """
    Users can be grouped into work teams
    """
    name = models.CharField(max_length=50)

    # info = models.ManyToManyField(DigitalResource, related_name='team_info')

    def __str__(self):
        return str(self.name)


ROLES_CHOICES = [
    ('GUEST', 'G'),  # user can log in the app
    ('VIEWER', 'V'),  # user can view files
    ('CREATOR', 'C'),  # user can create and edit files
    ('OWNER', 'O'),  # user can delete files
    ('ADMIN', 'A'),  # user can create, edit and delete teams and projects
]


class Role(DigitalResource):
    """
    Each role gives a user different capabilities when interacting with the app
    """
    role_name = models.CharField(max_length=20, choices=ROLES_CHOICES)

    # info = models.ManyToManyField(DigitalResource, related_name='role_info')

    def __str__(self):
        return str(self.role_name)


class Membership(DigitalResource):
    """
    Represents the role a user can be given at a certain team
    """
    member = models.ForeignKey(User, default='deleted user', on_delete=models.CASCADE)
    user_team = models.ForeignKey(Team, default='deleted team', on_delete=models.SET_DEFAULT)
    user_role = models.ForeignKey(Role, default=ROLES_CHOICES[0], on_delete=models.SET_DEFAULT)

    # info = models.ManyToManyField(DigitalResource, related_name='membership_info')

    def __str__(self):
        return f'{self.user_team} - {self.member}'


###############

class Project(DigitalResource):
    """
    Class to represent a working project
    """
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    finished = models.BooleanField(default=False)

    # info = models.ManyToManyField(DigitalResource, related_name='project_info')

    def __str__(self):
        return str(self.name)


class Assignations(DigitalResource):
    """
    Class to represent which team is working on a certain project
    """
    assignated_project = models.ForeignKey(
        Project,
        default='deleted project',
        on_delete=models.SET_DEFAULT
    )
    assignated_team = models.ForeignKey(
        Team,
        default='deleted team',
        on_delete=models.SET_DEFAULT
    )
    assignation_date = models.DateTimeField(now())

    # info = models.ManyToManyField(DigitalResource, related_name='assignations_info')

    def __str__(self):
        return f"{self.assignated_project} - {self.assignated_team}"


###############

class File(DigitalResource):
    """
    Class to represent a digital file of any kind
    """
    name = models.CharField(max_length=200)

    # info = models.ManyToManyField(DigitalResource, related_name='file_info')

    def __str__(self):
        return str(self.name)

    @staticmethod
    def count_existing():
        return File.objects.count()


class Access(DigitalResource):
    """
    Class to specify which team has access to a certain file
    """
    accessed_file = models.ForeignKey(File, default='deleted file', on_delete=models.SET_DEFAULT)
    accessing_team = models.ForeignKey(Team, default='deleted team', on_delete=models.SET_DEFAULT)

    # info = models.ManyToManyField(DigitalResource, related_name='access_info')

    def __str__(self):
        return f"{self.accessed_file} - {self.accessing_team}"


###############

class Folder(DigitalResource):
    """
    Class to represent a folder from a file system
    """
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True
    )

    # info = models.ManyToManyField(DigitalResource, related_name='folder_info')

    def __str__(self):
        """
        Returns the folder's name
        """
        return f"{self.parent}/{self.name}" if self.parent else self.name

    @property
    def path(self):
        """
        Recursively build the full path of the folder.
        """
        if self.parent:
            return f"{self.parent.name}/{self.name}"
        return str(self.name)


class Location(DigitalResource):
    """
    Class to represent a file location under a project file system
    """
    located_file = models.ForeignKey(
        File, default='deleted file', on_delete=models.SET_DEFAULT)
    located_project = models.ForeignKey(
        Project, default='deleted project', on_delete=models.SET_DEFAULT)
    located_folder = models.ForeignKey(
        Folder, on_delete=models.SET_NULL, null=True, blank=True)
    # info = models.ManyToManyField(DigitalResource, related_name='location_info')

    path = models.CharField(max_length=1024, editable=False)

    def save(self, *args, **kwargs):
        # Build the full path dynamically
        folder_path = self.located_folder.name if self.located_folder else ""
        self.path = f"{folder_path}/{self.located_file.name}".lstrip('/')
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.path)


###############

class Category(DigitalResource):
    """
    Represents different types of classification for files
    """
    related_file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)
    label = models.CharField(max_length=50)

    # info = models.ManyToManyField(DigitalResource, related_name='category_info')

    def __str__(self):
        return str(self.label)


###############

# class Filetype(DigitalResource):
#     file = models.ForeignKey(File, on_delete=models.SET_NULL)


GEOJSON_GEOMETRY_TYPE_CHOICES = [
    ('point', 'point'),
    ('multipoint', 'multipoint'),
    ('line', 'line'),
    ('polygon', 'polygon'),
    ('multipolygon', 'multipolygon'),
]

GEOJSON_TYPE_CHOICES = [
    ('Feature', 'Feature'),
    ('FeatureCollection', 'FeatureCollection'),
]

GEOJSON_ATTR_TYPE_CHOICES = [
    ('int', 'int'),
    ('float', 'float'),
    ('str', 'str'),

]


class GeoJSONFeature(models.Model):
    """
    Class to represent a single GeoJSON feature
    """
    feature_type = models.CharField(max_length=50, choices=GEOJSON_GEOMETRY_TYPE_CHOICES)
    geometry = models.GeometryField(null=True, blank=True)
    attribute_name = models.CharField(max_length=100)
    attribute_type = models.CharField(max_length=50, choices=GEOJSON_ATTR_TYPE_CHOICES)
    attribute_value = models.CharField(max_length=250)

    def __str__(self):
        return str(self.feature_type) + str(self.pk)


class GeoJSON(File):
    """
    Class to represent a GeoJSON filetype
    """
    content_type = models.CharField(max_length=50, choices=GEOJSON_TYPE_CHOICES)

    # content = models.ManyToManyField(GeoJSONFeature, related_name='content')

    def __str__(self):
        return str(self.name)


class Content(models.Model):
    """
    Class to represent the features contained in a GeoJSON file
    """
    geojson_file = models.ForeignKey(GeoJSON, null=True, blank=True, on_delete=models.SET_NULL)
    feature = models.ForeignKey(GeoJSONFeature, null=True, blank=True, on_delete=models.SET_NULL)

# class Shapefile(File):
#     """
#     Class to represent a Shapefile filetype
#     Warning: not implemented yet.
#     """
#     # geometry =
#     geometry_type = models.CharField(max_length=50, choices=GEOMETRY_CHOICES)
#     properties = models.JSONField()
#
#     def __str__(self):
#         return str(self.name)
