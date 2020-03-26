from django.test import TestCase
from .models import Occurrence, Biology
from .models import Taxon, IdentificationQualifier
from django.core.urlresolvers import reverse
from datetime import datetime
from .forms import UploadKMLForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from omo_mursi.ontologies import BASIS_OF_RECORD_VOCABULARY, \
    COLLECTING_METHOD_VOCABULARY, COLLECTOR_CHOICES, ITEM_TYPE_VOCABULARY
from random import random
from django.contrib.auth import authenticate

######################################
# Tests for models and their methods #
######################################


class OccurrenceMethodsTests(TestCase):
    """
    Test omo_mursi Occurrence instance creation and methods
    """
    fixtures = [
        'fixtures/fiber_data_150611.json',
    ]

    def test_omo_mursi_occurrence_save_simple(self):
        """
        Test omo_mursi_occurrence instance save method with the simplest possible attributes.
        """
        starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
        # The simplest occurrence instance we can create needs six bits of data.
        # Using the instance creation and then save methods
        new_occurrence = Occurrence(id=1, item_type="Faunal", basis_of_record="HumanObservation",
                                    collecting_method="Surface Standard", field_number=datetime.now(),
                                    geom="POINT (40.8352906016 11.5303732536)")
        new_occurrence.save()
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 40.8352906016)
        self.assertEqual(new_occurrence.point_y(), 11.5303732536)

    def test_omo_mursi_create_method(self):
        """
        Test Occurrence instance create method with simple set of attributes.
        :return:
        """
        starting_record_count = Occurrence.objects.count()
        new_occurrence = Occurrence.objects.create(id=1, item_type="Faunal", basis_of_record="HumanObservation",
                                                   collecting_method="Surface Standard", field_number=datetime.now(),
                                                   geom="POINT (40.8352906016 11.5303732536)")
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 40.8352906016)

    def test_omo_mursi_create_method_invalid_item_type(self):
        """
        """
        starting_record_count = Occurrence.objects.count()
        new_occurrence = Occurrence.objects.create(id=1, item_type="Fake", basis_of_record="HumanObservation",
                                                   collecting_method="Surface Standard", field_number=datetime.now(),
                                                   geom="POINT (40.8352906016 11.5303732536)")
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 40.8352906016)
        self.assertEqual(new_occurrence.item_type, "Fake")

    def test_omo_mursi_save_method_valid_item_type(self):
        """
        """
        starting_record_count = Occurrence.objects.count()
        new_occurrence = Occurrence()
        new_occurrence.item_type = "Faunal"
        new_occurrence.basis_of_record = "HumanObservation"
        new_occurrence.collecting_method = "Surface Standard"
        new_occurrence.field_number = datetime.now()
        new_occurrence.geom = "POINT (40.8352906016 11.5303732536)"
        new_occurrence.save()

        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 40.8352906016)
        self.assertEqual(new_occurrence.item_type, "Faunal")

    def test_omo_mursi_save_method_invalid_item_type(self):
        """
        """
        starting_record_count = Occurrence.objects.count()
        new_occurrence = Occurrence()
        new_occurrence.item_type = "Fake"
        new_occurrence.basis_of_record = "HumanObservation"
        new_occurrence.collecting_method = "Surface Standard"
        new_occurrence.field_number = datetime.now()
        new_occurrence.geom = "POINT (40.8352906016 11.5303732536)"
        new_occurrence.save()

        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 40.8352906016)
        self.assertEqual(new_occurrence.item_type, "Fake")


