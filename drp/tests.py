from django.test import TestCase
from drp.models import Occurrence, Biology, Locality
from drp.models import Taxon, IdentificationQualifier
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, Polygon


class LocalityMethodsTests(TestCase):
    """
    Test Locality instance creation and methods
    """
    def test_locality_save_simple(self):
        starting_record_count = Locality.objects.count()  # get current record count

        # Create a simple square polygon
        # Note that the first tuple and last tuple must have exact same coordinates.
        poly = Polygon(
            ((41.6, 11.2), (41.8, 11.2), (41.8, 11.0), (41.6, 11.0), (41.6, 11.2))
        )
        new_locality = Locality(paleolocality_number=1, geom=poly)
        new_locality.save()
        self.assertEqual(Locality.objects.count(), starting_record_count+1)

    def test_locality_create_simple(self):
        starting_record_count = Locality.objects.count()  # get current record count
        poly = Polygon(
            ((41.2, 11.2), (41.4, 11.2), (41.4, 11.0), (41.2, 11.0), (41.2, 11.2))
        )
        Locality.objects.create(paleolocality_number=2, geom=poly)
        self.assertEqual(Locality.objects.count(), starting_record_count+1)


# class OccurrenceCreationMethodTests(TestCase):
#     """
#     Test Occurrence instance creation and methods
#     """
#
#     def setUp(self):
#         def create_square_locality(x, y):
#             return Polygon(
#                 (
#                     (x-0.01, y+0.01),
#                     (x+0.01, y+0.01),
#                     (x+0.01, y-0.01),
#                     (x-0.01, y-0.01),
#                     (x-0.01, y+0.01)
#                 )
#             )
#
#         Locality.objects.create(paleolocality_number=1, geom=create_square_locality(41.1, 11.1))
#         Locality.objects.create(paleolocality_number=2, geom=create_square_locality(41.2, 11.2))
#         Locality.objects.create(paleolocality_number=3, geom=create_square_locality(41.3, 11.3))
#         Locality.objects.create(paleolocality_number=4, geom=create_square_locality(41.4, 11.4))
#
#     def test_occurrence_save_simple(self):
#         """
#         Test Occurrence instance save method with the simplest possible attributes, coordinates only
#         """
#         starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
#         new_occurrence = Occurrence(geom="POINT (41.1 11.1)",
#                                     locality=Locality.objects.get(paleolocality_number=1),
#                                     field_number=datetime.now())
#         new_occurrence.save()
#         now = datetime.now()
#         self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
#         self.assertEqual(new_occurrence.catalog_number, "--")  # test catalog number generation in save method
#         self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
#         self.assertEqual(new_occurrence.point_x(), 41.1)
#         self.assertEqual(new_occurrence.locality.paleolocality_number, 1)
#
#     def test_occurrence_create_simple(self):
#         """
#         Test Occurrence instance creation with the simplest possible attributes, coordinates only
#         """
#         starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
#         new_occurrence = Occurrence.objects.create(geom=Point(41.2, 11.2),
#                                                    locality=Locality.objects.get(paleolocality_number=2),
#                                                    field_number=datetime.now())
#         now = datetime.now()
#         self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
#         self.assertEqual(new_occurrence.catalog_number, "--")  # test catalog number generation in save method
#         self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
#         self.assertEqual(new_occurrence.point_x(), 41.2)
#
#     def test_occurrence_admin_view(self):
#         starting_record_count = Occurrence.objects.count()  # get current number of occurrence records
#         # The simplest occurrence instance we can create needs only a location.
#         # Using the instance creation and then save methods
#
#         new_occurrence = Occurrence.objects.create(geom=Point(41.3, 11.3),
#                                                    locality=Locality.objects.get(paleolocality_number=3),
#                                                    field_number=datetime.now())
#         now = datetime.now()
#         self.assertEqual(Occurrence.objects.count(), starting_record_count+1)  # test that one record has been added
#         self.assertEqual(new_occurrence.catalog_number, "--")  # test catalog number generation in save method
#         self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
#         self.assertEqual(new_occurrence.point_x(), 41.3)
#
#         response = self.client.get('/admin/mlp/', follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Username')  # redirects to login form


