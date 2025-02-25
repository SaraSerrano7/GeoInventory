"""
Tests to validate Files' app
"""
import json
import os
from datetime import datetime

import requests
from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from Files.models import Role, Team, Membership, Project, Assignations


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
        print(f'starting searching in {self.test_folder}')
        print(os.listdir(self.test_folder))
        files = [f for f in os.listdir(self.test_folder) if f.endswith(".geojson")]
        print(f'files found: {files}')
        if files:
            self._real_data_creation(files)
        else:
            self._sample_data_creation()

    def _real_data_creation(self, files: list):
        end_time = datetime.now()
        print(f'Ending test at {end_time}')
        print(f'Real data creation test duration: {end_time - self.start_time}')

    def _sample_data_creation(self):
        files = [f for f in os.listdir(self.sample_folder) if f.endswith(".geojson")]
        for filename in files:
            print(filename)
            with self.subTest(geojson_file=filename):
                file_path = os.path.join(self.sample_folder, filename)

                # Leer el contenido del archivo
                with open(file_path, "r", encoding="utf-8") as f:
                    geojson_content = f.read()

                print(geojson_content)

                # Crear el FormData con el archivo leído
                form_data = {
                    "fileName": (None, filename),
                    "project": (None, self.project.name),
                    "location": (None, self.project.name),
                    "teams": (None, json.dumps([self.team.name])),
                    "categories": (None, json.dumps('')),
                }

                files_data = {
                    "geojson_file": (filename, geojson_content, "application/json"),
                }

                # Enviar la solicitud POST
                self.client.login(username="creatorUser", password="jamon")
                response = self.client.post(
                    self.upload_endpoint,
                    data=form_data,
                    files=files_data)

                # Verificar que el backend responde correctamente
                self.assertEqual(response.status_code, 200, f"Error al subir {filename}: {response}")

        end_time = datetime.now()
        print(f'Ending test at {end_time}')
        print(f'Test data creation test duration: {end_time - self.start_time}')

    def test_data_analysis(self):
        end_time = datetime.now()
        print(f'Ending test at {end_time}')
        print(f'Data analysis test duration: {end_time - self.start_time}')
