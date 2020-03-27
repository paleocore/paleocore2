from django.contrib.gis.db import models
import os
from django.db.models import Manager as GeoManager
from django.utils.html import format_html

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class ExcavationUnit(models.Model):
    unit = models.CharField(max_length=6, blank=False)
    extent = models.GeometryField(dim=3, blank=True, null=True, srid=-1)
    objects = GeoManager()

    class Meta:
        managed = True
        verbose_name_plural = "Excavation units"
        verbose_name = "Excavation Unit"
        db_table = "cc_excavation_unit"

    def __str__(self):
        return self.unit


class Context(models.Model):
    cat_no = models.CharField(max_length=12, blank=False)
    unit = models.CharField(max_length=6, blank=False)
    id_no = models.CharField('ID', max_length=6, blank=False)
    level = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=25, blank=True, null=True)
    excavator = models.CharField(max_length=50, blank=True, null=True)
    exc_date = models.DateField('Date', blank=True, null=True)
    exc_time = models.TimeField('Time', blank=True, null=True)
    points = models.GeometryField(dim=3, blank=True, null=True, srid=-1)
    objects = GeoManager()

    class Meta:
        managed = True
        verbose_name_plural = "cc Context (Catalog)"
        verbose_name = "cc Context"

    def __str__(self):
        return self.cat_no


class Lithic(Context):
    dataclass = models.CharField(max_length=20, blank=True, null=True)
    cortex = models.CharField(max_length=10, blank=True, null=True)
    technique = models.CharField(max_length=20, blank=True, null=True)
    alteration = models.CharField(max_length=20, blank=True, null=True)
    edge_damage = models.CharField(max_length=20, blank=True, null=True)
    fb_type = models.IntegerField('Bordes Type', blank=True, null=True)
    fb_type_2 = models.IntegerField('Bordes Type 2', blank=True, null=True)
    fb_type_3 = models.IntegerField('Bordes Type 3', blank=True, null=True)
    platform_surface = models.CharField(max_length=20, blank=True, null=True)
    platform_exterior = models.CharField(max_length=20, blank=True, null=True)
    form = models.CharField(max_length=20, blank=True, null=True)
    scar_morphology = models.CharField(max_length=20, blank=True, null=True)
    retouched_edges = models.IntegerField(blank=True, null=True)
    retouch_intensity = models.CharField(max_length=20, blank=True, null=True)
    reprise = models.CharField(max_length=20, blank=True, null=True)
    length = models.DecimalField(decimal_places=2,max_digits=10, blank=True, null=True)
    width = models.DecimalField(decimal_places=2,max_digits=10, blank=True, null=True)
    maximum_width = models.DecimalField(decimal_places=2,max_digits=10, blank=True, null=True)
    thickness = models.DecimalField(decimal_places=2,max_digits=10, blank=True, null=True)
    platform_width = models.DecimalField(decimal_places=2,max_digits=10, blank=True, null=True)
    platform_thickness = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    raw_material = models.CharField(max_length=20, blank=True, null=True)
    exterior_surface = models.CharField(max_length=20, blank=True, null=True)
    exterior_type = models.CharField(max_length=20, blank=True, null=True)
    weight = models.DecimalField(decimal_places=2,max_digits=10, blank=True, null=True)
    platform_technique = models.CharField(max_length=20, blank=True, null=True)
    platform_angle = models.DecimalField(decimal_places=0,max_digits=3, null=True, blank=True)
    multiple = models.NullBooleanField(default=False, blank=True, null=True)
    epa = models.IntegerField(blank=True, null=True)
    core_shape = models.CharField(max_length=20, blank=True, null=True)
    core_blank = models.CharField(max_length=20, blank=True, null=True)
    core_surface_percentage = models.DecimalField(decimal_places=0,max_digits=3, blank=True, null=True)
    proximal_removals = models.IntegerField(blank=True, null=True)
    prepared_platforms = models.IntegerField(blank=True, null=True)
    flake_direction = models.CharField(max_length=20, blank=True, null=True)
    scar_length = models.DecimalField(decimal_places=2,max_digits=10, blank=True, null=True)
    scar_width = models.DecimalField(decimal_places=2,max_digits=10, blank=True, null=True)

    class Meta:
        managed = True
        verbose_name = "cc Lithic"
        verbose_name_plural = "cc Lithics"


class SmallFind(Context):
    coarse_stone_weight = models.IntegerField(blank=True, null=True)
    coarse_fauna_weight = models.IntegerField(blank=True, null=True)
    fine_stone_weight = models.IntegerField(blank=True, null=True)
    fine_fauna_weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        verbose_name_plural = "cc Small finds (buckets)"
        verbose_name = "cc Small find (bucket)"
        db_table = "cc_small_find"


class Photo(Context):
    image01 = models.ImageField('Image', upload_to='cc/', null=True, blank=True)

    def thumb01(self):
        return format_html('<a href="%s"><img src="%s" style="width:300px" /></a>' % (os.path.join(self.image01.url),
                                                                           os.path.join(self.image01.url)))
    thumb01.short_description = 'Image'

    class Meta:
        managed = True
        verbose_name = "cc Image"
        verbose_name_plural = "cc Images"


class LithicsWithPhotos(Context):
    """
    Proxy model of Context. No associated db table.
    """
    class Meta:
        proxy = True
        managed = True
        verbose_name_plural = "cc Lithics (only with photos)"
        verbose_name = "cc Lithic (only with photo)"
