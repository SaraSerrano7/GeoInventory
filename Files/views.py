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

from Management.models import GlobalMembership, GlobalRole
from .models import File, Project, Assignations, Membership, Folder, Location, Access, Team, Category


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

    user_projects = Assignations.objects.filter(assignated_team__in=user_teams, assignated_project__active=True)
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


def find_user_teams(user: User):
    # TODO si eres superadmin debes poder elegir cualquier proyecto

    user_membership = Membership.objects.filter(member=user)
    user_teams = [membership.user_team for membership in user_membership]
    return user_teams


def query_user_teams(user: User):
    user_teams = Team.objects.filter(membership__member=user)
    return user_teams


@login_required
@require_http_methods(["GET"])
def get_user_projects(request):
    try:
        # Get projects accessible to the current user

        # TODO si eres super admin puedes ver todos los proyectos activos
        user_global_role = GlobalMembership.objects.get(related_user=request.user.id)
        if user_global_role.user_type.name == 'superadmin':
            projects = Project.objects.filter(active=True).values('pk', 'name')
        else:
            user_teams = find_user_teams(request.user)
            user_assignations = Assignations.objects.filter(assignated_team__in=user_teams)
            user_projects = user_assignations.values(
                'assignated_project')  # [assignation.assignated_project for assignation in user_assignations]
            projects = Project.objects.filter(pk__in=user_projects, active=True).values('pk', 'name')

        # projects = Project.objects.filter(users=request.user).values('id', 'name')
        return JsonResponse({'projects': list(projects)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def user_is_superadmin(user):
    gloabl_role = GlobalRole.objects.get(globalmembership__related_user=user)
    return gloabl_role.name == 'superadmin'


def user_is_project_admin(user, project):
    assignations = Assignations.objects.filter(assignated_project__name=project,
                                               assignated_team__membership__member=user,
                                               assignated_team__membership__user_role=5)
    return True if assignations else False


@login_required
@require_http_methods(["GET"])
def get_user_teams(request, project_name=None):
    try:
        print('wtf bro')
        # Get teams where current user is member
        # TODO si eres superadmin deberias tener todos los teams del proyecto
        # TODO si en el proyecto seleccionado eres admin, puedes seleccionar a cualquier equipo asignado al proyecto

        current_user = request.user
        print(current_user)

        if user_is_superadmin(current_user) or user_is_project_admin(current_user, project_name):
            user_teams = Team.objects.filter(assignations__assignated_project__name=project_name).values('name')
            # user_teams = query_user_teams(request.user).values('name')
        else:
            user_teams = query_user_teams(request.user).values('name')

        # projects = Project.objects.filter(users=request.user).values('id', 'name')
        return JsonResponse({'teams': list(user_teams)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_categories(request):
    try:
        # categories = query_user_teams(request.user).values('name')
        categories = Category.objects.all().values('label')
        return JsonResponse({'categories': list(categories)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def upload_file(request):
    try:
        print('uploading')

        file_name = request.POST.get("fileName")
        file_project = request.POST.get("project")
        file_location = request.POST.get("location")
        file_teams = request.POST.get("teams")
        file_categories = request.POST.get("categories")
        geojson_content = request.FILES["geojson_file"].read().decode("utf-8")

        if not geojson_content:
            return JsonResponse({"error": "No se recibió un GeoJSON válido"}, status=400)

        try:
            geojson_data = json.loads(geojson_content)
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "El contenido no es un JSON válido", "details": str(e)}, status=400)

        #     # Process file and save to database
        #     file_record = File.objects.create(
        #         name=file_name,
        #         location=location,
        #         uploaded_by=request.user,
        #         file=file  # Assuming you have configured file storage
        #     )

        return JsonResponse({'test': 'test'}, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_project_folders(request, project_name=None):
    try:
        locations = []
        if project_name:

            # nota: para haber obtenido un project name, ya se ha seleccionado de una lista de proyectos activos
            project_locations = Location.objects.filter(located_project__name=project_name)
            for location in project_locations:
                file = location.located_file
                if file:
                    accessible = Access.objects.filter(accessed_file=file,
                                                       accessing_team__membership__member=request.user.id)
                    if accessible:
                        locations.append(location)
                # folders = Folder.objects.filter(project__name=project_name)

        else:
            # Get root folders
            # TODO simplificacion: si no hay project name, son ficheros 'sin clasificar'
            locations = Folder.objects.filter(project__isnull=True)

        # Convert to list of dicts with path and empty status
        folder_list = [{
            'path': location.located_folder.path,
            'is_empty': location.located_file is None  # Assuming you have a related_name='files' on your File model
        } for location in locations]

        print(folder_list)
        return JsonResponse(folder_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def delete_folder(request):
    try:
        data = json.loads(request.body)
        path = data.get('path')

        folder = Folder.objects.get(path=path)

        if folder.files.exists():
            return JsonResponse({'message': 'Cannot delete folder: it contains files'}, status=400)

        folder.delete()
        return JsonResponse({'message': 'Folder deleted successfully'})
    except Folder.DoesNotExist:
        return JsonResponse({'message': 'Folder not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
