from django.contrib import admin
from origins.models import *
import origins.util
from projects.admin import PaleoCoreLocalityAdminGoogle
from django.utils.html import format_html
from django.contrib.gis.measure import Distance
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import permission_required
from django.conf.urls import url
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import origins.views
from django.contrib import messages
from django.contrib.gis.geos import Point


class ReferenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'reference_no', 'author1last', 'reftitle']
    search_fields = ['reference_no', 'author1init', 'author1last', 'author2init', 'author2last',
                     'otherauthors', 'pubyr', 'reftitle', 'pubtitle', 'editors', 'pubvol', 'publication_type']
    list_filter = ['publication_type']
    list_per_page = 200


class ContextInline(admin.TabularInline):
    model = Context


# fields = ['id', 'collection_name', 'collection_subset', 'collection_aka', 'n_occs', 'formation', 'member',
#              'max_ma', 'min_ma']


class SiteAdmin(PaleoCoreLocalityAdminGoogle):
    save_as = True
    list_display = ['id', 'name', 'country',
                    # 'verbatim_collection_name',
                    # 'longitude', 'latitude',
                    # 'verbatim_early_interval',
                    # 'verbatim_late_interval',
                    'max_ma',
                    'min_ma',
                    'fossil_count',
                    'formation',
                    'verbatim_collection_name',
                    # 'context_usages',
                    # 'verbatim_reference_no',
                    # 'origins'
                    ]
    # list_editable = ['name', 'origins']
    readonly_fields = ['latitude', 'longitude', 'fossil_usages', 'context_usages']
    search_fields = ['id', 'name', 'alternate_names', 'country', 'verbatim_collection_name',
                     'verbatim_early_interval',
                     'verbatim_late_interval',
                     'verbatim_max_ma',
                     'verbatim_min_ma',
                     'verbatim_reference_no',
                     'origins'
                     ]
    list_filter = ['origins', 'country']
    list_per_page = 500
    # inlines = [ContextInline]

    fieldsets = [
        ('Occurrence Details', {
            'fields': [('name',), ('alternate_names',), ('origins',), ('remarks',)],
        }),
        ('Geological Context', {
            'fields': [('min_ma', 'max_ma'), ('formation',)]
        }),
        ('Verbatim', {
            'fields': ['source', 'verbatim_collection_no', 'verbatim_record_type', 'verbatim_formation',
                       'verbatim_lng', 'verbatim_lat', 'verbatim_collection_name', 'verbatim_collection_subset',
                       'verbatim_collection_aka', 'verbatim_n_occs', 'verbatim_early_interval',
                       'verbatim_late_interval', 'verbatim_max_ma', 'verbatim_min_ma', 'verbatim_reference_no'],
            'classes': ['collapse'],
        }),
        ('Location', {
            'fields': [('country', ), ('latitude', 'longitude'), ('geom',)]
        }),
    ]


class ActiveSiteAdmin(SiteAdmin):
    list_display = ['id', 'name', 'country', 'max_ma', 'min_ma', 'fossil_count', 'formation']

    def get_queryset(self, request):
        return Site.objects.filter(origins=True)


