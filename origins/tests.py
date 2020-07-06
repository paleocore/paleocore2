from django.test import TestCase
import origins.ontologies as ontologies


######################################
# Tests for models and their methods #
######################################


class OriginsOntologiesTests(TestCase):
    """
    Test origins ontologies
    """

    def test_origins_continent_choices(self):
        """
        Test that the integrity of continent ontology
        """
        self.assertEqual(ontologies.africa, 'Africa')  # test Africa variable
        self.assertEqual(len(ontologies.CONTINENT_CHOICES), 7)  # test there are 7 continents

    def test_origins_choices2list(self):
        """
        Test choices2list method
        :return:
        """
        self.assertEqual(len(ontologies.choices2list(ontologies.CONTINENT_CHOICES)), 7)
        self.assertEqual(ontologies.choices2list(ontologies.CONTINENT_CHOICES)[0], 'Africa')
        self.assertEqual(type(ontologies.choices2list(ontologies.CONTINENT_CHOICES)), list)


