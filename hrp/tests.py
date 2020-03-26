from django.test import TestCase, Client
from hrp.models import Occurrence, Biology, Locality
from hrp.models import Taxon, IdentificationQualifier
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, Polygon


class OccurrenceCreationMethodTests(TestCase):
    """
    Test Occurrence instance creation and methods
    """

    def setUp(self):
        User.objects.create_superuser(username='test', email='foo@yahoo.com', password='test')

        # id values need to be added explicitly
        Locality.objects.create(id=1, locality_number=1, geom=Point(41.1, 11.1))
        Locality.objects.create(id=2, locality_number=2, geom=Point(41.2, 11.2))
        Locality.objects.create(id=3, locality_number=3, geom=Point(41.3, 11.3))
        Locality.objects.create(id=4, locality_number=4, geom=Point(41.4, 11.4))

    def test_occurrence_save_simple(self):
        """
        Test Occurrence instance save method with the simplest possible attributes, coordinates only
        """
        starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
        new_occurrence = Occurrence(geom="POINT (41.1 11.1)",
                                    locality=Locality.objects.get(locality_number=1),
                                    field_number=datetime.now())
        new_occurrence.save()
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.catalog_number(), None)  # test catalog number generation in save method
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 41.1)
        self.assertEqual(new_occurrence.locality.locality_number, 1)

    def test_occurrence_create_simple(self):
        """
        Test Occurrence instance creation with the simplest possible attributes, coordinates only
        """
        starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
        new_occurrence = Occurrence.objects.create(geom=Point(41.2, 11.2),
                                                   locality=Locality.objects.get(locality_number=2),
                                                   field_number=datetime.now())
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.catalog_number(), None)  # test catalog number generation in save method
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 41.2)

    def test_occurrence_admin_view(self):
        starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
        # The simplest occurrence instance we can create needs only a location.
        # Using the instance creation and then save methods

        new_occurrence = Occurrence.objects.create(geom=Point(41.3, 11.3),
                                                   locality=Locality.objects.get(locality_number=3),
                                                   field_number=datetime.now())
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.catalog_number(), None)  # test catalog number generation in save method
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 41.3)

        # While not logged in should redirect to admin login page
        response = self.client.get('/django-admin/hrp/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username')  # redirects to login form

        # When logged in should proceed to admin page
        user = User.objects.get(username='test')
        self.client.force_login(user)
        response = self.client.get('/django-admin/hrp/occurrence/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select HRP Occurrence to change | Django site admin')
        self.assertContains(response, '0 of 1 selected')


class OccurrenceMethodTests(TestCase):
    """
    Test Occurrence Methods
    """

    def setUp(self):

        # Create a simple square locality polygon
        Locality.objects.create(id=288, locality_number=288, collection_code='A.L.', geom=Point(41.1, 11.1))

        # Create one occurrence point in at Locality 1
        Occurrence.objects.create(geom=Point(41.1, 11.1),
                                  barcode=1,
                                  basis_of_record='Collection',
                                  item_number=1,
                                  item_part='a',
                                  locality=Locality.objects.get(locality_number=288),
                                  field_number=datetime.now())

    def test_point_x_method(self):
        occ1 = Occurrence.objects.get(barcode=1)
        self.assertEqual(occ1.point_x(), 41.1)

    def test_point_y_method(self):
        occ1 = Occurrence.objects.get(barcode=1)
        self.assertEqual(occ1.point_y(), 11.1)

    def test_easting_method(self):
        occ1 = Occurrence.objects.get(barcode=1)
        self.assertEqual(round(occ1.easting(), 4), round(729382.2689836712, 4))

    def test_northing_method(self):
        occ1 = Occurrence.objects.get(barcode=1)
        self.assertEqual(round(occ1.northing(), 4), round(1227846.080614904, 4))

    def test_catalog_number(self):
        occ1 = Occurrence.objects.get(barcode=1)
        occ1.collection_code = 'A.L.'
        self.assertEqual(occ1.catalog_number(), 'A.L. 288-1a')

    def test_get_all_field_names(self):
        hrp1 = Occurrence.objects.get(barcode=1)
        self.assertEqual(len(hrp1.get_all_field_names()), 52)  # currently 52 fields for HRP Occurrence
        self.assertTrue("name" in hrp1.get_all_field_names())


