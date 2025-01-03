"""
Files' app views to develop file management functions
"""

# Create your views here.
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import File


# @login_required
def homepageView(request):
    """
    Main view where the user interacts with the Files app
    """
    available_files = File.count_existing()#.objects.count()

    context = {
        'available_files': available_files,
    }

    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'Files/home.html', context)


@login_required
def uploadFilesView(request):
    return render(request, 'upload_files/upload_files.html')