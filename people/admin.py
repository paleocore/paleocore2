from django.contrib import admin
from .models import Person
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin


class PersonResource(resources.ModelResource):

    class Meta:
        model = Person


class PersonAdmin(ImportExportActionModelAdmin):
    list_display = ['order', 'biblio', 'name', 'last', 'first', 'orcid', 'academic_rank', 'area', 'affiliation', 'email']
    list_display_links = ['name']
    # list_editable = ['biblio']
    resource_class = PersonResource


admin.site.register(Person, PersonAdmin)