class BiologyMethodsTests(TestCase):
    """
    Test omo_mursi Biology instance creation and methods
    """
    fixtures = [
        'fixtures/fiber_data_150611.json',
        'taxonomy/fixtures/taxonomy_data_150611.json'
    ]

    def test_omo_mursi_biology_save_simple(self):
        """
        Test Biology instance save method with the simplest possible attributes.
        """
        starting_record_count = Biology.objects.count()  # get current number of occurrence records
        new_taxon = Taxon.objects.get(name__exact="Primates")
        id_qualifier = IdentificationQualifier.objects.get(name__exact="None")
        new_occurrence = Biology(barcode=1111, item_type="Faunal", basis_of_record="HumanObservation",
                                 collecting_method="Surface Standard", field_number=datetime.now(),
                                 taxon=new_taxon,
                                 identification_qualifier=id_qualifier,
                                 geom="POINT (-122.4376 37.7577)")
        new_occurrence.save()
        now = datetime.now()
        self.assertEqual(Biology.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_y(), 37.7577)
        self.assertEqual(new_occurrence.point_x(), -122.4376)
        self.assertEqual(new_occurrence.easting(), 549539.4374838244)
        self.assertEqual(new_occurrence.northing(), 4179080.7650798513)

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
            field_number=datetime.now()
        )
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), occurrence_starting_record_count+1)  # test that a record was added
        self.assertEqual(new_occurrence.catalog_number, None)  # test catalog number generation in save method
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_y(), 37.7577)
        self.assertEqual(new_occurrence.northing(), 4179080.7650798513)
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
        self.assertEqual(new_occurrence.northing(), 4179080.7650798513)
        self.assertEqual(Biology.objects.count(), biology_starting_record_count+1)  # test no biology record was added
        self.assertEqual(Biology.objects.filter(basis_of_record__exact="FossilSpecimen").count(), 1)


