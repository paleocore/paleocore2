from django.contrib.gis.db import models
import projects.models
from .ontologies import LAETOLI_AREAS, LAETOLI_UNITS, DATING_PROTOCOLS, DATING_REFERENCES
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.html import mark_safe
from django.db.models import Manager as GeoManager


class TaxonRank(projects.models.TaxonRank):
    class Meta:
        verbose_name = "Laetoli Taxon Rank"
        verbose_name_plural = "Laetoli Taxon Ranks"


class Taxon(projects.models.Taxon):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    rank = models.ForeignKey('TaxonRank', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Laetoli Taxon"
        verbose_name_plural = "Laetoli Taxa"


class IdentificationQualifier(projects.models.IdentificationQualifier):
    class Meta:
        verbose_name = "Laetoli ID Qualifier"
        verbose_name_plural = "Laetoli ID Qualifiers"


# Locality Class
class Locality(projects.models.PaleoCoreLocalityBaseClass):
    """
    Inherits name, date_created, date_modified, formation, member
    """
    area = models.CharField(max_length=255, null=True, blank=True, choices=LAETOLI_AREAS)
    unit = models.CharField(max_length=255, null=True, blank=True, choices=LAETOLI_UNITS)
    horizon = models.CharField(max_length=255, null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)
    geom = models.PolygonField(srid=4326, blank=True, null=True)
    date_last_modified = models.DateTimeField("Date Last Modified", auto_now=True)
    objects = GeoManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Laetoli Locality"
        verbose_name_plural = "Laetoli Localities"
        ordering = ("name",)


class Context(projects.models.PaleoCoreBaseClass):
    """
    Context <- PaleoCoreBaseClass
    inherits: name, date_creeated, date_modified

    """
    upper_unit = models.CharField(max_length=256, null=True, blank=True, default='Ma', choices=LAETOLI_UNITS)
    lower_unit = models.CharField(max_length=256, null=True, blank=True, default='Ma', choices=LAETOLI_UNITS)
    likely_unit = models.CharField(max_length=256, null=True, blank=True, default='Ma', choices=LAETOLI_UNITS)
    max_age = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    max_age_system = models.CharField(max_length=10, null=True, blank=True, default='Ma')
    min_age = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    min_age_system = models.CharField(max_length=10, null=True, blank=True, default='Ma')
    age_uncertainty_help_text = "In years as defined by DwC"
    age_uncertainty = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True,
                                          help_text=age_uncertainty_help_text)
    age_protocol = models.CharField(max_length=256, null=True, blank=True, choices=DATING_PROTOCOLS)
    age_references = models.TextField(null=True, blank=True)
    age_remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def usage_count(self):
        return Find.objects.filter(context=self).count()


