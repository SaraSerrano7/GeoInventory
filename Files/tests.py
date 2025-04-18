"""
Tests to validate Files' app
"""
import json
import os
from datetime import datetime

import requests
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import TestCase
from django.contrib.auth.hashers import make_password

# Create your tests here.
from Files.models import Role, Team, Membership, Project, Assignations, GeoJSONFeature, GeoJSONFeatureProperties


class SimpleTest(TestCase):
    """
    Class for future app tests
    """
    # TODO rememeber to also be executing server app
    # upload_endpoint = "http://localhost:8000/api/upload/"
    upload_endpoint = "http://geoinventory.irtav7.cat/api/upload/"
    start_time = None
    sample_folder = "Files/sample_geojson"
    test_folder = "Files/test_data"

    def setUp(self):
        self.start_time = datetime.now()
        print('\n\n----------------------------------------------')
        print(f'Starting tests at {self.start_time}\n')
        '''
        User → test_user
        Role → creator
        Team → test_team
        Membership → test_membership (test_team, test_user, creator)
        Project → test_project
        Assignation → test_assignation (test_team, test_project)
        '''

    @classmethod
    def setUpTestData(cls):
        with connection.cursor() as cur:
            plain = "jamon"
            hashed = make_password(plain)

            query_create_user = """
            INSERT INTO public.auth_user (username, email, password, is_superuser, is_staff, first_name, last_name, is_active, date_joined)
            VALUES ('creatorUser', 'creatorUser@example.com', %(password)s, false, false, '', '', true, NOW())
            returning id;
            """
            cur.execute(query_create_user, {
                'password': hashed
            })
            user_id = cur.fetchone()[0]

            # user = User.objects.create_user(
            #     username="creatorUser",
            #     email="creatorUser@example.com",
            #     password="jamon",
            #     is_superuser=False,
            #     is_staff=False
            # )

            cls.user = user_id

            query_create_role = """
            WITH digital_resource AS (
                INSERT INTO public."Files_digitalresource" (creator_id, created_at, deleted)
                VALUES (%(creator_id)s, NOW(), false)
                RETURNING id
            )
            INSERT INTO public."Files_role" (digitalresource_ptr_id, role_name)
            VALUES ((SELECT id FROM digital_resource), 'creator') 
            RETURNING digitalresource_ptr_id;
            """

            cur.execute(query_create_role, {
                'creator_id': user_id,
            })
            role_id = cur.fetchone()[0]

        # role = Role.objects.create(
        #     role_name="creator",
        #     creator=user,
        # )

            cls.role = role_id

            query_create_team = """
                WITH digital_resource AS (
                    INSERT INTO public."Files_digitalresource" (creator_id, created_at, deleted)
                    VALUES (%(creator_id)s, NOW(), false)
                    RETURNING id
                )
                INSERT INTO public."Files_team" (digitalresource_ptr_id, name)
                VALUES ((SELECT id FROM digital_resource), 'team_patata') 
                RETURNING digitalresource_ptr_id, name;
            """

            cur.execute(query_create_team, {
                'creator_id': user_id,
            })
            team = cur.fetchone()
            team_id = team[0]
            team_name = team[1]

        # team = Team.objects.create(
        #     name="team_patata",
        # )

            cls.team = team_id
            cls.team_name = team_name

        # membership = Membership.objects.create(
        #     member=user,
        #     user_role=role,
        #     user_team=team
        # )
        #
        # cls.membership = membership

            query_create_membership = """
                WITH digital_resource AS (
                    INSERT INTO public."Files_digitalresource" (creator_id, created_at, deleted)
                    VALUES (%(creator_id)s, NOW(), false)
                    RETURNING id
                )
                INSERT INTO public."Files_membership" (digitalresource_ptr_id, member_id, user_role_id, user_team_id)
                VALUES ((SELECT id FROM digital_resource), %(member_id)s, %(user_role_id)s, %(user_team_id)s) 
                RETURNING digitalresource_ptr_id;
            """

            cur.execute(query_create_membership, {
                'creator_id': user_id,
                'member_id': user_id,
                'user_role_id': role_id,
                'user_team_id': team_id,
            })
            membership_id = cur.fetchone()[0]
            cls.membership = membership_id

            query_create_project = """
                WITH digital_resource AS (
                    INSERT INTO public."Files_digitalresource" (creator_id, created_at, deleted)
                    VALUES (%(creator_id)s, NOW(), false)
                    RETURNING id
                )
                INSERT INTO public."Files_project" (digitalresource_ptr_id, name, active, finished)
                VALUES ((SELECT id FROM digital_resource), 'proyecto_cultivos_herbaceos', true, false) 
                RETURNING digitalresource_ptr_id, name;
            """

            cur.execute(query_create_project, {
                'creator_id': user_id,
            })
            project = cur.fetchone()
            project_id = project[0]
            project_name = project[1]
            cls.project = project_id
            cls.project_name = project_name

            query_create_assignations = """
                WITH digital_resource AS (
                    INSERT INTO public."Files_digitalresource" (creator_id, created_at, deleted)
                    VALUES (%(creator_id)s, NOW(), false)
                    RETURNING id
                )
                INSERT INTO public."Files_assignations" (digitalresource_ptr_id, assignated_project_id, assignated_team_id, assignation_date)
                VALUES ((SELECT id FROM digital_resource), %(assignated_project_id)s, %(assignated_team_id)s, NOW()) 
                RETURNING digitalresource_ptr_id;
            """

            cur.execute(query_create_assignations, {
                'creator_id': user_id,
                'assignated_project_id': project_id,
                'assignated_team_id': team_id,
            })
            assignation_id = cur.fetchone()[0]
            cls.assignation = assignation_id

        # project = Project.objects.create(
        #     name="proyecto_cultivos_herbaceos",
        # )
        #
        # cls.project = project
        #
        # assignation = Assignations.objects.create(
        #     assignated_project=project,
        #     assignated_team=team,
        # )
        #
        # cls.assignation = assignation

    def test_sample_creation(self):
        files = [f for f in os.listdir(self.test_folder) if f.endswith(".geojson")]

        if files:
            self._real_data_creation(files)
        else:
            self._sample_data_creation()

    def _test_creation(self, files: list, target_folder: str):

        for filename in files:
            with self.subTest(geojson_file=filename):
                file_path = os.path.join(target_folder, filename)

                with open(file_path, "rb") as f:
                    geojson_content = f.read()

                form_data = {
                    "fileName": filename,
                    "project": self.project_name,
                    "location": self.project_name,
                    "teams": json.dumps([self.team_name]),
                    "categories": json.dumps([]),
                }

                files_data = {
                    "geojson_file": SimpleUploadedFile(name=filename,
                                                       content=geojson_content,
                                                       content_type="application/json"),
                }

                self.client.login(username="creatorUser", password="jamon")

                response = requests.post(
                    self.upload_endpoint,
                    data=form_data,
                    files={"geojson_file": (filename, geojson_content, "application/json")}
                )

                # response = requests.post(
                #     self.upload_endpoint,
                #     data={**form_data, **files_data}
                # )

                    # response = self.client.post(
                #     self.upload_endpoint,
                #     data={**form_data, **files_data})

                # print(response.content)

                self.assertEqual(response.status_code, 200, f"Error al subir {filename}: {response}")

                end_time = datetime.now()
                print(f'Ending {filename} test at {end_time}')

                with connection.cursor() as cur:
                    query_geojsonfeature_counter = """
                        SELECT count(*) FROM public."Files_geojsonfeature"
                    """
                    cur.execute(query_geojsonfeature_counter, {})
                    geojsonfeature_counter = cur.fetchone()[0]

                    query_geojsonfeatureproperties_counter = """
                                            SELECT count(*) FROM public."Files_geojsonfeatureproperties"
                                        """
                    cur.execute(query_geojsonfeatureproperties_counter, {})
                    geojsonfeatureproperties_counter = cur.fetchone()[0]

                # print(
                #     f'{GeoJSONFeature.objects.count()} features created ({GeoJSONFeatureProperties.objects.count()} properties created)')

                print(
                    f'{geojsonfeature_counter} features created ({geojsonfeatureproperties_counter} properties created)')

                print(f'Creation test duration: {end_time - self.start_time}\n')

    def _real_data_creation(self, files: list):
        # print('Files found', files)
        # print(GeoJSONFeature.objects.count())
        self._test_creation(files, self.test_folder)
        # print(f'{GeoJSONFeature.objects.count()} features created ({GeoJSONFeatureProperties.objects.count()} properties created)')
        # TODO printear facil para luego coger datos para graficos
        # TODO dejar en testoutput
        # TODO añadir nº features, tiempo

        # end_time = datetime.now()
        # print(f'Ending test at {end_time}')
        # print(f'Real data creation test duration: {end_time - self.start_time}')
        # print('----------------------------------------------\n\n')

    def _sample_data_creation(self):
        files = [f for f in os.listdir(self.sample_folder) if f.endswith(".geojson")]
        self._test_creation(files, self.sample_folder)
        # for filename in files:
        #     with self.subTest(geojson_file=filename):
        #         file_path = os.path.join(self.sample_folder, filename)
        #
        #         with open(file_path, "rb") as f:
        #             geojson_content = f.read()
        #
        #         form_data = {
        #             "fileName": filename,
        #             "project": self.project.name,
        #             "location": self.project.name,
        #             "teams": json.dumps([self.team.name]),
        #             "categories": json.dumps([]),
        #         }
        #
        #         files_data = {
        #             "geojson_file": SimpleUploadedFile(name=filename,
        #                                                content=geojson_content,
        #                                                content_type="application/json"),
        #         }
        #
        #         self.client.login(username="creatorUser", password="jamon")
        #
        #         response = self.client.post(
        #             self.upload_endpoint,
        #             data={**form_data, **files_data})
        #
        #         print(response.content)
        #
        #         self.assertEqual(response.status_code, 200, f"Error al subir {filename}: {response}")

        end_time = datetime.now()
        print(f'Ending test at {end_time}')
        print(f'Test data creation test duration: {end_time - self.start_time}')
        print('----------------------------------------------\n\n')

    def test_data_analysis(self):
        end_time = datetime.now()
        print(f'Ending test at {end_time}')
        print(f'Data analysis test duration: {end_time - self.start_time}')
        print('----------------------------------------------\n\n')
