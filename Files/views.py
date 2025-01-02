"""
Files' app views to develop file management functions
"""

# Create your views here.
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    """
    Main view where the user interacts with the Files app
    """
    template_name = 'Files/home.html'
