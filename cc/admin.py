from django.contrib import admin
from .models import *


class LithicsInline(admin.StackedInline):
    model = Lithic
    extra = 0
    fieldsets = [
        ('State', {
            'fields': [('raw_material', 'cortex', 'alteration', 'edge_damage')]}),
        ('Typology/Technolopgy', {
            'fields': [('dataclass', 'technique', 'form', 'scar_morphology'), ('fb_type', 'fb_type_2', 'fb_type_3'),
                       ('retouched_edges', 'retouch_intensity', 'reprise')]}),
        ('Platforms', {
            'fields': [('platform_technique', 'platform_surface', 'platform_exterior'),
                       ('platform_width', 'platform_thickness', 'epa')]}),
        ('Cores', {
            'fields': [('core_shape', 'core_blank', 'multiple'), ('core_surface_percentage', 'proximal_removals'),
                       ('prepared_platforms', 'flake_direction'), ('scar_length', 'scar_width')]}),
        ('Measurements', {
            'fields': [('length', 'width', 'maximum_width', 'thickness', 'weight')]})]


class PhotosInline(admin.StackedInline):
    model = Photo
    extra = 0
    readonly_fields = ('thumb01',)
    fieldsets = [
        ('Photos', {
            'fields': [('image01', 'thumb01')]})]


class SmallFindsInline(admin.StackedInline):
    model = SmallFind
    extra = 0
    fieldsets = [
        (None, {
            'fields': [('coarse_stone_weight', 'coarse_fauna_weight', 'fine_stone_weight', 'fine_fauna_weight')]})]


class ContextAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': [('unit', 'id_no', 'level', 'code'), ('points',)]})]
    list_display = ('cat_no', 'unit', 'id_no', 'level', 'code',)
    list_display_links = ('cat_no', 'unit', 'id_no',)
    search_fields = ['=cat_no', 'unit', 'id_no', 'level', 'code']
    list_filter = ['unit', 'level', 'code']
    inlines = [PhotosInline, LithicsInline, SmallFindsInline]
    ordering = ('unit', 'id',)


class LithicsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Field Information', {
            'fields': [('cat_no', 'level', 'code')]}),
        ('State', {
            'fields': [('raw_material', 'cortex', 'alteration', 'edge_damage')]}),
        ('Typology/Technolopgy', {
            'fields': [('dataclass', 'technique', 'form', 'scar_morphology'), ('fb_type', 'fb_type_2', 'fb_type_3'),
                       ('retouched_edges', 'retouch_intensity', 'reprise')]}),
        ('Platforms', {
            'fields': [('platform_technique', 'platform_surface', 'platform_exterior'),
                       ('platform_width', 'platform_thickness', 'epa')]}),
        ('Cores', {
            'fields': [('core_shape', 'core_blank', 'multiple'), ('core_surface_percentage', 'proximal_removals'),
                       ('prepared_platforms', 'flake_direction'), ('scar_length', 'scar_width')]}),
        ('Measurements', {
            'fields': [('length', 'width', 'maximum_width', 'thickness', 'weight')]})]
    list_display = ('cat_no', 'unit', 'id_no', 'level', 'dataclass', 'technique', 'fb_type',)
    list_display_links = ('cat_no', 'unit', 'id_no',)
    search_fields = ['=cat_no', 'unit', 'id_no', 'level', 'dataclass', 'technique', 'form', 'core_shape', 'fb_type']
    list_filter = ['level', 'dataclass', 'technique', 'core_shape', 'fb_type']
    ordering = ('unit', 'id',)


class SmallFindsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Field Information', {
            'fields': [('cat_no', 'level', 'code')]}),
        ('Small Find Analysis', {
            'fields': [('coarse_stone_weight', 'coarse_fauna_weight', 'fine_stone_weight', 'fine_fauna_weight')]})]
    list_display = (
        'cat_no', 'unit', 'id_no', 'level', 'coarse_stone_weight', 'coarse_fauna_weight', 'fine_stone_weight',
        'fine_fauna_weight',)
    list_display_links = ('cat_no', 'unit', 'id_no',)
    list_filter = ['level', 'unit']
    search_fields = ['=cat_no', 'unit', 'id_no', 'level', ]
    ordering = ('unit', 'id',)


class PhotosAdmin(admin.ModelAdmin):
    readonly_fields = ('thumb01',)
    # fieldsets = [
    #           ('Photos', {
    #              'fields': [('image01','thumb01')]})]
    list_display = ('cat_no', 'unit', 'id_no', 'level', 'code', 'thumb01')
    search_fields = ['cat_no', 'unit', 'id_no', 'level', 'code']
    list_display_links = ('cat_no', 'unit', 'id_no',)
    list_filter = ['level', 'code', ]
    ordering = ('unit', 'id')


class UnitsAdmin(admin.ModelAdmin):
    list_filter = ['unit', ]
    search_fields = ['=unit']
    ordering = ("unit",)


class LithicsWithPhotosAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': [('unit', 'id_no', 'level', 'code'), ('points',)]})]
    list_display = ('cat_no', 'unit', 'id_no', 'level', 'code',)
    list_display_links = ('cat_no', 'unit', 'id_no',)
    search_fields = ['=cat_no', 'unit', 'id_no', 'level', 'code']
    list_filter = ['unit', 'level', 'code']
    inlines = [PhotosInline, LithicsInline]
    ordering = ('unit', 'id',)

    def get_queryset(self, request):
        return Photo.objects.all()


admin.site.register(Context, ContextAdmin)
admin.site.register(SmallFind, SmallFindsAdmin)
admin.site.register(Photo, PhotosAdmin)
admin.site.register(Lithic, LithicsAdmin)
admin.site.register(ExcavationUnit, UnitsAdmin)
admin.site.register(LithicsWithPhotos, LithicsWithPhotosAdmin)
