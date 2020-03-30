# IMPORTS
import os
# Django imports
from django.db.models import Manager as GeoManager
from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.apps import apps
from django.utils import timezone
from django.contrib.gis.geos import Point
from django_countries.fields import CountryField
from django.utils.html import format_html

# Python imports
import math

# Wagtail imports
from wagtail.core import blocks
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.search import index
from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, StreamFieldPanel
)
from wagtailgeowidget.edit_handlers import GeoPanel
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from utils.models import RelatedLink, CarouselItem
from ckeditor.fields import RichTextField as CKRichTextField


# MODELS
# Abstract Models - Not managed by migrations, not in DB
class PaleoCoreBaseClass(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField('Created',
                                        default=timezone.now,
                                        # auto_now_add=True,
                                        help_text='The date and time this resource was first created.')
    date_last_modified = models.DateTimeField('Modified',
                                              default=timezone.now,
                                              # auto_now=True,
                                              help_text='The date and time this resource was last altered.')
    problem = models.BooleanField(default=False,
                                  help_text='Is there a problem with this record that needs attention?')
    problem_comment = models.TextField(max_length=255, blank=True, null=True,
                                       help_text='Description of the problem.')
    remarks = CKRichTextField("Record Remarks", null=True, blank=True,
                              help_text='General remarks about this database record.')
    last_import = models.BooleanField(default=False)

    # TODO make sure the str method on this class is optimized and producing unnecessary queries
    def __str__(self):
        id_string = '['+str(self.id)+']'
        if self.name:
            id_string = id_string+' '+self.name
        return id_string

    def get_app_label(self):
        """
        Get the app label associated with an instance of this class.
        returns the app label as a string, e.g. 'mlp'
        """
        return ContentType.objects.get_for_model(self).app_label

    def get_concrete_field_names(self):
        """
        Get field names that correspond to columns in the DB
        :return: returns a lift
        """
        field_list = self._meta.get_fields()
        return [f.name for f in field_list if f.concrete]

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

    def photo(self):
        try:
            return format_html('<a href="%s"><img src="%s" style="width:600px" /></a>' \
                   % (os.path.join(self.image.url), os.path.join(self.image.url)))
        except:
            return None
    photo.short_description = 'Photo'

    def thumbnail(self):
        try:
            return format_html('<a href="%s"><img src="%s" style="width:100px" /></a>' \
                   % (os.path.join(self.image.url), os.path.join(self.image.url)))
        except:
            return None
    thumbnail.short_description = 'Thumb'

    class Meta:
        abstract = True
        ordering = ['name']


class TaxonRank(PaleoCoreBaseClass):
    """
    The rank of a taxon in the standard Linaean hierarchy, e.g. Kingdom, Phylum, Class, Order etc.
    """
    name = models.CharField(null=False, blank=False, max_length=50, unique=True)
    plural = models.CharField(null=False, blank=False, max_length=50, unique=True)
    ordinal = models.IntegerField(null=False, blank=False, unique=True)

    class Meta:
        abstract = True
        verbose_name = "Taxon Rank"


class Taxon(PaleoCoreBaseClass):
    """
    Taxon <- PaleoCoreBaseClass
    A biological taxon at any rank, e.g. Mammalia, Homo, Homo sapiens idaltu

    Attributes of Taxon:

    Attributes "name" through "last_import" are inherited from PaleoCoreBaseClass

    The attributes "parent" and "rank" are assumed to be defined in each inheriting class.
    They cannot be defined here because they are foreign keys and fks cannot be included in Abstract Classes.
    The methods included in this abstract class assume that the fields rank and parent are defined.

    name
    date_created
    date_last_modified
    problem, problem_comment
    remarks,
    last_import
    ------
    parent
    rank
    ------
    label

    """
    # For a species, the name field contains the specific epithet and
    # the label field contains the full scientific name.
    # e.g. Homo sapiens
    # name = sapiens
    # label = Homo sapiens
    label_help_text = """For a species, the name field contains the specific epithet and the label contains the full
    scientific name, e.g. Homo sapiens, name = sapiens, label = Homo sapiens"""
    label = models.CharField(max_length=244, null=True, blank=True, help_text=label_help_text)

    def __str__(self):
        return str(self.label)

    def update_label(self):
        """
        Update the values in the label field to match the name field.
        If the taxon is a species then the label should be the genus name and the specific epithet
        For all higher taxa the label == name
        :return:
        """
        if self.rank.name == 'Species' and self.parent:
            self.label = self.parent.name + ' ' + self.name
        else:
            self.label = self.name

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

    def biology_usages(self):
        """
        Method to get a count of the number of Biology objects pointing to the taxon instance. This method usese
        the content type system to find the containing app and model.
        :return: Returns and integer count of the number of biology instances in the app that point to the taxon.
        """
        result = None
        app = self._meta.app_label
        try:
            content_type = ContentType.objects.get(app_label=app, model='biology')  # assumes the model is named Biology
            this_biology = content_type.model_class()
            result = this_biology.objects.filter(taxon=self).count()
        except ContentType.DoesNotExist:
            pass  # If no matching content type then we'll pass here and return None
        return result

    def get_higher_taxon(self, rank):
        """
        Method to get arbitrary higher rank for a taxon.
        :param rank: The target TaxonRank object
        :return: returns a Taxon object of a specified rank if higher taxon exists.
        Returns None for lower taxonomic rank.

        """
        if self.taxon.rank == rank:  # if current taxon rank equals target return current
            current_taxon = self.taxon  # set current taxon
        elif self.taxon.rank.ordinal < rank:
            current_taxon = None
        else:
            while current_taxon.rank > rank:  # iterate through taxon hierarchy until rank equals target
                current_taxon = current_taxon.parent
        return current_taxon  # return the appropriate higher taxon object

        # if taxon_rank_object.ordinal >= self.rank:  # trying to bet lower rank
        #     raise: ObjectDoesNotExist

    def get_children(self):
        """
        Method to get the children taxa
        :return: Returns a queryset of children Taxon objects that have existing Biology instances
        """
        return type(self).objects.filter(parent=self)

    class Meta:
        abstract = True
        verbose_name = "Taxon"
        verbose_name_plural = "Taxa"
        ordering = ['rank__ordinal', 'name']


class IdentificationQualifier(PaleoCoreBaseClass):
    """
    A modifier to a taxonomic designation, e.g. cf., aff.
    """
    name = models.CharField(null=False, blank=True, max_length=15, unique=True)
    qualified = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Person(PaleoCoreBaseClass):
    """
    A person or agent.
    """
    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        verbose_name = "Person"
        verbose_name_plural = "People"


class PaleoCoreGeomBaseClass(PaleoCoreBaseClass):
    # Location
    georeference_remarks = models.TextField(max_length=500, null=True, blank=True)
    geom = models.PointField(srid=4326, null=True, blank=True)
    objects = GeoManager()

    def gcs_coordinates(self, coordinate):
        """
        Get the wgs84 gcs coordinates for a point regardless of the point's srs.  Assumes gdal can transform any srs
        to gcs.
        :param coordinate: lat, lon, both
        :return: lat, lon, (lon, lat)
        """
        result = None
        if self.geom:
            if self.geom.geom_type != 'Point':
                result = None
            else:
                if self.geom.srid == 4326:
                    pt = self.geom
                else:
                    # Assumes all SRS can be converted to 4326
                    pt = self.geom.transform(4326, clone=True)
                if coordinate in ['lat', 'latitude']:
                    result = pt.y
                elif coordinate in ['lon', 'longitude']:
                    result = pt.x
                elif coordinate == 'both':
                    result = pt.coords
        return result

    def utm_coordinates(self, coordinate='both'):
        """
        Get get the wgs84 Universal Transverse Mercator (UTM) coordinates for any point.
        :param coordinate: easting, northing, both
        :return: easting, northing, (easting, northing)
        """

        result = None
        if self.geom and self.geom.geom_type == 'Point':
            # EPSG 32701 = UTM Zone 1 South and 32760 = UTM Zone 60 South
            # EPSG 32601 = UTM Zone 1 North and 32660 = UTM Zone 60 North
            if 32701 <= self.geom.srid <= 32760 or 32601 <= self.geom.srid <= 32660:  # If wgs84 utm just return value
                pt = self.geom
            # if wgs84 gcs find zone and convert to utm
            elif self.geom.srid == 4326:  # if pt is in WGS84 geographic then get EPSG for WGS84 UTM
                utm_zone = math.floor((((self.geom.x + 180) / 6) % 60) + 1)  # UTM Zone from lon
                coordinate_system = 32600 + utm_zone  # epsg identifiers follow a pattern by zone
                if self.geom.y < 0:
                    coordinate_system = coordinate_system + 100
                pt = self.geom.transform(coordinate_system, clone=True)
            else:
                try:
                    pt = self.geom.transform(4326, clone=True)
                except:
                    pt = None
            if coordinate in ['easting', 'east']:
                result = pt.x
            elif coordinate in ['northing', 'north']:
                result = pt.y
            elif coordinate == 'both':
                result = pt.coords
        return result

    def point_x(self):
        """
        Return the x coordinate for the point in its native coordinate system
        :return:
        """
        if self.geom and type(self.geom) == Point:
            return self.geom.x
        else:
            return None

    def point_y(self):
        """
        Return the y coordinate for the point in its native coordinate system
        :return:
        """
        if self.geom and type(self.geom) == Point:
            return self.geom.y
        else:
            return None

    def longitude(self):
        """
        Return the longitude for the point in the WGS84 datum
        see PaleoCoreOccurrenceBaseClass.gcs_coordinates
        :return:
        """
        return self.gcs_coordinates(coordinate='lon')

    def latitude(self):
        """
        Return the latitude for the point in the WGS84 datum
        see PaleoCoreOccurrenceBaseClass.gcs_coordinates
        :return:
        """
        return self.gcs_coordinates(coordinate='lat')

    def easting(self):
        """
        Return the easting for the point in UTM meters using the WGS84 datum
        see PaleoCoreOccurrenceBaseClass.utm_coordinates
        :return:
        """
        return self.utm_coordinates(coordinate='easting')

    def northing(self):
        """
        Return the easting for the point in UTM meters using the WGS84 datum
        see PaleoCoreOccurrenceBaseClass.utm_coordinates
        :return:
        """
        return self.utm_coordinates(coordinate='northing')

    class Meta:
        abstract = True


class PaleoCoreOccurrenceBaseClass(PaleoCoreGeomBaseClass):
    """
    An Occurrence == Find; a general class for things discovered in the field.
    Occurrences-Find's have three subtypes: Archaeology, Biology, Geology
    Occurrence is a deprecated terminology, replaced by Find.
    Model fields below are grouped by their ontological classes in Darwin Core: Occurrence, Event, etc.
    """
    # Record-level - inherited from PaleoCoreBaseClass

    # Event
    date_recorded = models.DateTimeField("Date Rec", blank=True, null=True, editable=True,
                                         help_text='Date and time the item was observed or collected.')
    year_collected = models.IntegerField("Year", blank=True, null=True,
                                         help_text='The year, event or field campaign during which the item was found.')
    # Find
    barcode = models.IntegerField("Barcode", null=True, blank=True,
                                  help_text='For collected items only.')  # dwc:recordNumber
    field_number = models.CharField(max_length=50, null=True, blank=True)  # dwc:fieldNumber

    class Meta:
        abstract = True


class PaleoCoreLocalityBaseClass(PaleoCoreGeomBaseClass):
    formation = models.CharField(null=True, blank=True, max_length=50)  # Formation
    member = models.CharField(null=True, blank=True, max_length=50)

    class Meta:
        abstract = True


class PaleoCoreSiteBaseClass(PaleoCoreGeomBaseClass):
    country = CountryField('Country', blank=True, null=True)

    class Meta:
        abstract = True


class PaleoCoreContextBaseClass(PaleoCoreBaseClass):
    geological_formation = models.CharField("Formation", max_length=50, null=True, blank=True)
    geological_member = models.CharField("Member", max_length=50, null=True, blank=True)
    geological_bed = models.CharField(max_length=50, null=True, blank=True)
    older_interval = models.CharField(max_length=50, null=True, blank=True)
    younger_interval = models.CharField(max_length=50, null=True, blank=True)
    max_age = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    min_age = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    best_age = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)

    class Meta:
        abstract = True


