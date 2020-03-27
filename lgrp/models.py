from django.contrib.gis.db import models
from django.db.models import Manager as GeoManager
import projects.models
from lgrp.ontologies import *
from projects.ontologies import ITEM_TYPE_VOCABULARY
import os
from django.utils.html import mark_safe


# Occurrence Class and Subclasses
class Occurrence(projects.models.PaleoCoreOccurrenceBaseClass):
    """
    lgrp.Occurrence <- projects.models.PaleoCoreOccurrenceBaseClass <- projects.models.PaleoCoreBaseClass
    """
    # Record-level
    basis_of_record = models.CharField("Basis of Record", max_length=50, blank=True, null=False,
                                       choices=LGRP_BASIS_OF_RECORD_VOCABULARY)  # NOT NULL
    # Event - inherited

    # Find
    item_type = models.CharField("Item Type", max_length=255, blank=True, null=False,
                                 choices=ITEM_TYPE_VOCABULARY)  # NOT NULL
    # item_scientific_name should be transfered to inherited name field
    item_scientific_name = models.CharField("Sci Name", max_length=255, null=True, blank=True)
    item_description = models.CharField("Description", max_length=255, blank=True, null=True)

    item_count = models.IntegerField(blank=True, null=True, default=1)
    collector = models.CharField(max_length=50, blank=True, null=True,
                                 choices=LGRP_COLLECTOR_CHOICES)  # dwc:recordedBy
    finder = models.CharField(null=True, blank=True, max_length=50,
                              choices=LGRP_FINDER_CHOICES)
    collector_person = models.ForeignKey('Person', null=True, blank=True,
                                         related_name='person_collector',
                                         on_delete=models.SET_NULL)
    finder_person = models.ForeignKey('Person', null=True, blank=True,
                                      related_name='person_finder',
                                      on_delete=models.SET_NULL)
    collecting_method = models.CharField(max_length=50,
                                         choices=LGRP_COLLECTING_METHOD_VOCABULARY,
                                         null=True, blank=True)  # dwc:sampling_protocol
    # locality number is deprecated
    locality_number = models.IntegerField("Locality", null=True, blank=True)
    # item number is deprecated
    item_number = models.CharField("Item #", max_length=10, null=True, blank=True)
    # item part is deprecated
    item_part = models.CharField("Item Part", max_length=10, null=True, blank=True)
    old_cat_number = models.CharField("Old Cat Number", max_length=255, blank=True, null=True)
    disposition = models.CharField(max_length=255, blank=True, null=True)  # dwc:disposition
    preparation_status = models.CharField(max_length=50, blank=True, null=True)  # Drop? - 2 specimens with entries
    # TODO rename collection_remarks to find_remarks
    collection_remarks = models.TextField(max_length=500, null=True, blank=True)  # dwc:occurrence_remarks

    # Geological Context
    stratigraphic_formation = models.CharField("Formation", max_length=255, blank=True, null=True)  # dwc:formation
    stratigraphic_member = models.CharField("Member", max_length=255, blank=True, null=True)  # dwc:member
    analytical_unit_1 = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_2 = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_3 = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_found = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_likely = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_simplified = models.CharField(max_length=255, blank=True, null=True)  # dwc:bed
    in_situ = models.BooleanField(default=False)
    ranked = models.BooleanField(default=False)  # Drop? One record is True
    weathering = models.SmallIntegerField(blank=True, null=True, choices=LGRP_WEATHERING_CHOICES)
    surface_modification = models.CharField(max_length=255, blank=True, null=True)
    geology_remarks = models.TextField(max_length=500, null=True, blank=True)
    unit_found = models.ForeignKey('StratigraphicUnit', null=True, blank=True,
                                   related_name='occurrence_unit_found',
                                   on_delete=models.SET_NULL)
    unit_likely = models.ForeignKey('StratigraphicUnit', null=True, blank=True,
                                    related_name='occurrence_unit_likely',
                                    on_delete=models.SET_NULL)
    unit_simplified = models.ForeignKey('StratigraphicUnit', null=True, blank=True,
                                        related_name='occurrence_unit_simplified',
                                        on_delete=models.SET_NULL)

    # Location
    coll_code = models.ForeignKey('CollectionCode', null=True, blank=True,
                                  on_delete=models.SET_NULL)
    collection_code = models.CharField(max_length=20, blank=True, null=True,
                                       choices=LGRP_COLLECTION_CODES)  # dwc:collectionCode, change to locality?
    drainage_region = models.CharField(null=True, blank=True, max_length=255)  # merge with collection_code?

    # Media
    image = models.FileField(max_length=255, blank=True, upload_to="uploads/images/lgrp", null=True)

    # Verbatim
    verbatim_kml_data = models.TextField(null=True, blank=True)
    related_catalog_items = models.CharField("Related Catalog Items", max_length=50, null=True, blank=True)

    def __str__(self):
        nice_name = str(self.catalog_number()) + ' ' + '[' + str(self.item_scientific_name) + ' ' \
                    + str(self.item_description) + "]"
        return nice_name.replace("None", "").replace("--", "")

    def save(self, *args, **kwargs):
        """
        Custom save method for Occurrence objects. Automatically updates catalog_number field
        :param args:
        :param kwargs:
        :return:
        """
        super(Occurrence, self).save(*args, **kwargs)

    @staticmethod
    def fields_to_display():
        fields = ("id", "barcode")
        return fields

    @staticmethod
    def method_fields_to_export():
        """
        Method to store a list of fields that should be added to data exports.
        Called by export admin actions.
        These fields are defined in methods and are not concrete fields in the DB so have to be declared.
        :return:
        """
        return ['longitude', 'latitude', 'easting', 'northing', 'catalog_number', 'photo']

    def catalog_number(self):
        """
        Generate a pretty string formatted catalog number from constituent fields
        :return: catalog number as string
        """
        if self.basis_of_record == 'Collection':
            if self.coll_code and self.barcode:
                catalog_number_string = self.coll_code.name + " " + str(self.barcode)
            elif self.coll_code:
                catalog_number_string = self.coll_code.name + " ??"
            elif self.barcode:
                catalog_number_string = "?? " + str(self.barcode)
            else:
                catalog_number_string = "[{}]".format(self.id)
            return catalog_number_string
        else:
            return None

    def old_catalog_number(self):
        """
        Generate a pretty string formated catalog number from constituent fields
        :return: old version of catalog number as string
        """
        if self.basis_of_record == 'Collection':
            #  Crate catalog number string. Null values become None when converted to string
            if self.item_number:
                if self.item_part:
                    item_text = '-' + str(self.item_number) + str(self.item_part)
                else:
                    item_text = '-' + str(self.item_number)
            else:
                item_text = ''

            catalog_number_string = str(self.collection_code) + " " + str(self.locality_number) + item_text
            return catalog_number_string.replace('None', '').replace('- ', '')  # replace None with empty string
        else:
            return None

    class Meta:
        verbose_name = "01-LGRP Occurrence"
        verbose_name_plural = "01-LGRP Occurrences"
        ordering = ["collection_code", "item_number", "item_part"]


