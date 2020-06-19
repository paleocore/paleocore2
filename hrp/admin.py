from .models import *  # import database models from models.py
import unicodecsv
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.gis import admin
from django.contrib.gis.admin import OSMGeoAdmin
from projects.admin import TaxonomyAdmin, TaxonRankAdmin
from import_export import resources

###############
# Media Admin #
###############


class ImagesInline(admin.TabularInline):
    model = Image
    extra = 0
    readonly_fields = ("id",)


class FilesInline(admin.TabularInline):
    model = File
    extra = 0
    readonly_fields = ("id",)


class DGGeoAdmin(OSMGeoAdmin):
    """
    Modified Geographic Admin Class using Digital Globe basemaps
    GeoModelAdmin -> OSMGeoAdmin -> DGGeoAdmin
    """
    # turban - removed for now till this can be comprehensively added back in.
    map_template = 'hrp/digital_globe.html'


###################
# Hydrology Admin #
###################
class HydrologyAdmin(DGGeoAdmin):
    list_display = ("id", "size")
    search_fields = ("id",)
    list_filter = ("size",)

    options = {
        'layers': ['google.terrain']
    }


##################
# Locality Admin #
##################
locality_fieldsets = (
    ('Record Details', {
        'fields': [('id',)]
    }),
    ('Item Details', {
        'fields': [('collection_code', 'locality_number', 'sublocality')]
    }),

    ('Occurrence Details', {
        'fields': [('description',)]
    }),
    ('Geological Context', {
        'fields': [('upper_limit_in_section', 'lower_limit_in_section'),
                   ('error_notes', 'notes')]
    }),

    ('Location Details', {
        'fields': [('longitude', 'latitude'),
                   ('easting', 'northing',),
                   ('geom',)]
    }),
)


class LocalityAdmin(DGGeoAdmin):
    list_display = ('id', 'collection_code', 'locality_number', 'sublocality')
    list_filter = ('collection_code',)
    readonly_fields = ('point_x', 'point_y', 'longitude', 'latitude', 'easting', 'northing')
    search_fields = ('locality_number,', 'id')
    fieldsets = locality_fieldsets
    options = {
        'layers': ['google.terrain']
    }


####################
# Occurrence Admin #
####################
geological_context_fieldset = ('Geological Context', {
        'fields': [
            ('analytical_unit_1', 'analytical_unit_2', 'analytical_unit_3'),
            ('analytical_unit_found', 'analytical_unit_likely', 'analytical_unit_simplified'),
            ('in_situ', 'ranked'),
            ('stratigraphic_member',),
            ('drainage_region')]
    })

occurrence_fieldsets = (
    ('Record Details', {
        'fields': [('id', 'date_last_modified',)]
    }),
    ('Occurrence Details', {
        'fields': [('barcode', 'catalog_number',),
                   ('date_recorded', 'year_collected',),
                   ('basis_of_record', 'item_type', 'disposition', 'preparation_status'),
                   ("collection_code", "locality", "item_number", "item_part"),
                   ('collecting_method', 'finder', 'collector',),
                   ('item_description', 'item_scientific_name', 'image'),
                   ('problem', 'problem_comment'),
                   ('remarks',)]
    }),
    geological_context_fieldset,

    ('Location Details', {
        'fields': [('longitude', 'latitude'),
                   ('easting', 'northing',),
                   ('geom',)]
    }),
)

default_list_display = ('barcode', 'field_number', 'catalog_number', 'basis_of_record', 'item_type',
                        'collecting_method', 'collector', 'item_scientific_name', 'item_description',
                        'year_collected',
                        'in_situ', 'problem', 'disposition', 'easting', 'northing')


class OccurrenceResource(resources.ModelResource):
    class Meta:
        model = Occurrence


class OccurrenceAdmin(projects.admin.PaleoCoreOccurrenceAdmin):
    resource_class = OccurrenceResource
    default_read_only_fields = ('id', 'point_x', 'point_y', 'easting', 'northing', 'date_last_modified')
    readonly_fields = default_read_only_fields + ('photo', 'catalog_number', 'longitude', 'latitude')
    list_display = list(default_list_display + ('thumbnail',))
    default_list_filter = ['basis_of_record', 'item_type',
                           'field_number', 'collector', 'problem', 'disposition']
    list_index = list_display.index('field_number')
    list_display.pop(list_index)
    list_display.insert(1, 'locality')
    list_display.insert(2, 'item_number')
    list_display.insert(3, 'item_part')
    fieldsets = occurrence_fieldsets
    list_filter = default_list_filter
    #default_search_fields = ('id', 'item_scientific_name', 'item_description', 'barcode', 'catalog_number')
    search_fields = ['id', 'item_scientific_name', 'item_description', 'barcode', 'cat_number']
    list_per_page = 500
    options = {
        'layers': ['google.terrain'], 'editable': False, 'default_lat': -122.00, 'default_lon': 38.00,
    }


#################
# Biology Admin #
#################


biology_inline_fieldsets = (
    ('Taxonomy', {'fields': (('taxon',), 'id')}),
)

