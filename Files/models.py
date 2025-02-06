"""
These model classes represents Files and Users relations.
"""

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.utils.timezone import now


# Create your models here.

class DigitalResource(models.Model):  # PolymorphicModel
    """
    Historic info about data manipulation
    """
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='creator_info'
    )
    created_at = models.DateTimeField(default=now, editable=False)

    editor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='editor_info',
        null=True,
        blank=True
    )
    edited_at = models.DateTimeField(null=True, blank=True)

    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "self.pk"


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
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    user_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
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
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    assignated_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    assignation_date = models.DateTimeField(default=now, editable=False)

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
    def count_all_existing_files():
        return File.objects.count()

    @staticmethod
    def count_user_files(current_user: User):
        return File.objects.filter(creator=current_user.id).count()


class Access(DigitalResource):
    """
    Class to specify which team has access to a certain file
    """
    accessed_file = models.ForeignKey(
        File,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    accessing_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

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
    path = models.CharField(
        max_length=255,
        editable=False,
        # unique=True,
        default=''
    )

    # info = models.ManyToManyField(DigitalResource, related_name='folder_info')

    def __str__(self):
        """
        Returns the folder's name
        """
        # return f"{self.parent}/{self.name}" if self.parent else str(self.name)
        return f"{self.path}"

    def save(self, *args, **kwargs):
        self.path = self.build_path()
        super().save(*args, **kwargs)

    # @property
    def build_path(self):
        """
        Recursively build the full path of the folder.
        """
        if self.parent:
            return f"{self.parent.path}/{self.name}"
        return str(self.name)


class Location(DigitalResource):
    """
    Class to represent a file location under a project file system
    """
    # TODO el path este no deberia estar en folder realmente???
    located_file = models.ForeignKey(
        File, on_delete=models.SET_NULL, null=True, blank=True)
    located_project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True)
    located_folder = models.ForeignKey(
        Folder, on_delete=models.SET_NULL, null=True, blank=True)
    # info = models.ManyToManyField(DigitalResource, related_name='location_info')

    path = models.CharField(max_length=1024, editable=False, default='')

    def save(self, *args, **kwargs):
        # Build the full path dynamically
        folder_path = self.located_folder.path if self.located_folder else ""
        self.path = f"{folder_path}/{self.located_file.name}".lstrip('/') if self.located_file else f"{folder_path}"
        # todo dudo que esto sea necesario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.located_project} - {self.path}"


###############

class Category(DigitalResource):
    label = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str(self.label)


class Classification(DigitalResource):
    """
    Represents different types of classification for files
    """
    related_file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)
    category_name = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    # info = models.ManyToManyField(DigitalResource, related_name='category_info')

    def __str__(self):
        return f"{self.related_file} - {self.category_name.label}"


###############

# class Filetype(DigitalResource):
#     file = models.ForeignKey(File, on_delete=models.SET_NULL)


GEOJSON_GEOMETRY_TYPE_CHOICES = [
    ('Point', 'Point'),
    ('MultiPoint', 'MultiPoint'),
    ('Line', 'Line'),
    ('Polygon', 'Polygon'),
    ('MultiPolygon', 'MultiPolygon'),
]

GEOJSON_TYPE_CHOICES = [
    ('Feature', 'Feature'),
    ('FeatureCollection', 'FeatureCollection'),
]

GEOJSON_ATTR_TYPE_CHOICES = [
    ('int', 'int'),
    ('float', 'float'),
    ('str', 'str'),
    ('bool', 'bool')
]


class GeoJSON(File):
    """
    Class to represent a GeoJSON filetype
    """
    content_type = models.CharField(max_length=50, choices=GEOJSON_TYPE_CHOICES)

    # content = models.ManyToManyField(GeoJSONFeature, related_name='content')

    def __str__(self):
        return str(self.name)


class GeoJSONFeature(models.Model):
    """
    Class to represent a single GeoJSON feature
    """
    file = models.ForeignKey(GeoJSON, on_delete=models.SET_NULL, null=True, blank=True)
    feature_type = models.CharField(max_length=50, choices=GEOJSON_GEOMETRY_TYPE_CHOICES)
    geometry = models.GeometryField(null=True, blank=True)

    def __str__(self):
        return str(self.feature_type) + str(self.pk)


class PropertyAttribute(models.Model):
    attribute_name = models.CharField(max_length=100)
    attribute_type = models.CharField(max_length=50, choices=GEOJSON_ATTR_TYPE_CHOICES)

    def __str__(self):
        return f"({self.attribute_type}) {self.attribute_name}"


class GeoJSONFeatureProperties(models.Model):
    feature = models.ForeignKey(GeoJSONFeature, on_delete=models.SET_NULL, blank=True, null=True)
    attribute = models.ForeignKey(PropertyAttribute, on_delete=models.SET_NULL, null=True, blank=True)
    attribute_value = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.attribute} = {self.attribute_value}"
