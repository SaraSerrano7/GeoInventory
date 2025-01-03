"""
URLs-VIEWS mapping file
"""
from django.urls import path

from .views import homepageView, uploadFilesView

urlpatterns = [
    path('', homepageView, name='home'),
    path('upload_files/', uploadFilesView, name='upload_files'),
]
