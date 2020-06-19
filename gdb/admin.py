from django.contrib import admin
from django.http import HttpResponse
from .models import Occurrence, Biology, Locality, Taxon, TaxonRank
import unicodecsv
import os
import projects.admin

curatorial_fields = ('Curatorial', {
        'fields': [('catalog_number',),
                   ('cm_catalog_number',),
                   ('year_collected', 'date_collected', 'date_time_collected', 'date_last_modified')]
    })

occurrence_fields = ('Occurrence Details', {
        'fields': [('basis_of_record', 'item_type',),
                   ('collecting_method',),
                   ('item_description', 'item_scientific_name', 'image'),
                   ('on_loan', 'loan_date', 'loan_recipient'),
                   ('problem', 'problem_comment'),
                   ('remarks',)],
    })

occurrence_fields_biology = ('Occurrence Details', {
        'fields': [('basis_of_record', 'item_type',),
                   ('collecting_method',),
                   ('item_description', 'item_scientific_name', 'image'),
                   ('on_loan', 'loan_date', 'loan_recipient'),
                   ('problem', 'problem_comment'),
                   ('remarks', 'notes')],
    })

locality_fields = ('Locality', {
        'fields': [
                    ('locality',), ('nalma', 'sub_age',),
                   ],
    })

default_admin_fieldsets = (
    curatorial_fields,
    occurrence_fields,
    locality_fields
)

biology_default_admin_fieldsets = (
    curatorial_fields,
    occurrence_fields_biology,
    locality_fields,
)

description_fieldsets = ('Description', {
    'fields': [('sex', 'life_stage'),
               ('element', 'side', 'attributes'),
               ('lower_tooth', 'upper_tooth'),
               ('mandible', 'maxilla'),
               ('teeth', 'cranial', 'miscellaneous'),
               ('vertebral', 'forelimb', 'hindlimb'),
               ('morphobank_num', 'preparations'),
               ('notes',)]
})

taxonomy_fieldsets = ('Identification', {
    'fields': [('taxon', 'identification_qualifier',),
               ('identified_by', 'date_identified'),
               ('type_status',),
               ]
})

old_taxonomy_fieldsets = ('Old Taxonomic Descriptions', {
    'fields': [('tax_order', 'family',),
               ('genus', 'specific_epithet',),
               ],
    'classes': ['collapse']
})

locality_fieldsets = (('Record', {
        'fields': [('name',),
                   ('locality_number',),
                   ('locality_field_number',),
                   ('cm_locality_number',),
                   ('date_discovered',),
                   ('survey',),
                   ('notes',),
                   ('date_created', 'date_last_modified')]
    }),
    ('Geological Context', {
        'fields': [('formation',),
                   ('member',),
                   ('NALMA', 'sub_age')],
    }),
    ('Verbatim Location', {
        'fields': [
                   ('quad_sheet',),
                   ('region',),
                   ('blm_district',),
                   ('county',),
                   ('resource_area',),
                   ('gps_date',),
                   ('verbatim_gps_coordinates',),
                   ('verbatim_longitude', 'verbatim_latitude'),
                   ('verbatim_utm',),
                   ('verbatim_elevation',),
                   ('georeference_remarks',)]
    }),
    ('Location', {
        'fields': [
                   ('longitude', 'latitude'),
                   ('easting', 'northing'),
                   ('geom',)],
    }),
    ('Image', {
        'fields': [('image',)],
    }),
    ('Problem', {
        'fields': [('problem',),
                   ('problem_comment',),
                   ('remarks',),
                   ],
    }),
)

default_search_fields = ['item_scientific_name', 'catalog_number', 'cm_catalog_number']
biology_search_fields = ['tax_class', 'tax_order', 'family', 'tribe', 'genus', 'specific_epithet']


class OccurrenceAdmin(admin.ModelAdmin):
    # readonly_fields = ['catalog_number', 'latitude', 'longitude', 'easting', 'northing']
    readonly_fields = ['catalog_number', 'nalma', 'sub_age']
    fieldsets = default_admin_fieldsets
    list_display = ['catalog_number', 'cm_catalog_number', 'item_scientific_name', 'item_description', 'locality',
                    'date_collected', 'year_collected', 'on_loan', 'date_last_modified']
    list_select_related = ['locality']  # improves performance, causes server to conduct 4 queries instead of 1004
    list_filter = ['date_collected', 'year_collected', 'on_loan', 'date_last_modified']

    list_per_page = 1000
    search_fields = default_search_fields


class LocalityAdmin(projects.admin.PaleoCoreLocalityAdminGoogle):
    list_display = ('locality_number', 'name', 'locality_field_number', 'latitude', 'longitude', 'region', 'quad_sheet')
    fieldsets = locality_fieldsets
    readonly_fields = ('date_created', 'date_last_modified', 'longitude', 'latitude', 'easting', 'northing')
    list_filter = ['date_discovered', 'formation', 'NALMA', 'region', 'county']
    search_fields = ('locality_number', 'locality_field_number', 'name')
    # create a dictionary of field names and output labels for csv export
    locality_fields = [f.name for f in Locality._meta.fields]
    field_mapping = dict(zip(locality_fields, locality_fields))
    actions = ['export_csv']


# class LocalityInline(admin.TabularInline):
#     model = Locality


