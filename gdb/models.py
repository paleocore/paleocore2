from django.contrib.gis.db import models
import gdb.ontologies
import projects.models
from ckeditor.fields import RichTextField as CKRichTextField


class Occurrence(projects.models.PaleoCoreOccurrenceBaseClass):
    """
    Occurrence <- PaleoCoreOccurrenceBaseClass <- PaleoCoreGeomBaseClass <- PaleoCoreBaseClass
    """
    catalog_number = models.AutoField(primary_key=True)  # NOT NULL
    cm_catalog_number = models.IntegerField(null=True, blank=True)  # CM SPec #
    locality = models.ForeignKey("Locality", to_field="locality_number", null=True, blank=True,
                                 on_delete=models.SET_NULL)
    date_time_collected = models.DateTimeField(null=True, blank=True)
    date_collected = models.DateField(null=True, blank=True, editable=True)
    time_collected = models.CharField(null=True, blank=True, max_length=50)
    basis_of_record = models.CharField("Basis of Record", max_length=50, blank=False, null=False,  # NOT NULL
                                       choices=gdb.ontologies.BASIS_OF_RECORD_VOCABULARY,
                                       default=gdb.ontologies.fossil)
    item_type = models.CharField("Item Type", max_length=255, blank=True, null=True,
                                 choices=gdb.ontologies.ITEM_TYPE_VOCABULARY,
                                 default=gdb.ontologies.faunal)
    collecting_method = models.CharField("Collecting Method", max_length=50, blank=True, null=True,
                                         choices=gdb.ontologies.COLLECTING_METHOD_VOCABULARY, )
    related_catalog_items = models.CharField("Related Catalog Items", max_length=50, null=True, blank=True)
    item_scientific_name = models.CharField("Scientific Name", null=True, blank=True, max_length=255)  # Taxon
    item_description = models.CharField("Description", null=True, blank=True, max_length=255)
    image = models.FileField(max_length=255, blank=True, upload_to="uploads/images/gdb", null=True)

    # Disposition fields
    loan_date = models.DateField(null=True, blank=True)
    loan_recipient = models.CharField(null=True, blank=True, max_length=255)
    on_loan = models.BooleanField(default=False)  # Loan Status

    # Geospatial
    elevation = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    def __str__(self):
        return str(self.catalog_number)

    @staticmethod
    def method_fields_to_export():
        """
        Method to store a list of fields that should be added to data exports.
        Called by export admin actions.
        These fields are defined in methods and are not concrete fields in the DB so have to be declared.
        :return:
        """
        return []  # The GDB project has no method fields to export

    class Meta:
        verbose_name = "GDB Occurrence"


class Biology(Occurrence):
    # Taxonomy fields
    kingdom = models.CharField("Kingdom", null=True, blank=True, max_length=50)
    phylum = models.CharField("Phylum", null=True, blank=True, max_length=50)
    tax_class = models.CharField("Class", null=True, blank=True, max_length=50)  # Class
    tax_order = models.CharField("Order", null=True, blank=True, max_length=50)  # Order
    family = models.CharField("Family", null=True, blank=True, max_length=50)
    subfamily = models.CharField("Subfamily", null=True, blank=True, max_length=50)
    tribe = models.CharField("Tribe", null=True, blank=True, max_length=50)
    genus = models.CharField("Genus", null=True, blank=True, max_length=50)
    specific_epithet = models.CharField("Species Name", null=True, blank=True, max_length=50)  # Species
    infraspecific_epithet = models.CharField("Infraspecies", null=True, blank=True, max_length=50)
    infraspecific_rank = models.CharField("Infraspecies rank", null=True, blank=True, max_length=50)
    # Identification fields
    author_year_of_scientific_name = models.CharField(null=True, blank=True, max_length=50)
    nomenclatural_code = models.CharField(null=True, blank=True, max_length=50)
    identification_qualifier_original = models.CharField(null=True, blank=True, max_length=50)
    identified_by = models.CharField(null=True, blank=True, max_length=100)
    date_identified = models.DateTimeField(null=True, blank=True)
    type_status = models.CharField(null=True, blank=True, max_length=50)
    # Description fields
    sex = models.CharField(null=True, blank=True, max_length=50)
    life_stage = models.CharField(null=True, blank=True, max_length=50)
    preparations = models.CharField(null=True, blank=True, max_length=50)
    morphobank_num = models.IntegerField(null=True, blank=True)
    element = models.CharField(null=True, blank=True, max_length=50)
    side = models.CharField(null=True, blank=True, max_length=50)
    attributes = models.CharField(null=True, blank=True, max_length=50)
    notes = CKRichTextField(null=True, blank=True)
    lower_tooth = models.CharField(null=True, blank=True, max_length=50)
    upper_tooth = models.CharField(null=True, blank=True, max_length=50)
    jaw = models.CharField(null=True, blank=True, max_length=50)
    mandible = models.CharField(null=True, blank=True, max_length=50)
    maxilla = models.CharField(null=True, blank=True, max_length=50)
    teeth = models.CharField(null=True, blank=True, max_length=50)
    cranial = models.CharField(null=True, blank=True, max_length=50)
    miscellaneous = models.CharField(null=True, blank=True, max_length=50)
    vertebral = models.CharField(null=True, blank=True, max_length=50)
    forelimb = models.CharField(null=True, blank=True, max_length=50)
    hindlimb = models.CharField(null=True, blank=True, max_length=50)

    taxon = models.ForeignKey('Taxon',
                              default=0, on_delete=models.SET_DEFAULT,  # prevent deletion when taxa deleted
                              related_name='gdb_taxon_bio_occurrences')
    identification_qualifier = models.ForeignKey('IdentificationQualifier',
                                                 on_delete=models.SET_NULL,
                                                 related_name='gdb_id_qualifier_bio_occurrences',
                                                 null=True, blank=True)

    class Meta:
        verbose_name = "GDB Biology"
        verbose_name_plural = "GDB Biology Items"