class Archaeology(Occurrence):
    find_type = models.CharField(null=True, blank=True, max_length=255)
    length_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    width_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)

    class Meta:
        verbose_name = "02-LGRP Archaeology"
        verbose_name_plural = "02-LGRP Archaeology"


class Biology(Occurrence):
    # Biology
    sex = models.CharField(null=True, blank=True, max_length=50)
    life_stage = models.CharField(null=True, blank=True, max_length=50)
    biology_remarks = models.TextField(max_length=500, null=True, blank=True)

    # Taxon
    taxon = models.ForeignKey('Taxon',
                              default=0, on_delete=models.SET_DEFAULT,  # prevent deletion when taxa deleted
                              related_name='lgrp_taxon_bio_occurrences')
    identification_qualifier = models.ForeignKey('IdentificationQualifier',
                                                 on_delete=models.SET_NULL,
                                                 related_name='lgrp_id_qualifier_bio_occurrences',
                                                 null=True, blank=True)
    qualifier_taxon = models.ForeignKey('Taxon', null=True, blank=True,
                                        on_delete=models.SET_NULL,
                                        related_name='lgrp_qualifier_taxon_bio_occurrences')
    verbatim_taxon = models.CharField(null=True, blank=True, max_length=1024)
    verbatim_identification_qualifier = models.CharField(null=True, blank=True, max_length=255)
    taxonomy_remarks = models.TextField(max_length=500, null=True, blank=True)

    # Identification
    identified_by = models.CharField(null=True, blank=True, max_length=100, choices=LGRP_IDENTIFIER_CHOICES)
    year_identified = models.IntegerField(null=True, blank=True)
    type_status = models.CharField(null=True, blank=True, max_length=50)

    fauna_notes = models.TextField(null=True, blank=True, max_length=64000)

    # Element
    side = models.CharField(null=True, blank=True, max_length=50, choices=LGRP_SIDE_CHOICES)

    element = models.CharField(null=True, blank=True, max_length=50, choices=LGRP_ELEMENT_CHOICES)
    element_modifier = models.CharField(null=True, blank=True, max_length=50, choices=LGRP_ELEMENT_MODIFIER_CHOICES)
    element_portion = models.CharField(null=True, blank=True, max_length=50, choices=LGRP_ELEMENT_PORTION_CHOICES)
    element_number = models.CharField(null=True, blank=True, max_length=50, choices=LGRP_ELEMENT_NUMBER_CHOICES)
    element_remarks = models.TextField(max_length=500, null=True, blank=True)

    tooth_upper_or_lower = models.CharField(null=True, blank=True, max_length=50)
    tooth_number = models.CharField(null=True, blank=True, max_length=50)
    tooth_type = models.CharField(null=True, blank=True, max_length=50)

    # upper dentition fields
    uli1 = models.BooleanField(default=False)
    uli2 = models.BooleanField(default=False)
    uli3 = models.BooleanField(default=False)
    uli4 = models.BooleanField(default=False)
    uli5 = models.BooleanField(default=False)
    uri1 = models.BooleanField(default=False)
    uri2 = models.BooleanField(default=False)
    uri3 = models.BooleanField(default=False)
    uri4 = models.BooleanField(default=False)
    uri5 = models.BooleanField(default=False)
    ulc = models.BooleanField(default=False)
    urc = models.BooleanField(default=False)
    ulp1 = models.BooleanField(default=False)
    ulp2 = models.BooleanField(default=False)
    ulp3 = models.BooleanField(default=False)
    ulp4 = models.BooleanField(default=False)
    urp1 = models.BooleanField(default=False)
    urp2 = models.BooleanField(default=False)
    urp3 = models.BooleanField(default=False)
    urp4 = models.BooleanField(default=False)
    ulm1 = models.BooleanField(default=False)
    ulm2 = models.BooleanField(default=False)
    ulm3 = models.BooleanField(default=False)
    urm1 = models.BooleanField(default=False)
    urm2 = models.BooleanField(default=False)
    urm3 = models.BooleanField(default=False)
    # lower dentition fields
    lli1 = models.BooleanField(default=False)
    lli2 = models.BooleanField(default=False)
    lli3 = models.BooleanField(default=False)
    lli4 = models.BooleanField(default=False)
    lli5 = models.BooleanField(default=False)
    lri1 = models.BooleanField(default=False)
    lri2 = models.BooleanField(default=False)
    lri3 = models.BooleanField(default=False)
    lri4 = models.BooleanField(default=False)
    lri5 = models.BooleanField(default=False)
    llc = models.BooleanField(default=False)
    lrc = models.BooleanField(default=False)
    llp1 = models.BooleanField(default=False)
    llp2 = models.BooleanField(default=False)
    llp3 = models.BooleanField(default=False)
    llp4 = models.BooleanField(default=False)
    lrp1 = models.BooleanField(default=False)
    lrp2 = models.BooleanField(default=False)
    lrp3 = models.BooleanField(default=False)
    lrp4 = models.BooleanField(default=False)
    llm1 = models.BooleanField(default=False)
    llm2 = models.BooleanField(default=False)
    llm3 = models.BooleanField(default=False)
    lrm1 = models.BooleanField(default=False)
    lrm2 = models.BooleanField(default=False)
    lrm3 = models.BooleanField(default=False)
    # indeterminate dental fields
    indet_incisor = models.BooleanField(default=False)
    indet_canine = models.BooleanField(default=False)
    indet_premolar = models.BooleanField(default=False)
    indet_molar = models.BooleanField(default=False)
    indet_tooth = models.BooleanField(default=False)
    deciduous = models.BooleanField(default=False)

    # Measurements
    um_tooth_row_length_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    um_1_length_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    um_1_width_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    um_2_length_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    um_2_width_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    um_3_length_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    um_3_width_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    lm_tooth_row_length_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    lm_1_length = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    lm_1_width = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    lm_2_length = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    lm_2_width = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    lm_3_length = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    lm_3_width = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "03-LGRP Biology"
        verbose_name_plural = "03-LGRP Biology"

    @staticmethod
    def find_unmatched_values(field_name):
        """
        For every field in the data model this function compares the values in the DB against the values
        in the choice lists and reports any unmatched values, i.e. DB values not in choices lists.
        :param field_name:
        :return:
        """
        lgrp_bio = Biology.objects.all()
        values = list(set([getattr(bio, field_name) for bio in lgrp_bio]))
        field = Biology._meta.get_field(field_name)[0]
        choices = [i[0] for i in field.choices]
        result = [v for v in values if v not in choices]
        if (not result) or result == [None]:
            result_tuple = (False, None, None)
            return result_tuple
        else:
            result_tuple = (True, len(result), result)
            return result_tuple