biology_element_fieldsets = (
    ('Elements', {'fields': (
        ('element', 'element_modifier'),
        ('uli1', 'uli2', 'ulc', 'ulp3', 'ulp4', 'ulm1', 'ulm2', 'ulm3'),
        ('uri1', 'uri2', 'urc', 'urp3', 'urp4', 'urm1', 'urm2', 'urm3'),
        ('lri1', 'lri2', 'lrc', 'lrp3', 'lrp4', 'lrm1', 'lrm2', 'lrm3'),
        ('lli1', 'lli2', 'llc', 'llp3', 'llp4', 'llm1', 'llm2', 'llm3'),
        ('indet_incisor', 'indet_canine', 'indet_premolar', 'indet_molar', 'indet_tooth'),
        'deciduous'
    )}),
)


biology_fieldsets = (
    ('Record Details', {
        'fields': [('id', 'date_last_modified',)]
    }),
    ('Item Details', {
        'fields': [('barcode', 'catalog_number',),
                   ('date_recorded', 'year_collected',),
                   ("collection_code", "locality", "item_number", "item_part")]
    }),

    ('Occurrence Details', {
        'fields': [('basis_of_record', 'item_type', 'disposition', 'preparation_status'),
                   ('collecting_method', 'finder', 'collector', 'item_count'),
                   ('item_description', 'item_scientific_name', 'image'),
                   ('problem', 'problem_comment'),
                   ('remarks',)]
    }),
    biology_element_fieldsets[0],
    geological_context_fieldset,

    ('Location Details', {
        'fields': [('longitude', 'latitude'),
                   ('easting', 'northing',),
                   ('geom',)]
    }),
)


class BiologyInline(admin.TabularInline):
    model = Biology
    extra = 0
    readonly_fields = ("id",)
    fieldsets = biology_inline_fieldsets


class ElementInLine(admin.StackedInline):
    model = Biology
    extra = 0
    fieldsets = biology_element_fieldsets


class BiologyAdmin(OccurrenceAdmin):
    # fieldsets = biology_fieldsets
    inlines = (BiologyInline, ImagesInline, FilesInline)
    list_display = list(default_list_display) + ['thumbnail', 'element']
    list_display.pop(list_display.index('item_type'))
    list_display.pop(list_display.index('field_number'))

    list_filter = ['basis_of_record', 'year_collected', 'collector', 'problem', 'element']

    def create_data_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')  # declare the response type
        response['Content-Disposition'] = 'attachment; filename="HRP_Biology.csv"'  # declare the file name
        writer = unicodecsv.writer(response)  # open a .csv writer
        o = Occurrence()  # create an empty instance of an occurrence object
        b = Biology()  # create an empty instance of a biology object

        occurrence_field_list = list(o.__dict__.keys())  # fetch the fields names from the instance dictionary
        try:  # try removing the state field from the list
            occurrence_field_list.remove('_state')  # remove the _state field
        except ValueError:  # raised if _state field is not in the dictionary list
            pass
        try:  # try removing the geom field from the list
            occurrence_field_list.remove('geom')
        except ValueError:  # raised if geom field is not in the dictionary list
            pass
        # Replace the geom field with new fields
        occurrence_field_list.append("longitude")  # add new fields for coordinates of the geom object
        occurrence_field_list.append("latitude")
        occurrence_field_list.append("easting")
        occurrence_field_list.append("northing")

        biology_field_list = list(b.__dict__.keys())  # get biology fields
        try:  # try removing the state field
            biology_field_list.remove('_state')
        except ValueError:  # raised if _state field is not in the dictionary list
            pass

        #################################################################
        # For now this method handles all occurrences and corresponding #
        # data from the biology table for faunal occurrences.           #
        #################################################################
        writer.writerow(occurrence_field_list + biology_field_list)  # write column headers

        for occurrence in queryset:  # iterate through the occurrence instances selected in the admin
            # The next line uses string comprehension to build a list of values for each field
            occurrence_dict = occurrence.__dict__
            # Check that instance has geom
            try:
                occurrence_dict['longitude'] = occurrence.longitude()  # translate the occurrence geom object
                occurrence_dict['latitude'] = occurrence.latitude()
                occurrence_dict['easting'] = occurrence.easting()
                occurrence_dict['northing'] = occurrence.northing()
            except AttributeError:  # If no geom data exists write None to the dictionary
                occurrence_dict['longitude'] = None
                occurrence_dict['latitude'] = None
                occurrence_dict['easting'] = None
                occurrence_dict['northing'] = None

            # Next we use the field list to fetch the values from the dictionary.
            # Dictionaries do not have a reliable ordering. This code insures we get the values
            # in the same order as the field list.
            try:  # Try writing values for all keys listed in both the occurrence and biology tables
                writer.writerow([occurrence.__dict__.get(k) for k in occurrence_field_list] +
                                [occurrence.Biology.__dict__.get(k) for k in biology_field_list])
            except ObjectDoesNotExist:  # Django specific exception
                writer.writerow([occurrence.__dict__.get(k) for k in occurrence_field_list])
            except AttributeError:  # Django specific exception
                writer.writerow([occurrence.__dict__.get(k) for k in occurrence_field_list])

        return response
    create_data_csv.short_description = "Download Selected to .csv"


class ArchaeologyAdmin(OccurrenceAdmin):
    pass


class GeologyAdmin(OccurrenceAdmin):
    pass


##########################
# Register Admin Classes #
##########################

admin.site.register(Biology, BiologyAdmin)
admin.site.register(Archaeology, ArchaeologyAdmin)
admin.site.register(Geology, GeologyAdmin)
admin.site.register(Hydrology, HydrologyAdmin)
admin.site.register(Locality, LocalityAdmin)
admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(Taxon, TaxonomyAdmin)
admin.site.register(TaxonRank, TaxonRankAdmin)