class Locality(projects.models.PaleoCoreLocalityBaseClass):
    """
    Locality <- PaleoCoreLocalityBaseClass <- PaleoCoreGeomBaseClass <- PaleoCoreBaseClass
    """
    locality_number = models.IntegerField(primary_key=True)  # NOT NULL
    locality_field_number = models.CharField(null=True, blank=True, max_length=50)
    date_discovered = models.DateField(null=True, blank=True)
    NALMA = models.CharField(null=True, blank=True, max_length=50,
                             choices=gdb.ontologies.NALMA_CHOICES,
                             default=gdb.ontologies.wasatchian
                             )
    sub_age = models.CharField(null=True, blank=True, max_length=50,
                               choices=gdb.ontologies.NALMA_SUB_AGE_CHOICES)
    survey = models.CharField(null=True, blank=True, max_length=50)
    quad_sheet = models.CharField(null=True, blank=True, max_length=50)
    verbatim_latitude = models.CharField(null=True, blank=True, max_length=50)  # Latitude
    verbatim_longitude = models.CharField(null=True, blank=True, max_length=50)  # Longitude
    verbatim_utm = models.CharField(null=True, blank=True, max_length=50)  # UTM
    verbatim_gps_coordinates = models.CharField(null=True, blank=True, max_length=50)  # GPS
    verbatim_elevation = models.IntegerField(null=True, blank=True)  # Elevation
    gps_date = models.DateField(null=True, blank=True, editable=True)
    resource_area = models.CharField(null=True, blank=True, max_length=50)
    notes = CKRichTextField(null=True, blank=True)
    cm_locality_number = models.IntegerField(null=True, blank=True)  # CM Loc #
    region = models.CharField(null=True, blank=True, max_length=50)
    blm_district = models.CharField(null=True, blank=True, max_length=50)
    county = models.CharField(null=True, blank=True, max_length=50)
    image = models.FileField(max_length=255, blank=True, upload_to="uploads/images/gdb", null=True)

    def __str__(self):
        """
        This method returns the locality number and name if both exist, or a string with
        just the locality number if there is no name.
        """
        if self.name:
            return str(self.locality_number)+"-"+self.name
        else:
            return str(self.locality_number)

    def update_geom_from_verbatim(self):
        if self.verbatim_latitude is not None:
            lat_dms = self.verbatim_latitude
            lon_dms = self.verbatim_longitude
            lat_string = lat_dms.split()
            lon_string = lon_dms.split()
            if len(lat_string) == 4 and len(lon_string) == 4:
                lat_dd = (float(lat_string[2])/60+float(lat_string[1]))/60+float(lat_string[0])
                if lat_string[3] == "S":
                    lat_dd *= -1  # southern latitudes should be negative
                lon_dd = (float(lon_string[2])/60+float(lon_string[1]))/60+float(lon_string[0])
                if lon_string[3] == "W":
                    lon_dd *= -1
            return "POINT ("+str(lon_dd)+" "+str(lat_dd)+")"

    def fossil_count(self):
        """
        Method to count the number of fossils at a locality
        :return:
        """
        return Biology.objects.filter(locality=self).count

    class Meta:
        verbose_name_plural = "GDB Localities"
        ordering = ['locality_number']


class TaxonRank(projects.models.TaxonRank):
    class Meta:
        verbose_name = "GDB Taxon Rank"
        verbose_name_plural = "GDB Taxon Ranks"


class Taxon(projects.models.Taxon):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    rank = models.ForeignKey(TaxonRank, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "GDB Taxon"
        verbose_name_plural = "GDB Taxa"
        ordering = ['rank__ordinal', 'name']


class IdentificationQualifier(projects.models.IdentificationQualifier):

    class Meta:
        verbose_name = "GDB ID Qualifier"