class ContextAdmin(PaleoCoreLocalityAdminGoogle):
    save_as = True
    list_display = ['id', 'name', 'site_link', 'geological_formation', 'geological_member',
                    'older_interval', 'younger_interval', 'max_age', 'min_age', 'best_age']
    search_fields = ['id', 'name', 'geological_formation', 'geological_member',
                     'older_interval', 'younger_interval', 'max_age', 'min_age', 'best_age']
    list_filter = ['origins', 'site__name']
    list_per_page = 500
    # readonly_fields = ['latitude', 'longitude']
    fieldsets = [
        ('Context Details', {
            'fields': [('name', 'origins', 'source')],
        }),
        ('Stratigraphy', {
            'fields': [('geological_formation', 'geological_member',)],
        }),
        ('Geochronology', {
            'fields': [('older_interval', 'younger_interval',),
                       ('max_age', 'min_age', 'best_age')],
        }),
        ('Location', {'fields': [('site',), ]}),
        ('Verbatim', {
            'fields': ['verbatim_collection_no', 'verbatim_record_type', 'verbatim_formation',
                       'verbatim_lng', 'verbatim_lat', 'verbatim_collection_name', 'verbatim_collection_subset',
                       'verbatim_collection_aka', 'verbatim_n_occs', 'verbatim_early_interval',
                       'verbatim_late_interval', 'verbatim_max_ma', 'verbatim_min_ma', 'verbatim_reference_no'],
            'classes': ['collapse'],
        }),
    ]

    actions = ['create_site_from_context']

    def site_link(self, obj):
        if obj.site:
            site_url = reverse('admin:origins_site_change', args=(obj.site.id,))
            return format_html('<a href={}>{}</a>'.format(site_url, obj.site))
        else:
            return None

    site_link.admin_order_field = 'context'
    site_link.short_description = 'Site'

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.current_obj = obj
        return super(ContextAdmin, self).get_form(request, obj, **kwargs)

    def create_site_from_context(self, request, queryset):
        def create_site(context):
            new_site = Site()
            for key in new_site.get_concrete_field_names():
                try:
                    new_site.__dict__[key] = context.__dict__[key]
                except KeyError:
                    pass
            if new_site.verbatim_lat and new_site.verbatim_lng:
                new_site.geom = Point(float(new_site.verbatim_lng), float(new_site.verbatim_lat))
                new_site.country = origins.util.get_country_from_geom(new_site.geom)
            new_site.save()
            return new_site

        obj_count = 0
        for obj in queryset:
            new_site=create_site(obj)  # create a new site based on the data in the context
            obj.site = new_site  # assign the newly created site to the context
            obj_count += 1
        if obj_count == 1:
            count_string = '1 record'
        if obj_count > 1:
            count_string = '{} records'.format(obj_count)
        messages.add_message(request, messages.INFO,
                             'Successfully updated {}'.format(count_string))
    create_site_from_context.short_description = 'Create Site object(s) from Context(s)'

    # def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
    #     """
    #     Simplify choice list for sites to only those sites from the designated country.
    #     :param db_field:
    #     :param request:
    #     :param kwargs:
    #     :return:
    #     """
    #
    #     if db_field.name == "site":
    #         kwargs["queryset"] = Site.objects.filter(country=self.current_obj.country).filter(origins=True)
    #     return super(ContextAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class FossilElementInline(admin.TabularInline):
    model = FossilElement
    fields = ['skeletal_element', 'skeletal_element_subunit', 'skeletal_element_subunit_descriptor',
              'skeletal_element_side', 'skeletal_element_position', 'skeletal_element_complete',
              'skeletal_element_class']
    extra = 0


class ReferenceInline(admin.TabularInline):
    model = Reference.fossil.through
    extra = 1


class PhotosInline(admin.StackedInline):
    model = Photo
    extra = 0
    readonly_fields = ('thumbnail',)
    fieldsets = [
        ('Photos', {
            'fields': [('default_image', 'image', 'thumbnail', 'description')]})]


