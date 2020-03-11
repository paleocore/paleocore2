from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.contrib.gis.geos import Point
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.core.files.uploadedfile import TemporaryUploadedFile

from mlp.models import Occurrence, Biology, Taxon, IdentificationQualifier
from mlp.utilities import html_escape

from datetime import datetime
import pytz
from zipfile import ZipFile
from fastkml import kml, Placemark, Folder, Document
from mlp.views import ImportKMZ

# from django.core.urlresolvers import reverse
# from mlp.forms import UploadKMLForm
# from django.core.files.uploadedfile import SimpleUploadedFile
#
# from django.contrib.auth.models import User
# from mlp.ontologies import BASIS_OF_RECORD_VOCABULARY, \
#     COLLECTING_METHOD_VOCABULARY, COLLECTOR_CHOICES, ITEM_TYPE_VOCABULARY
# from random import random


######################################
# Tests for models and their methods #
######################################


class UtilitiesMethodsTests(TestCase):
    def test_mlp_utilities_html_clean(self):
        test_text = """I like hippos & Horses and smug "monkeys" that think they > are < snails."""
        clean_text = """I like hippos &amp; Horses and smug "monkeys" that think they > are < snails."""
        escaped_text = html_escape(test_text)
        self.assertEqual(escaped_text, clean_text)


class ImportKMZMethodsTests(TestCase):
    """
    Test mlp.views.py Import methods
    """
    fixtures = [
        'mlp/fixtures/mlp_taxonomy_test_data.json'
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.import_kmz = ImportKMZ()
        self.test_file_path = 'mlp/fixtures/mlp_test_import.kmz'
        infile = open(self.test_file_path, 'rb')
        request = self.factory.post('/django-admin/mlp/occurrence/import_kmz/', {'kmlfileUpload': infile})
        self.import_kmz.request = request

    def setup_request(self, request):
        """Annotate a request object with a session"""
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        """Annotate a request object with a messages"""
        middleware = MessageMiddleware()
        middleware.process_request(request)
        request.session.save()

        request.session['some'] = 'some'
        request.session.save()

    def test_get_import_file(self):
        self.assertEqual(self.import_kmz.get_import_file().name, self.test_file_path.split('/')[-1])
        self.assertEqual(type(self.import_kmz.get_import_file()), TemporaryUploadedFile)

    def test_get_import_extension(self):
        self.assertEqual(self.import_kmz.get_import_file_extension(), 'kmz')

    def test_get_kmz_file(self):
        self.assertEqual(type(self.import_kmz.get_kmz_file()), ZipFile)
        self.assertEqual(self.import_kmz.get_kmz_file().filelist[0].filename, '374.jpg')

    def test_get_kml_file(self):
        self.assertEqual(type(self.import_kmz.get_kml_file()), kml.KML)
        self.assertEqual(self.import_kmz.get_kml_file().to_string()[:10], '<kml xmlns')

    def test_mlp_import_placemarks(self):
        starting_record_count = Occurrence.objects.count()  # No occurrences in empty db
        self.assertEqual(starting_record_count, 0)
        kml_file = self.import_kmz.get_kml_file()
        level1_elements = list(kml_file.features())
        self.assertEqual(len(level1_elements), 1)
        self.assertEqual(type(level1_elements[0]), Document)
        document = level1_elements[0]
        level2_elements = list(document.features())
        self.assertEqual(len(level2_elements), 6)
        self.assertEqual(type(level2_elements[0]), Placemark)
        placemark_list = level2_elements
        self.assertEqual(len(placemark_list), 6)
        self.setup_request(self.import_kmz.request)  # annotate the request with a message
        self.import_kmz.import_placemarks(placemark_list)
        self.assertEqual(Occurrence.objects.count(), 6)
        self.assertEqual(Occurrence.objects.filter(basis_of_record='HumanObservation').count(), 3)


class OccurrenceMethodsTests(TestCase):
    """
    Test mlp Occurrence instance creation and methods
    """

    def test_mlp_occurrence_save_simple(self):
        """
        Test mlp_occurrence instance save method with the simplest possible attributes.
        """
        starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
        new_occurrence = Occurrence(id=1, item_type="Faunal",
                                    basis_of_record="HumanObservation",
                                    collecting_method="Surface Standard",
                                    field_number=datetime.now(pytz.utc),
                                    geom="POINT (40.8352906016 11.5303732536)")
        new_occurrence.save()
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 40.8352906016)
        self.assertEqual(new_occurrence.point_y(), 11.5303732536)

    def test_mlp_create_method(self):
        """
        Test Occurrence instance create method with simple set of attributes.
        :return:
        """
        starting_record_count = Occurrence.objects.count()
        new_occurrence = Occurrence.objects.create(id=1, item_type="Faunal",
                                                   basis_of_record="HumanObservation",
                                                   collecting_method="Surface Standard",
                                                   field_number=datetime.now(pytz.utc),
                                                   geom="POINT (40.8352906016 11.5303732536)")
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 40.8352906016)

    def test_mlp_create_method_invalid_item_type(self):
        """
        """
        starting_record_count = Occurrence.objects.count()
        new_occurrence = Occurrence.objects.create(id=1, item_type="Fake",
                                                   basis_of_record="HumanObservation",
                                                   collecting_method="Surface Standard",
                                                   field_number=datetime.now(pytz.utc),
                                                   geom="POINT (40.8352906016 11.5303732536)")
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 40.8352906016)
        self.assertEqual(new_occurrence.item_type, "Fake")

    def test_mlp_save_method_valid_item_type(self):
        """
        """
        starting_record_count = Occurrence.objects.count()
        new_occurrence = Occurrence()
        new_occurrence.item_type = "Faunal"
        new_occurrence.basis_of_record = "HumanObservation"
        new_occurrence.collecting_method = "Surface Standard"
        new_occurrence.field_number = datetime.now(pytz.utc)
        new_occurrence.geom = "POINT (40.8352906016 11.5303732536)"
        new_occurrence.save()

        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 40.8352906016)
        self.assertEqual(new_occurrence.item_type, "Faunal")

    def test_mlp_save_method_invalid_item_type(self):
        """
        """
        starting_record_count = Occurrence.objects.count()
        new_occurrence = Occurrence()
        new_occurrence.item_type = "Fake"
        new_occurrence.basis_of_record = "HumanObservation"
        new_occurrence.collecting_method = "Surface Standard"
        new_occurrence.field_number = datetime.now(pytz.utc)
        new_occurrence.geom = "POINT (40.8352906016 11.5303732536)"
        new_occurrence.save()

        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 40.8352906016)
        self.assertEqual(new_occurrence.item_type, "Fake")