class PaleoCoreCollectionCodeBaseClass(PaleoCoreBaseClass):
    drainage_region = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        name_string = self.name
        if self.drainage_region:
            name_string = self.name + ' [{}]'.format(self.drainage_region)
        return name_string

    class Meta:
        abstract = True


class PaleoCoreStratigraphicUnitBaseClass(PaleoCoreBaseClass):
    age_ma = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    facies_type = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True


# Wagtail models
# class ProjectsIndexPage(Page):
#     intro = RichTextField(blank=True)
#
#     content_panels = Page.content_panels + [
#         FieldPanel('intro', classname='full')
#     ]


class ProjectsIndexPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('projects.ProjectsIndexPage', related_name='related_links')


class ProjectsIndexPage(Page):
    intro = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
    ]

    @property
    def projects(self):
        # Get list of live project pages that are descendants of this page
        projects = ProjectPage.objects.live().descendant_of(self)

        # Order by most recent date first
        projects = projects.order_by('title')

        return projects

    def get_context(self, request):
        # Get projects
        projects = self.projects

        # Filter by tag
        tag = request.GET.get('tag')
        if tag:
            projects = projects.filter(tags__name=tag)

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(projects, 10)  # Show 10 projects per page
        try:
            projects = paginator.page(page)
        except PageNotAnInteger:
            projects = paginator.page(1)
        except EmptyPage:
            projects = paginator.page(paginator.num_pages)

        # Update template context
        context = super(ProjectsIndexPage, self).get_context(request)
        context['projects'] = projects
        return context


ProjectsIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel('related_links', label="Related links"),
]

ProjectsIndexPage.promote_panels = Page.promote_panels


class ProjectPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('projects.ProjectPage', related_name='carousel_items')


class ProjectPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('projects.ProjectPage', related_name='related_links')


class ProjectPageTag(TaggedItemBase):
    content_object = ParentalKey('projects.ProjectPage', related_name='tagged_items')


class ProjectPage(Page):
    intro = RichTextField()
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ])
    tags = ClusterTaggableManager(through=ProjectPageTag, blank=True)
    date = models.DateField("Post date")
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    location = models.PointField(srid=4326, null=True, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]
    is_public = models.BooleanField(default=False)

    def record_count(self):
        """
        Function to tabulate the number of Finds in a project database. Counts are based on the number of
        records in the occurrence table for most projects, or the context table for cc and fc. This function
        assumes that base finds are stored in an occurrence table or a context table. Ideally all these should
        be changed to a Find table which will provide a standardized structure.
        :return: Returns an integer record count.
        """
        result = 0
        if apps.is_installed(self.slug):  # check if slug matches an installed app name
            try:
                content_type = ContentType.objects.get(app_label=self.slug, model='occurrence')
            except ContentType.DoesNotExist:
                try:
                    content_type = ContentType.objects.get(app_label=self.slug, model='context')
                except ContentType.DoesNotExist:
                    content_type = ContentType.objects.get(app_label=self.slug, model='find')
            model_class = content_type.model_class()
            result = model_class.objects.all().count()
        return result

    @property
    def project_index(self):
        # Find closest ancestor which is a project index
        return self.get_ancestors().type(ProjectsIndexPage).last()


ProjectPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('date'),
    FieldPanel('intro', classname="full"),
    StreamFieldPanel('body'),
    InlinePanel('carousel_items', label="Carousel items"),
    InlinePanel('related_links', label="Related links"),
    GeoPanel('location')
]

ProjectPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
    FieldPanel('tags'),
]
