from django.test import TestCase
from lgrp.models import Occurrence, Biology,Taxon, IdentificationQualifier
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, Polygon


class OccurrenceCreationMethodTests(TestCase):
    """
    Test Occurrence instance creation and methods
    """

    def test_occurrence_save_simple(self):
        """
        Test Occurrence instance save method with the simplest possible attributes, coordinates only
        """
        starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
        new_occurrence = Occurrence(geom="POINT (41.1 11.1)",
                                    field_number=datetime.now())
        new_occurrence.save()
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.catalog_number(), None)  # test catalog number generation in save method
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 41.1)

    def test_occurrence_create_simple(self):
        """
        Test Occurrence instance creation with the simplest possible attributes, coordinates only
        """
        starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
        new_occurrence = Occurrence.objects.create(geom=Point(41.2, 11.2),
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
                                                   field_number=datetime.now())
        now = datetime.now()
        self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
        self.assertEqual(new_occurrence.old_cat_number, None)  # test catalog number generation in save method
        self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
        self.assertEqual(new_occurrence.point_x(), 41.3)

        response = self.client.get('/django-admin/lgrp/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username')  # redirects to login form


class OccurrenceMethodTests(TestCase):
    """
    Test Occurrence Methods
    """

    def setUp(self):

        # Create one occurrence point in polygon 1
        Occurrence.objects.create(geom=Point(41.123456789, 11.123456789),
                                  barcode=1,
                                  field_number=datetime.now())

    def test_point_x_method(self):
        obj1 = Occurrence.objects.get(barcode=1)
        self.assertEqual(obj1.point_x(), 41.123456789)

    def test_point_y_method(self):
        obj1 = Occurrence.objects.get(barcode=1)
        self.assertEqual(obj1.point_y(), 11.123456789)

    def test_latitude_method(self):
        obj1 = Occurrence.objects.get(barcode=1)
        self.assertEqual(obj1.latitude(), 11.123456789)

    def test_longitude_method(self):
        obj1 = Occurrence.objects.get(barcode=1)
        self.assertEqual(obj1.longitude(), 41.123456789)

    def test_easting_method(self):
        obj1 = Occurrence.objects.get(barcode=1)
        self.assertAlmostEqual(obj1.easting(), 731926.9879, 4)

    def test_northing_method(self):
        obj1 = Occurrence.objects.get(barcode=1)
        self.assertAlmostEqual(obj1.northing(), 1230459.5853, 4)

    def test_get_all_field_names(self):
        obj1 = Occurrence.objects.get(barcode=1)
        field_names_list = obj1.get_all_field_names()
        self.assertEqual(len(field_names_list), 58)  # check the length of the field name list.
        self.assertTrue('basis_of_record' in field_names_list)

    def test_get_foreign_key_field_names(self):
        obj1 = Occurrence.objects.get(barcode=1)
        foreign_key_list = obj1.get_foreign_key_field_names()
        self.assertEqual(len(foreign_key_list), 11)
        self.assertTrue('biology' in foreign_key_list)
        self.assertFalse('basis_of_record' in foreign_key_list)

    def test_get_concrete_field_names(self):
        obj1 = Occurrence.objects.get(barcode=1)
        concrete_field_list = obj1.get_concrete_field_names()
        self.assertEqual(len(concrete_field_list), 53)
        self.assertTrue('basis_of_record' in concrete_field_list)
        self.assertFalse('biology' in concrete_field_list)


class ImportKMZTests(TestCase):
    pass

