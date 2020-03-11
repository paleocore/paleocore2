from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.gis.db import models
from django.forms import TextInput, Textarea  # import custom form widgets
from mapwidgets.widgets import GooglePointFieldWidget
import csv
from django.http import StreamingHttpResponse


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


class BingGeoAdmin(OSMGeoAdmin):
    """
    Modified Geographic Admin Class using Digital Globe default_projectmaps
    GeoModelAdmin -> OSMGeoAdmin -> BingGeoAdmin
    """
    map_template = './bing.html'


####################################
# PaleoCore Default Admin Settings #
####################################

default_list_display = ('catalog_number',
                        'basis_of_record',
                        'item_type',
                        'collecting_method',
                        'collector',
                        'item_scientific_name',
                        'item_description',
                        'year_collected',
                        'in_situ',
                        'thumbnail'
                        )
default_list_display_links = ('catalog_number',)
default_list_filter = ('basis_of_record',
                       'item_type',
                       'collecting_method'
                       'year_collected',)
default_search_fields = ('id',
                         'item_scientific_name',
                         'item_description',
                         'barcode',
                         'catalog_number')

default_list_per_page = 1000
default_read_only_fields = ('id', 'point_x', 'point_y', 'easting', 'northing', 'date_last_modified')
default_admin_fieldsets = (
    ('Curatorial', {
        'fields': [('barcode', 'catalog_number', 'id'),
                   ('field_number', 'year_collected', 'date_last_modified'),
                   ('collection_code', 'item_number', 'item_part')]
    }),

    ('Occurrence Details', {
        'fields': [('basis_of_record', 'item_type', 'disposition', 'preparation_status'),
                   ('collecting_method', 'finder', 'collector', 'individual_count'),
                   ('item_description', 'item_scientific_name', 'image'),
                   ('problem', 'problem_comment'),
                   ('remarks', )],
    }),
    ('Taphonomic Details', {
        'fields': [('weathering', 'surface_modification')],
    }),
    ('Provenience', {
        'fields': [('analytical_unit',),
                   ('in_situ',),
                   # The following fields are based on methods and must be included in the read only field list
                   ('point_x', 'point_y'),
                   ('easting', 'northing'),
                   ('geom', )],
    })
)

default_list_editable = ['problem', 'disposition']


default_biology_inline_fieldsets = (

    ('Element', {
        'fields': (('side',), )
    }),

    ('Taxonomy', {
        'fields': (('taxon',), ("id",))
    }),
)

default_biology_admin_fieldsets = (
    ('Taxonomy', {
        'fields': (('taxon', 'identification_qualifier'),)
    }),
)


class PaleoCoreOccurrenceAdmin(admin.ModelAdmin):
    save_as = True
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '25'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
        models.PointField: {"widget": GooglePointFieldWidget}
    }

    def get_search_results(self, request, queryset, search_term):
        # search_term is what you input in admin site
        # queryset is search results
        queryset, use_distinct = super(PaleoCoreOccurrenceAdmin, self).get_search_results(request,
                                                                                          queryset, search_term)

        try:
            search_term_as_int = int(search_term)
        except ValueError:
            pass
        else:
            queryset |= self.model.objects.filter(barcode=search_term_as_int)
        return queryset, use_distinct

    class Media:
        js = ['admin/js/list_filter_collapse.js']


class PaleoCoreLocalityAdmin(BingGeoAdmin):
    list_display = ("collection_code", "paleolocality_number", "paleo_sublocality")
    list_filter = ("collection_code",)
    search_fields = ("paleolocality_number",)
    field_mapping = {}

    def export_csv(self, request, queryset):
        mapping_dict = self.field_mapping
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)

        def get_headers():
            return mapping_dict.keys()

        # Trick to get foreign key field values
        # see https://stackoverflow.com/questions/20235807/how-to-get-foreign-key-values-with-getattr-from-models
        def get_field_value(instance, field):
            field_path = field.split('.')
            attr = instance
            for elem in field_path:
                try:
                    attr = getattr(attr, elem)
                except AttributeError:
                    return None
            return attr

        def get_row_data(o, md):
            row_data = []
            for key in md:
                # for each item in the field mapping dict get the db value for that field
                field_value = get_field_value(o, md[key])
                if callable(field_value):  # method attribute
                    row_data.append(field_value())
                else:
                    row_data.append(field_value)
            # Return list without empty strings and Nulls.
            return ['' if i in [None, False, 'None', 'False'] else i for i in row_data]

        def get_rows(items):
            yield writer.writerow(get_headers())
            for item in items:
                yield writer.writerow(get_row_data(item, mapping_dict))

        response = StreamingHttpResponse(
            streaming_content=(get_rows(queryset)),
            content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="DwC_Export.csv"'
        return response


class PaleoCoreLocalityAdminGoogle(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '25'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
        models.PointField: {"widget": GooglePointFieldWidget}
    }

    def export_csv(self, request, queryset):
        mapping_dict = self.field_mapping
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)

        def get_headers():
            return mapping_dict.keys()

        # Trick to get foreign key field values
        # see https://stackoverflow.com/questions/20235807/how-to-get-foreign-key-values-with-getattr-from-models
        def get_field_value(instance, field):
            field_path = field.split('.')
            attr = instance
            for elem in field_path:
                try:
                    attr = getattr(attr, elem)
                except AttributeError:
                    return None
            return attr

        def get_row_data(o, md):
            row_data = []
            for key in md:
                # for each item in the field mapping dict get the db value for that field
                field_value = get_field_value(o, md[key])
                if callable(field_value):  # method attribute
                    row_data.append(field_value())
                else:
                    row_data.append(field_value)
            # Return list without empty strings and Nulls.
            return ['' if i in [None, False, 'None', 'False'] else i for i in row_data]

        def get_rows(items):
            yield writer.writerow(get_headers())
            for item in items:
                yield writer.writerow(get_row_data(item, mapping_dict))

        response = StreamingHttpResponse(
            streaming_content=(get_rows(queryset)),
            content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="DwC_Export.csv"'
        return response


class TaxonomyAdmin(admin.ModelAdmin):
    list_display = ('label', 'rank', 'full_name', 'biology_usages')
    readonly_fields = ['id', 'biology_usages']
    fields = ['id', 'name', 'parent', 'label', 'rank']
    search_fields = ['name', 'label']
    list_filter = ['rank']
    list_select_related = ['rank', 'parent']


class IDQAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'qualified']


class TaxonRankAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'ordinal']


class CollectionCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'drainage_region']
    list_display_links = ['id']
    list_editable = ['name', 'drainage_region']


