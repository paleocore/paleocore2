from django.contrib import admin
from .models import Occurrence, Biology
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import unicodecsv
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.gis import admin
from django.contrib.gis.admin import OSMGeoAdmin


default_biology_inline_fieldsets = (

    ('Element', {
        'fields': (('side',), )
    }),

    ('Taxonomy', {
        'fields': (('taxon',), ("id",))
    }),
)
default_read_only_fields = ('id', 'point_x', 'point_y', 'easting', 'northing', 'date_last_modified')
default_list_display = ('barcode', 'field_number', 'catalog_number', 'basis_of_record', 'item_type',
                        'collecting_method', 'collector', 'item_scientific_name', 'item_description', 'year_collected',
                        'in_situ', 'problem', 'disposition', 'easting', 'northing')


class BiologyInline(admin.TabularInline):
    model = Biology
    extra = 0
    readonly_fields = ("id",)
    fieldsets = default_biology_inline_fieldsets


class DGGeoAdmin(OSMGeoAdmin):
    """
    Modified Geographic Admin Class using Digital Globe basemaps
    GeoModelAdmin -> OSMGeoAdmin -> DGGeoAdmin
    """
    # turban - removed for now till this can be comprehensively added back in.
    map_template = 'omo_mursi/digital_globe.html'


class BiologyAdmin(OSMGeoAdmin):
    models = Biology


class OccurrenceAdmin(OSMGeoAdmin):
    actions = ["create_data_csv", "change_xy"]
    readonly_fields = default_read_only_fields+('photo',)
    list_display = default_list_display+('thumbnail',)
    fieldsets = (
        ('Curatorial', {
            'fields': [('barcode', 'catalog_number', 'id'),
                       ('field_number', 'year_collected', 'date_last_modified'),
                       ('collection_code', 'item_number', 'item_part')]
        }),

        ('Occurrence Details', {
            'fields': [('basis_of_record', 'item_type', 'disposition', 'preparation_status'),
                       ('collecting_method', 'finder', 'collector', 'individual_count'),
                       ('item_description', 'item_scientific_name',),
                       ('problem', 'problem_comment'),
                       ('remarks',)],
            # 'classes': ['collapse']
        }),
        ('Photos', {
            'fields': [('photo', 'image')],
            # 'classes': ['collapse'],
        }),
        ('Taphonomic Details', {
            'fields': [('weathering', 'surface_modification')],
            # 'classes': ['collapse'],
        }),
        ('Provenience', {
            'fields': [('analytical_unit',),
                       ('in_situ',),
                       # The following fields are based on methods and must be included in the read only field list
                       ('point_x', 'point_y'),
                       ('easting', 'northing'),
                       ('geom',)],
            # 'classes': ['collapse'],
        })
    )

    # admin action to manually enter coordinates
    def change_xy(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        redirect_url = reverse("projects:omo_mursi:omo_mursi_change_xy")
        return HttpResponseRedirect(redirect_url + "?ids=%s" % (",".join(selected)))
    change_xy.short_description = "Manually change coordinates for a point"

    # admin action to download data in csv format
    def create_data_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')  # declare the response type
        response['Content-Disposition'] = 'attachment; filename="MLP_data.csv"'  # declare the file name
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
        # Replace the geom field with two new fields
        occurrence_field_list.append("point_x")  # add new fields for coordinates of the geom object
        occurrence_field_list.append("point_y")

        biology_field_list = list(b.__dict__.keys())  # get biology fields
        try:  # try removing the state field
            biology_field_list.remove('_state')
        except ValueError:  # raised if _state field is not in the dictionary list
            pass

        #################################################################
        # For now this method handles all occurrences and corresponding #
        # data from the biology table for faunal occurrences.           #
        #################################################################
        writer.writerow(occurrence_field_list+biology_field_list)  # write column headers

        for occurrence in queryset:  # iterate through the occurrence instances selected in the admin
            # The next line uses string comprehension to build a list of values for each field
            occurrence_dict = occurrence.__dict__
            # Check that instance has geom
            try:
                occurrence_dict['point_x'] = occurrence.geom.get_x()  # translate the occurrence geom object
                occurrence_dict['point_y'] = occurrence.geom.get_y()
            except AttributeError:  # If no geom data exists write None to the dictionary
                occurrence_dict['point_x'] = None
                occurrence_dict['point_y'] = None

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


##########################
# Register Admin Classes #
##########################
admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(Biology, BiologyAdmin)