class Find(projects.models.PaleoCoreOccurrenceBaseClass):
    """
    A class used to represent a Find or Occurrence.

    Find <- PaleoCoreOccurrenceBaseClass <- PaleoCoreGeomBaseClass <- PaleoCoreBaseClass
    name, created*, date_last_modified*, problem*, problem_comment*, remarks, last_import, georeference_remarks,
    geom, date_recorded*, year, barcode, field_number

    Attributes
    ----------
    catalog_number : str
        A unique alphanumeric value identifying the item.
    """
    catalog_number = models.CharField('Cat. No.', max_length=255, null=True, blank=True)
    locality_name = models.CharField('Locality', max_length=255, null=True, blank=True)
    area_name = models.CharField('Locality', max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    item_count = models.IntegerField(null=True, blank=True)
    disposition = models.CharField(max_length=255, null=True, blank=True)
    institution = models.CharField(max_length=255, null=True, blank=True)
    geological_context_name = models.CharField('Geol. Context', max_length=255, null=True, blank=True)
    context = models.ForeignKey(Context, null=True, blank=True, on_delete=models.CASCADE)

    # Verbatim fields to store data read directly from spreadsheet versions of the catalog
    verbatim_workbook_name = models.TextField(null=True, blank=True)
    verbatim_workbook_year = models.IntegerField(null=True, blank=True)
    verbatim_specimen_number = models.CharField('specimen_number', max_length=255, null=True, blank=True)
    verbatim_date_discovered = models.DateField(null=True, blank=True)
    verbatim_storage = models.CharField(max_length=255, null=True, blank=True)
    verbatim_tray = models.CharField(max_length=255, null=True, blank=True)
    verbatim_locality = models.CharField(max_length=255, null=True, blank=True)
    verbatim_horizon = models.CharField(max_length=255, null=True, blank=True)
    verbatim_element = models.TextField(max_length=255, null=True, blank=True)
    verbatim_kingdom = models.CharField(max_length=255, null=True, blank=True)
    verbatim_phylum_subphylum = models.CharField(max_length=255, null=True, blank=True)
    verbatim_class = models.CharField(max_length=255, null=True, blank=True)
    verbatim_order = models.CharField(max_length=255, null=True, blank=True)
    verbatim_family = models.CharField(max_length=255, null=True, blank=True)
    verbatim_tribe = models.CharField(max_length=255, null=True, blank=True)
    verbatim_genus = models.CharField(max_length=255, null=True, blank=True)
    verbatim_species = models.CharField(max_length=255, null=True, blank=True)
    verbatim_other = models.TextField(null=True, blank=True)
    verbatim_weathering = models.CharField(max_length=255, null=True, blank=True)
    verbatim_breakage = models.CharField(max_length=255, null=True, blank=True)
    verbatim_animal_damage = models.TextField(null=True, blank=True)
    verbatim_nonanimal_damage = models.TextField(null=True, blank=True)
    verbatim_comments = models.TextField(null=True, blank=True)
    verbatim_published = models.TextField(null=True, blank=True)
    verbatim_problems = models.TextField(null=True, blank=True)

    # method fields, many that provide static literal values for Darwin Core output
    def event_date(self):
        """
        create event data from date_recorded datatime object
        :return:
        """
        event_date = None
        if self.date_recorded:
            event_date = self.date_recorded.date()
        return event_date

    # @staticmethod
    # def basis_of_record():
    #     return 'FossilSpecimen'

    @staticmethod
    def country():
        return 'Ethiopia'

    @staticmethod
    def institution_code():
        return 'NMT'

    @staticmethod
    def collection_code():
        return 'EP'

    @staticmethod
    def organism_quantity_type():
        return 'NISP'

    @staticmethod
    def max_age_units():
        return 'Ma'

    def min_age_units(self):
        return self.max_age_units()

    @staticmethod
    def method_fields_to_export():
        """
        Method to store a list of fields that should be added to data exports.
        Called by export admin actions.
        These fields are defined in methods and are not concrete fields in the DB so have to be declared.
        :return:
        """
        return ['event_date']
        # return ['longitude', 'latitude', 'easting', 'northing', 'catalog_number', 'photo']


class Fossil(Find):
    sex = models.CharField("Sex", null=True, blank=True, max_length=50)
    tkingdom = models.CharField('Kingdom', max_length=255, null=True, blank=True)
    tphylum = models.CharField('Phylum', max_length=255, null=True, blank=True)
    tsubphylum = models.CharField('Phylum', max_length=255, null=True, blank=True)
    tclass = models.CharField('Class', max_length=255, null=True, blank=True)
    torder = models.CharField('Order', max_length=255, null=True, blank=True)
    tfamily = models.CharField('Family', max_length=255, null=True, blank=True)
    tsubfamily = models.CharField('Subfamily', max_length=255, null=True, blank=True)
    ttribe = models.CharField('Tribe', max_length=255, null=True, blank=True)
    tgenus = models.CharField('Genus', max_length=255, null=True, blank=True)
    tspecies = models.CharField('Trivial', max_length=255, null=True, blank=True)
    scientific_name = models.CharField(max_length=255, null=True, blank=True)
    taxon_rank = models.CharField(max_length=255, null=True, blank=True)
    identification_qualifier = models.CharField(max_length=255, null=True, blank=True)
    taxon_remarks = models.TextField(max_length=255, null=True, blank=True)
    identified_by = models.CharField(max_length=20, null=True, blank=True)
    full_taxon = models.TextField(max_length=255, null=True, blank=True)
    identifications = models.ManyToManyField(Taxon, through='Identification')

    @staticmethod
    def basis_of_record():
        return 'FossilSpecimen'

    def taxon_path(self):

        snl = [self.tkingdom, self.tphylum, self.tsubphylum, self.tclass, self.torder, self.tfamily, self.tsubfamily,
               self.ttribe, self.tgenus, self.tspecies]
        snl = ['' if x is None else x for x in snl]  # replace None elements with empty strings
        sn = ':'.join(snl)  # join all elements in the sci name list, colon delimited
        return sn

    def verbatim_taxon_path(self):
        snl = [self.verbatim_kingdom, self.verbatim_phylum_subphylum, self.verbatim_class,
               self.verbatim_order, self.verbatim_family, self.ttribe,
               self.tgenus, self.tspecies]
        snl = ['' if x is None else x for x in snl]  # replace None elements with empty strings
        sn = ':'.join(snl)  # join all elements in the sci name list, colon delimited
        return sn

    class Meta:
        verbose_name = 'Laetoli Fossil'
        verbose_name_plural = 'Laetoli Fossils'


class Identification(models.Model):
    fossil = models.ForeignKey(Fossil, on_delete=models.CASCADE)
    taxon = models.ForeignKey(Taxon,  on_delete=models.CASCADE)
    identified_by = models.CharField(max_length=255, null=True, blank=True)
    date_identified = models.DateField(null=True, blank=True)
    reference = models.TextField(null=True, blank=True)

