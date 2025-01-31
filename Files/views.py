"""
Files' app views to develop file management functions
"""

import json
import os

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from Management.models import GlobalMembership, GlobalRole
from .models import File, Project, Assignations, Membership, Folder, Location, Access, Team, Category, \
    Classification, GeoJSON, GEOJSON_TYPE_CHOICES, GeoJSONFeature, PropertyAttribute, GeoJSONFeatureProperties
from shapely.geometry import shape


# @login_required
def homepageView(request):
    """
    Main view where the user interacts with the Files app
    """
    # available_files = File.count_all_existing_files()
    # TODO: ficheros relacionados con proyectos no archivados que el usuario está asignado, no ficheros que haya creado el usuario
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
@transaction.atomic
def upload_file(request):
    try:
        file_name = request.POST.get("fileName")
        file_project = request.POST.get("project")
        file_location = request.POST.get("location")
        file_teams = request.POST.get("teams")
        file_categories = request.POST.get("categories")
        geojson_content = request.FILES["geojson_file"].read().decode("utf-8")

        if not geojson_content:
            return JsonResponse({"error": "No se recibió un GeoJSON válido"}, status=400)

        teams_list = json.loads(file_teams)
        categories_list = json.loads(file_categories)
        geojson_data = json.loads(geojson_content)

        # Create GeoJSONFile
        content_type = geojson_data['type']
        content_type_id = GEOJSON_TYPE_CHOICES.index((content_type, content_type))
        current_user_object = User.objects.get(pk=request.user.id)
        geojson_file = GeoJSON.objects.create(
            creator=current_user_object,
            content_type=content_type_id,
            name=file_name
        )

        geojson_file_instance = File.objects.get(id=geojson_file.id)

        # Define file access
        for team_name in teams_list:
            team = Team.objects.get(name=team_name)
            access = Access.objects.create(accessed_file=geojson_file_instance, accessing_team=team)

        project = Project.objects.get(name=file_project)

        # Locate Folder
        if file_location == file_project:

            location = Location.objects.create(
                located_folder=None,
                located_project=project,
                located_file=geojson_file_instance
            )
        else:
            # TODO folder nueva
            # TODO subfolder de folder nueva
            folder = Folder.objects.filter(path=file_location)
            if not folder.exists():
                # si estamos aqui, la folder no es Project root
                # pero puede tener parents
                file_location_path = file_location.split('/')
                if len(file_location_path) == 1 or (len(file_location_path) == 2 and file_location_path[0] == file_project):
                    name = file_location_path[1] if len(file_location_path) == 2 else file_location_path[0]
                    folder = Folder.objects.create(name=name, parent=None)
                else:



                    # def getFolderParent(folder_name):

                    folder = build(file_location_path)


                    # Folder.objects.create(name=???, parent=???)
            else:
                folder = folder.first()
            location = Location.objects.create(
                located_folder=folder,
                located_project=project,
                located_file=geojson_file_instance
            )

        # Classify file
        if categories_list:
            for category_name in categories_list:
                category = Category.objects.get(label=category_name)
                classification = Classification.objects.create(related_file=geojson_file, category_name=category)

        # Add each geojson feature
        # content_type
        if content_type == 'Feature':
            geometry = geojson_data['geometry']
            geometry_type = geometry["type"]
            coordinates = geometry["coordinates"]

            # TODO create GeoJSONFeature geojson_file - geometry_type - geometry

            feature = shape({
                "type": geometry_type,
                "coordinates": coordinates
            })
            geojsonfeature = GeoJSONFeature.objects.create(
                file=geojson_file,
                feature_type=geometry_type,
                geometry=GEOSGeometry(feature.wkt)
            )


            properties = geojson_data['properties']
            for (key, value) in properties.items():
                attribute_name = key
                attribute_type = type(json.loads(f'"{value}"'))
                attribute_value = value
        #       TODO create PropertyAttribute attribute_name - attribute_type
                propertyAttribute = PropertyAttribute.objects.create(
                    attribute_name=attribute_name,
                    attribute_type=attribute_type
                )


        #       TODO create GeoJSONFeatureProperties GeoJSONFeature - PropertyAttribute - attribute_value
                geojsonFeatureProperty = GeoJSONFeatureProperties.objects.create(
                    feature=geojsonfeature,
                    attribute=propertyAttribute,
                    attribute_value=attribute_value
                )

        else:
            for feature in geojson_data['features']:
                # TODO
                pass
        '''
        1. Create a GeoJSONFile
            - content_type = geojson_content.type
            - name = filename
            
        2. ACCESS
            - accessed_file
            - accessing_team = file_team
            
        3. FOLDER
            (if file_location does not exist)
            - name
            - parent
            
        4. LOCATION
            - located_file
            - located_project
            - located_folder
            - path
        
        5. CLASSIFICATION
            - related_file
            - category_name
            
            
        6. GEOJSONFEATURE
            - feature_type = geojson_content.features.type
            - geometry = geojson_content.features.coordinates
            - attribute_name = geojson_content.properties.key
            - attribute_type = type(geojson_content.properties.value)
            - attribute_value = geojson_content.properties.value
        
        7. CONTENT
            - geojson_file
            - feature
                
        '''

        return JsonResponse({'status': 'success'}, status=200)
    except json.JSONDecodeError as e:
        return JsonResponse({"error": "El contenido no es un JSON válido", "details": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def create_folder(name, parent):
    return Folder.objects.create(name=name, parent=parent)


def folderExists(name, path):
    return Folder.objects.filter(name=name, path=path).exists()



def build(file_location_path):
    parent = file_location_path[:-1] if len(file_location_path) > 2 else file_location_path[:-1]

    # if len(parent) == 1:
    # aqui hemos llegado a la subcarpeta antes de raiz
    parent_name = parent[0] if len(parent) == 1 else parent[-2]
    parent_path = parent_name#None

    # else:
    if len(parent) > 1:
        # TODO TEST
        # parent_path = os.path.join(file_location_path[:-4], parent)
        new_parent = build(parent)
        parent_path = new_parent.path
        parent_name = new_parent.name


    if not folderExists(parent_name, parent_path):
        parent = create_folder(parent_name, parent_path)
    else:
        parent = Folder.objects.filter(name=parent_name, path=parent_path).first()
    folder = create_folder(file_location_path[-1], parent)
    return folder

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
            'path': location.located_folder.path if location.located_folder else '',
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