class BiologyMethodTests(TestCase):
    """
    Test Biology instance methods
    """
    fixtures = [
        'hrp/fixtures/hrp_taxon_test_data.json'
    ]

    def setUp(self):
        User.objects.create_superuser(username='test', email='foo@yahoo.com', password='test')

        Locality.objects.create(id=1, locality_number=1, geom=Point(41.1, 11.1))
        Locality.objects.create(id=2, locality_number=2, geom=Point(41.2, 11.2))
        Locality.objects.create(id=3, locality_number=3, geom=Point(41.3, 11.3))
        Locality.objects.create(id=4, locality_number=4, geom=Point(41.4, 11.4))

    def test_biology_save_method(self):
        """
        Test Biology instance creation with save method
        """

        # self.biology_setup()
        locality_1 = Locality.objects.get(pk=1)
        new_taxon = Taxon.objects.get(name__exact="Primates")
        id_qual = IdentificationQualifier.objects.get(name__exact="None")

        starting_occurrence_record_count = Occurrence.objects.count()  # get current number of occurrence records
        starting_biology_record_count = Biology.objects.count()  # get the current number of biology records
        # The simplest occurrence instance we can create needs only a location.
        # Using the instance creation and then save methods

        new_bio = Biology(
            barcode=1111,
            basis_of_record='Collection',
            collection_code="HRP",
            item_number="1",
            geom="POINT (41.1 11.1)",
            locality=locality_1,
            taxon=new_taxon,
            identification_qualifier=id_qual,
            field_number=datetime.now()
        )
        new_bio.save()
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_occurrence_record_count+1)
        self.assertEqual(Biology.objects.count(), starting_biology_record_count+1)

        self.assertEqual(new_bio.catalog_number(), "HRP 1-1")  # test catalog number generation in save method
        self.assertEqual(new_bio.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_bio.point_x(), 41.1)

    def test_biology_create_observation(self):
        """
        Test Biology instance creation for observations
        """
        occurrence_starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
        biology_starting_record_count = Biology.objects.count()  # get the current number of biology records
        # The simplest occurrence instance we can create needs only a location.
        # Using the instance creation and then save methods
        new_occurrence = Biology.objects.create(
            barcode=2222,
            basis_of_record="Observation",
            collection_code="COL",
            item_number="1",
            geom=Point(41.21, 11.21),
            locality=Locality.objects.get(locality_number__exact=2),
            taxon=Taxon.objects.get(name__exact="Primates"),
            identification_qualifier=IdentificationQualifier.objects.get(name__exact="None"),
            field_number=datetime.now()
        )
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), occurrence_starting_record_count+1)  # one record added?
        self.assertEqual(new_occurrence.catalog_number(), None)  # test catalog number generation in save method
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 41.21)
        self.assertEqual(Biology.objects.count(), biology_starting_record_count+1)  # no biology record was added?
        self.assertEqual(Biology.objects.filter(basis_of_record__exact="Observation").count(), 1)
        response = self.client.get('/django-admin/hrp/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username')  # redirects to login form

    def test_biology_admin_view(self):
        """
        Create a single Biology object then test that we can open and render the Biology admin page
        :return:
        """
        Biology.objects.create(
            barcode=2222,
            basis_of_record="Observation",
            collection_code="COL",
            item_number="1",
            geom=Point(41.21, 11.21),
            locality=Locality.objects.get(locality_number__exact=2),
            taxon=Taxon.objects.get(name__exact="Primates"),
            identification_qualifier=IdentificationQualifier.objects.get(name__exact="None"),
            field_number=datetime.now()
        )

        # While not logged in should redirect to admin login page
        response = self.client.get('/django-admin/hrp/biology', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username')  # redirects to login form

        # When logged in should proceed to admin page
        user = User.objects.get(username='test')
        self.client.force_login(user)
        response = self.client.get('/django-admin/hrp/biology/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select HRP Biology to change | Django site admin')
        self.assertContains(response, '0 of 1 selected')
