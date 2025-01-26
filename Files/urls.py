"""
URLs-VIEWS mapping file
"""
from django.urls import path

from .views import homepageView, uploadFilesView, upload_file, get_user_projects, get_project_folders, delete_folder, \
    get_user_teams, get_categories

urlpatterns = [
    path('', homepageView, name='home'),
    path('upload_files/', uploadFilesView, name='upload_files'),
    path('api/user_projects/', get_user_projects, name='user-projects'),
    path('api/user_teams/<str:project_name>', get_user_teams, name='user-teams'),
    path('api/categories/', get_categories, name='categories'),
    path('api/upload/', upload_file, name='upload-file'),
    path('api/project_folders/<str:project_name>', get_project_folders, name='project-folders'),
    path('api/project_folders/', get_project_folders, name='root-folders'),
    path('api/delete-folder/', delete_folder, name='delete-folder'),
]
