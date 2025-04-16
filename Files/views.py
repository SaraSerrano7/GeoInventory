"""
Files' app views to develop file management functions
"""

import json

import requests
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Polygon
from django.core.handlers.wsgi import WSGIRequest
from django.db import connection
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from shapely.geometry import shape

from Management.models import GlobalMembership, GlobalRole
from .models import File, Project, Assignations, Membership, Folder, Location, Access, Team, Category, \
    Classification, GeoJSON, GEOJSON_TYPE_CHOICES, GeoJSONFeature, PropertyAttribute, GeoJSONFeatureProperties

import psycopg2
from psycopg2.extras import RealDictCursor


# from django.contrib.gis.db.models.functions import GeometryDump


# @login_required
def homepageView(request):
    """
    Main view where the user interacts with the Files app
    """
    # available_files = File.count_all_existing_files()
    user_files = File.count_user_files(request.user)

    # proyectos en los que está asignado el usuario
    user_memberships = Membership.objects.filter(member=request.user.id)
    user_teams = [membership.user_team for membership in user_memberships]

    user_projects = Assignations.objects.filter(assignated_team__in=user_teams, assignated_project__active=True)

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
        # Get teams where current user is member

        current_user = request.user

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

        sql_queries(request_user_id=request.user.id,
                    content_type_id=content_type_id,
                    file_name=file_name,
                    teams_list=teams_list,
                    file_project=file_project,
                    file_location=file_location,
                    categories_list=categories_list,
                    geojson_data=geojson_data,
                    content_type=content_type)

        # current_user_object = User.objects.get(pk=request.user.id)
        # geojson_file = GeoJSON.objects.create(
        #     creator=current_user_object,
        #     content_type=content_type_id,
        #     name=file_name
        # )
        #
        # geojson_file_instance = File.objects.get(id=geojson_file.id)
        #
        # # Define file access
        # for team_name in teams_list:
        #     team = Team.objects.get(name=team_name)
        #     access = Access.objects.create(accessed_file=geojson_file_instance, accessing_team=team)
        #
        # project = Project.objects.get(name=file_project)
        #
        # # Locate Folder
        # if file_location == file_project:
        #
        #     location = Location.objects.create(
        #         located_folder=None,
        #         located_project=project,
        #         located_file=geojson_file_instance
        #     )
        # else:
        #     folder = Folder.objects.filter(path=file_location)
        #     if not folder.exists():
        #         # si estamos aqui, la folder no es Project root
        #         # pero puede tener parents
        #         file_location_path = file_location.split('/')
        #         if len(file_location_path) == 1 or (
        #                 len(file_location_path) == 2 and file_location_path[0] == file_project):
        #             name = file_location_path[1] if len(file_location_path) == 2 else file_location_path[0]
        #             folder = Folder.objects.create(name=name, parent=None)
        #         else:
        #
        #             folder = build(file_location_path)
        #     else:
        #         folder = folder.first()
        #     location = Location.objects.create(
        #         located_folder=folder,
        #         located_project=project,
        #         located_file=geojson_file_instance
        #     )
        #
        # # Classify file
        # if categories_list:
        #     for category_name in categories_list:
        #         category = Category.objects.get(label=category_name)
        #         classification = Classification.objects.create(related_file=geojson_file, category_name=category)
        #
        # # Add each geojson feature
        # if content_type == 'Feature':
        #     create_feature(geojson_file, geojson_data)
        #
        # else:
        #     for feature in geojson_data['features']:
        #         create_feature(geojson_file, feature)

        return JsonResponse({'status': 'success'}, status=200)
    except json.JSONDecodeError as e:
        return JsonResponse({"error": "El contenido no es un JSON válido", "details": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def sql_queries(request_user_id, content_type_id, file_name, teams_list,
                file_project, file_location, categories_list,
                geojson_data, content_type):
    from django.conf import settings
    from django.db import connection

    with open('GeoInventory/config/db.conf') as db_file:
        credentials = db_file.read()

    cred_keys = [key.split('=') for key in credentials.split('\n')]
    keys = {}
    for key in cred_keys:
        if key != ['']:
            keys[key[0]] = key[1][1:-1]

    DB_CONFIG = {
        'host': settings.DATABASES['default']['HOST'] or 'localhost',
        'database': settings.DATABASES['default']['NAME'],
        'user': settings.DATABASES['default']['USER'],
        'password': settings.DATABASES['default']['PASSWORD'],
        'port': settings.DATABASES['default']['PORT'] or 5432,
    }

    try:
        # Conectar a la base de datos
        # conn = psycopg2.connect(**DB_CONFIG)
        # # Utilizamos RealDictCursor para obtener resultados como diccionarios
        # cur = conn.cursor(cursor_factory=RealDictCursor)

        # Iniciar la transacción
        # conn.autocommit = False

        # 1. Obtener el usuario actual
        # query_get_user = "SELECT * FROM public.auth_user WHERE id = %(user_id)s;"
        # cur.execute(query_get_user, {'user_id': request_user_id})
        # current_user_object = cur.fetchone()
        current_user_object = None
        with connection.cursor() as cur:
            query_get_user = "SELECT * FROM public.auth_user WHERE id = %s;"
            cur.execute(query_get_user, [request_user_id])
            current_user_object = cur.fetchone()

            if not current_user_object:
                raise Exception("Usuario no encontrado")

            # 2. Crear registro en GeoJSON
            # query_create_geojson = """
            #     INSERT INTO public."Files_geojson" (creator_id, content_type, name)
            #     VALUES (%(creator_id)s, %(content_type)s, %(name)s)
            #     RETURNING id;
            #     """
            query_create_geojson = """
            WITH digital_resource AS (
                INSERT INTO public."Files_digitalresource" (creator_id, created_at, deleted)
                VALUES (%(creator_id)s, NOW(), false)
                RETURNING id
            ), file AS (
                INSERT INTO public."Files_file" (digitalresource_ptr_id, name)
                VALUES ((SELECT id FROM digital_resource), %(name)s)
                RETURNING digitalresource_ptr_id
            )
            INSERT INTO public."Files_geojson" (file_ptr_id, content_type)
            VALUES ((SELECT digitalresource_ptr_id FROM file), %(content_type)s) 
            RETURNING file_ptr_id;
            """

            cur.execute(query_create_geojson, {
                'creator_id': current_user_object[0],
                'content_type': content_type_id,
                'name': file_name
            })
            geojson_file = cur.fetchone()
            geojson_file_id = geojson_file[0]

            geojson_fields = GeoJSON._meta.fields
            geojson_model_info = [(geojson_fields[i].name, attr) for i, attr in enumerate(geojson_file)]

            # 3. Obtener el objeto File asociado. Nota: innecesario, sql solo me devolverá el id
            # Suponiendo que la tabla file tiene el mismo id que geojson
            query_get_file = """SELECT * FROM public."Files_file" WHERE digitalresource_ptr_id = %(file_id)s;"""
            cur.execute(query_get_file, {'file_id': geojson_file_id})
            geojson_file_instance = cur.fetchone()
            if not geojson_file_instance:
                raise Exception("No se encontró el registro en file para el GeoJSON creado")

            # 4. Definir accesos para cada equipo en teams_list
            for team_name in teams_list:
                # 4.a Obtener el equipo
                query_get_team = """SELECT * FROM public."Files_team" WHERE name = %(team_name)s;"""
                cur.execute(query_get_team, {'team_name': team_name})
                team = cur.fetchone()
                if not team:
                    raise Exception(f"Equipo {team_name} no encontrado")

                # 4.b Crear el registro de acceso
                query_create_access = """
                    WITH digital_resource AS (
                        INSERT INTO public."Files_digitalresource" (creator_id, created_at, deleted)
                        VALUES (%(creator_id)s, NOW(), false)
                        RETURNING id
                    )
                    
                    INSERT INTO public."Files_access" (digitalresource_ptr_id, accessed_file_id, accessing_team_id)
                    VALUES ((SELECT id FROM digital_resource), %(file_id)s, %(team_id)s);
                    """
                cur.execute(query_create_access, {
                    'creator_id': current_user_object[0],
                    'file_id': geojson_file_instance[0],
                    'team_id': team[0]
                })

            # 5. Obtener el proyecto a partir de file_project
            query_get_project = """SELECT * FROM public."Files_project" WHERE name = %(project_name)s;"""
            cur.execute(query_get_project, {'project_name': file_project})
            project = cur.fetchone()
            if not project:
                raise Exception("Proyecto no encontrado")

            # 6. Ubicar Folder y registrar la ubicación (Location)
            if file_location == file_project:
                # Si file_location equivale al nombre del proyecto
                query_create_location = """
                    WITH digital_resource AS (
                        INSERT INTO public."Files_digitalresource" (creator_id, created_at, deleted)
                        VALUES (%(creator_id)s, NOW(), false)
                        RETURNING id
                    )
                    
                    INSERT INTO public."Files_location" (digitalresource_ptr_id, path, located_folder_id, located_project_id, located_file_id)
                    VALUES ((SELECT id FROM digital_resource), '', NULL, %(project_id)s, %(file_id)s);
                    """
                cur.execute(query_create_location, {
                    'creator_id': current_user_object[0],
                    'project_id': project[0],
                    'file_id': geojson_file_instance[0]
                })
            else:
                # TODO
                # Buscar si la carpeta ya existe
                query_get_folder = "SELECT * FROM public.Files_Folder WHERE path = %(folder_path)s;"
                cur.execute(query_get_folder, {'folder_path': file_location})
                folder = cur.fetchone()

                if not folder:
                    # Si la carpeta no existe, se determina si es de raíz o se necesita construir la ruta.
                    file_location_path = file_location.split('/')
                    if len(file_location_path) == 1 or (
                            len(file_location_path) == 2 and file_location_path[0] == file_project):
                        # Carpeta sin padre (root o subcarpeta inmediata)
                        # Si hay 2 elementos, usamos el segundo como nombre; si es 1, ese es el nombre.
                        name = file_location_path[1] if len(file_location_path) == 2 else file_location_path[0]
                        query_create_folder = """
                            INSERT INTO public.Files_Folder (name, parent_id, path)
                            VALUES (%(name)s, NULL, %(path)s)
                            RETURNING id;
                            """
                        cur.execute(query_create_folder, {'name': name, 'path': file_location})
                        folder = cur.fetchone()
                    else:
                        # Aquí se implementaría la lógica recursiva de 'build'
                        # Para efectos de ejemplo, se simula la creación de la carpeta intermedia
                        # Nota: Implementa la función build utilizando bucles y llamadas recursivas si es necesario
                        # En este ejemplo, se crea la carpeta final sin procesar la jerarquía.
                        query_create_folder = """
                            INSERT INTO public.Files_Folder (name, parent_id, path)
                            VALUES (%(name)s, NULL, %(path)s)
                            RETURNING id;
                            """
                        cur.execute(query_create_folder, {'name': file_location_path[-1], 'path': file_location})
                        folder = cur.fetchone()
                # Crear la ubicación con la carpeta identificada
                query_create_location = """
                    INSERT INTO public.Files_Location (located_folder_id, located_project_id, located_file_id)
                    VALUES (%(folder_id)s, %(project_id)s, %(file_id)s);
                    """
                cur.execute(query_create_location, {
                    'folder_id': folder['id'],
                    'project_id': project['id'],
                    'file_id': geojson_file_instance['id']
                })

            # 7. Clasificar el archivo si hay categorías
            if categories_list:
                for category_name in categories_list:
                    # Obtener la categoría
                    query_get_category = "SELECT * FROM category WHERE label = %(label)s;"
                    cur.execute(query_get_category, {'label': category_name})
                    category = cur.fetchone()
                    if not category:
                        raise Exception(f"Categoría {category_name} no encontrada")
                    # Crear la clasificación
                    query_create_classification = """
                        INSERT INTO classification (related_file_id, category_name_id)
                        VALUES (%(file_id)s, %(category_id)s);
                        """
                    cur.execute(query_create_classification, {
                        'file_id': geojson_file_id,
                        'category_id': category['id']
                    })

            # 8. Crear GeoJSON Features y sus propiedades
            def create_feature(geojson_file_id, feature_data):
                # Extraer la geometría
                geometry = feature_data['geometry']
                geometry_type = geometry["type"]
                # Convierte la geometría a WKT, suponiendo que usas la librería shapely
                from shapely.geometry import shape
                feature_shape = shape(geometry)
                wkt = feature_shape.wkt

                # Crear la feature
                query_create_feature = """
                    INSERT INTO public."Files_geojsonfeature" (file_id, feature_type, geometry)
                    VALUES (%(file_id)s, %(feature_type)s, ST_GeomFromText(%(wkt)s))
                    RETURNING id;
                    """
                cur.execute(query_create_feature, {
                    'file_id': geojson_file_id,
                    'feature_type': geometry_type,
                    'wkt': wkt
                })
                geojsonfeature = cur.fetchone()
                geojsonfeature_id = geojsonfeature[0]

                # Insertar las propiedades (cada par clave-valor)
                properties = feature_data.get('properties', {})
                for key, value in properties.items():
                    # Determinar el tipo de atributo; en este ejemplo simplemente se usa el nombre del tipo devuelto por type()
                    attribute_type = type(value).__name__
                    query_create_attribute = """
                        INSERT INTO public."Files_propertyattribute" (attribute_name, attribute_type)
                        VALUES (%(attribute_name)s, %(attribute_type)s)
                        RETURNING id;
                        """
                    cur.execute(query_create_attribute, {
                        'attribute_name': key,
                        'attribute_type': attribute_type
                    })
                    property_attribute = cur.fetchone()
                    property_attribute_id = property_attribute[0]

                    query_create_feature_property = """
                        INSERT INTO public."Files_geojsonfeatureproperties" (feature_id, attribute_id, attribute_value)
                        VALUES (%(feature_id)s, %(attribute_id)s, %(attribute_value)s);
                        """
                    cur.execute(query_create_feature_property, {
                        'feature_id': geojsonfeature_id,
                        'attribute_id': property_attribute_id,
                        'attribute_value': value
                    })

            # Llamar a create_feature en función del content_type y geojson_data recibido
            if content_type == 'Feature':
                create_feature(geojson_file_id, geojson_data)
            else:
                # Para cada feature en geojson_data['features']
                for feature in geojson_data.get('features', []):
                    create_feature(geojson_file_id, feature)

        # Si todo fue exitoso, se confirma la transacción
        # conn.commit()
        print("Operación completada exitosamente.")

    except Exception as e:
        # En caso de error, se revierte la transacción
        # if conn:
        #     conn.rollback()
        print(f"Error: {e}")

    finally:
        # Cerrar cursor y conexión
        if cur:
            cur.close()
        # if conn:
        #     conn.close()


def create_feature(geojson_file, geojson_data):
    geometry = geojson_data['geometry']
    geometry_type = geometry["type"]
    coordinates = geometry["coordinates"]

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
        propertyAttribute = PropertyAttribute.objects.create(
            attribute_name=attribute_name,
            attribute_type=attribute_type
        )

        geojsonFeatureProperty = GeoJSONFeatureProperties.objects.create(
            feature=geojsonfeature,
            attribute=propertyAttribute,
            attribute_value=attribute_value
        )


def create_folder(name, parent):
    return Folder.objects.create(name=name, parent=parent)


def folderExists(name, path):
    return Folder.objects.filter(name=name, path=path).exists()


def build(file_location_path):
    parent = file_location_path[:-1] if len(file_location_path) > 2 else file_location_path[:-1]

    # aqui hemos llegado a la subcarpeta antes de raiz
    parent_name = parent[0] if len(parent) == 1 else parent[-2]
    parent_path = parent_name  # None

    # else:
    if len(parent) > 1:
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
            locations = Folder.objects.filter(project__isnull=True)

        # Convert to list of dicts with path and empty status
        folder_list = [{
            'path': location.located_folder.path if location.located_folder else '',
            'is_empty': location.located_file is None  # Assuming you have a related_name='files' on your File model
        } for location in locations]

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


#################
# File explorer #
#################


def get_user_project_files(user, project_name):
    try:
        locations = []
        files = []

        project_locations = Location.objects.filter(located_project__name=project_name)
        for location in project_locations:
            file = location.located_file
            if file:
                accessible = Access.objects.filter(accessed_file=file,
                                                   accessing_team__membership__member=user.id)
                if accessible or user_is_superadmin(user):
                    locations.append(location)
                    files.append({
                        'path': location.located_folder.path if location.located_folder else '',
                        'file': file.name,
                        'id': file.id
                    })

        return files

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_file_structure(request):
    test_structure = []

    current_user = request.user
    user_projects = json.loads(get_user_projects(request).content.decode('utf-8'))['projects']
    for project in user_projects:
        # get_project_folders ya me retorna las ubicaciones accesibles por el usuario
        # '' significa que usa el Project's root
        user_files = get_user_project_files(current_user, project['name'])
        print(f'{len(user_files)} files')
        for user_file in user_files:

            find_equal = [project_struct['name'] == project['name'] for project_struct in test_structure]
            exists_proj = find_equal.count(True)
            if exists_proj:
                proj_index = find_equal.index(True)
                test_structure[proj_index].update(
                    {
                        'type': 'folder',
                        'name': project['name'],
                        'path': f'/{project["name"]}/',
                        'children': build_file_structure(
                            test_structure[proj_index]['children'],
                            user_file,
                            project['name'])
                    }
                )
            else:

                test_structure.append(
                    {
                        'type': 'folder',
                        'name': project['name'],
                        'path': f'/{project["name"]}/',
                        'children': build_file_structure(
                            [],
                            user_file,
                            project['name'])
                    }
                )

    structure = [
        {
            "type": "folder",
            "name": "Project 1",
            "path": "/project1",
            "children": [
                {
                    "type": "file",
                    "id": "1",
                    "name": "data.txt",
                    "path": "/project1/data.txt"
                }
            ]
        },
        {
            "type": "folder",
            "name": "Project 2",
            "path": "/project2",
            "children": [
                {
                    "type": "folder",
                    "name": "input",
                    "path": "/project2/input",
                    "children": [
                        {
                            "type": "file",
                            "id": "2",
                            "name": "rawData",
                            "path": "/project2/input/rawData.geojson"
                        }
                    ]
                }
            ]
        }
    ]
    return JsonResponse(test_structure, safe=False)


def build_file_structure(current_structure, user_file, project_name):
    file_name = user_file['file']
    file_id = user_file['id']
    folder_path = user_file['path']
    acc_path = f'{project_name}'

    if folder_path == '':
        current_structure.append(build_recursive(current_structure, file_name, folder_path, acc_path, file_id)[0])
        return current_structure

    struct = build_recursive(current_structure, file_name, folder_path, acc_path, file_id)
    return struct


def build_recursive(current_structure, file_name, folder_path, acc_path, file_id):
    file_path_parts = folder_path.split('/')
    if len(file_path_parts[0]) == 0:
        return [{
            'type': 'file',
            'name': file_name,
            'id': file_id,
            'path': f'{acc_path}/{file_name}'
        }]
    else:
        folder_name = file_path_parts[0]
        next_folder_path = folder_path.removeprefix(folder_name)[1:]
        next_acc_path = f'{acc_path}/{folder_name}'

        if current_structure:
            for children in current_structure:
                if children['type'] == 'folder' and children['name'] == folder_name:
                    child_struct_index = current_structure.index(children)
                    child_struct = current_structure[child_struct_index]['children']

                    if next_folder_path == '':
                        child_struct.append(
                            build_recursive(child_struct, file_name, next_folder_path, next_acc_path, file_id)

                        )
                        return current_structure
                    else:

                        current_structure[child_struct_index].update(
                            {
                                'type': 'folder',
                                'name': folder_name,
                                'path': f'{acc_path}/{folder_name}',
                                'children': build_recursive(child_struct, file_name, next_folder_path, next_acc_path,
                                                            file_id)
                            }
                        )
                        return current_structure

                else:
                    continue
            next_struct = [children for children in current_structure]
            next_struct.append({
                'type': 'folder',
                'name': folder_name,
                'path': f'{acc_path}/{folder_name}',
                'children': build_recursive([], file_name, next_folder_path, next_acc_path, file_id)
            })
            return next_struct

        else:

            return [{
                'type': 'folder',
                'name': folder_name,
                'path': f'{acc_path}/{folder_name}',
                'children': build_recursive(current_structure, file_name, next_folder_path, next_acc_path, file_id)
            }]


@require_http_methods(["POST"])
def get_file_content(request):
    try:
        data = json.loads(request.body)
        files = data.get('files', [])
        files_id_list = [file['id'] for file in files]
        files_list = GeoJSON.objects.filter(pk__in=files_id_list)
        _content = []
        for file in files_list:
            _content.append({
                'file_id': file.pk,
                'file_content': build_geojson(file)
            })

        content = ""
        for file_path in files:
            content += f"Content of {file_path}\n"

        return JsonResponse({"content": _content})
    except Exception as e:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def build_geojson(geojson_file: GeoJSON):
    geojson = {}

    geojson_type = geojson_file.content_type
    if geojson_type.isdigit():
        geojson_type = GEOJSON_TYPE_CHOICES[int(geojson_type)][0]

    geojson['type'] = geojson_type
    if geojson_type == 'Feature':
        geojson_feature = GeoJSONFeature.objects.get(file=geojson_file)
        geojson = add_geojson_feature(geojson, geojson_feature)

    else:
        # TODO
        features = []
        geojson_features = GeoJSONFeature.objects.filter(file=geojson_file)
        for feature in geojson_features:
            prepared_feautre = add_geojson_feature({}, feature)
            prepared_feautre['type'] = 'Feature'
            features.append(prepared_feautre)

        geojson['features'] = features

    return geojson


def add_geojson_feature(geojson, geojson_feature):
    geojson['geometry'] = json.loads(geojson_feature.geometry.geojson)
    properties = {}

    feature_properties_list = GeoJSONFeatureProperties.objects.filter(feature=geojson_feature)
    for feature_property in feature_properties_list:
        property_name = feature_property.attribute.attribute_name
        # Para este caso de uso realmente no me hace falta el tipo, estoy mandando un geojson, acabara en str....
        property_value = feature_property.attribute_value
        properties[property_name] = property_value

    geojson['properties'] = properties
    return geojson


@require_http_methods(["POST"])
def analyze_files(request):
    '''
    se supone que le llega el perimetro del area a buscar y los ficheros seleccionados
    si no sabes donde tienes los datos, puedes seleccioanrlos todos y buscar entre todos
    si sabes que pueden estar en unos en concreto pero no recuerdas en cual, puedes buscar entre ellos
    - podrias darle a visualizar los ficheros y navegar con el mapa
    - y si no recuerdas donde esta el fichero?
    - aparte, tu quiza recuerdas que en la zona de lleida (provincia) tienes los ficheros F1, F2 y F3.
        - aqui tu puedes elegir buscar cuales son los ficheros que tienen geometrias de Lleida (ciudad)
        - sin embargo, quiza no recuerdes que también tenías el fichero F4, relativo al municipio de Lleida.
        - por tanto, el resultado de la busqueda será:
            - Ficheros resultantes de los que tu has seleccionado
            - Ficheros resultantes del resto que no has seleccionado, por si acaso
    '''
    data = json.loads(request.body)
    files = data.get('fileIds', [])
    points = data.get('points', [])
    if not files or not points:
        return JsonResponse({'error': 'No results found'}, status=404)

    # TODO
    analysis_type = data.get('analysisType', 'default')
    if analysis_type == 'default':
        return find_content_by_area(files, points, request)
    elif analysis_type == 'find_content_by_area':
        return find_content_by_area(files, points, request)
    return JsonResponse({'error': 'Internal server error'}, status=500)


def find_content_by_area(selected_files: list, points: list, request: WSGIRequest) -> JsonResponse:
    # id, file_id, geometry, matching_type
    found_features = search_geometries_in_roi(points)
    found_contained_files = [feature[1] for feature in found_features if feature[3] == 'Contenida']
    found_intersected_files = [feature[1] for feature in found_features if feature[3] == 'Intersectando']

    # max_dist = max(Point(p1).distance(Point(p2)) for p1 in points for p2 in points)
    # search_threshold = max_dist * 0.05

    # near = GeoJSONFeature.objects.annotate(dist=Distance('geometry', roi)).filter(dist__lte=search_threshold)

    matching_contained_files = [fileId for fileId in found_contained_files if str(fileId) in selected_files]
    matching_intersected_files = [fileId for fileId in found_intersected_files if str(fileId) in selected_files]
    # matching_near_files = any([file.pk for file in found_near_files if file.pk in selected_files])

    all_files_ids = get_user_files(request)

    non_matching_contained_files = [file for file in all_files_ids if file not in matching_contained_files]
    non_matching_intersected_files = [file for file in all_files_ids if file not in matching_contained_files]
    # non_matching_near_files = any(
    #     [file.pk for file in found_near_files if file.pk not in selected_files and file.pk in all_files_ids])

    matching_contained_files_content = build_geojson_files(matching_contained_files)
    matching_intersected_files_content = build_geojson_files(matching_intersected_files)
    # TODO los primeros ficheros estan bugueados, pero esto deberia funcionar
    # non_matching_contained_files_content = build_geojson_files(non_matching_contained_files)
    # non_matching_intersected_files_content = build_geojson_files(non_matching_intersected_files)

    return JsonResponse({
        "matching_contained_files": matching_contained_files_content,
        "matching_intersected_files": matching_intersected_files_content,
        # "matching_near_files": matching_near_files,
        # "non_matching_contained_files": non_matching_contained_files_content,
        # "non_matching_intersected_files": non_matching_intersected_files_content,
        # "non_matching_near_files": non_matching_near_files
    })


def build_geojson_files(files: list[int]) -> list[dict]:
    files_content = []
    for fileId in files:
        file = GeoJSON.objects.get(pk=fileId)
        files_content.append({
            'file_id': file.pk,
            'file_content': build_geojson(file)
        })
    return files_content


def search_geometries_in_roi(roi_points: list) -> list:
    roiX = Polygon(roi_points + [roi_points[0]])
    roi = Polygon([(point[1], point[0]) for point in roi_points] + [(roi_points[0][1], roi_points[0][0])])

    roi_wkt = roi.wkt
    # roi_wkt = roi.geojson
    # roi_wkt2 = "E'" + roi.wkt

    query = """
        WITH multipoligonos AS (
    -- Extraemos cada polígono del MULTIPOLYGON como una geometría individual
    SELECT (ST_Dump(geometry)).geom AS poligono_individual,
    id,
    file_id
    FROM public."Files_geojsonfeature"
    -- WHERE id = 1
)
SELECT 
    id,
    file_id,
    poligono_individual, 
    'Contenida' AS tipo
FROM multipoligonos
WHERE ST_Within(
    poligono_individual, 
    ST_GeomFromText(%s, 4326)
)

UNION ALL

SELECT 
    id,
    file_id,
    poligono_individual, 
    'Intersectando' AS tipo
FROM multipoligonos
WHERE ST_Intersects(
    poligono_individual, 
    ST_GeomFromText(%s, 4326)
);
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [roi_wkt, roi_wkt])
        results = cursor.fetchall()

    return results


def get_user_files(request: WSGIRequest) -> list:
    current_user = request.user
    user_projects = requests.get('http://127.0.0.1:8000/api/user_projects/', cookies=request.COOKIES).json()['projects']
    files_ids = []
    for project in user_projects:
        user_files = get_user_project_files(current_user, project['name'])
        for file in user_files:
            files_ids.append(file['id'])
    return files_ids