class BiologyMethodsTests(TestCase):
    """
    Test mlp Biology instance creation and methods
    """
    fixtures = [
        'mlp/fixtures/mlp_taxonomy_test_data.json'
    ]

    def test_mlp_biology_save_simple(self):
        """
        Test Biology instance save method with the simplest possible attributes.
        """
        starting_record_count = Biology.objects.count()  # get current number of occurrence records
        new_taxon = Taxon.objects.get(name__exact="Primates")
        id_qualifier = IdentificationQualifier.objects.get(name__exact="None")
        new_occurrence = Biology(barcode=1111, item_type="Faunal", basis_of_record="HumanObservation",
                                 collecting_method="Surface Standard", field_number=datetime.now(pytz.utc),
                                 taxon=new_taxon,
                                 identification_qualifier=id_qualifier,
                                 geom="POINT (-122.4376 37.7577)")
        new_occurrence.save()
        now = datetime.now()
        self.assertEqual(Biology.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_y(), 37.7577)
        self.assertEqual(new_occurrence.point_x(), -122.4376)

    def test_biology_create_observation(self):
        """
        Test Biology instance creation for observations
        """
        new_taxon = Taxon.objects.get(name__exact="Primates")
        id_qualifier = IdentificationQualifier.objects.get(name__exact="None")

        occurrence_starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
        biology_starting_record_count = Biology.objects.count()  # get the current number of biology records
        # The simplest occurrence instance we can create needs only a location.
        # Using the instance creation and then save methods
        new_occurrence = Biology.objects.create(
            barcode=1111,
            basis_of_record="HumanObservation",
            collection_code="COL",
            item_number="1",
            geom="POINT (-122.4376 37.7577)",
            taxon=new_taxon,
            identification_qualifier=id_qualifier,
            field_number=datetime.now(pytz.utc)
        )
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), occurrence_starting_record_count+1)  # test that a record was added
        self.assertEqual(new_occurrence.catalog_number, None)  # test catalog number generation in save method
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_y(), 37.7577)
        self.assertEqual(Biology.objects.count(), biology_starting_record_count+1)  # test no biology record was added
        self.assertEqual(Biology.objects.filter(basis_of_record__exact="HumanObservation").count(), 1)

    def test_biology_create_biology(self):
        """
        Test Biology instance creation for observations
        """

        # self.biology_setup()
        new_taxon = Taxon.objects.get(name__exact="Primates")
        id_qualifier = IdentificationQualifier.objects.get(name__exact="None")

        occurrence_starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
        biology_starting_record_count = Biology.objects.count()  # get the current number of biology records
        # The simplest occurrence instance we can create needs only a location.
        # Using the instance creation and then save methods
        new_occurrence = Biology.objects.create(
            barcode=1111,
            basis_of_record="FossilSpecimen",
            collection_code="COL",
            item_number="1",
            geom=Point(-122.4376, 37.7577),  # An alternate point creation method
            taxon=new_taxon,
            identification_qualifier=id_qualifier,
            field_number=datetime.now()
        )
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), occurrence_starting_record_count+1)  # test that a record was added
        self.assertEqual(new_occurrence.catalog_number, None)  # test catalog number generation in save method
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_y(), 37.7577)
        self.assertAlmostEqual(new_occurrence.northing(), 4179080.7650798513, 3)  # UTMs match to mm
        self.assertEqual(Biology.objects.count(), biology_starting_record_count+1)  # test no biology record was added
        self.assertEqual(Biology.objects.filter(basis_of_record__exact="FossilSpecimen").count(), 1)


