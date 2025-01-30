from typing import Type

from astroid.interpreter.objectmodel import ObjectModel
from django.contrib.auth.models import User
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.management.base import BaseCommand
from django.db import connection

from Files.models import Role, Team, Membership, Project, Assignations, Category, Classification, GeoJSON, \
    File, Folder, Location, GeoJSONFeature, GeoJSONFeatureProperties, PropertyAttribute
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
            {"name": "team_olivo"},
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
        team_olivo = Team.objects.get(name='team_olivo')

        membership_data = [
            {"member": superadmin_user, "user_role": admin_role, "user_team": team_patata},
            {"member": superadmin_user, "user_role": admin_role, "user_team": team_arroz},
            {"member": superadmin_user, "user_role": admin_role, "user_team": team_cereal},
            {"member": superadmin_user, "user_role": admin_role, "user_team": team_olivo},

            {"member": admin_user, "user_role": admin_role, "user_team": team_patata},

            {"member": creator_user, "user_role": creator_role, "user_team": team_patata},
            {"member": creator_user, "user_role": creator_role, "user_team": team_olivo},

            {"member": viewer_user, "user_role": viewer_role, "user_team": team_patata},
            {"member": viewer_user, "user_role": viewer_role, "user_team": team_olivo},

            {"member": guest_user, "user_role": guest_role, "user_team": team_olivo},
        ]
        self.create_objects(notice_message, membership_data, Membership)

    def create_projects(self):
        notice_message = "Checking projects..."

        projects_data = [
            {"name": "proyecto_cultivos_herbaceos"},
            {"name": "proyecto_cultivos_leñosos"},
        ]
        self.create_objects(notice_message, projects_data, Project)

    def create_assignations(self):

        notice_message = "Checking assignations..."

        project1 = Project.objects.get(name="proyecto_cultivos_herbaceos")
        project2 = Project.objects.get(name="proyecto_cultivos_leñosos")
        team_patata = Team.objects.get(name="team_patata")
        team_arroz = Team.objects.get(name="team_arroz")
        team_cereal = Team.objects.get(name="team_cereal")
        team_olivo = Team.objects.get(name="team_olivo")

        assignations_data = [
            {"assignated_project": project1, "assignated_team": team_patata},
            {"assignated_project": project1, "assignated_team": team_arroz},
            {"assignated_project": project1, "assignated_team": team_cereal},
            {"assignated_project": project2, "assignated_team": team_olivo},
        ]
        self.create_objects(notice_message, assignations_data, Assignations)

    def create_categories(self):
        notice_message = "Checking categories..."

        categories_data = [
            {"label": "Farms"},
            {"label": "Vectorial"},
        ]
        self.create_objects(notice_message, categories_data, Category)

    def create_geojson(self):
        notice_message = "Checking geojsons..."

        geojson_data = [
            {"name": "example.geojson", "content_type": 1},
        ]
        self.create_objects(notice_message, geojson_data, GeoJSON)

    def create_classifications(self):
        notice_message = "Checking classifications..."

        farm_category = Category.objects.get(label='Farms')
        vectorial_category = Category.objects.get(label='Vectorial')

        geojson = GeoJSON.objects.get(name="example.geojson", content_type=1)
        file_instance = File.objects.get(id=geojson.id)

        categories_data = [
            {"category_name": farm_category, "related_file": file_instance},
            {"category_name": vectorial_category, "related_file": file_instance},
        ]
        self.create_objects(notice_message, categories_data, Classification)

    def create_folders(self):

        notice_message = "Checking folders..."

        folder_data = [
            {"name": 'input', "parent": None},
        ]

        self.create_objects(notice_message, folder_data, Folder)
        ###########
        parent = Folder.objects.get(**folder_data[0])

        subfolders_data = [
            {"name": 'type1', "parent": parent},
            {"name": 'type2', "parent": parent},
        ]

        self.create_objects(notice_message, subfolders_data, Folder)

        ###########
        subparent = Folder.objects.get(**subfolders_data[1])

        subsubfolders_data = [
            {"name": 'subtype1', "parent": subparent},
            {"name": 'subtype2', "parent": subparent},
        ]

        self.create_objects(notice_message, subsubfolders_data, Folder)

    def create_locations(self):

        notice_message = "Checking locations..."

        geojson = GeoJSON.objects.get(name="example.geojson", content_type=1)
        file_instance = File.objects.get(id=geojson.id)

        folder1 = Folder.objects.get(path="input")
        folder2 = Folder.objects.get(path="input/type1")
        folder3 = Folder.objects.get(path="input/type2/subtype2")

        project1 = Project.objects.get(name="proyecto_cultivos_herbaceos")
        project2 = Project.objects.get(name="proyecto_cultivos_leñosos")

        locations_data = [
            {"located_file": file_instance, "located_folder": folder1, "located_project": project1},
            {"located_file": file_instance, "located_folder": folder2, "located_project": project2},
            {"located_file": file_instance, "located_folder": folder3, "located_project": project1},
        ]

        self.create_objects(notice_message, locations_data, Location)

    def create_geojsonfeature(self):

        notice_message = "Checking geojson features..."

        geojson = GeoJSON.objects.get(name="example.geojson", content_type=1)
        file_instance = File.objects.get(id=geojson.id)

        polygon1 = Polygon((
            (-3.68275, 40.41525), (-3.68024, 40.41487),
            (-3.68024, 40.41802), (-3.68275, 40.41843),
            (-3.68275, 40.41525)
        ))

        polygon2 = Polygon((
            (-3.7451, 40.4196), (-3.7359, 40.4196),
            (-3.7359, 40.4259), (-3.7451, 40.4259),
            (-3.7451, 40.4196)
        ))

        multipolygon1 = MultiPolygon(polygon1, polygon2)

        ################

        polygon1 = Polygon((
            (0.0420, 42.6798), (0.0478, 42.6798),
            (0.0478, 42.6843), (0.0420, 42.6843),
            (0.0420, 42.6798)
        ))

        polygon2 = Polygon(
            ((0.0550, 42.6850), (0.0600, 42.6850),
             (0.0600, 42.6900), (0.0550, 42.6900),
             (0.0550, 42.6850)),  # Contorno exterior
            ((0.0565, 42.6865), (0.0585, 42.6865),
             (0.0585, 42.6885), (0.0565, 42.6885),
             (0.0565, 42.6865))  # Hueco interior
        )

        multipolygon2 = MultiPolygon(polygon1, polygon2)

        features_data = [
            {"feature_type": 4, "geometry": multipolygon1, "file": geojson},
            {"feature_type": 4, "geometry": multipolygon2, "file": geojson},
        ]

        self.create_objects(notice_message, features_data, GeoJSONFeature)

    def create_propertyattribute(self):
        notice_message = "Checking properties attributes..."

        attributes_data = [
            {"attribute_name": "crop", "attribute_type": "string"},
            {"attribute_name": "owner", "attribute_type": "string"},
            {"attribute_name": "yield", "attribute_type": "int"},
        ]

        self.create_objects(notice_message, attributes_data, PropertyAttribute)

    def create_geojsonfeatureproperty(self):

        notice_message = "Checking feature properties..."

        geojson = GeoJSON.objects.get(name="example.geojson", content_type=1)
        file_instance = File.objects.get(id=geojson.id)

        feature1 = GeoJSONFeature.objects.get(id=1)
        feature2 = GeoJSONFeature.objects.get(id=2)

        attribute1 = PropertyAttribute.objects.get(attribute_name="crop")
        attribute2 = PropertyAttribute.objects.get(attribute_name="owner")
        attribute3 = PropertyAttribute.objects.get(attribute_name="yield")

        properties_data = [
            {"feature": feature1, "attribute": attribute1, "attribute_value": file_instance},
            {"feature": feature1, "attribute": attribute2, "attribute_value": file_instance},
            {"feature": feature2, "attribute": attribute3, "attribute_value": file_instance},
        ]

        self.create_objects(notice_message, properties_data, GeoJSONFeatureProperties)

    def db_autofill(self):
        self.chech_postgis_extensions()
        self.create_users()
        self.create_roles()
        self.create_global_roles()
        self.create_global_membership()
        self.create_teams()
        self.create_membership()
        self.create_projects()
        self.create_assignations()
        self.create_categories()
        self.create_geojson()
        self.create_classifications()
        self.create_folders()
        self.create_locations()
        self.create_geojsonfeature()
        self.create_propertyattribute()
        self.create_geojsonfeatureproperty()

    def handle(self, *args, **options):
        self.db_autofill()
