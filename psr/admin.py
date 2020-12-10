from django.contrib.gis import admin
from django.urls import reverse, path
from .views import ImportKMZ

from import_export import resources
import unicodecsv

from .models import *  # import database models from models.py
import projects.admin


class ImagesInline(admin.TabularInline):
    model = Image
    extra = 0
    readonly_fields = ("id",)


class FilesInline(admin.TabularInline):
    model = File
    extra = 0
    readonly_fields = ("id",)


# Define Occurrence resource class for django import-export
class OccurrenceResource(resources.ModelResource):
    class Meta:
        model = Occurrence


class OccurrenceAdmin(projects.admin.PaleoCoreOccurrenceAdmin):
    resource_class = OccurrenceResource
    default_read_only_fields = ('id', 'point_x', 'point_y', 'easting', 'northing', 'date_last_modified')
    readonly_fields = default_read_only_fields + ('photo', 'catalog_number', 'longitude', 'latitude')
    default_list_filter = ['basis_of_record', 'item_type',
                           'field_number', 'collector', 'problem', 'disposition']
    list_filter = default_list_filter
    search_fields = ['id', 'item_scientific_name', 'item_description', 'barcode', 'cat_number']
    list_per_page = 500

    def get_urls(self):
        tool_item_urls = [
            path(r'import_kmz/', ImportKMZ.as_view()),
            # path(r'^summary/$',permission_required('mlp.change_occurrence',
            #                         login_url='login/')(self.views.Summary.as_view()),
            #     name="summary"),
        ]
        return tool_item_urls + super(OccurrenceAdmin, self).get_urls()


class ArchaeologyResource(resources.ModelResource):
    class Meta:
        model = Archaeology


class ArchaeologyAdmin(OccurrenceAdmin):
    model = Archaeology
    resource_class = ArchaeologyResource


class BiologyResource(resources.ModelResource):
    class Meta:
        model = Biology


class BiologyAdmin(OccurrenceAdmin):
    model = Archaeology
    resource_class = ArchaeologyResource


class GeologyResource(resources.ModelResource):
    class Meta:
        model = Geology


class GeologyAdmin(OccurrenceAdmin):
    model = Geology
    resource_class = GeologyResource


class AggregateResource(resources.ModelResource):
    class Meta:
        model = Aggregate


class AggregateAdmin(OccurrenceAdmin):
    model = Aggregate
    resource_class = AggregateResource


admin.site.register(Biology, BiologyAdmin)
admin.site.register(Archaeology, ArchaeologyAdmin)
admin.site.register(Geology, GeologyAdmin)
admin.site.register(Locality)
admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(Taxon, projects.admin.TaxonomyAdmin)
admin.site.register(Aggregate, AggregateAdmin)
