"""
Files' app views to develop file management functions
"""

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import File, Project, Assignations, Membership, Team


# @login_required
def homepageView(request):
    """
    Main view where the user interacts with the Files app
    """
    # available_files = File.count_all_existing_files()
    # TODO: ficheros relacionados con proyectos no archivados que el usuario está asignado
    user_files = File.count_user_files(request.user)

    # proyectos en los que está asignado el usuario
    user_memberships = Membership.objects.filter(member=request.user.id)
    user_teams = [membership.user_team for membership in user_memberships]

    user_projects = Assignations.objects.filter(assignated_team__in=user_teams)
    print(user_projects)

    context = {
        'available_files': user_files,
        'projects': user_projects,
    }

    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'Files/home.html', context)


@login_required
def uploadFilesView(request):
    # proyectos en los que está asignado el usuario
    # user_memberships = Membership.objects.filter(member=request.user.id)
    # user_teams = [membership.user_team for membership in user_memberships]
    #
    # user_projects = Assignations.objects.filter(assignated_team__in=user_teams)
    # print(user_projects)
    #
    # context = {
    #     'projects': user_projects,
    # }

    return render(request, 'Files/upload_files/upload_files.html')
