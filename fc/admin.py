from django.contrib import admin
from django.utils.html import mark_safe
from .models import *



class GrainsInLine(admin.TabularInline):
    model = Granulometry
    extra = 0
    fieldsets = [
        ('', {
            'fields': ['weight']})]


class SmallFindWeightsInLine(admin.TabularInline):
    model = Small_Find_Weights
    extra = 0
    fieldsets = [
        ('', {
            'fields': ['weight']})]


class FaunaInLine(admin.StackedInline):
    model = Fauna
    extra = 0
    fieldsets = [
        ('', {
            'fields': [('tentative_ID', 'genus', 'side', 'part', 'portion', 'segment', 'bone_type')]})]


class LithicsInline(admin.StackedInline):
    model = Lithic
    extra = 0
    fieldsets = [
        ('State', {
            'fields': [('raw_material', 'cortex', 'alteration', 'edge_damage', 'discard')]}),
        ('Typology/Technolopgy', {
            'fields': [('dataclass', 'technique', 'form', 'support', 'scar_morphology'),
                       ('fb_type', 'fb_type_2', 'biface_type'), ('retouched_edges', 'retouch_intensity'),
                       ('tf_character', 'tf_surface', 'tf_location')]}),
        ('Platforms', {
            'fields': [('platform_surface', 'platform_exterior'), ('platform_width', 'platform_thickness', 'epa')]}),
        ('Cores', {
            'fields': [('core_type', 'core_faces', 'platforms', 'platform_technique_1', 'platform_technique_2',
                        'proximal_removals', 'scar_length')]}),
        ('Measurements', {
            'fields': [('length', 'width', 'thickness'), ('small_pw', 'bulb', 'weight')]})]


class PhotosInline(admin.StackedInline):
    model = Photo
    extra = 0
    readonly_fields = ('thumb01',)
    fieldsets = [
        ('Photos', {
            'fields': [('image01', 'thumb01')]})]


class SmallFindsInline(admin.StackedInline):
    model = Small_Find
    extra = 0
    fieldsets = [
        (None, {
            'fields': [('screen_size', 'platform_count', 'platform_weight')]})]


class Context_admin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': [('unit', 'id_no', 'level', 'code'), ('points')]})]
    list_display = ('cat_no', 'unit', 'id_no', 'level', 'code',)
    list_display_links = ('cat_no', 'unit', 'id_no',)
    search_fields = ['=cat_no', 'unit', 'id_no', 'level', 'code']
    list_filter = ['unit', 'level', 'code']
    inlines = [PhotosInline, LithicsInline, FaunaInLine, SmallFindsInline]
    ordering = ('unit', 'id',)


class Fauna_admin(admin.ModelAdmin):
    fieldsets = [
        ('Field Information', {
            'fields': [('cat_no', 'level', 'code')]}),
        ('Faunal Analysis', {
            'fields': [('tentative_ID', 'genus', 'side', 'part', 'portion', 'segment', 'bone_type')]})]
    list_display = ('cat_no', 'unit', 'id_no', 'level', 'genus',)
    list_display_links = ('cat_no', 'unit', 'id_no',)
    search_fields = ['=cat_no', 'unit', 'id_no', 'level', 'genus']
    list_filter = ['level', 'genus']
    ordering = ('unit', 'id',)


class Lithics_admin(admin.ModelAdmin):
    fieldsets = [
        ('Field Information', {
            'fields': [('cat_no', 'level', 'code')]}),
        ('State', {
            'fields': [('raw_material', 'cortex', 'alteration', 'edge_damage', 'discard')]}),
        ('Typology/Technolopgy', {
            'fields': [('dataclass', 'technique', 'form', 'support', 'scar_morphology'),
                       ('fb_type', 'fb_type_2', 'biface_type'), ('retouched_edges', 'retouch_intensity'),
                       ('tf_character', 'tf_surface', 'tf_location')]}),
        ('Platforms', {
            'fields': [('platform_surface', 'platform_exterior'), ('platform_width', 'platform_thickness', 'epa')]}),
        ('Cores', {
            'fields': [('core_type', 'core_faces', 'platforms', 'platform_technique_1', 'platform_technique_2',
                        'proximal_removals', 'scar_length')]}),
        ('Measurements', {
            'fields': [('length', 'width', 'thickness'), ('small_pw', 'bulb', 'weight')]})]
    list_display = ('cat_no', 'unit', 'id_no', 'level', 'dataclass', 'technique', 'fb_type',)
    list_display_links = ('cat_no', 'unit', 'id_no',)
    search_fields = ['=cat_no', 'unit', 'id_no', 'level', 'dataclass', 'technique', 'form', 'fb_type']
    list_filter = ['level', 'dataclass', 'technique', 'fb_type']
    ordering = ('unit', 'id',)


class Small_finds_admin(admin.ModelAdmin):
    fieldsets = [
        ('Field Information', {
            'fields': [('cat_no', 'level', 'code')]}),
        ('Small Find Analysis', {
            'fields': [('screen_size', 'platform_count', 'platform_weight')]})]
    list_display = ('cat_no', 'unit', 'id_no', 'level', 'screen_size', 'platform_count', 'platform_weight',)
    list_display_links = ('cat_no', 'unit', 'id_no',)
    list_filter = ['level', 'unit']
    search_fields = ['=cat_no', 'unit', 'id_no', 'level', ]
    ordering = ('unit', 'id',)


