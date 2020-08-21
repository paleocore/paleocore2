from django.contrib import admin
from .models import CollectionCode
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin


class CollectionCodeResource(resources.ModelResource):

    class Meta:
        model = CollectionCode


class CollectionCodeAdmin(ImportExportActionModelAdmin):
    list_filter = ['geography', 'institution']
    list_display = ['code', 'institution', 'description', 'example', 'example_taxon', 'geography']
    resource_class = CollectionCodeResource


admin.site.register(CollectionCode, CollectionCodeAdmin)
