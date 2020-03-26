from django.contrib import admin
from django.contrib.auth.decorators import permission_required
from django.conf.urls import url
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.urls import reverse, path

from .models import *
import lgrp.views
import csv
import projects.admin


class Echo(object):
    """
    From the django docs on streaming large csv files
    https://docs.djangoproject.com/en/1.11/howto/outputting-csv/#streaming-csv-files
    An object that implement just the write method of the file-like interface.
    """
    def write(self, value):
        """
        Wrtie the value by returning it, instead of storing in a buffer
        :param value:
        :return:
        """
        return value


class ImagesInline(admin.TabularInline):
    model = Image
    readonly_fields = ['id', 'thumbnail']
    fields = ['id', 'image', 'thumbnail', 'description']
    extra = 0


class FilesInline(admin.TabularInline):
    model = File
    extra = 0
    readonly_fields = ("id",)


lgrp_default_list_display = ('coll_code',
                             'barcode',
                             'basis_of_record',
                             'item_type',
                             'collecting_method',
                             'collector_person',
                             'year_collected',
                             'in_situ',
                             'thumbnail')

lgrp_default_list_select_related = ('coll_code',
                                    'collector_person',
                                    'finder_person',
                                    'unit_found',
                                    'unit_likely',
                                    'unit_simplified')

lgrp_default_list_filter = ('coll_code',
                            'basis_of_record',
                            'item_type',
                            'collecting_method',
                            'collector_person',
                            'finder_person',
                            'year_collected',
                            'last_import',
                            'date_created',
                            'date_last_modified')

lgrp_readonly_fields = ('id',
                        'catalog_number',
                        'date_created',
                        'date_last_modified',
                        'easting', 'northing',
                        'longitude', 'latitude',
                        'photo')

lgrp_search_fields = ('id',
                      'basis_of_record',
                      'item_type',
                      'barcode',
                      'collection_code',
                      'coll_code__name',
                      'item_scientific_name',
                      'item_description',
                      'analytical_unit_found',
                      'analytical_unit_likely',
                      'finder',
                      'collector',
                      'finder_person__name',
                      'collector_person__name',
                      'old_cat_number',
                      'unit_found__name',
                      'unit_likely__name',
                      'unit_simplified__name')

lgrp_occurrence_fieldsets = (
    ('Record Details', {
        'fields': [('id', 'date_created', 'date_last_modified',),
                   ('basis_of_record',),
                   ('remarks',)]
    }),  # lgrp_occurrence_fieldsets[0]
    ('Find Details', {
        'fields': [('date_recorded', 'year_collected',),
                   ('barcode', 'catalog_number', 'old_cat_number', 'field_number',),
                   # ('item_type', 'item_scientific_name', 'item_description', 'item_count',),
                   ('item_type', 'item_count',),
                   ('collector_person', 'finder_person', 'collecting_method'),
                   # ('locality_number', 'item_number', 'item_part', ),
                   ('disposition', 'preparation_status'),
                   ('collection_remarks',),
                   ('verbatim_kml_data',),
                   ]
    }),  # lgrp_occurrence_fieldsets[1]
    ('Photos', {
        'fields': [('photo', 'image')],
        # 'classes': ['collapse'],
    }),  # lgrp_occurrence_fieldsets[2]
    ('Geological Context', {
        'fields': [('unit_found', 'unit_likely', 'unit_simplified'),
                   ('analytical_unit_1', 'analytical_unit_2', 'analytical_unit_3'),
                   ('stratigraphic_formation', 'stratigraphic_member',),
                   ('in_situ', 'ranked'),
                   ('geology_remarks',)]
    }),  # lgrp_occurrence_fieldsets[3]
    ('Location', {
        'fields': [('coll_code',),
                   ('georeference_remarks',),
                   ('longitude', 'latitude'),
                   ('easting', 'northing',),
                   ('geom',)]
    }),  # lgrp_occurrence_fieldsets[4]
    ('Problems', {
        'fields': [('problem', 'problem_comment'),
                   ],
        'classes': ['collapse']
    }),  # lgrp_occurrence_fieldsets[5]
)