class Galet_weights_admin(admin.ModelAdmin):
    fieldsets = [
        ('Field Information', {
            'fields': [('cat_no', 'level', 'code')]}),
        ('Weight', {
            'fields': [('weight')]})]
    list_display = ('cat_no', 'unit', 'id_no', 'level', 'weight',)
    list_display_links = ('cat_no', 'unit', 'id_no',)
    list_filter = ['level', 'unit']
    search_fields = ['=cat_no', 'unit', 'id_no', 'level', ]
    ordering = ('unit', 'id',)


class Photos_admin(admin.ModelAdmin):
    readonly_fields = ('thumb01',)
    # fieldsets = [
    #           ('Photos', {
    #              'fields': [('image01','thumb01')]})]
    list_display = ('cat_no', 'unit', 'id_no', 'level', 'code', 'thumb02',)
    search_fields = ['=cat_no', 'unit', 'id_no', 'level', 'code']
    list_display_links = ('cat_no', 'unit', 'id_no',)
    list_filter = ['level', 'code', ]
    ordering = ('unit', 'id',)


class Units_admin(admin.ModelAdmin):
    list_filter = ['unit', ]
    search_fields = ['=unit']
    ordering = ("unit",)


class Refits_admin(admin.ModelAdmin):
    list_display = ('unit', 'id_no',)


class Lithics_with_Photos_admin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': [('unit', 'id_no', 'level', 'code'), ('points',)]})]
    list_display = ('cat_no', 'unit', 'id_no', 'level', 'code', 'get_thumb')
    list_display_links = ('cat_no', 'unit', 'id_no')
    search_fields = ['=cat_no', 'unit', 'id_no', 'level', 'code']
    list_filter = ['unit', 'level', 'code']
    inlines = [PhotosInline, LithicsInline]
    ordering = ('unit', 'id',)

    def get_thumb(self, instance):
        return mark_safe('<a href="%s"><img src="%s" style="width:100px" /></a>' % (
            os.path.join(instance.photo.image01.url), os.path.join(instance.photo.image01.url)))

    def get_queryset(self, request):
        return Photo.objects.all()


class Buckets_with_Granulometry(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': [('unit', 'id_no', 'level', 'code'), ('points')]})]
    list_display = ('cat_no', 'unit', 'id', 'level')
    list_display_links = ('cat_no', 'unit', 'id')
    list_filter = ['level', 'unit']
    search_fields = ['=cat_no', '=level', '=unit']
    ordering = ('unit', 'id',)
    inlines = [GrainsInLine]

    def get_queryset(self, request):
        return Context.objects.filter(granulometry__weight__isnull=False).distinct()


class Small_Find_Weights_by_Bucket(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': [('unit', 'id_no', 'level', 'code'), ('points')]})]
    list_display = ('cat_no', 'unit', 'id_no', 'level')
    list_display_links = ('cat_no', 'unit', 'id_no')
    list_filter = ['level', 'unit']
    search_fields = ['=cat_no', '=level', '=unit']
    ordering = ('unit', 'id_no',)
    inlines = [SmallFindWeightsInLine]

    def get_queryset(self, request):
        return Context.objects.filter(small_find_weights__weight__isnull=False).distinct()


class Small_find_weights_admin(admin.ModelAdmin):
    readonly_fields = ('get_cat_no', 'get_level',)
    fieldsets = [
        ('Field Information', {
            'fields': [('get_cat_no', 'get_level')]}),
        ('Weight', {
            'fields': [('weight')]})]
    list_display = ('get_cat_no', 'smalls_id', 'get_level', 'weight',)
    list_display_links = ('get_cat_no',)
    list_filter = ['context__level']
    search_fields = ['=context__cat_no', '=context__level']
    ordering = ('context__unit', 'context__id_no')

    def get_level(self, instance):
        return instance.context.level

    def get_cat_no(self, instance):
        return instance.context.cat_no

    get_level.short_description = 'Level'
    get_cat_no.short_description = 'Cat no'


class Granulometry_admin(admin.ModelAdmin):
    readonly_fields = ('get_cat_no', 'get_level',)
    fieldsets = [
        ('Field Information', {
            'fields': [('get_cat_no', 'get_level')]}),
        ('Weight', {
            'fields': [('weight')]})]
    list_display = ('get_cat_no', 'grain_id', 'get_level', 'weight',)
    list_display_links = ('get_cat_no',)
    list_filter = ['context__level']
    search_fields = ['=context__cat_no', '=context__level']
    ordering = ('context__unit', 'context__id_no',)

    def get_level(self, instance):
        return instance.context.level

    def get_cat_no(self, instance):
        return instance.context.cat_no

    get_level.short_description = 'Level'
    get_cat_no.short_description = 'Cat no'


admin.site.register(Small_Find_Weights, Small_find_weights_admin)
admin.site.register(Granulometry, Granulometry_admin)
admin.site.register(Context, Context_admin)
admin.site.register(Small_Find, Small_finds_admin)
admin.site.register(Photo, Photos_admin)
admin.site.register(Lithic, Lithics_admin)
admin.site.register(Excavation_unit, Units_admin)
admin.site.register(Lithics_with_Photos, Lithics_with_Photos_admin)
admin.site.register(Fauna, Fauna_admin)
admin.site.register(Refits, Refits_admin)
admin.site.register(Galet_Weights, Galet_weights_admin)
admin.site.register(Buckets_with_Grains, Buckets_with_Granulometry)
admin.site.register(Small_find_weights_summary, Small_Find_Weights_by_Bucket)