# class OccurrenceMethodTests(TestCase):
#     """
#     Test Occurrence Methods
#     """
#
#     def setUp(self):
#         def create_square_locality(x, y):
#             return Polygon(
#                 (
#                     (x-0.01, y+0.01),
#                     (x+0.01, y+0.01),
#                     (x+0.01, y-0.01),
#                     (x-0.01, y-0.01),
#                     (x-0.01, y+0.01)
#                 )
#             )
#         # Create four simple square locality polygons
#         Locality.objects.create(paleolocality_number=1, geom=create_square_locality(41.1, 11.1))
#
#         # Create one occurrence point in polygon 1
#         Occurrence.objects.create(geom=Point(41.1, 11.1),
#                                   barcode=1,
#                                   catalog_number='DIK-1-1',
#                                   locality=Locality.objects.get(paleolocality_number=1),
#                                   field_number=datetime.now())
#
#     def test_point_x_method(self):
#         dik1 = Occurrence.objects.get(barcode=1)
#         self.assertEqual(dik1.point_x(), 41.1)
#
#     def test_point_y_method(self):
#         dik1 = Occurrence.objects.get(barcode=1)
#         self.assertEqual(dik1.point_y(), 11.1)
#
#     def test_easting_method(self):
#         dik1 = Occurrence.objects.get(barcode=1)
#         self.assertEqual(dik1.easting(), 729382.2689836712)
#
#     def test_northing_method(self):
#         dik1 = Occurrence.objects.get(barcode=1)
#         self.assertEqual(dik1.northing(), 1227846.080614904)
#
#
#
# class BiologyMethodTests(TestCase):
#     """
#     Test Biology instance methods
#     """
#     fixtures = [
#         'fixtures/fiber_data_150611.json',
#         'taxonomy/fixtures/taxonomy_data_150611.json'
#     ]
#
#     def setUp(self):
#         def create_square_locality(x, y):
#             return Polygon(
#                 (
#                     (x-0.01, y+0.01),
#                     (x+0.01, y+0.01),
#                     (x+0.01, y-0.01),
#                     (x-0.01, y-0.01),
#                     (x-0.01, y+0.01)
#                 )
#             )
#
#         Locality.objects.create(paleolocality_number=1, geom=create_square_locality(41.1, 11.1))
#         Locality.objects.create(paleolocality_number=2, geom=create_square_locality(41.2, 11.2))
#         Locality.objects.create(paleolocality_number=3, geom=create_square_locality(41.3, 11.3))
#         Locality.objects.create(paleolocality_number=4, geom=create_square_locality(41.4, 11.4))
#
#     def test_biology_save_method(self):
#         """
#         Test Biology instance creation with save method
#         """
#
#         # self.biology_setup()
#         locality_1 = Locality.objects.get(paleolocality_number__exact=1)
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
#             basis_of_record="FossilSpecimen",
#             collection_code="DRP",
#             paleolocality_number="1",
#             item_number="1",
#             geom="POINT (41.1 11.1)",
#             locality=locality_1,
#             taxon=new_taxon,
#             identification_qualifier=id_qual,
#             field_number=datetime.now()
#         )
#         new_bio.save()
#         now = datetime.now()
#         self.assertEqual(Occurrence.objects.count(), starting_occurrence_record_count+1)
#         self.assertEqual(Biology.objects.count(), starting_biology_record_count+1)
#
#         self.assertEqual(new_bio.catalog_number, "DRP-1-1")  # test catalog number generation in save method
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
#             basis_of_record="HumanObservation",
#             collection_code="COL",
#             paleolocality_number="2",
#             item_number="1",
#             geom=Point(41.21, 11.21),
#             locality=Locality.objects.get(paleolocality_number__exact=2),
#             taxon=Taxon.objects.get(name__exact="Primates"),
#             identification_qualifier=IdentificationQualifier.objects.get(name__exact="None"),
#             field_number=datetime.now()
#         )
#         now = datetime.now()
#         self.assertEqual(Occurrence.objects.count(), occurrence_starting_record_count+1)  # one record added?
#         self.assertEqual(new_occurrence.catalog_number, "COL-2-1")  # test catalog number generation in save method
#         self.assertEqual(new_occurrence.date_last_modified.day, now.day)  # test date last modified is correct
#         self.assertEqual(new_occurrence.point_x(), 41.21)
#         self.assertEqual(Biology.objects.count(), biology_starting_record_count+1)  # no biology record was added?
#         self.assertEqual(Biology.objects.filter(basis_of_record__exact="HumanObservation").count(), 1)
#         response = self.client.get('/admin/mlp/', follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Username')  # redirects to login form
#
# #        response = self.client.get('/admin/mlp/biology/')
# #        self.assertEqual(response.status_code, 200)
# #        response = self.client.get('/admin/mlp/biology/'+str(new_occurrence.pk)+'/')
# #        self.assertEqual(response.status_code, 200)
#
#
# class DRPViewsTests(TestCase):
#     """
#     The DRP Views Test Case depends on two fixtures.
#     """
#     fixtures = [
#         'fixtures/fiber_data_150611.json',
#         'taxonomy/fixtures/taxonomy_data_150611.json',
#     ]
#
#     def setUp(self):
#
#         # Populate Localities
#         def create_square_locality(x, y):
#             return Polygon(
#                 (
#                     (x-0.01, y+0.01),
#                     (x+0.01, y+0.01),
#                     (x+0.01, y-0.01),
#                     (x-0.01, y-0.01),
#                     (x-0.01, y+0.01)
#                 )
#             )
#
#         Locality.objects.create(paleolocality_number=1, geom=create_square_locality(41.1, 11.1))
#         Locality.objects.create(paleolocality_number=2, geom=create_square_locality(41.2, 11.2))
#         Locality.objects.create(paleolocality_number=3, geom=create_square_locality(41.3, 11.3))
#         Locality.objects.create(paleolocality_number=4, geom=create_square_locality(41.4, 11.4))
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
#                 collection_code="DRP",
#                 paleolocality_number="1",
#                 item_number=barcode_index,
#                 geom=Point(41.11, 11.11),
#                 locality=Locality.objects.get(paleolocality_number__exact=1),
#                 taxon=Taxon.objects.get(name__exact=order_tuple_element[0]),
#                 identification_qualifier=id_qualifier,
#                 field_number=datetime.now()
#             )
#             barcode_index += 1
#
#         self.assertEqual(Locality.objects.count(), 4)
#         self.assertEqual(Occurrence.objects.count(), len(mammal_orders))
#
#     def test_admin_list_view(self):
#         response = self.client.get('/admin/mlp/', follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Username')  # redirects to login form
#
#
# class DRPAdminViewTests(TestCase):
#     """
#     The DRP Views Test Case depends on two fixtures.
#     """
#     fixtures = [
#         'fixtures/fiber_data_150611.json',
#         'taxonomy/fixtures/taxonomy_data_150611.json',
#     ]
#
#     def setUp(self):
#
#         # Populate Localities
#         def create_square_locality(x, y):
#             return Polygon(
#                 (
#                     (x-0.01, y+0.01),
#                     (x+0.01, y+0.01),
#                     (x+0.01, y-0.01),
#                     (x-0.01, y-0.01),
#                     (x-0.01, y+0.01)
#                 )
#             )
#
#         Locality.objects.create(paleolocality_number=1, geom=create_square_locality(41.1, 11.1))
#         Locality.objects.create(paleolocality_number=2, geom=create_square_locality(41.2, 11.2))
#         Locality.objects.create(paleolocality_number=3, geom=create_square_locality(41.3, 11.3))
#         Locality.objects.create(paleolocality_number=4, geom=create_square_locality(41.4, 11.4))
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
#                 collection_code="DRP",
#                 paleolocality_number="1",
#                 item_number=barcode_index,
#                 geom=Point(41.11, 11.11),
#                 locality=Locality.objects.get(paleolocality_number__exact=1),
#                 taxon=Taxon.objects.get(name__exact=order_tuple_element[0]),
#                 identification_qualifier=id_qualifier,
#                 field_number=datetime.now()
#             )
#             barcode_index += 1
#
#         self.assertEqual(Locality.objects.count(), 4)
#         self.assertEqual(Occurrence.objects.count(), len(mammal_orders))
#
#         test_user = User.objects.create_user(username='test_user', password='password')
#         test_user.is_staff = True
#         test_user.save()
#
#     def test_admin_list_view(self):
#         response = self.client.get('/admin/mlp/', follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Username')  # redirects to login form
#
#     def test_admin_list_view_with_login(self):
#         test_user = User.objects.get(username='test_user')
#         self.assertEqual(test_user.is_staff, True)  # Test user is staff
#         self.client.login(username='test_user', password='password')
#         response = self.client.get('/admin/mlp/', follow=True)
#         self.assertEqual(response.status_code, 403)
#         #self.assertContains(response, 'Username')  # redirects to login form
