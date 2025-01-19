"""
Files' app views to develop file management functions
"""

import json

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .models import File, Project, Assignations, Membership


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


def get_user_teams(user: User):
    user_membership = Membership.objects.filter(member=user.id)
    user_teams = [membership.user_team for membership in user_membership]
    return user_teams


@login_required
@require_http_methods(["GET"])
def get_user_projects(request):
    try:
        # Get projects accessible to the current user

        user_teams = get_user_teams(request.user)
        user_assignations = Assignations.objects.filter(assignated_team__in=user_teams)
        user_projects = user_assignations.values('assignated_project') #[assignation.assignated_project for assignation in user_assignations]
        projects = Project.objects.filter(pk__in=user_projects).values('pk', 'name')

        # projects = Project.objects.filter(users=request.user).values('id', 'name')
        return JsonResponse({'projects': list(projects)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def upload_file(request):
    return JsonResponse({'test': 'test'}, status=200)
    # TODO pirula
    try:
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'status': 'error', 'message': 'No file provided'}, status=400)

        # Get other form data
        file_name = request.POST.get('fileName', file.name)
        projects = json.loads(request.POST.get('projects', '[]'))
        location = request.POST.get('location', '')
        teams = json.loads(request.POST.get('teams', '[]'))
        categories = json.loads(request.POST.get('categories', '[]'))

        # Process file and save to database
        file_record = File.objects.create(
            name=file_name,
            location=location,
            uploaded_by=request.user,
            file=file  # Assuming you have configured file storage
        )

        # Add relationships
        if projects:
            file_record.projects.set(Project.objects.filter(name__in=projects))

        # Add other relationships (teams, categories) as needed

        return JsonResponse({
            'status': 'success',
            'fileId': file_record.id,
            'message': 'File uploaded successfully'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
