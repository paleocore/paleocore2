from django.contrib import admin
from django.contrib.auth.decorators import permission_required
from django.conf.urls import url
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, path

from .models import *

import unicodecsv

from django.core.exceptions import ObjectDoesNotExist


mlp_default_list_display = ('barcode', 'date_recorded', 'catalog_number', 'basis_of_record', 'item_type',
                            'collecting_method', 'collector', 'item_scientific_name', 'item_description',
                            'year_collected',
                            'in_situ', 'problem', 'easting', 'northing')

mlp_default_readonly_fields = ('id', 'point_x', 'point_y', 'easting', 'northing', 'date_last_modified', 'thumbnail')

mlp_search_fields = ('id',
                     'basis_of_record',
                     'item_type',
                     'barcode',
                     'collection_code',
                     'item_scientific_name',
                     'item_description',
                     'stratigraphic_marker_found',
                     'stratigraphic_marker_likely',
                     'analytical_unit',
                     'finder',
                     'collector',)


class OccurrenceAdmin(projects.admin.PaleoCoreOccurrenceAdmin):
    """
    OccurrenceAdmin <- PaleoCoreOccurrenceAdmin <- BingGeoAdmin <- OSMGeoAdmin <- GeoModelAdmin
    """
    # default_read_only_fields = ('id', 'point_x', 'point_y', 'easting', 'northing', 'date_last_modified')

    # default_list_display = ('barcode', 'date_recorded', 'catalog_number', 'basis_of_record', 'item_type',
    #                         'collecting_method', 'collector', 'item_scientific_name', 'item_description',
    #                         'year_collected',
    #                         'in_situ', 'problem', 'disposition', 'easting', 'northing')
    list_display = mlp_default_list_display+('thumbnail',)  # defaults plus thumbnail
    list_select_related = ['archaeology', 'biology', 'geology']
    list_filter = ['basis_of_record', 'item_type', 'field_season',
                   'date_recorded', 'collector', 'problem', 'disposition', 'last_import']
    fieldsets = [
        ('Curatorial', {
            'fields': [('barcode', 'catalog_number', 'id'),
                       ('date_recorded', 'year_collected', 'field_season', 'date_last_modified'),
                       ('collection_code', 'item_number', 'item_part')]
        }),
        ('Occurrence Details', {
            'fields': [('basis_of_record', 'item_type', 'disposition', 'preparation_status'),
                       ('collector', 'finder', 'collecting_method', 'individual_count'),
                       ('item_description', 'item_scientific_name',),
                       ('problem', 'problem_comment'),
                       ('remarks',)],
            'classes': ['collapse']
        }),
        ('Verbatim Data', {
            'fields': ['verbatim_kml_data'],
            #'classes': ['collapse']
        }),
        ('Photos', {
            'fields': [('photo', 'image')],
            'classes': ['collapse'],
        }),
        ('Taphonomic Details', {
            'fields': [('weathering', 'surface_modification')],
            'classes': ['collapse'],
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
    ]
    readonly_fields = mlp_default_readonly_fields + ('photo',)  # defaults plus photo
    search_fields = mlp_search_fields
    actions = ["create_data_csv", "change_xy", "change_occurrence2biology", "create_simple_data_csv"]

    # admin action to manually enter coordinates
    def change_xy(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        redirect_url = reverse("projects:mlp:mlp_change_xy")
        return HttpResponseRedirect(redirect_url + "?ids=%s" % (",".join(selected)))
    change_xy.short_description = "Manually change coordinates for a point"

    def change_occurrence2biology(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        redirect_url = reverse("projects:mlp:mlp_occurrence2biology")
        return HttpResponseRedirect(redirect_url + "?ids=%s" % (",".join(selected)))
    change_occurrence2biology.short_description = "Change Occurrence to Biology"

    def create_simple_data_csv(self, request, queryset):
        fields_to_export = ['id', 'date_created', 'date_last_modified', 'problem', 'problem_comment', 'remarks',
                            'georeference_remarks', 'date_recorded', 'year_collected', 'barcode', 'field_number',
                            'basis_of_record', 'item_type', 'collection_code', 'item_number', 'item_part',
                            'catalog_number', 'item_scientific_name', 'item_description', 'collecting_method',
                            'collector', 'finder', 'disposition', 'field_season', 'individual_count', 'in_situ',
                            'ranked', 'image', 'weathering', 'surface_modification', 'geom']
        response = HttpResponse(content_type='text/csv')  # declare the response type
        response['Content-Disposition'] = 'attachment; filename="MLP_data.csv"'  # declare the file name
        writer = unicodecsv.writer(response)  # open a .csv writer

        writer.writerow(fields_to_export+['longitude', 'latitude'])  # write column headers
        for o in queryset.order_by('item_type', 'barcode'):
            try:
                row_list = [o.__dict__.get(k) for k in fields_to_export]
                row_list.append(o.point_x())
                row_list.append(o.point_y())
                # row_list.append(o.taxon)
                writer.writerow(row_list)
            except:
                writer.writerow(o.id)
        return response
    create_simple_data_csv.short_description = "Export simple report to csv"

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


class ArchaeologyAdmin(OccurrenceAdmin):
    list_select_related = ['occurrence_ptr']  # required here b/c inherited values won't work


class BiologyAdmin(OccurrenceAdmin):
    biology_fieldsets = list(OccurrenceAdmin.fieldsets)  # creates a separate copy of the fieldset list
    taxonomy_fieldsets = ('Identification', {'fields': [('taxon', 'identification_qualifier', 'identified_by')]})
    element_fieldsets = ('Detailed Description', {'fields': [('element', 'element_modifier')]})
    biology_fieldsets.insert(2, taxonomy_fieldsets)
    biology_fieldsets.insert(3, element_fieldsets)
    fieldsets = biology_fieldsets
    list_select_related = ['occurrence_ptr', 'taxon']  # required here b/c inherited values won't work


class GeologyAdmin(OccurrenceAdmin):
    list_select_related = ['occurrence_ptr']  # required here b/c inherited values won't work


############################
#  Register Admin Classes  #
############################
admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(Archaeology, ArchaeologyAdmin)
admin.site.register(Biology, BiologyAdmin)
admin.site.register(Geology, GeologyAdmin)
admin.site.register(Taxon, projects.admin.TaxonomyAdmin)

