import os
from django.db.models import Manager as GeoManager
from django.contrib.gis.db import models

from hrp.ontologies import *
# from hrp.ontologies import ITEM_TYPE_VOCABULARY, HRP_COLLECTOR_CHOICES, \
#     HRP_COLLECTING_METHOD_VOCABULARY, HRP_BASIS_OF_RECORD_VOCABULARY, HRP_COLLECTION_CODES

from django.contrib.gis.geos import Point
import projects.models


class TaxonRank(projects.models.TaxonRank):
    class Meta:
        verbose_name = "HRP Taxon Rank"
        verbose_name_plural = "HRP Taxon Ranks"


class Taxon(projects.models.Taxon):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    rank = models.ForeignKey(TaxonRank, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "HRP Taxon"
        verbose_name_plural = "HRP Taxa"


class IdentificationQualifier(projects.models.IdentificationQualifier):
    class Meta:
        verbose_name = "HRP ID Qualifier"
        verbose_name_plural = "HRP ID Qualifiers"


# Locality Class
class Locality(projects.models.PaleoCoreLocalityBaseClass):
    id = models.CharField(primary_key=True, max_length=255)
    collection_code = models.CharField(null=True, blank=True, choices=HRP_COLLECTION_CODES, max_length=10)
    locality_number = models.IntegerField(null=True, blank=True)
    sublocality = models.CharField(null=True, blank=True, max_length=50)
    description = models.TextField(null=True, blank=True, max_length=255)
    stratigraphic_section = models.CharField(null=True, blank=True, max_length=50)
    upper_limit_in_section = models.IntegerField(null=True, blank=True)
    lower_limit_in_section = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    error_notes = models.CharField(max_length=255, null=True, blank=True)
    notes = models.CharField(max_length=254, null=True, blank=True)
    geom = models.PointField(srid=4326, blank=True, null=True)
    date_last_modified = models.DateTimeField("Date Last Modified", auto_now=True)
    objects = GeoManager()

    def __str__(self):
        nice_name = str(self.collection_code) + " " + str(self.locality_number) + str(self.sublocality)
        return nice_name.replace("None", "").replace("--", "")

    class Meta:
        verbose_name = "HRP Locality"
        verbose_name_plural = "HRP Localities"
        ordering = ("locality_number", "sublocality")


class Person(projects.models.Person):
    last_name = models.CharField("Last Name", null=True, blank=True, max_length=256)
    first_name = models.CharField("First Name", null=True, blank=True, max_length=256)

    class Meta:
        verbose_name = "HRP Person"
        verbose_name_plural = "HRP People"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        if self.last_name and self.first_name:
            name = self.last_name+', '+self.first_name
        else:
            name = self.last_name
        return name


# Occurrence Class and Subclasses
class Occurrence(projects.models.PaleoCoreOccurrenceBaseClass):
    """
        Occurrence == Specimen, a general class for things discovered in the field.
        Find's have three subtypes: Archaeology, Biology, Geology
        Fields are grouped by comments into logical sets (i.e. ontological classes)
        """
    basis_of_record = models.CharField("Basis of Record", max_length=50, blank=True, null=False,
                                       help_text='e.g. Observed item or Collected item',
                                       choices=HRP_BASIS_OF_RECORD_VOCABULARY)  # NOT NULL  dwc:basisOfRecord
    field_number = models.CharField("Field Number", max_length=50, null=True, blank=True)
    item_type = models.CharField("Item Type", max_length=255, blank=True, null=False,
                                 choices=ITEM_TYPE_VOCABULARY)  # NOT NULL
    # TODO merge with taxon
    item_scientific_name = models.CharField("Sci Name", max_length=255, null=True, blank=True)
    # TODO merge with element
    item_description = models.CharField("Description", max_length=255, blank=True, null=True)
    item_count = models.IntegerField("Item Count", blank=True, null=True, default=1)
    collector = models.CharField("Collector", max_length=50, blank=True, null=True, choices=HRP_COLLECTOR_CHOICES)
    recorded_by = models.ForeignKey("Person", null=True, blank=True, related_name="occurrence_recorded_by",
                                    on_delete=models.SET_NULL)
    finder = models.CharField("Finder", null=True, blank=True, max_length=50, choices=HRP_COLLECTOR_CHOICES)
    found_by = models.ForeignKey("Person", null=True, blank=True, related_name="occurrence_found_by",
                                 on_delete=models.SET_NULL)
    collecting_method = models.CharField("Collecting Method", max_length=50,
                                         choices=HRP_COLLECTING_METHOD_VOCABULARY,
                                         null=True, blank=True)
    locality = models.ForeignKey("Locality", null=True, blank=True, on_delete=models.SET_NULL)
    item_number = models.IntegerField("Item #", null=True, blank=True)
    item_part = models.CharField("Item Part", max_length=10, null=True, blank=True)
    cat_number = models.CharField("Cat Number", max_length=255, blank=True, null=True)
    disposition = models.CharField("Disposition", max_length=255, blank=True, null=True)
    preparation_status = models.CharField("Prep Status", max_length=50, blank=True, null=True)
    # TODO rename collection remarks to find remarks
    collection_remarks = models.TextField("Collection Remarks", null=True, blank=True, max_length=255)

    # Geological Context
    stratigraphic_formation = models.CharField("Formation", max_length=255, blank=True, null=True)
    stratigraphic_member = models.CharField("Member", max_length=255, blank=True, null=True)
    analytical_unit_1 = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_2 = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_3 = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_found = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_likely = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_simplified = models.CharField(max_length=255, blank=True, null=True)
    in_situ = models.BooleanField(default=False)
    ranked = models.BooleanField(default=False)
    weathering = models.SmallIntegerField(blank=True, null=True)
    surface_modification = models.CharField("Surface Mod", max_length=255, blank=True, null=True)
    geology_remarks = models.TextField("Geol Remarks", max_length=500, null=True, blank=True)

    # Location
    collection_code = models.CharField("Collection Code", max_length=20, blank=True, null=True)
    drainage_region = models.CharField("Drainage Region", null=True, blank=True, max_length=255)

    # Media
    image = models.FileField(max_length=255, blank=True, upload_to="uploads/images/hrp", null=True)

    class Meta:
        verbose_name = "HRP Occurrence"
        verbose_name_plural = "HRP Occurrences"
        ordering = ["collection_code", "locality", "item_number", "item_part"]

    def catalog_number(self):
        """
        Generate a pretty string formatted catalog number from constituent fields
        :return: catalog number as string
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

            catalog_number_string = str(self.collection_code) + " " + str(self.locality_id) + item_text
            return catalog_number_string.replace('None', '').replace('- ', '')  # replace None with empty string
        else:
            return None

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

    def get_all_field_names(self):
        """
        Field names from model
        :return: list with all field names
        """
        field_list = self._meta.get_fields()  # produce a list of field objects
        return [f.name for f in field_list]  # return a list of names from each field

    def get_foreign_key_field_names(self):
        """
        Get foreign key fields
        :return: returns a list of for key field names
        """
        field_list = self._meta.get_fields()  # produce a list of field objects
        return [f.name for f in field_list if f.is_relation]  # return a list of names for fk fields

    def get_concrete_field_names(self):
        """
        Get field names that correspond to columns in the DB
        :return: returns a lift
        """
        field_list = self._meta.get_fields()
        return [f.name for f in field_list if f.concrete]


class Biology(Occurrence):
    # Biology
    sex = models.CharField("Sex", null=True, blank=True, max_length=50)
    life_stage = models.CharField("Life Stage", null=True, blank=True, max_length=50, choices=HRP_LIFE_STAGE_CHOICES)
    size_class = models.CharField("Size Class", null=True, blank=True, max_length=50, choices=HRP_SIZE_CLASS_CHOICES)
    # Taxon
    taxon = models.ForeignKey(Taxon,
                              default=0, on_delete=models.SET_DEFAULT,  # prevent deletion when taxa deleted
                              related_name='hrp_taxon_bio_occurrences')
    identification_qualifier = models.ForeignKey(IdentificationQualifier, null=True, blank=True,
                                                 on_delete=models.SET_NULL,
                                                 related_name='hrp_id_qualifier_bio_occurrences')
    qualifier_taxon = models.ForeignKey(Taxon, null=True, blank=True,
                                        on_delete=models.SET_NULL,
                                        related_name='hrp_qualifier_taxon_bio_occurrences')
    verbatim_taxon = models.CharField(null=True, blank=True, max_length=1024)
    verbatim_identification_qualifier = models.CharField(null=True, blank=True, max_length=255)
    taxonomy_remarks = models.TextField(max_length=500, null=True, blank=True)

    # Identification
    identified_by = models.CharField(null=True, blank=True, max_length=100, choices=HRP_IDENTIFIER_CHOICES)
    year_identified = models.IntegerField(null=True, blank=True)
    type_status = models.CharField(null=True, blank=True, max_length=50)

    fauna_notes = models.TextField(null=True, blank=True, max_length=64000)

    # Element
    side = models.CharField("Side", null=True, blank=True, max_length=50, choices=HRP_SIDE_CHOICES)
    element = models.CharField("Element", null=True, blank=True, max_length=50, choices=HRP_ELEMENT_CHOICES)
    # TODO add element_modifier choices once field is cleaned
    element_modifier = models.CharField("Element Mod", null=True, blank=True, max_length=50,
                                        choices=HRP_ELEMENT_MODIFIER_CHOICES)
    # TODO populate portion after migrate
    element_portion = models.CharField("Element Portion", null=True, blank=True, max_length=50,
                                       choices=HRP_ELEMENT_PORTION_CHOICES)
    # TODO populate number choices after migrate
    element_number = models.CharField(null=True, blank=True, max_length=50, choices=HRP_ELEMENT_NUMBER_CHOICES)
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
    # TODO delete attributes, preparations and morphobank number
    attributes = models.CharField(null=True, blank=True, max_length=50)
    preparations = models.CharField(null=True, blank=True, max_length=50)
    morphobank_number = models.IntegerField(null=True, blank=True)  # empty, ok to delete

    def __str__(self):
        return str(self.taxon.__str__())

    class Meta:
        verbose_name = "HRP Biology"
        verbose_name_plural = "HRP Biology"


class Archaeology(Occurrence):
    find_type = models.CharField(null=True, blank=True, max_length=255)
    length_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    width_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)

    class Meta:
        verbose_name = "HRP Archaeology"
        verbose_name_plural = "HRP Archaeology"


class Geology(Occurrence):
    find_type = models.CharField(null=True, blank=True, max_length=255)
    dip = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    strike = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    color = models.CharField(null=True, blank=True, max_length=255)
    texture = models.CharField(null=True, blank=True, max_length=255)

    class Meta:
        verbose_name = "HRP Geology"
        verbose_name_plural = "HRP Geology"


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
        verbose_name = "HRP Hydrology"
        verbose_name_plural = "HRP Hydrology"


# Media Classes
class Image(models.Model):
    occurrence = models.ForeignKey("Occurrence", related_name='hrp_occurrences', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="uploads/images", null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class File(models.Model):
    occurrence = models.ForeignKey("Occurrence", on_delete=models.CASCADE)
    file = models.FileField(upload_to="uploads/files", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
