from django.contrib import admin
from .models import *
import projects
from projects.admin import TaxonomyAdmin, TaxonRankAdmin
from import_export import resources


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
    # list_display = list(default_list_display + ('thumbnail',))
    default_list_filter = ['basis_of_record', 'item_type',
                           'field_number', 'collector', 'problem', 'disposition']
    # list_index = list_display.index('field_number')
    # list_display.pop(list_index)
    # list_display.insert(1, 'locality')
    # list_display.insert(2, 'item_number')
    # list_display.insert(3, 'item_part')
    # fieldsets = occurrence_fieldsets
    list_filter = default_list_filter
    #default_search_fields = ('id', 'item_scientific_name', 'item_description', 'barcode', 'catalog_number')
    search_fields = ['id', 'item_scientific_name', 'item_description', 'barcode', 'cat_number']
    list_per_page = 500
    options = {
        'layers': ['google.terrain'], 'editable': False, 'default_lat': -122.00, 'default_lon': 38.00,
    }


# Register your models here.
admin.site.register(Biology)
admin.site.register(Archaeology)
admin.site.register(Geology)
admin.site.register(Locality)
admin.site.register(Occurrence)
admin.site.register(Taxon, TaxonomyAdmin)
admin.site.register(TaxonRank, TaxonRankAdmin)
