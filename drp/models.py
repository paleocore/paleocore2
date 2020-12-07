import os
from datetime import datetime
from django.contrib.gis.db import models
from django.db.models import Manager as GeoManager
from django.utils.html import mark_safe
import projects.models

from drp.ontologies import BASIS_OF_RECORD_VOCABULARY, ITEM_TYPE_VOCABULARY, COLLECTING_METHOD_VOCABULARY, \
    COLLECTOR_CHOICES


class TaxonRank(projects.models.TaxonRank):

    class Meta:
        verbose_name = "Taxon Rank"
        verbose_name_plural = "Taxon Ranks"

    def __str__(self):
        return str(self.name)


class Taxon(projects.models.Taxon):
    name = models.CharField(null=False, blank=False, max_length=255, unique=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    rank = models.ForeignKey(TaxonRank, null=True, blank=True, on_delete=models.SET_NULL)

    def parent_rank(self):
        return self.parent.rank.name

    def rank_ordinal(self):
        return self.rank.ordinal

    def parent_name(self):
        if self.parent is None:
            return "NA"
        else:
            return self.parent.name

    def full_name(self):
        if self.parent is None:
            return self.name
        elif self.parent.parent is None:
            return self.name
        else:
            return self.parent.full_name() + ", " + self.name

    def full_lineage(self):
        """
        Get a list of taxon object representing the full lineage hierarchy
        :return: list of taxon objects ordered highest rank to lowest
        """
        if self.parent is None:
            return [self]
        if self.parent.parent is None:
            return [self]
        else:
            return self.parent.full_lineage()+[self]

    def __str__(self):
        if self.rank.name == 'Species' and self.parent:
            return "[" + self.rank.name + "] " + self.parent.name + " " + self.name
        else:
            return "[" + self.rank.name + "] " + str(self.name)

    class Meta:
        verbose_name = "Taxon"
        verbose_name_plural = "taxa"
        ordering = ['rank__ordinal', 'name']


class IdentificationQualifier(projects.models.IdentificationQualifier):
    name = models.CharField(null=False, blank=True, max_length=15, unique=True)
    qualified = models.BooleanField()

    def __str__(self):
        return self.name


item_typeCHOICES = (("Artifactual", "Artifactual"),
                    ("Faunal", "Faunal"),
                    ("Floral", "Floral"),
                    ("Geological", "Geological"))


class Locality(projects.models.PaleoCoreLocalityBaseClass):
    paleolocality_number = models.IntegerField(null=True, blank=True)
    collection_code = models.CharField(null=True, blank=True, choices=(("DIK", "DIK"), ("ASB", "ASB")), max_length=10)
    paleo_sublocality = models.CharField(null=True, blank=True, max_length=50)
    description_1 = models.TextField(null=True, blank=True, max_length=255)
    description_2 = models.TextField(null=True, blank=True, max_length=255)
    description_3 = models.TextField(null=True, blank=True, max_length=255)
    stratigraphic_section = models.CharField(null=True, blank=True, max_length=50)
    upper_limit_in_section = models.IntegerField(null=True, blank=True)
    lower_limit_in_section = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    error_notes = models.CharField(max_length=255, null=True, blank=True)
    notes = models.CharField(max_length=254, null=True, blank=True)
    geom = models.PolygonField(srid=4326)
    objects = GeoManager()

    class Meta:
        verbose_name = "DRP Locality"
        verbose_name_plural = "DRP Localities"
        ordering = ("collection_code", "paleolocality_number", "paleo_sublocality")

    def __str__(self):
        name_string = ''
        if self.name:
            name_string = self.name
        return name_string


# This is the DRP data model. It is only partly PaleoCore compliant.
class Occurrence(projects.models.PaleoCoreOccurrenceBaseClass):
    # date_last_modified = models.DateTimeField("Date Last Modified", auto_now=True)
    basis_of_record = models.CharField("Basis of Record", max_length=50, blank=True, null=False,
                                       choices=BASIS_OF_RECORD_VOCABULARY)  # NOT NULL
    item_type = models.CharField("Item Type", max_length=255, blank=True, null=False,
                                 choices=ITEM_TYPE_VOCABULARY)  # NOT NULL
    collection_code = models.CharField("Collection Code", max_length=20, blank=True, null=True,
                                       choices=(('DIK', 'DIK'), ('ASB', 'ASB')))
    item_number = models.IntegerField("Item #", null=True, blank=True)
    item_part = models.CharField("Item Part", max_length=10, null=True, blank=True)
    catalog_number = models.CharField("Catalog #", max_length=255, blank=True, null=True)
    item_scientific_name = models.CharField("Sci Name", max_length=255, null=True, blank=True)
    item_description = models.CharField("Description", max_length=255, blank=True, null=True)
    collecting_method = models.CharField("Collecting Method", max_length=50,
                                         choices=COLLECTING_METHOD_VOCABULARY, null=False)
    related_catalog_items = models.CharField("Related Catalog Items", max_length=50, null=True, blank=True)
    collector = models.CharField(max_length=50, blank=True, null=True, choices=COLLECTOR_CHOICES)
    finder = models.CharField(null=True, blank=True, max_length=50)
    disposition = models.CharField(max_length=255, blank=True, null=True)
    field_number_orig = models.DateTimeField(blank=True, null=True, editable=True)
    individual_count = models.IntegerField(blank=True, null=True, default=1)
    preparation_status = models.CharField(max_length=50, blank=True, null=True)
    stratigraphic_marker_upper = models.CharField(max_length=255, blank=True, null=True)
    distance_from_upper = models.DecimalField(max_digits=38, decimal_places=8, blank=True, null=True)
    stratigraphic_marker_lower = models.CharField(max_length=255, blank=True, null=True)
    distance_from_lower = models.DecimalField(max_digits=38, decimal_places=8, blank=True, null=True)
    stratigraphic_marker_found = models.CharField(max_length=255, blank=True, null=True)
    distance_from_found = models.DecimalField(max_digits=38, decimal_places=8, blank=True, null=True)
    stratigraphic_marker_likely = models.CharField(max_length=255, blank=True, null=True)
    distance_from_likely = models.DecimalField(max_digits=38, decimal_places=8, blank=True, null=True)
    stratigraphic_member = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_2 = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_3 = models.CharField(max_length=255, blank=True, null=True)
    in_situ = models.BooleanField(default=False)
    ranked = models.BooleanField(default=False)
    image = models.FileField(max_length=255, blank=True, upload_to="uploads/images/drp", null=True)
    weathering = models.SmallIntegerField(blank=True, null=True)
    surface_modification = models.CharField(max_length=255, blank=True, null=True)

    # DRP Specific Fields
    paleolocality_number = models.IntegerField("Locality #", null=True, blank=True)
    paleo_sublocality = models.CharField("Sublocality", null=True, blank=True, max_length=50)
    locality_text = models.CharField(null=True, blank=True, max_length=255, db_column="locality")
    verbatim_coordinates = models.CharField(null=True, blank=True, max_length=50)
    verbatim_coordinate_system = models.CharField(null=True, blank=True, max_length=50)
    geodetic_datum = models.CharField(null=True, blank=True, max_length=20)
    collection_remarks = models.CharField("Remarks", null=True, blank=True, max_length=255)
    stratigraphic_section = models.CharField(null=True, blank=True, max_length=50)
    stratigraphic_height_in_meters = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    locality = models.ForeignKey(Locality, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        nice_name = str(self.collection_code) + "-" + str(self.paleolocality_number) + "-" + str(self.item_number) + \
                    str(self.item_part) + " [" + str(self.item_scientific_name) + " " + str(self.item_description) + "]"
        return nice_name.replace("None", "").replace("--", "")

    @staticmethod
    def fields_to_display():
        fields = ("id", "barcode")
        return fields

    def save(self, *args, **kwargs):  # custom save method for occurrence
        the_catalog_number = str(self.collection_code) + "-" + str(self.paleolocality_number) + \
                             str(self.paleo_sublocality) + "-" + str(self.item_number) + str(self.item_part)
        self.catalog_number = the_catalog_number.replace("None", "")
        self.date_last_modified = datetime.now()  # TODO change date_last_modified autonow option to accomplish this

        # call the normal drp_occurrence save method using alternate database
        super(Occurrence, self).save(*args, **kwargs)


class Image(models.Model):
    occurrence = models.ForeignKey("Occurrence", related_name='drp_occurrences', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="uploads/images", null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class File(models.Model):
    occurrence = models.ForeignKey("Occurrence", on_delete=models.CASCADE)
    file = models.FileField(upload_to="uploads/files", null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class Biology(Occurrence):
    infraspecific_epithet = models.CharField(null=True, blank=True, max_length=50)
    infraspecific_rank = models.CharField(null=True, blank=True, max_length=50)
    author_year_of_scientific_name = models.CharField(null=True, blank=True, max_length=50)
    nomenclatural_code = models.CharField(null=True, blank=True, max_length=50)
    # identification_qualifier = models.CharField(null=True, blank=True, max_length=50)
    identified_by = models.CharField(null=True, blank=True, max_length=100)
    date_identified = models.DateTimeField(null=True, blank=True)
    type_status = models.CharField(null=True, blank=True, max_length=50)
    sex = models.CharField(null=True, blank=True, max_length=50)
    life_stage = models.CharField(null=True, blank=True, max_length=50)
    preparations = models.CharField(null=True, blank=True, max_length=50)
    morphobank_number = models.IntegerField(null=True, blank=True)
    side = models.CharField(null=True, blank=True, max_length=50)
    attributes = models.CharField(null=True, blank=True, max_length=50)
    fauna_notes = models.TextField(null=True, blank=True, max_length=64000)
    tooth_upper_or_lower = models.CharField(null=True, blank=True, max_length=50)
    tooth_number = models.CharField(null=True, blank=True, max_length=50)
    tooth_type = models.CharField(null=True, blank=True, max_length=50)
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
    element = models.CharField(null=True, blank=True, max_length=50)
    element_modifier = models.CharField(null=True, blank=True, max_length=50)
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
    taxon = models.ForeignKey(Taxon,
                              default=0, on_delete=models.SET_DEFAULT,  # prevent deletion when taxa deleted
                              related_name='drp_biology_occurrences')
    identification_qualifier = models.ForeignKey(IdentificationQualifier, null=True, blank=True,
                                                 on_delete=models.SET_NULL,
                                                 related_name='drp_biology_occurrences')

    class Meta:
        verbose_name = "DRP Biology"
        verbose_name_plural = "DRP Biology"

    def __str__(self):
        return str(self.taxon.__str__())


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
        verbose_name = "DRP Hydrology"
        verbose_name_plural = "DRP Hydrology"
