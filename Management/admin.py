from django.contrib import admin

from .models import GlobalRole, GlobalMembership

# Register your models here.

admin.site.register(GlobalMembership)
admin.site.register(GlobalRole)