biology_additional_fieldsets = (
    ('Elements', {
        'fields': [
            ('element', 'element_portion', 'side', 'element_number', 'element_modifier'),
            ('uli1', 'uli2', 'ulc', 'ulp3', 'ulp4', 'ulm1', 'ulm2', 'ulm3'),
            ('uri1', 'uri2', 'urc', 'urp3', 'urp4', 'urm1', 'urm2', 'urm3'),
            ('lri1', 'lri2', 'lrc', 'lrp3', 'lrp4', 'lrm1', 'lrm2', 'lrm3'),
            ('lli1', 'lli2', 'llc', 'llp3', 'llp4', 'llm1', 'llm2', 'llm3'),
            ('indet_incisor', 'indet_canine', 'indet_premolar', 'indet_molar', 'indet_tooth'), 'deciduous',
            ('element_remarks',)]
    }),  # biology_additional_fieldsets[0]
    ('Taxonomy', {
        'fields': [
            ('taxon', 'identification_qualifier'),
            ('identified_by', 'year_identified', 'type_status'),
            ('taxonomy_remarks',)]
    }),  # biology_additional_fieldsets[1]
    ('Taphonomy', {  # biology_additional_fieldsets[2]
        'fields': [('weathering', 'surface_modification')],
        # 'classes': ['collapse'],
    }),  # biology_additional_fieldsets[2]
)

biology_fieldsets = (
    lgrp_occurrence_fieldsets[0],  # Record Details
    lgrp_occurrence_fieldsets[1],  # Find Details
    lgrp_occurrence_fieldsets[2],  # Photos
    biology_additional_fieldsets[0],  # Elements
    biology_additional_fieldsets[1],  # Taxonomy
    biology_additional_fieldsets[2],  # Taphonomy
    lgrp_occurrence_fieldsets[3],  # Geological Context
    lgrp_occurrence_fieldsets[4],  # Location
    lgrp_occurrence_fieldsets[5],  # Problems
)

lgrp_biology_list_display = ('coll_code',
                             'barcode',
                             'basis_of_record',
                             'item_type',
                             'collecting_method',
                             'collector_person',
                             'taxon',
                             'element',
                             'year_collected',
                             'in_situ',
                             'thumbnail')


