"""
Files' app views to develop file management functions
"""

# Create your views here.
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# @login_required
def homepageView(request):
    """
    Main view where the user interacts with the Files app
    """
    return render(request, 'Files/home.html')