# class BiologyMethodTests(TestCase):
#     """
#     Test Biology instance methods
#     """
#     fixtures = [
#         'fixtures/fiber_data_150611.json',
#         'taxonomy/fixtures/taxonomy_161020.json'
#     ]
#
#     def test_biology_save_method(self):
#         """
#         Test Biology instance creation with save method
#         """
#
#         # self.biology_setup()
#         new_taxon = Taxon.objects.get(name__exact="Primates")
#         id_qual = IdentificationQualifier.objects.get(name__exact="None")
#
#         starting_occurrence_record_count = Occurrence.objects.count()  # get current number of occurrence records
#         starting_biology_record_count = Biology.objects.count()  # get the current number of biology records
#         # The simplest occurrence instance we can create needs only a location.
#         # Using the instance creation and then save methods
#
#         new_bio = Biology(
#             barcode=1111,
#             basis_of_record="Collection",
#             collection_code="AA",
#             locality_number="1",
#             item_number="1",
#             old_cat_number='AA-1-1',
#             geom="POINT (41.1 11.1)",
#             taxon=new_taxon,
#             identification_qualifier=id_qual,
#             field_number=datetime.now()
#         )
#         new_bio.save()
#         now = datetime.now()
#         self.assertEqual(Occurrence.objects.count(), starting_occurrence_record_count+1)
#         self.assertEqual(Biology.objects.count(), starting_biology_record_count+1)
#
#         self.assertEqual(new_bio.old_cat_number, "AA-1-1")  # test catalog number generation in save method
#         self.assertEqual(new_bio.date_last_modified.day, now.day)  # test date last modified is correct
#         self.assertEqual(new_bio.point_x(), 41.1)
#
#     def test_biology_create_observation(self):
#         """
#         Test Biology instance creation for observations
#         """
#         occurrence_starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
#         biology_starting_record_count = Biology.objects.count()  # get the current number of biology records
#         # The simplest occurrence instance we can create needs only a location.
#         # Using the instance creation and then save methods
#         new_occurrence = Biology.objects.create(
#             barcode=2222,
#             basis_of_record="Observation",
#             collection_code="COL",
#             locality_number="2",
#             item_number="1",
#             geom=Point(41.21, 11.21),
#             taxon=Taxon.objects.get(name__exact="Primates"),
#             identification_qualifier=IdentificationQualifier.objects.get(name__exact="None"),
#             field_number=datetime.now()
#         )
#         now = datetime.now()
#         self.assertEqual(Occurrence.objects.count(), occurrence_starting_record_count+1)  # one record added?
#         self.assertEqual(new_occurrence.old_cat_number, None)  # test catalog number generation in save method
#         self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
#         self.assertEqual(new_occurrence.point_x(), 41.21)
#         self.assertEqual(Biology.objects.count(), biology_starting_record_count+1)  # no biology record was added?
#         self.assertEqual(Biology.objects.filter(basis_of_record__exact="Observation").count(), 1)
#         response = self.client.get('/admin/lgrp/', follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Username')  # redirects to login form
#
# #        response = self.client.get('/admin/lgrp/biology/')
# #        self.assertEqual(response.status_code, 200)
# #        response = self.client.get('/admin/lgrp/biology/'+str(new_occurrence.pk)+'/')
# #        self.assertEqual(response.status_code, 200)
#
#
# class HRPViewsTests(TestCase):
#     """
#     The HRP Views Test Case depends on two fixtures.
#     """
#     fixtures = [
#         'fixtures/fiber_data_150611.json',
#         'taxonomy/fixtures/taxonomy_data_150611.json',
#     ]
#
#     def setUp(self):
#
#         # Populate Biology instances
#         id_qualifier = IdentificationQualifier.objects.get(name__exact="None")
#         barcode_index = 1
#         mammal_orders = (("Primates", "Primates"),
#                          ("Perissodactyla", "Perissodactyla"),
#                          ("Artiodactyla", "Artiodactyla"),
#                          ("Rodentia", "Rodentia"),
#                          ("Carnivora", "Carnivora"),)
#
#         for order_tuple_element in mammal_orders:
#             Biology.objects.create(
#                 barcode=barcode_index,
#                 basis_of_record="HumanObservation",
#                 collection_code="HRP",
#                 locality_number="1",
#                 item_number=barcode_index,
#                 geom=Point(41.11, 11.11),
#                 taxon=Taxon.objects.get(name__exact=order_tuple_element[0]),
#                 identification_qualifier=id_qualifier,
#                 field_number=datetime.now()
#             )
#             barcode_index += 1
#
#         self.assertEqual(Occurrence.objects.count(), len(mammal_orders))
#
#     def test_admin_list_view(self):
#         response = self.client.get('/admin/lgrp/', follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Username')  # redirects to login form
#
#
# class HRPAdminViewTests(TestCase):
#     """
#     The HRP Views Test Case depends on two fixtures.
#     """
#     fixtures = [
#         'fixtures/fiber_data_150611.json',
#         'taxonomy/fixtures/taxonomy_data_150611.json',
#     ]
#
#     def setUp(self):
#
#         # Populate Biology instances
#         id_qualifier = IdentificationQualifier.objects.get(name__exact="None")
#         barcode_index = 1
#         mammal_orders = (("Primates", "Primates"),
#                          ("Perissodactyla", "Perissodactyla"),
#                          ("Artiodactyla", "Artiodactyla"),
#                          ("Rodentia", "Rodentia"),
#                          ("Carnivora", "Carnivora"),)
#
#         for order_tuple_element in mammal_orders:
#             Biology.objects.create(
#                 barcode=barcode_index,
#                 basis_of_record="HumanObservation",
#                 collection_code="HRP",
#                 locality_number="1",
#                 item_number=barcode_index,
#                 geom=Point(41.11, 11.11),
#                 taxon=Taxon.objects.get(name__exact=order_tuple_element[0]),
#                 identification_qualifier=id_qualifier,
#                 field_number=datetime.now()
#             )
#             barcode_index += 1
#
#         self.assertEqual(Occurrence.objects.count(), len(mammal_orders))
#
#         test_user = User.objects.create_user(username='test_user', password='password')
#         test_user.is_staff = True
#         test_user.save()
#
#     def test_admin_list_view(self):
#         response = self.client.get('/admin/lgrp/', follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Username')  # redirects to login form
#
#     def test_admin_list_view_with_login(self):
#         test_user = User.objects.get(username='test_user')
#         self.assertEqual(test_user.is_staff, True)  # Test user is staff
#         self.client.login(username='test_user', password='password')
#         response = self.client.get('/admin/lgrp/', follow=True)
#         self.assertEqual(response.status_code, 403)
#         # self.assertContains(response, 'Username')  # redirects to login form
