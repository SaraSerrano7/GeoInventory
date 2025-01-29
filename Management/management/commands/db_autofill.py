import os
import subprocess
from typing import Type

from astroid.interpreter.objectmodel import ObjectModel
from django.db import connection
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Files.models import Role, Team
from django.conf import settings

from Management.models import GlobalRole, GlobalMembership


class Command(BaseCommand):
    help = "This command auto populates db for sample use"

    def add_arguments(self, parser):
        pass

    def chech_postgis_extensions(self):
        self.stdout.write(self.style.NOTICE("Checking postgis extensions..."))
        with connection.cursor() as cursor:
            # Comprobar si PostGIS está instalado
            cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis');")
            postgis_installed = cursor.fetchone()[0]

            # Comprobar si PostGISTopology está instalado
            cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis_topology');")
            postgistopology_installed = cursor.fetchone()[0]

            # Si PostGIS no está instalado, lo instalamos
            if not postgis_installed:
                self.stdout.write(self.style.NOTICE("PostGIS is not installed. Installing..."))
                cursor.execute("CREATE EXTENSION postgis;")
                self.stdout.write(self.style.SUCCESS("PostGIS has been installed successfully."))
            else:
                self.stdout.write(self.style.SUCCESS("PostGIS is already installed."))

            # Si PostGISTopology no está instalado, lo instalamos
            if not postgistopology_installed:
                self.stdout.write(self.style.NOTICE("PostGISTopology is not installed. Installing..."))
                cursor.execute("CREATE EXTENSION postgis_topology;")
                self.stdout.write(self.style.SUCCESS("PostGISTopology has been installed successfully."))
            else:
                self.stdout.write(self.style.SUCCESS("PostGISTopology is already installed."))

    def create_users(self):
        self.stdout.write(self.style.NOTICE("Checking users..."))
        users_data = [
            {"username": "guestUser", "email": "guestUser@example.com", "password": "jamon", "is_superuser": False},
            {"username": "viewerUser", "email": "viewerUser@example.com", "password": "jamon", "is_superuser": False},
            {"username": "creatorUser", "email": "creatorUser@example.com", "password": "jamon", "is_superuser": False},
            {"username": "adminUser", "email": "adminUser@example.com", "password": "jamon", "is_superuser": False},
            {"username": "superadminUser", "email": "superadminUser@example.com", "password": "jamon",
             "is_superuser": True},

        ]

        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password']
                )

                if user_data['is_superuser']:
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()

                self.stdout.write(self.style.SUCCESS(f" '{user.username}' created successfully."))
            else:
                self.stdout.write(self.style.WARNING(f"User '{user_data['username']}' already exists."))

    def create_roles(self):
        self.stdout.write(self.style.NOTICE("Checking roles..."))
        creator = User.objects.get(username='superadminUser')
        roles_data = [
            {"role_name": "guest", "creator": creator},
            {"role_name": "viewer", "creator": creator},
            {"role_name": "creator", "creator": creator},
            {"role_name": "admin", "creator": creator},
        ]

        for role_data in roles_data:
            if not Role.objects.filter(role_name=role_data['role_name']).exists():
                role = Role.objects.create(
                    role_name=role_data['role_name'],
                    creator=role_data['creator'],
                )

                self.stdout.write(self.style.SUCCESS(f" '{role.role_name}' created successfully."))
            else:
                self.stdout.write(self.style.WARNING(f"Role '{role_data['role_name']}' already exists."))

    def create_objects(self, notice_message: str,
                       objects_data: list[dict],
                       classname: Type[ObjectModel],
                       related_classes=None):
        self.stdout.write(self.style.NOTICE(notice_message))
        for object_data in objects_data:
            # attr = list(object_data.keys())
            if not classname.objects.filter(**object_data).exists():
                created = classname.objects.create(**object_data)

                self.stdout.write(self.style.SUCCESS(f" '{created}' created successfully."))
            else:
                self.stdout.write(self.style.WARNING(f"'{str(classname)}' already exists."))


    def create_global_roles(self):
        notice_message = "Checking global roles..."
        global_roles_data = [
            {"name": "regular"},
            {"name": "superadmin"},
        ]
        self.create_objects(notice_message, global_roles_data, GlobalRole)


    def create_global_membership(self):
        notice_message = "Checking global membership..."
        superadmin_type = GlobalRole.objects.get(name="superadmin")
        superadmin_user = User.objects.get(username='superadminUser')
        global_membership_data = [
            {"user_type": superadmin_type, "related_user": superadmin_user},
        ]

        self.create_objects(notice_message, global_membership_data, GlobalMembership)


    def create_teams(self):
        notice_message = "Checking teams..."
        teams_data = [
            {"name", "team_patata"},
            {"name", "team_arroz"},
            {"name", "team_cereal"},
            {"name", "team_viña"},
        ]
        self.create_objects(notice_message, teams_data, Team)

    def db_autofill(self):
        self.chech_postgis_extensions()
        self.create_users()
        self.create_roles()
        self.create_global_roles()
        # TODO añadir el resto de usuarios a regular,
        self.create_global_membership()


        print('Creating teams: team_patata')
        print('Creating teams: team_cereal')
        print('Creating teams: team_arroz')
        print('Creating teams: team_viña')
        print('Creating Membership: team_patata - superadminUser - creator')
        print('Creating Membership: team_viña - adminUser - admin')
        print('Creating projects: proyecto_cultivos_herbaceos')
        print('Creating projects: proyecto_cultivos_leñosos')
        print('Creating assignations: proyecto_cultivos_herbaceos - team_patata')
        print('Creating assignations: proyecto_cultivos_herbaceos - team_arroz')
        print('Creating assignations: proyecto_cultivos_herbaceos - team_cereal')
        print('Creating assignations: proyecto_cultivos_leñosos - team_viña')
        print('Creating categories: vectorial')
        print('Creating categories: farms')
        print('Creating geojson: sample_file1.txt - featurecollection')
        print('Creating classification: sample_file1.txt - farms')
        print('Creating classification: sample_file1.txt - vectorial')
        print('Creating folder: input')
        print('Creating folder: input/type1')
        print('Creating folder: input/type2')
        print('Creating folder: input/type2/subtype1')
        print('Creating location: proyecto_cultivos_herbaceos - input/type1 - sample_file1.txt')
        print('Creating location: proyecto_cultivos_herbaceos - input/type2/subtype1 - sample_file1.txt')
        print('Creating geojsonfeature: polygon1 - multipolygon - crop - string - patata')
        print('Creating geojsonfeature: polygon1 - multipolygon - yield - int - "250"')
        print('Creating content: sample_file1.txt - geojsonfeature1')
        print('Creating content: sample_file1.txt - geojsonfeature1')

    def handle(self, *args, **options):
        self.db_autofill()