class Geology(Occurrence):
    find_type = models.CharField(null=True, blank=True, max_length=255)
    dip = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    strike = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    color = models.CharField(null=True, blank=True, max_length=255)
    texture = models.CharField(null=True, blank=True, max_length=255)

    class Meta:
        verbose_name = "04-LGRP Geology"
        verbose_name_plural = "04-LGRP Geology"


class Person(projects.models.Person):

    class Meta:
        verbose_name = "05-LGRP Person"
        verbose_name_plural = "05-LGRP People"
        ordering = ['name']


class CollectionCode(projects.models.PaleoCoreCollectionCodeBaseClass):

    class Meta:
        verbose_name = "06-LGRP Collection Code"
        ordering = ['name']


class StratigraphicUnit(projects.models.PaleoCoreStratigraphicUnitBaseClass):

    class Meta:
        verbose_name = "07-LGRP Stratigraphic Unit"


class TaxonRank(projects.models.TaxonRank):

    class Meta:
        verbose_name = "08-LGRP Taxon Rank"


class Taxon(projects.models.Taxon):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    rank = models.ForeignKey('TaxonRank', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "09-LGRP Taxon"
        verbose_name_plural = "09-LGRP Taxa"
        ordering = ['rank__ordinal', 'name']


class IdentificationQualifier(projects.models.IdentificationQualifier):

    class Meta:
        verbose_name = "10-LGRP ID Qualifier"


# Hydrology Class
class Hydrology(models.Model):
    length = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    name = models.CharField(null=True, blank=True, max_length=50)
    size = models.IntegerField(null=True, blank=True)
    map_sheet = models.CharField(null=True, blank=True, max_length=50)
    geom = models.LineStringField(srid=4326)
    objects = GeoManager()

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "11-LGRP Hydrology"
        verbose_name_plural = "11-LGRP Hydrology"


# Media Classes
class Image(models.Model):
    # Default is cascade on delete.
    occurrence = models.ForeignKey("Occurrence", related_name='occurrence_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="uploads/images", null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def thumbnail(self):
        try:
            return mark_safe('<a href="%s"><img src="%s" style="width:100px" /></a>' \
                   % (os.path.join(self.image.url), os.path.join(self.image.url)))
        except:
            return None
    thumbnail.short_description = 'Thumb'


class File(models.Model):
    occurrence = models.ForeignKey("Occurrence", related_name='occurrence_files', on_delete=models.CASCADE)
    file = models.FileField(upload_to="uploads/files", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