class TestViews(TestCase):
    """
    The TestCase depends on two fixtures, which contain public data and are included on the GitHub repository.
    """
    fixtures = [
        'fixtures/fiber_data_150611.json',
        'taxonomy/fixtures/taxonomy_data_150611.json',
    ]

    def setUp(self):
        """
        The setup function populates the test database with records for various permutations
        of basis of record, collecting method, collectors and taxonomic orders. The method creates
        Occurrence and Biology instances and some of the Occurrence instances will be of type "Faunal". We can
        use these for testing the function to convert instances of an Occurrence class to instances of a
        Biology class.
        :return:
        """
        id_qualifier = IdentificationQualifier.objects.get(name__exact="None")
        barcode_index = 1
        mammal_orders = (("Primates", "Primates"),
                         ("Perissodactyla", "Perissodactyla"),
                         ("Artiodactyla", "Artiodactyla"),
                         ("Rodentia", "Rodentia"),
                         ("Carnivora", "Carnivora"),)

        for basis_tuple_element in BASIS_OF_RECORD_VOCABULARY:
            for method_tuple_element in COLLECTING_METHOD_VOCABULARY:
                for collector_tuple_element in COLLECTOR_CHOICES:
                    for order_tuple_element in mammal_orders:
                        Biology.objects.create(
                            barcode=barcode_index,
                            basis_of_record=basis_tuple_element[0],
                            collection_code="TEST",
                            item_number=barcode_index,
                            geom=Point(-122+random(), 37+random()),
                            taxon=Taxon.objects.get(name__exact=order_tuple_element[0]),
                            identification_qualifier=id_qualifier,
                            field_number=datetime.now(),
                            collecting_method=method_tuple_element[0],
                            collector=collector_tuple_element[0],
                            item_type="Faunal"
                        )
                        barcode_index += 1

        for basis_tuple_element in BASIS_OF_RECORD_VOCABULARY:
            for method_tuple_element in COLLECTING_METHOD_VOCABULARY:
                for item_type_element in ITEM_TYPE_VOCABULARY:
                    Occurrence.objects.create(
                        barcode=barcode_index,
                        basis_of_record=basis_tuple_element[0],
                        collection_code="TEST",
                        item_number=barcode_index,
                        geom=Point(-122+random(), 37+random()),
                        field_number=datetime.now(),
                        collecting_method=method_tuple_element[0],
                        collector="Michelle Drapeau",
                        item_type=item_type_element[0]
                    )
                    barcode_index += 1

        total_permutations = len(BASIS_OF_RECORD_VOCABULARY) * \
                             len(COLLECTING_METHOD_VOCABULARY) * len(COLLECTOR_CHOICES * len(mammal_orders))
        self.assertEqual(Biology.objects.all().count(), total_permutations)
        self.assertEqual(Biology.objects.filter(basis_of_record__exact="FossilSpecimen").count(),
                         total_permutations/len(BASIS_OF_RECORD_VOCABULARY))
        object1 = Biology.objects.get(barcode=1)
        object2 = Biology.objects.get(barcode=2)
        self.assertNotEqual(object1.geom.x, object2.geom.x)
        self.assertNotEqual(object1.geom.y, object2.geom.y)
        self.assertEqual(object1.collecting_method, "Surface Standard")

        test_user = User.objects.create_user(username='test_user', password='password')
        test_user.is_superuser = True
        test_user.is_staff = True
        test_user.save()

    def test_upload_view(self):
        response = self.client.get(reverse('projects:omo_mursi:omo_mursi_upload_kml'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload a kml")

    def test_confirmation_view(self):
        response = self.client.get(reverse('projects:omo_mursi:omo_mursi_upload_confirmation'))
        self.assertEqual(response.status_code, 200)

    def test_download_view(self):
        response = self.client.get(reverse('projects:omo_mursi:omo_mursi_download_kml'))
        self.assertEqual(response.status_code, 200)

    def test_kml_form_with_no_data(self):
        # get starting count of records in DB
        occurrence_starting_record_count = Occurrence.objects.count()

        # create an empty form
        post_dict = {}
        file_dict = {}
        form = UploadKMLForm(post_dict, file_dict)

        # test that form is not valid with empty data
        self.assertFalse(form.is_valid())

        # get the post response and test page reload and error message
        response = self.client.post(reverse('projects:omo_mursi:omo_mursi_upload_kml'), file_dict, follow=True)
        self.assertEqual(response.status_code, 200)  # test reload
        self.assertContains(response, 'Upload a')
        self.assertContains(response, 'This field is required')

        # test nothing is saved to DB
        self.assertEqual(Occurrence.objects.count(), occurrence_starting_record_count)

    def test_kml_upload_form_with_with_valid_data(self):
        """
        Test the import kml form. This test uses a sample kmz file with one placemark.
        This code based on stack overflow question at
        http://stackoverflow.com/questions/7304248/writing-tests-for-forms-in-django
        :return:
        """
        upload_file = open('omo_mursi/fixtures/OMM_test.kmz', 'rb')
        post_dict = {}
        file_dict = {'kmlfileUpload': SimpleUploadedFile(upload_file.name, upload_file.read())}
        upload_file.close()
        form = UploadKMLForm(post_dict, file_dict)
        self.assertTrue(form.is_valid())

        # get current number of occurrence records in DB and verify count
        occurrence_starting_record_count = Occurrence.objects.count()

        # follow redirect to confirmation page
        response = self.client.post('/projects/omo_mursi/upload/', file_dict, follow=True)

        # test redirect to confirmation page
        self.assertRedirects(response, '/projects/omo_mursi/confirmation/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'upload was successful!')  # test message in conf page

        # test that new occurrence was added to DB
        self.assertEqual(Occurrence.objects.count(), occurrence_starting_record_count+1)

    def test_admin_list_view_with_login(self):
        test_user = User.objects.get(username='test_user')
        self.assertEqual(test_user.is_active, True)
        self.assertEqual(test_user.is_superuser, True)  # Test user is superuser
        self.assertEqual(test_user.is_staff, True)
        test_user = authenticate(username='test_user', password='password')
        self.assertNotEqual(test_user, None)
        self.assertEqual(self.client.login(), False)
        self.client.login(username='test_user', password='password')
        self.assertEqual(self.client.login(username='test_user', password='password'), True)

        response = self.client.get('/admin/omo_mursi/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PaleoCore administration')  # omo_mursi admin
        self.assertContains(response, 'Omo Mursi')

        response = self.client.get('/admin/omo_mursi/occurrence/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PaleoCore administration')  # omo_mursi occurrences admin
        self.assertContains(response, 'Omo Mursi Occurrences')

        occurrences = Occurrence.objects.all()
        response = self.client.get('/admin/omo_mursi/occurrence/'+str(occurrences[0].pk), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PaleoCore administration')  # redirects to login form
        self.assertContains(response, 'Change Omo Mursi Occurrence')


