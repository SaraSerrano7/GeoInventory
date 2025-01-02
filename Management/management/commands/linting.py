import os
import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "This command helps pylinting project files"

    FILES_TO_CHECK = [
        # "manage.py",
        "GeoInventory/settings.py",
        "GeoInventory/urls.py",
        # "GeoInventory/wsgi.py",
        # "GeoInventory/asgi.py",
        # "Api/admin.py",
        # "Api/apps.py",
        # "Api/models.py",
        # "Api/tests.py",
        # "Api/urls.py",
        # "Api/views.py",
        "Files/admin.py",
        "Files/apps.py",
        "Files/models.py",
        "Files/tests.py",
        "Files/urls.py",
        "Files/views.py",
    ]

    def add_arguments(self, parser):
        pass

    def run_pylint(self, files):
        """
        Executes Pylint for a file list
        :param files: File list to analyze
        """
        for file in files:
            if os.path.exists(file):
                print(f"Running pylint for: {file}")
                try:
                    # Ejecuta pylint y captura la salida
                    subprocess.run(
                        ["pylint", file],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    print(f"✔ Pylint passed for {file}\n")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Pylint issues found in {file}:\n{e.stdout}\n{e.stderr}")
            else:
                print(f"❌ File or directory not found: {file}")

        print('Remember to perform python3 manage.py check before use!')

    def handle(self, *args, **options):
        self.run_pylint(self.FILES_TO_CHECK)