class BiologyAdmin(admin.ModelAdmin):
    readonly_fields = ['catalog_number', 'nalma', 'sub_age']
    biology_fieldsets = list(biology_default_admin_fieldsets)
    #
    # chronology_fieldsets = ('Chronology', {'fields': [('locality','nalma', 'sub_age')]})
    # # biology_fieldsets.insert(2, description_fieldsets)
    biology_fieldsets.insert(2, taxonomy_fieldsets)
    biology_fieldsets.insert(3, old_taxonomy_fieldsets)
    # biology_fieldsets.insert(4, chronology_fieldsets)
    fieldsets = biology_fieldsets
    list_display = ['catalog_number', 'cm_catalog_number', 'item_scientific_name', 'taxon', 'item_description',
                    'locality', 'date_collected', 'nalma']
    list_per_page = 1000
    list_filter = ['year_collected', 'taxon', 'locality', 'locality__NALMA']
    search_fields = default_search_fields + biology_search_fields
    actions = ['create_data_csv', 'generate_specimen_labels']
    list_select_related = ['locality', 'taxon', 'occurrence_ptr']

    def create_data_csv(self, request, queryset):
        """
        Export biology data to csv format. Still some issues with unicode characters.
        :param request:
        :param queryset:
        :return:
        """
        response = HttpResponse(content_type='text/csv')  # declare the response type
        # TODO generalize project file name
        # Use ContentType.objects.get_for_model(myobject)
        response['Content-Disposition'] = 'attachment; filename="GDB_Biology.csv"'  # declare the file name
        writer = unicodecsv.writer(response)  # open a .csv writer
        b = Biology()  # create an empty instance of a biology object

        # Fetch model field names. We need to account for data originating from tables, relations and methods.
        concrete_field_names = b.get_concrete_field_names()  # fetch a list of concrete field names
        method_field_names = b.method_fields_to_export()  # fetch a list for method field names

        fk_fields = [f for f in b._meta.get_fields() if f.is_relation]  # get a list of field objects
        fk_field_names = [f.name for f in fk_fields]  # fetch a list of foreign key field names

        # Concatenate to make a master field list
        field_names = concrete_field_names + method_field_names + fk_field_names
        writer.writerow(field_names)  # write column headers

        def get_fk_values(o, fk):
            """
            Get the values associated with a foreign key relation
            :param o: an occurrence instance
            :param fk: the name of the foreign key field
            :return: returns the value of the foreign key field as a string.
            """
            qs = None
            return_string = ''
            try:
                qs = [obj for obj in getattr(o, fk).all()]  # if fk is one to many try getting all objects
            except AttributeError:
                return_string = str(getattr(o, fk))  # if one2one or many2one get single related value

            if qs:
                try:
                    # Getting the name of related objects requires calling the file or image object.
                    # This solution may break if relation is neither file nor image.
                    return_string = '|'.join([str(os.path.basename(p.image.name)) for p in qs])
                except AttributeError:
                    return_string = '|'.join([str(os.path.basename(p.file.name)) for p in qs])

            return return_string

        for occurrence in queryset:  # iterate through the occurrence instances selected in the admin
            # The next line uses string comprehension to build a list of values for each field.
            # All values are converted to strings.
            concrete_values = [getattr(occurrence, field) for field in concrete_field_names]
            # Create a list of values from method calls. Note the parenthesis after getattr in the list comprehension.
            method_values = [getattr(occurrence, method)() for method in method_field_names]
            # Create a list of values from related tables. One to many fields have related values concatenated in str.
            fk_values = [get_fk_values(occurrence, fk) for fk in fk_field_names]

            row_data = concrete_values + method_values + fk_values
            cleaned_row_data = ['' if i in [None, False, 'None', 'False'] else i for i in row_data]  # Replace ''.
            writer.writerow(cleaned_row_data)

        return response

    class Media:
        js = ['admin/js/list_filter_collapse.js']

    create_data_csv.short_description = 'Download Selected to .csv'

    def generate_specimen_labels(self, request, queryset):
        """
        Export a text report with biology specimen data formatted for labels
        :param queryset:
        :param request:
        :return:
        """
        content = ""
        for b in queryset:
            specimen_data = "GDB Project\n{catalog_number}  {sci_name}\n" \
                            "CM #: {cm_catalog_number}\n" \
                            "{description}\nLocality {locality}\n" \
                            "{nalma} {date_collected}\n\n".format(catalog_number=b.catalog_number,
                                                                  sci_name=b.item_scientific_name,
                                                                  cm_catalog_number=b.cm_catalog_number,
                                                                  description=b.item_description,
                                                                  locality=b.locality,
                                                                  nalma=b.locality.NALMA,
                                                                  date_collected=b.date_collected)
            content = content + specimen_data
        response = HttpResponse(content, content_type='text/plain')  # declare the response type
        response['Content-Disposition'] = 'attachment; filename="Specimens.txt"'  # declare the file name
        return response
    generate_specimen_labels.short_description = 'Specimen Labels'


admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(Biology, BiologyAdmin)
admin.site.register(Locality, LocalityAdmin)
admin.site.register(Taxon, projects.admin.TaxonomyAdmin)
admin.site.register(TaxonRank, projects.admin.TaxonRankAdmin)
