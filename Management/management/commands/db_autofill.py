from typing import Type

from astroid.interpreter.objectmodel import ObjectModel
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import connection

from Files.models import Role, Team, Membership, Project
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
                self.stdout.write(self.style.WARNING("PostGIS is already installed."))

            # Si PostGISTopology no está instalado, lo instalamos
            if not postgistopology_installed:
                self.stdout.write(self.style.NOTICE("PostGISTopology is not installed. Installing..."))
                cursor.execute("CREATE EXTENSION postgis_topology;")
                self.stdout.write(self.style.SUCCESS("PostGISTopology has been installed successfully."))
            else:
                self.stdout.write(self.style.WARNING("PostGISTopology is already installed."))

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
            result, created = classname.objects.get_or_create(**object_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f" '{result}' created successfully."))
            else:
                self.stdout.write(self.style.WARNING(f"'{result}' already exists."))

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

        regular_type = GlobalRole.objects.get(name="regular")
        admin_user = User.objects.get(username='adminUser')
        creator_user = User.objects.get(username='creatorUser')
        viewer_user = User.objects.get(username='viewerUser')
        guest_user = User.objects.get(username='guestUser')

        global_membership_data = [
            {"user_type": superadmin_type, "related_user": superadmin_user},
            {"user_type": regular_type, "related_user": admin_user},
            {"user_type": regular_type, "related_user": creator_user},
            {"user_type": regular_type, "related_user": viewer_user},
            {"user_type": regular_type, "related_user": guest_user},
        ]

        self.create_objects(notice_message, global_membership_data, GlobalMembership)

    def create_teams(self):
        notice_message = "Checking teams..."
        teams_data = [
            {"name": "team_patata"},
            {"name": "team_arroz"},
            {"name": "team_cereal"},
            {"name": "team_viña"},
        ]
        self.create_objects(notice_message, teams_data, Team)

    # TODO añadir el creator superadmin

    def create_membership(self):
        notice_message = "Checking membership..."
        superadmin_user = User.objects.get(username='superadminUser')

        admin_user = User.objects.get(username='adminUser')
        creator_user = User.objects.get(username='creatorUser')
        viewer_user = User.objects.get(username='viewerUser')
        guest_user = User.objects.get(username='guestUser')

        admin_role = Role.objects.get(role_name='admin')
        creator_role = Role.objects.get(role_name='creator')
        viewer_role = Role.objects.get(role_name='viewer')
        guest_role = Role.objects.get(role_name='guest')

        team_patata = Team.objects.get(name='team_patata')
        team_arroz = Team.objects.get(name='team_arroz')
        team_cereal = Team.objects.get(name='team_cereal')
        team_viña = Team.objects.get(name='team_viña')

        membership_data = [
            {"member": superadmin_user, "user_role": admin_role, "user_team": team_patata},
            {"member": superadmin_user, "user_role": admin_role, "user_team": team_arroz},
            {"member": superadmin_user, "user_role": admin_role, "user_team": team_cereal},
            {"member": superadmin_user, "user_role": admin_role, "user_team": team_viña},

            {"member": admin_user, "user_role": admin_role, "user_team": team_patata},

            {"member": creator_user, "user_role": creator_role, "user_team": team_patata},
            {"member": creator_user, "user_role": creator_role, "user_team": team_viña},

            {"member": viewer_user, "user_role": viewer_role, "user_team": team_patata},
            {"member": viewer_user, "user_role": viewer_role, "user_team": team_viña},

            {"member": guest_user, "user_role": guest_role, "user_team": team_viña},
        ]
        self.create_objects(notice_message, membership_data, Membership)

    def create_projects(self):
        notice_message = "Checking projects..."

        projects_data = [
            {"name": "proyecto_cultivo_herbaceos"},
            {"name": "proyecto_cultivo_leñosos"},
        ]
        self.create_objects(notice_message, projects_data, Project)

    def create_assignations(self):
        print('Creating assignations: proyecto_cultivos_herbaceos - team_patata')
        print('Creating assignations: proyecto_cultivos_herbaceos - team_arroz')
        print('Creating assignations: proyecto_cultivos_herbaceos - team_cereal')
        print('Creating assignations: proyecto_cultivos_leñosos - team_viña')

    def create_categories(self):
        print('Creating categories: vectorial')
        print('Creating categories: farms')

    def create_classifications(self):
        print('Creating classification: sample_file1.txt - farms')
        print('Creating classification: sample_file1.txt - vectorial')

    def create_geojson(self):
        print('Creating geojson: sample_file1.txt - featurecollection')

    def create_folders(self):
        print('Creating folder: input')
        print('Creating folder: input/type1')
        print('Creating folder: input/type2')
        print('Creating folder: input/type2/subtype1')

    def create_locations(self):
        print('Creating location: proyecto_cultivos_herbaceos - input/type1 - sample_file1.txt')
        print('Creating location: proyecto_cultivos_herbaceos - input/type2/subtype1 - sample_file1.txt')

    def create_geojsonfeature(self):
        print('Creating geojsonfeature: file1 - multipolygon - polygon1')
        print('Creating geojsonfeature: file1 - multipolygon - polygon2')

    def create_geojsonfeatureproperty(self):
        print('Creating feature property: feature1 - atribute1 - value')
        print('Creating feature property: feature1 - atribute2 - value')
        print('Creating feature property: feature2 - atribute3 - value')

    def create_propertyattribute(self):
        print('Creating feature attribute1: cropname - string')
        print('Creating feature attribute2: owner - string')
        print('Creating feature attribute3: yield - int')

    def db_autofill(self):
        self.chech_postgis_extensions()
        self.create_users()
        self.create_roles()
        self.create_global_roles()
        self.create_global_membership()
        self.create_teams()
        self.create_membership()
        self.create_projects()

        ##############

        self.create_assignations()
        self.create_categories()
        self.create_classifications()
        self.create_geojson()
        self.create_folders()
        self.create_locations()
        self.create_geojsonfeature()
        self.create_geojsonfeatureproperty()
        self.create_propertyattribute()



    def handle(self, *args, **options):
        self.db_autofill()
