"""
Accessible Files' classes at django admin panel
"""

from django.contrib import admin

from Files.models import DigitalResource, Team, Role, Membership, Project, Assignations, \
    File, Access, Location, Category, Folder, Classification, GeoJSON, GeoJSONFeature, \
    GeoJSONFeatureProperties

# Register your models here.

admin.site.register(DigitalResource)
admin.site.register(Team)
admin.site.register(Role)
admin.site.register(Membership)
admin.site.register(Project)
admin.site.register(Assignations)
admin.site.register(File)
admin.site.register(Access)
admin.site.register(Location)
admin.site.register(Folder)
admin.site.register(Category)
admin.site.register(Classification)
admin.site.register(GeoJSON)
admin.site.register(GeoJSONFeature)
admin.site.register(GeoJSONFeatureProperties)
