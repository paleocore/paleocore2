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


# class PaleoCoreBaseClassMethodsTests(ModelMixinTestCase):
#     mixin = PaleoCoreBaseClass
#
#     def setUpTestData(cls=PaleoCoreBaseClass):
#         cls.model.objects.create(pk=1,
#                                   geom=Point(40.75, 11.5))
#         cls.model.objects.create(pk=2,
#                                   geom=Point(500000, 100000, srid=32637))
#
#     def test_get_app_label_method(self):
#         ci = self.model.objects.get(pk=1)
#         self.assertEqual(ci.get_app_label(), 'projects')


class PaleoCoreGeomBaseClassMethodsTests(ModelMixinTestCase):
    """
    Test projects Context instance methods
    """
    mixin = PaleoCoreGeomBaseClass

    @classmethod
    def setUpTestData(cls):
        cls.gcspoint = cls.model.objects.create(pk=1,
                                  geom=Point(40.75, 11.5))
        cls.utmpoint = cls.model.objects.create(pk=2,
                                  geom=Point(500000, 100000, srid=32637))
        cls.gcspointbad = cls.model.objects.create(pk=3,
                                                   geom=Point(40.76, -111.5, srid=4326))
        cls.gcspointnone = cls.model.objects.create(pk=4,
                                                    geom=None)

    def test_pcbase_gcs_coordinate_method(self):
        # test that gcs returns lat lon
        self.assertEqual(self.gcspoint.gcs_coordinates('lat'), 11.5)
        self.assertEqual(self.gcspoint.gcs_coordinates('lon'), 40.75)
        self.assertEqual(self.gcspoint.gcs_coordinates('both'), (40.75, 11.5))
        # test that utm returns proper lat lon
        pt_utm = self.gcspoint.geom.transform(32637, clone=True)
        self.gcspoint.geom = pt_utm
        self.assertAlmostEqual(self.gcspoint.gcs_coordinates('lat'), 11.5, 2)
        # test correct response when missing geom altogether
        self.assertEqual(self.gcspointnone.gcs_coordinates('lat'), None)

        # return None when geom is other than point -  this code raises an error
        # poly = Polygon([[40.75, 11.5], [40.76, 11.5], [40.76, 11.4], [40.75, 11.4], [40.75, 11.5]])
        # gcspoint.geom = poly
        # self.assertEqual(gcspoint.gcs_coordinate('lat'), None)

        # what if coordinates set to erroneous values?
        self.assertEqual(self.gcspointbad.gcs_coordinates('lat'), -111.5)  # Accepts values greater than +/- 90?

    def test_pcbase_utm_coordinates_method(self):
        self.assertAlmostEqual(self.gcspoint.utm_coordinates()[0], 690874.796037099, 2)
        self.assertAlmostEqual(self.gcspoint.utm_coordinates()[1], 1271846.8732660324, 2)
        self.assertAlmostEqual(self.gcspoint.utm_coordinates('east'), 690874.796037099, 2)
        self.assertAlmostEqual(self.gcspoint.utm_coordinates('north'), 1271846.8732660324, 2)
        self.assertAlmostEqual(self.utmpoint.utm_coordinates('east'), 500000, 3)
        self.assertAlmostEqual(self.utmpoint.utm_coordinates('north'), 100000, 3)

    def test_pcbase_get_app_label_method(self):
        self.assertEqual(self.gcspoint.get_app_label(), 'projects')

    def test_pcbase_get_concrete_field_names_method(self):
        # gcspoint = self.model.objects.get(pk=1)
        self.assertEqual(self.gcspoint.get_concrete_field_names(), ['id',
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
