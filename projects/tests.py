# Subclassing the django TestCase with Test Case for Abstract Models
# from django.test import TestCase
from projects.test_abstract_classes import ModelMixinTestCase
from projects.models import PaleoCoreBaseClass, PaleoCoreGeomBaseClass
from sys import path
import environ
from django.contrib.gis.geos import Point, Polygon
env = environ.Env(DEBUG=(bool, False),)  # create instance of an Env class
# root = environ.Path(__file__) - 3  # save absolute filesystem path to the root path as as an Env.Path object=
# PROJECT_ROOT = root()  # project path as string, e.g. '/Users/dnr266/Documents/pycharm/paleocore110'
# environ.Env.read_env(root('.env'))  # locate the .env file in the project root directory
# DJANGO_ROOT = '/Users/dnr266/Documents/pycharm/paleocore110'
# DJANGO_ROOT = root.path('paleocore110')  # e.g. '/Users/dnr266/Documents/pycharm/paleocore110/paleocore110'
environ.Env.read_env('/Users/dnr266/Documents/pycharm/paleocore110/.env')
PROJECT_ROOT = '/Users/dnr266/Documents/pycharm/paleocore110'
DJANGO_ROOT = '/Users/dnr266/Documents/pycharm/paleocore110/paleocore110'
path.append(DJANGO_ROOT)  # add DJANGO_ROOT to python path list


class PaleoCoreGeomBaseClassMethodsTests(ModelMixinTestCase):
    """
    Test projects Context instance methods
    """
    mixin = PaleoCoreGeomBaseClass

    def setUp(self):
        self.model.objects.create(pk=1,
                                  geom=Point(40.75, 11.5))
        self.model.objects.create(pk=2,
                                  geom=Point(500000, 100000, srid=32637))

    def test_pcbase_gcs_coordinate_method(self):
        context_instance = self.model.objects.get(pk=1)
        # test that gcs returns lat lon
        self.assertEqual(context_instance.gcs_coordinates('lat'), 11.5)
        self.assertEqual(context_instance.gcs_coordinates('lon'), 40.75)
        self.assertEqual(context_instance.gcs_coordinates('both'), (40.75, 11.5))
        # test that utm returns proper lat lon
        pt_utm = context_instance.geom.transform(32637, clone=True)
        context_instance.geom = pt_utm
        self.assertEqual(round(context_instance.gcs_coordinates('lat'), 2), 11.5)
        # test correct response when missing geom altogether
        context_instance.geom = None
        context_instance.save()
        self.assertEqual(context_instance.gcs_coordinates('lat'), None)
        # return None when geom is other than point
        # poly = Polygon([[40.75, 11.5], [40.76, 11.5], [40.76, 11.4], [40.75, 11.4], [40.75, 11.5]])
        # context_instance.geom = poly
        # self.assertEqual(context_instance.gcs_coordinate('lat'), None)
        # what if coordinates set to erroneous values?
        pt_bad = Point(40.75, -111.5)
        context_instance.geom = pt_bad
        self.assertEqual(context_instance.gcs_coordinates('lat'), -111.5)  # Accepts values greater than +/- 90?

    def test_pcbase_utm_coordinates_method(self):
        context_instance = self.model.objects.get(pk=1)
        transformed_pt = context_instance.geom.transform(32637, clone=True)
        self.assertEqual(context_instance.utm_coordinates(), transformed_pt.coords)
        self.assertEqual(context_instance.utm_coordinates('east'), transformed_pt.x)
        self.assertEqual(context_instance.utm_coordinates('north'), transformed_pt.y)
        context_instance2 = self.model.objects.get(pk=2)
        self.assertAlmostEqual(context_instance2.utm_coordinates('east'), 500000, 3)
        self.assertAlmostEqual(context_instance2.utm_coordinates('north'), 100000, 3)

    def test_pcbase_get_concrete_field_names_method(self):
        context_instance = self.model.objects.get(pk=1)
        self.assertEqual(context_instance.get_concrete_field_names(), ['id',
                                                                       'name',
                                                                       'date_created',
                                                                       'date_last_modified',
                                                                       'problem',
                                                                       'problem_comment',
                                                                       'remarks',
                                                                       'last_import',
                                                                       'georeference_remarks',
                                                                       'geom'
                                                                       ])


class TaxonTests(ModelMixinTestCase):
    mixin = PaleoCoreBaseClass

    fixtures = [
        'projects/fixtures/taxon_test_data.json',
        'projects/fixtures/taxonrank_test_data.json',
        'projects/fixtures/identification_qualifier_test_data.json'
    ]
    pass
