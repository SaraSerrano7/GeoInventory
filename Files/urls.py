"""
URLs-VIEWS mapping file
"""
from django.urls import path

from .views import homepageView, uploadFilesView, upload_file, get_user_projects

urlpatterns = [
    path('', homepageView, name='home'),
    path('upload_files/', uploadFilesView, name='upload_files'),
    path('api/user_projects/', get_user_projects, name='user-projects'),
    path('api/upload/', upload_file, name='upload-file'),
]
