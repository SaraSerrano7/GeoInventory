"""
Tests to validate Files' app
"""
import json
import os
from datetime import datetime

import requests
from bson import ObjectId
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from pymongo import MongoClient

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

        # user = mongo_db['auth_user'].insert_one({
        #     'id': ObjectId,
        #     'username': "creatorUser",
        #     'email': "creatorUser@example.com",
        #     'password': "jamon",
        #     'is_superuser': False,
        #     'is_staff': False
        # })

        user = User.objects.create_user(
            username="creatorUser",
            email="creatorUser@example.com",
            password="jamon",
            is_superuser=False,
            is_staff=False
        )
        mongo_db = MongoClient('mongodb://localhost:27017/')['test_geoinventory']

        # user_id = user.inserted_id
        cls.user = user.id

        digitalresource_result = mongo_db['Files_digitalresource'].insert_one({
            "id": ObjectId(),
            "creator_id": user.id,
            "created_at": datetime.now(),
        })

        role = mongo_db['Files_role'].insert_one({
            "digitalresource_ptr_id": digitalresource_result.inserted_id,
            'role_name':  "creator",
            'creator_id': user.id,
        })

        # role = Role.objects.create(
        #     role_name="creator",
        #     creator=user,
        # )
        role_id = role.inserted_id

        # team = Team.objects.create(
        #     name="team_patata",
        # )

        cls.role = role_id

        digitalresource_result = mongo_db['Files_digitalresource'].insert_one({
            "id": ObjectId(),
            "creator_id": user.id,
            "created_at": datetime.now(),
        })
        team = mongo_db['Files_team'].insert_one({
            "digitalresource_ptr_id": digitalresource_result.inserted_id,
            'name': "team_patata",
        })
        team_id = team.inserted_id

        cls.team = team_id
        cls.team_name = 'team_patata'

        # membership = Membership.objects.create(
        #     member=user,
        #     user_role=role,
        #     user_team=team
        # )

        digitalresource_result = mongo_db['Files_digitalresource'].insert_one({
            "id": ObjectId(),
            "creator_id": user.id,
            "created_at": datetime.now(),
        })
        membership = mongo_db['Files_membership'].insert_one({
            "digitalresource_ptr_id": digitalresource_result.inserted_id,
            'member_id': user.id,
            'user_role_id': role_id,
            'user_team_id': team_id
        })
        membership_id = membership.inserted_id
        cls.membership = membership_id

        # project = Project.objects.create(
        #     name="proyecto_cultivos_herbaceos",
        # )

        digitalresource_result = mongo_db['Files_digitalresource'].insert_one({
            "id": ObjectId(),
            "creator_id": user.id,
            "created_at": datetime.now(),
        })
        project = mongo_db['Files_project'].insert_one({
            "digitalresource_ptr_id": digitalresource_result.inserted_id,
            'name': "proyecto_cultivos_herbaceos",
        })
        project_id = project.inserted_id
        cls.project = project_id
        cls.project_name = 'proyecto_cultivos_herbaceos'

        # assignation = Assignations.objects.create(
        #     assignated_project=project,
        #     assignated_team=team,
        # )

        digitalresource_result = mongo_db['Files_digitalresource'].insert_one({
            "id": ObjectId(),
            "creator_id": user.id,
            "created_at": datetime.now(),
        })
        assignation = mongo_db['Files_assignation'].insert_one({
            "digitalresource_ptr_id": digitalresource_result.inserted_id,
            'assignated_project': project_id,
            'assignated_team': team_id,
        })
        assignation_id = assignation.inserted_id

        cls.assignation = assignation_id

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

                # self.client.login(username="creatorUser", password="jamon")

                # response = self.client.post(
                #     self.upload_endpoint,
                #     data={**form_data, **files_data})

                response = requests.post(
                    self.upload_endpoint,
                    data=form_data,
                    files={"geojson_file": (filename, geojson_content, "application/json")},
                )

                # print(response.content)

                self.assertEqual(response.status_code, 200, f"Error al subir {filename}: {response}")

                end_time = datetime.now()
                print(f'Ending {filename} test at {end_time}')
                print(f'{GeoJSONFeature.objects.count()} features created ({GeoJSONFeatureProperties.objects.count()} properties created)')

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
