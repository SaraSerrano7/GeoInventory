import os
import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "This command auto populates db for sample use"

    def add_arguments(self, parser):
        pass

    def db_autofill(self):
        print('Creating users: guestUser')
        print('Creating users: viewerUser')
        print('Creating users: creatorUser')
        print('Creating users: adminUser')
        print('Creating users: superadminUser')
        print('Creating roles: guest')
        print('Creating roles: viewer')
        print('Creating roles: creator')
        print('Creating roles: admin')
        print('Creating globalrole: regular')
        print('Creating globalrole: superadmin')
        print('Creating globalmembership: superadminUser - superadmin')
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