# class MilleLogyaViews(TestCase):
#     """
#     The TestCase depends on two fixtures, which contain public data and are included on the GitHub repository.
#     """
#     fixtures = [
#         'fixtures/fiber_data_150611.json',
#         'taxonomy/fixtures/taxonomy_data_150611.json',
#     ]
#
#     def setUp(self):
#         """
#         The setup function populates the test database with records for various permutations
#         of basis of record, collecting method, collectors and taxonomic orders. The method creates
#         Occurrence and Biology instances and some of the Occurrence instances will be of type "Faunal". We can
#         use these for testing the function to convert instances of an Occurrence class to instances of a
#         Biology class.
#         :return:
#         """
#         id_qualifier = IdentificationQualifier.objects.get(name__exact="None")
#         barcode_index = 1
#         mammal_orders = (("Primates", "Primates"),
#                          ("Perissodactyla", "Perissodactyla"),
#                          ("Artiodactyla", "Artiodactyla"),
#                          ("Rodentia", "Rodentia"),
#                          ("Carnivora", "Carnivora"),)
#
#         for basis_tuple_element in BASIS_OF_RECORD_VOCABULARY:
#             for method_tuple_element in COLLECTING_METHOD_VOCABULARY:
#                 for collector_tuple_element in COLLECTOR_CHOICES:
#                     for order_tuple_element in mammal_orders:
#                         Biology.objects.create(
#                             barcode=barcode_index,
#                             basis_of_record=basis_tuple_element[0],
#                             collection_code="MLP",
#                             item_number=barcode_index,
#                             geom=Point(-122+random(), 37+random()),
#                             taxon=Taxon.objects.get(name__exact=order_tuple_element[0]),
#                             identification_qualifier=id_qualifier,
#                             field_number=datetime.now(),
#                             collecting_method=method_tuple_element[0],
#                             collector=collector_tuple_element[0],
#                             item_type="Faunal"
#                         )
#                         barcode_index += 1
#
#         for basis_tuple_element in BASIS_OF_RECORD_VOCABULARY:
#             for method_tuple_element in COLLECTING_METHOD_VOCABULARY:
#                 for item_type_element in ITEM_TYPE_VOCABULARY:
#                     Occurrence.objects.create(
#                         barcode=barcode_index,
#                         basis_of_record=basis_tuple_element[0],
#                         collection_code="MLP",
#                         item_number=barcode_index,
#                         geom=Point(-122+random(), 37+random()),
#                         field_number=datetime.now(),
#                         collecting_method=method_tuple_element[0],
#                         collector="Denne Reed",
#                         item_type=item_type_element[0]
#                     )
#                     barcode_index += 1
#
#         total_permutations = len(BASIS_OF_RECORD_VOCABULARY) * \
#                              len(COLLECTING_METHOD_VOCABULARY) * len(COLLECTOR_CHOICES * len(mammal_orders))
#         self.assertEqual(Biology.objects.all().count(), total_permutations)
#         self.assertEqual(Biology.objects.filter(basis_of_record__exact="FossilSpecimen").count(),
#                          total_permutations/len(BASIS_OF_RECORD_VOCABULARY))
#         object1 = Biology.objects.get(barcode=1)
#         object2 = Biology.objects.get(barcode=2)
#         self.assertNotEqual(object1.geom.x, object2.geom.x)
#         self.assertNotEqual(object1.geom.y, object2.geom.y)
#         self.assertEqual(object1.collecting_method, "Surface Standard")
#
#         User.objects.create_user(username='test_user', password='password')
#
#     def test_upload_view_no_login(self):
#         response = self.client.get(reverse('projects:mlp:mlp_upload_kml'), follow=True)
#         self.assertContains(response, "login")
#         self.assertEqual(response.status_code, 200)
#
#     def test_upload_view_with_login(self):
#         self.client.login(username='test_user', password='password')  # login
#         response = self.client.get(reverse('projects:mlp:mlp_upload_kml'), follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Upload a kml")
#
#     def test_confirmation_view(self):
#         response = self.client.get(reverse('projects:mlp:mlp_upload_confirmation'))
#         self.assertEqual(response.status_code, 200)
#
#     def test_download_view(self):
#         response = self.client.get(reverse('projects:mlp:mlp_download_kml'))
#         self.assertEqual(response.status_code, 200)
#
#     def test_kml_form_with_no_data(self):
#         # get starting count of records in DB
#         occurrence_starting_record_count = Occurrence.objects.count()
#
#         # create an empty form
#         post_dict = {}
#         file_dict = {}
#         form = UploadKMLForm(post_dict, file_dict)
#
#         # test that form is not valid with empty data
#         self.assertFalse(form.is_valid())
#
#         # get the post response and test page reload and error message
#         response = self.client.post(reverse('projects:mlp:mlp_upload_kml'), file_dict, follow=True)
#         self.assertEqual(response.status_code, 200)  # test reload
#         self.assertContains(response, 'login')
#         self.client.login(username='test_user', password='password')
#         response = self.client.post(reverse('projects:mlp:mlp_upload_kml'), file_dict, follow=True)
#         self.assertEqual(response.status_code, 200)  # test reload
#         self.assertContains(response, 'Upload')
#         self.assertContains(response, 'This field is required')
#
#         # test nothing is saved to DB
#         self.assertEqual(Occurrence.objects.count(), occurrence_starting_record_count)
#
#     def test_kml_upload_form_with_with_valid_data_no_login(self):
#         """
#         Test the import kml form. This test uses a sample kmz file with one placemark.
#         This code based on stack overflow question at
#         http://stackoverflow.com/questions/7304248/writing-tests-for-forms-in-django
#         :return:
#         """
#         upload_file = open('mlp/fixtures/MLP_test.kmz', 'rb')
#         post_dict = {}
#         file_dict = {'kmlfileUpload': SimpleUploadedFile(upload_file.name, upload_file.read())}
#         upload_file.close()
#         form = UploadKMLForm(post_dict, file_dict)
#         self.assertTrue(form.is_valid())
#
#         # get current number of occurrence records in DB and verify count
#         occurrence_starting_record_count = Occurrence.objects.count()
#
#         # follow redirect to login page
#         response = self.client.post('/projects/mlp/upload/', file_dict, follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertRedirects(response, 'login/?next=/projects/mlp/upload/')  # test we hit the login page
#         self.assertContains(response, 'login')  # test we hit the login page
#
#         # test that new occurrence was added to DB
#         self.assertEqual(Occurrence.objects.count(), occurrence_starting_record_count)  # test nothing added to DB
#
#     def test_kml_upload_form_with_with_valid_data_and_login(self):
#         """
#         Test the import kml form. This test uses a sample kmz file with one placemark.
#         This code based on stack overflow question at
#         http://stackoverflow.com/questions/7304248/writing-tests-for-forms-in-django
#         :return:
#         """
#         upload_file = open('mlp/fixtures/MLP_test.kmz', 'rb')
#         post_dict = {}
#         file_dict = {'kmlfileUpload': SimpleUploadedFile(upload_file.name, upload_file.read())}
#         upload_file.close()
#         form = UploadKMLForm(post_dict, file_dict)
#         self.assertTrue(form.is_valid())
#
#         # get current number of occurrence records in DB and verify count
#         occurrence_starting_record_count = Occurrence.objects.count()
#
#         # login and test redirect to confirmation page
#         self.client.login(username='test_user', password='password')  # login
#         response = self.client.post('/projects/mlp/upload/', file_dict, follow=True)
#         self.assertRedirects(response, '/projects/mlp/confirmation/')
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'file upload was successful!')  # test message in conf page
#
#         # test that new occurrence was added to DB
#         self.assertEqual(Occurrence.objects.count(), occurrence_starting_record_count+1)  # test one record added
