"""
Tests to validate Files' app
"""
import json
import os
from datetime import datetime

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

# Create your tests here.
from Files.models import Role, Team, Membership, Project, Assignations, GeoJSONFeature


class SimpleTest(TestCase):
    """
    Class for future app tests
    """
    # TODO rememeber to also be executing server app
    upload_endpoint = "http://localhost:8000/api/upload/"
    start_time = None
    sample_folder = "Files/sample_geojson"
    test_folder = "Files/test_data"

    def setUp(self):
        self.start_time = datetime.now()
        print('\n\n----------------------------------------------')
        print(f'Starting test at {self.start_time}')
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
        user = User.objects.create_user(
            username="creatorUser",
            email="creatorUser@example.com",
            password="jamon",
            is_superuser=False,
            is_staff=False
        )

        cls.user = user

        role = Role.objects.create(
            role_name="creator",
            creator=user,
        )

        cls.role = role

        team = Team.objects.create(
            name="team_patata",
        )

        cls.team = team

        membership = Membership.objects.create(
            member=user,
            user_role=role,
            user_team=team
        )

        cls.membership = membership

        project = Project.objects.create(
            name="proyecto_cultivos_herbaceos",
        )

        cls.project = project

        assignation = Assignations.objects.create(
            assignated_project=project,
            assignated_team=team,
        )

        cls.assignation = assignation

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
                    "project": self.project.name,
                    "location": self.project.name,
                    "teams": json.dumps([self.team.name]),
                    "categories": json.dumps([]),
                }

                files_data = {
                    "geojson_file": SimpleUploadedFile(name=filename,
                                                       content=geojson_content,
                                                       content_type="application/json"),
                }

                self.client.login(username="creatorUser", password="jamon")

                response = self.client.post(
                    self.upload_endpoint,
                    data={**form_data, **files_data})

                # print(response.content)

                self.assertEqual(response.status_code, 200, f"Error al subir {filename}: {response}")


    def _real_data_creation(self, files: list):
        # print('Files found', files)
        # print(GeoJSONFeature.objects.count())
        self._test_creation(files, self.test_folder)
        print(f'{GeoJSONFeature.objects.count()} features created')
        # TODO printear facil para luego coger datos para graficos
        # TODO dejar en testoutput
        # TODO añadir nº features, tiempo

        end_time = datetime.now()
        print(f'Ending test at {end_time}')
        print(f'Real data creation test duration: {end_time - self.start_time}')
        print('----------------------------------------------\n\n')


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