class FossilAdmin(admin.ModelAdmin):
    list_display = ['id', 'catalog_number', 'site', 'context_link',
                    'country', 'context__best_age', 'default_image', 'element_description', 'source']
    list_filter = ['origins', 'holotype', 'source', 'country', ]
    list_display_links = ['id', 'catalog_number']
    search_fields = ['catalog_number', 'place_name', 'country', 'locality',
                     'fossil_element__skeletal_element']
    readonly_fields = ['element_count', 'aapa', 'id', 'default_image', 'element_description']

    list_per_page = 200
    inlines = [
        # ReferenceInline, # the number of references significantly slows page loads
        FossilElementInline,
        PhotosInline
    ]

    fieldsets = [
        ('Fossil Details', {
            'fields': [('id', 'catalog_number', 'source'),
                        (
                        #'guid',
                         'uuid', 'organism_id'),
                       ('description'),
                       ('nickname', 'place_name'),
                       ('holotype', 'lifestage', 'sex'),
                       ('origins',)],
        }),
        ('Verbatim', {
            'fields': [('verbatim_PlaceName', 'verbatim_HomininElement'),
                       ('verbatim_HomininElementNotes',),
                       ('verbatim_SkeletalElement', 'verbatim_SkeletalElementSubUnit',
                        'verbatim_SkeletalElementSubUnitDescriptor'),
                       ('verbatim_SkeletalElementSide',
                        'verbatim_SkeletalElementPosition', 'verbatim_SkeletalElementComplete',
                        'verbatim_SkeletalElementClass'),
                       ('verbatim_Locality', 'verbatim_Country')
                       ],
            'classes': ['collapse'],
        }),
        ('Location', {
            'fields': [('site', 'locality', 'country', 'continent', 'context')]
        }),
        # ('Image', {
        #     'fields': [('image',)]
        # })
    ]

    actions = ['toggle_origins', 'update_sites']

    def context__formation(self, obj):
        """
        Function to get the formation from via the context
        :param obj:
        :return:
        """
        if obj.context:
            return obj.context.geological_formation
        else:
            return None

    context__formation.admin_order_field = 'context'
    context__formation.short_description = 'Geo formation'

    def context_link(self, obj):
        if obj.context:
            context_url = reverse('admin:origins_context_change', args=(obj.context.id,))
            return format_html('<a href={}>{}</a>'.format(context_url, obj.context))
        else:
            return None

    context_link.admin_order_field = 'context'
    context_link.short_description = 'Context'

    def context__site(self, obj):
        """
        Function to get site information via the context. Returns a link to the site change detail page.
        :param obj:
        :return:
        """
        if obj.context and obj.context.site:
            site_url = reverse('admin:origins_site_change', args=(obj.context.site.id,))
            return format_html('<a href={}>{}</a>'.format(site_url, obj.context.site))
        else:
            return None

    context__site.admin_order_field = 'context'
    context__site.short_description = 'Site'

    def context__max_age(self, obj):
        """
        Function to get age via context.
        :param obj:
        :return:
        """
        if obj.context and obj.context.max_age:
            return obj.context.max_age
        else:
            return None

    context__max_age.short_description = "Max age"

    def context__min_age(self, obj):
        """
        Function to get age via context.
        :param obj:
        :return:
        """
        if obj.context and obj.context.min_age:
            return obj.context.min_age
        else:
            return None

    context__min_age.short_description = "Min age"

    def context__best_age(self, obj):
        """
        Function to get age via context.
        :param obj:
        :return:
        """
        if obj.context and obj.context.best_age:
            return obj.context.best_age
        else:
            return None

    context__min_age.short_description = "Best age"

    def get_form(self, request, obj=None, **kwargs):
        self.current_obj = None
        if obj:
            self.current_obj = obj
        return super(FossilAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Simplify choice list for context to only those context objects occurring at the site.
        :param db_field:
        :param request:
        :param kwargs:
        :return:
        """
        if db_field.name == "site" and self.current_obj:
            kwargs["queryset"] = Site.objects.filter(country=self.current_obj.country).order_by('name')
        # if db_field.name == "context":
        #     if self.current_obj:
        #         if self.current_obj.context and self.current_obj.context.site:
        #             kwargs["queryset"] = Context.objects.filter(site=self.current_obj.context.site)
        #         elif self.current_obj.country:
        #             kwargs["queryset"] = Context.objects.filter(site__country=self.current_obj.country).filter(origins=True)
        #         else:
        #             kwargs["queryset"] = Context.objects.filter(origins=True)
        #             # If ever I add geom for fossil specimens, then query below useful to find closest context objects
        #             # nearby = Context.objects.filter(geom__distance_lte=(self.geom, D(m=10000)))[:5]
        return super(FossilAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def update_sites(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ct = ContentType.objects.get_for_model(queryset.model)
        ids = '?ids={}'.format(','.join(selected))
        redirect_url = reverse('admin:update_sites')
        return HttpResponseRedirect(redirect_url + ids)

    def toggle_origins(modeladmin, request, queryset):
        for obj in queryset:
            obj.origins = not(obj.origins)
            obj.save()

    def change_xy(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        redirect_url = reverse("admin:change_xy")
        return HttpResponseRedirect(redirect_url + "?ids=%s" % (",".join(selected)))
    change_xy.short_description = "Manually change coordinates for a point"

    # Add to the admin urls
    def get_urls(self):
        return [
                   #url(r'^update_sites/(?P<ids>)/$',
                    url(r'^update_sites/$',
                    permission_required('origins.update_sites', login_url='login/')(
                        origins.views.UpdateSites.as_view()),
                    name="update_sites"),
                # url(r'^change_xy/$',
                #     permission_required('lgrp.change_occurrence',
                   # login_url='login/')(lgrp.views.change_coordinates_view),
                #     name="change_xy"),
               ] + super(FossilAdmin, self).get_urls()


# Register your models here.
admin.site.register(Context, ContextAdmin)
admin.site.register(Reference, ReferenceAdmin)
admin.site.register(Fossil, FossilAdmin)
admin.site.register(Site, SiteAdmin)