class OccurrenceAdmin(projects.admin.PaleoCoreOccurrenceAdmin):
    """
    OccurrenceAdmin <- PaleoCoreOccurrenceAdmin <- BingGeoAdmin <- OSMGeoAdmin <- GeoModelAdmin
    """
    list_display = lgrp_default_list_display  # use list() to clone rather than modify in place
    list_select_related = lgrp_default_list_select_related + ('archaeology', 'biology', 'geology')
    list_display_links = ['coll_code', 'barcode', 'basis_of_record']
    list_filter = lgrp_default_list_filter + ('analytical_unit_found', 'drainage_region')
    fieldsets = lgrp_occurrence_fieldsets
    readonly_fields = lgrp_readonly_fields
    search_fields = lgrp_search_fields
    inlines = (ImagesInline, FilesInline)
    change_list_template = 'admin/lgrp/occurrence/change_list.html'
    list_per_page = 500
    actions = ['change_xy']

    def change_xy(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        redirect_url = reverse("admin:change_xy")
        return HttpResponseRedirect(redirect_url + "?ids=%s" % (",".join(selected)))
    change_xy.short_description = "Manually change coordinates for a point"

    # Add to the admin urls
    def get_urls(self):
        return [path(r'import_kmz/',
                     permission_required('lgrp.add_occurrence', login_url='login/')(lgrp.views.ImportKMZ.as_view()),
                     name="import_kmz"),
                path(r'change_xy/',
                     permission_required('lgrp.change_occurrence', login_url='login/')(
                         lgrp.views.ChangeCoordinates.as_view()),
                     name="change_xy"),
                ] + super(OccurrenceAdmin, self).get_urls()


class ArchaeologyAdmin(OccurrenceAdmin):
    list_select_related = lgrp_default_list_select_related


class BiologyAdmin(OccurrenceAdmin):
    list_display = list(lgrp_biology_list_display)
    list_select_related = lgrp_default_list_select_related
    fieldsets = biology_fieldsets
    search_fields = lgrp_search_fields + ('taxon__name',)
    actions = ['create_data_csv']

    def create_data_csv(self, request, queryset):
        """
        Export data to csv format.  The LGRP version of this admin action uses StreamingHTTPResponse because it
        takes ca 155 seconds for the server to query the data, which causes a server timeout using the normal
        HTTPResponse class. Need to optimize the query to run faster, but in the meantime I implemented the
        streaming response to prevent the timeout. The lag seems to be caused by the large number of
        related tables and foreign key relations that need to be followed when exporting the data. The HRP dataset
        is larger but takes less time to export because it has fewer foreign key relationships. The long-term solution
        is to separate the export and the download actions, i.e. have the action save the export to a file and then
        redirect to another webpage showing all the export files available for download.
        :param request:
        :param queryset:
        :return:
        """
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)

        # Fetch model field names. We need to account for data originating from tables, relations and methods.
        b = Biology()  # create an empty instance of a biology object
        concrete_field_names = b.get_concrete_field_names()  # fetch a list of concrete field names
        method_field_names = b.method_fields_to_export()  # fetch a list for method field names
        fk_fields = [f for f in b._meta.get_fields() if f.is_relation]  # get a list of field objects
        fk_field_names = [f.name for f in fk_fields]  # fetch a list of foreign key field names

        def get_headers():
            return concrete_field_names + method_field_names + fk_field_names

        def get_fk_values(occurrence, fk):
            """
            Get the values associated with a foreign key relation
            :param occurrence:
            :param fk:
            :return:
            """
            qs = None
            return_string = ''
            try:
                qs = [obj for obj in getattr(occurrence, fk).all()]  # if fk is one to many try getting all objects
            except AttributeError:
                return_string = str(getattr(occurrence, fk))  # if one2one or many2one get single related value

            if qs:
                try:
                    # Getting the name of related objects requires calling the file or image object.
                    # This solution may break if relation is neither file nor image.
                    return_string = '|'.join([str(os.path.basename(p.image.name)) for p in qs])
                except AttributeError:
                    return_string = '|'.join([str(os.path.basename(p.file.name)) for p in qs])

            return return_string

        def get_row_data(o, cfs=concrete_field_names, mfs=method_field_names, fks=fk_field_names):
            concrete_values = [getattr(o, field) for field in cfs]
            method_values = [getattr(o, method)() for method in mfs]
            fk_values = [get_fk_values(o, fk) for fk in fks]
            row_data = concrete_values + method_values + fk_values
            return ['' if i in [None, False, 'None', 'False'] else i for i in row_data]  # Replace ''.

        def get_rows(items):
            yield writer.writerow(get_headers())
            for item in items:
                yield writer.writerow(get_row_data(item))

        response = StreamingHttpResponse(
            streaming_content=(get_rows(queryset)),
            content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="LGRP_Biology_Export.csv"'
        return response
    create_data_csv.short_description = 'Download Selected to .csv'


class GeologyAdmin(OccurrenceAdmin):
    list_select_related = lgrp_default_list_select_related


class PersonAdmin(admin.ModelAdmin):
    list_display = ['name']
    ordering = ['name']


class CollectionCodeAdmin(projects.admin.CollectionCodeAdmin):
    ordering = ['name', 'drainage_region']


class StratigraphicUnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'facies_type', 'age_ma']
    ordering = ['name']


class HydrologyAdmin(admin.ModelAdmin):
    list_display = ("id", "size")
    search_fields = ("id",)
    list_filter = ("size",)

    options = {
        'layers': ['google.terrain']
    }


admin.site.register(Biology, BiologyAdmin)
admin.site.register(Archaeology, ArchaeologyAdmin)
admin.site.register(Geology, GeologyAdmin)
admin.site.register(Hydrology, HydrologyAdmin)
admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(Taxon, projects.admin.TaxonomyAdmin)
admin.site.register(IdentificationQualifier, projects.admin.IDQAdmin)
admin.site.register(TaxonRank, projects.admin.TaxonRankAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(CollectionCode, CollectionCodeAdmin)
admin.site.register(StratigraphicUnit, StratigraphicUnitAdmin)
