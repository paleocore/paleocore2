__author__ = 'reedd'
"""
This loader/importer script is designed to read data from a sqlite database storing the Hadar Research Project (HRP)
data, and load those data into the PaleoCore postgres database. The script:
1) reads and validates the raw data read in from the occurrence table in the sqlite database and loads the data into
a dictionary (row_dict).  The validation function cleans the data and converts the data to an appropriate format
where necessar;
2) reads and validates related data from the biology table in the HRP sqlite database where appropriate and adds those
data to separate dictionary (bio_dict);
3) creates a new object of the appropriate subclass (e.g. Biology, Archaeology, Geology), validates the data in the
new object against the original data and if valid saves the new object.
4) the script reports the number of records processed, the number of objects of each class created and reports these at
the end.
"""

# Import libraries
import sqlite3
from hrp.models import Taxon, TaxonRank, IdentificationQualifier
from hrp.models import Occurrence, Locality, Archaeology, Biology, Geology
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
import datetime
import re

# Required imports for stand-alone django scripts
# http://stackoverflow.com/questions/25244631/models-arent-loaded-yet-error-while-populating-in-django-1-8-and-python-2-7-8
import django
django.setup()

# Global variables
# initiate a list of barcodes used to verify that each barcode added in the validate_row function is unique
barcode_list = []
# absolute file path to the HRP sqlite database from whihc we are reading data
hrpdb_path = '/Users/reedd/Documents/projects/PaleoCore/projects/HRP/HRP_Paleobase4_2016.sqlite'
record_limit = ('20000',)  # a limiter setting the maximum number of records to be read from the database, for debugging
# list of fields as they occur in the HRP sqlite database occurrence table. The list is used to correctly find
# specific data read in from each row of the occurrence table.
occurrence_field_list = ["OBJECTID", "Shape", "CatalogNumberNumeric", "CatalogNumberNumeric_OLD", "BasisOfRecord",
                         "ItemType", "InstitutionalCode", "CollectionCode", "PaleoLocalityNumber", "PaleoLocalityText",
                         "PaleoSubLocality", "ItemNumber", "ItemPart", "CatalogNumber", "GeneralRemarks",
                         "ItemScientificName", "ItemDescription",
                         "Continent", "Country", "StateProvince", "DrainageRegion", "County", "VerbatimCoordinates",
                         "VerbatimCoordinateSystem", "GeoreferenceRemarks", "UTMZone", "UTMEast", "UTMNorth",
                         "CollectingMethod",
                         "RelatedCatalogItems", "Collector", "Finder", "Disposition", "CollectionRemarks", "TimeStamp_",
                         "YearCollected", "IndividualCount", "PreparationStatus", "StratigraphicMarkerUpper",
                         "MetersFromUpper",
                         "StratigraphicMarkerLower", "MetersFromLower", "StratigraphicMarkerFound", "DistanceFromFound",
                         "StratigraphicMarkerLikely", "DistanceFromLikely", "StratigraphicFormation",
                         "StratigraphicMember",
                         "GeologyRemarks", "AnalyticalUnitFound", "AnalyticalUnit1", "AnalyticalUnit2",
                         "AnalyticalUnit3",
                         "AnalyticalUnitLikely", "AnalyticalUnitSimplified", "Insitu", "RankedUnit", "ImageURL",
                         "RelatedInformation", "LocalityID", "StratigraphicSection", "StratigraphicHeightInMeters",
                         "SpecimenImage", "Weathering", "SurfaceModification", "POINT_X", "POINT_Y", "Problem",
                         "ProblemComment", "MonthCollected", "GeodeticDatum", "Barcode", "DateLastModified",
                         "FieldNumber", "ProjectCode"]
# list of HRP collectors used as a structured vocabulary for the collector field and to validate the data in this field.
HRP_collector_list = ['C.J. Campisano', 'W.H. Kimbel', 'T.K. Nalley', 'D.N. Reed', 'K.E. Reed', 'B.J. Schoville',
                      'A.E. Shapiro',  'HFS Student', 'HRP Team']
# list of HRP stratigraphic members used as structured vocabulary for the member field
HRP_strat_member_list = ['Basal', 'Basal-Sidi Hakoma', 'Denen Dora', 'Denen Dora-Kada Hadar', 'Kada Hadar',
                         'Sidi Hakoma', 'Sidi Hakoma-Denen Dora']
# list of fields as they occur in the HRP sqlite database biology table.
biology_field_list = ["CatalogNumberNumeric", "CatalogNumberNumericOLD", "Kingdom", "Phylum", "Class", "Order",
                      "Family", "Subfamily", "Tribe", "Genus", "SpecificEpithet", "IdentificationQualifier",
                      "IdentifiedBy", "DateIdentified", "TypeStatus", "TaxonomyRemarks",
                      "Element", "ElementPortion", "Side", "ElementNumber", "ElementQualifier", "SizeClass",
                      "LifeStage", "ElementRemarks", "DateLastModified", "Barcode", "BiologyRemarks"]
# structured vocabularies for fields in the biology table.
rank_list = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family']

taxon_dict = {'Kingdom': '', 'Phylum': '', 'Class': '', 'Order': '', 'Family': '',
              'Subfamily': '', 'Tribe': '', 'Genus': '', 'Species': ''}

element_list = ['astragalus', 'bacculum', 'bone (indet.)', 'calcaneus', 'canine', 'capitate', 'carapace',
                        'carpal (indet.)', 'carpal/tarsal', 'carpometacarpus', 'carpus', 'chela', 'clavicle', 'coccyx',
                        'coprolite', 'cranium', 'cranium w/horn core', 'cuboid', 'cubonavicular', 'cuneiform',
                        'dermal plate', 'egg shell', 'endocast', 'ethmoid', 'femur', 'fibula', 'frontal', 'hamate',
                        'horn core', 'humerus', 'hyoid', 'ilium', 'incisor', 'innominate', 'ischium', 'lacrimal',
                        'long bone', 'lunate', 'mandible', 'manus', 'maxilla', 'metacarpal', 'metapodial',
                        'metatarsal', 'molar', 'nasal', 'navicular', 'naviculocuboid', 'occipital', 'ossicone',
                        'parietal', 'patella', 'pes', 'phalanx', 'pisiform', 'plastron', 'premaxilla', 'premolar',
                        'pubis', 'radioulna', 'radius', 'rib', 'sacrum', 'scaphoid', 'scapholunar', 'scapula', 'scute',
                        'sesamoid', 'shell', 'skeleton', 'skull', 'sphenoid', 'sternum', 'talon', 'talus',
                        'tarsal (indet.)', 'tarsometatarsus', 'tarsus', 'temporal', 'tibia', 'tibiotarsus',
                        'tooth (indet.)', 'trapezium', 'trapezoid', 'triquetrum', 'ulna', 'vertebra', 'vomer',
                        'zygomatic']


# Occurrence Helper Functions, used to clean and validate data.
def transform_point(row):
    """
    Create a point object from UTM coordinates and transform to GCS
    :param row:
    :return Point object in GCS or None
    """
    # Fetch coordinates from row data
    pointx, pointy = row[occurrence_field_list.index('POINT_X'):occurrence_field_list.index('POINT_Y') + 1]

    # Transform coordinates from UTM to GCS
    if pointx is None or pointy is None:  # Create Null point if no coordinates
        pt = None
    else:
        pt = Point([pointx, pointy], srid=32637)  # Create point in UTM
        pt.transform(4326)  # Transform to GCS
    return pt


def convert_date_recorded(row):
    """
    Convert date_recorded string to datetime object
    :param row:
    :return date_recorded as datetime object:
    """
    occurrence_id = row[occurrence_field_list.index('CatalogNumberNumeric')]
    date_recorded_string = row[occurrence_field_list.index('TimeStamp_')]

    # Import date_recorded from string
    if date_recorded_string and date_recorded_string != '':
        if len(date_recorded_string) == 9:
            date_recorded = datetime.datetime.strptime(date_recorded_string, '%d-%b-%y')
        elif len(date_recorded_string) == 19:
            date_recorded = datetime.datetime.strptime(date_recorded_string, '%Y-%m-%d %H:%M:%S')
        else:
            print("Import found Invalid date_recorded %s for Occurrence %s" % (date_recorded_string, occurrence_id))
            return False
    else:
        date_recorded = None
    return date_recorded


def convert_date_last_modified(row):
    """
    Convert row DateLastModified string to datetime object
    :param row:
    :return dlm as datetime object:
    """

    dlm = None
    dlm_string = row[occurrence_field_list.index('DateLastModified')]
    if dlm_string and dlm_string != '':
        dlm = datetime.datetime.strptime(dlm_string, '%m/%d/%y %H:%M:%S')
    return dlm


def convert_in_situ(row):
    """
    Convert in_situ floats to True/False, defaults to False
    :param row:
    :return:
    """
    in_situ_float = row[occurrence_field_list.index('Insitu')]
    in_situ = False
    if in_situ_float == 0.0:
        in_situ = False
    elif in_situ_float in (-1.0, 1.0):
        in_situ = True
    elif not in_situ_float:
        in_situ = False
    return in_situ


def convert_ranked(row):
    """
    Convert ranked floats to True/False, defaults to False
    :param row:
    :return:
    """
    ranked_float = row[occurrence_field_list.index('RankedUnit')]
    ranked = False
    if ranked_float == 0.0:
        ranked = False
    elif ranked_float in (-1.0, 1.0):
        ranked = True
    elif not ranked_float:
        ranked = False
    return ranked


def convert_problem(row):
    """
    Convert problem integer to Yes/No
    :param row:
    :return:
    """
    problem_integer = row[occurrence_field_list.index('Problem')]
    if problem_integer in (1, -1):
        return True
    elif not problem_integer or problem_integer == 0:
        return False


# Biology helper functions
def create_taxon_dictionary(brow):
    """
    Read a DB row and load into a dictionary
    :param brow:
    :return: Return a dictionary with taxonomic information
    """
    td = taxon_dict  # initiate a new taxon dictionary
    td['Kingdom'] = brow[biology_field_list.index('Kingdom')]
    td['Phylum'] = brow[biology_field_list.index('Phylum')]
    td['Class'] = brow[biology_field_list.index('Class')]
    td['Order'] = brow[biology_field_list.index('Order')]
    td['Family'] = brow[biology_field_list.index('Family')]
    td['Subfamily'] = brow[biology_field_list.index('Subfamily')]
    td['Tribe'] = brow[biology_field_list.index('Tribe')]
    td['Genus'] = brow[biology_field_list.index('Genus')]
    td['Trivial'] = brow[biology_field_list.index('SpecificEpithet')]
    td['Qualifier'] = brow[biology_field_list.index('IdentificationQualifier')]
    if td['Genus'] != '' and td['Trivial'] != '':
        td['Species'] = td['Genus'] + ' ' + ['Trivial']
    else:
        td['Species'] = ''

    return td


def get_taxon_list(brow):
    """"
    Get a list of all taxonomic names for the record in order from highest to lowest rank including Null values
    :param brow:
    :return: Returns a list with taxonomic names, e.g. (u'Animalia', u'Chordata', None, u'Bovini')
    """
    taxon_list = list(brow[biology_field_list.index('Kingdom'):biology_field_list.index('SpecificEpithet')+1])
    if taxon_list[-1] == 'sp.':  # Replace 'sp.' with None
        taxon_list[-1] = None
    return taxon_list


def get_verbatim_taxon_list(brow):
    """"
    Get a list of taxonomic names, unmodified from original in DB.
    :param brow:
    :return:
    """
    return brow[biology_field_list.index('Kingdom'):biology_field_list.index('SpecificEpithet')+1]


def get_taxon_name_rank(brow):
    """
    Function to look up a taxon object for a row in the Biology table
    :param brow:
    :return: Returns a tuple of (taxon_name, taxon_rank_name) for taxa of Genus or higher, e.g. ('Hominidae', 'Family')
    for species the function returns a tuple with the species binomen, e.g. ('Homo sapiens', 'SpecificEpithet')
    """
    taxon_list = get_taxon_list(brow)
    name_index = max([i for i, x in enumerate(taxon_list) if x])  # I love list comprehensions
    taxon_name = taxon_list[name_index]
    taxon_rank_name = biology_field_list[name_index+2]
    if taxon_rank_name == 'SpecificEpithet':
        taxon_name = taxon_list[name_index-1]+' '+taxon_list[name_index]
    return [taxon_name, taxon_rank_name]


def get_matching_taxon(brow):
    """
    Searches taxon objects for taxa matching an occurrence
    :param row:
    :return: returns a single element record set
    """
    # get data from all taxon fields and collect them in a list
    # e.g. ["Animalia", "Chordata", "Mammalia", "Primates", "", "Hominidae", "", "", "Homo", "sapiens"]
    taxon_list = get_taxon_list(brow)
    # get taxon name and rank
    taxon_name, taxon_rank_name = get_taxon_name_rank(brow)

    if taxon_rank_name == 'SpecificEpithet':
        genus_name, species_name = taxon_list[7:]
        if Taxon.objects.filter(parent__name=genus_name).filter(name=species_name).exists():
            taxon_object = Taxon.objects.get(parent__name=genus_name, name=species_name)
        else:
            taxon_object = None
    else:
        if Taxon.objects.filter(name=taxon_name).filter(rank__name=taxon_rank_name).exists():
            taxon_object = Taxon.objects.get(name=taxon_name, rank__name=taxon_rank_name)
        else:
            taxon_object = None
    return taxon_object


def get_matching_parent(brow):
    """
    For a given occurrence searches list of parent names to find a matching taxon
    :param brow:
    :return: Returns a taxon object, or None
    """
    taxon_list = get_taxon_list(brow)
    taxon_object = None
    for taxon_name in reversed(taxon_list[:-1]):
        if Taxon.objects.filter(name=taxon_name).count() == 1:  # if there's a single match, done
            taxon_object = Taxon.objects.get(name=taxon_name)
            break
    return taxon_object


def get_qualifier_taxon(taxon, name):
    """
    For a given taxon object find a parent taxon object that matches the name
    :param taxon:
    :param name:
    :return: Return a taxon object or None
    """
    # if len(name.split()) == 1:
    #     return [t for t in taxon.full_lineage() if t.name == name][0]
    # elif len(name.split()) == 2:
    #     return [t for t in taxon.full_lineage() if t.name == name.split()[1:]][0]
    # else:
    #     raise IndexError
    if taxon.name == name:
        return taxon
    elif len(name.split())==2 and name.split()[0] != 'sp.':
        species_name = name.split()[1]
        return [t for t in taxon.full_lineage() if t.name == species_name][0]


def create_taxon(brow):
    """
    Creates a new taxon for taxon names not encountered in the DB. Assumes ranks already exist.
    :param brow:
    :return: returns the newly created taxon object
    """
    taxon_name, taxon_rank_name = get_taxon_name_rank(brow)  # get taxon name and rank
    if taxon_name:
        print("Creating new %s: %s" % (taxon_rank_name, taxon_name))
        if taxon_rank_name == 'SpecificEpithet':
            # check genus and create if necessary
            genus_name = taxon_name.split()[0]  # taxon_name is binomen for rank SpecificEpithet, use split to get genus
            # Note trivial name may be more than word, e.g. 'Ugandax sp. nov.' the trivial will be 'sp. nov.'
            trivial_name = ' '.join(taxon_name.split()[1:])  # get species (and all infraspecific) name(s)
            if not Taxon.objects.filter(name=genus_name).exists():  # If genus name not in DB create it.
                genus = Taxon.objects.create(
                    name=genus_name,
                    parent=get_matching_parent(brow),
                    rank=TaxonRank.objects.get(name='Genus')
                )
            else:
                genus = Taxon.objects.get(name=genus_name)  # If genus name is in DB get it.
            if not Taxon.objects.filter(name=trivial_name, parent=genus).exists():
                new_species = Taxon.objects.create(
                    name=trivial_name,
                    parent=genus,
                    rank=TaxonRank.objects.get(name='Species')
                )
                return new_species
        else:
            if not Taxon.objects.filter(name=taxon_name, rank__name=taxon_rank_name).exists():
                new_taxon = Taxon.objects.create(
                    name=taxon_name,
                    parent=get_matching_parent(brow),
                    rank=TaxonRank.objects.get(name=taxon_rank_name)
                )
                return new_taxon


# Validation Functions, modularize the validation function below. Each function validates a specific field.
def valid_occurrence_id(row):
    """
    Validates occurrence id value for use as primary key
    :param row:
    :return:True if valid, False if not valid
    """
    occurrence_id = row[occurrence_field_list.index('CatalogNumberNumeric')]  # read id from row data
    if occurrence_id and occurrence_id > 0:  # if occurrence_id is not Null and positive
        if Occurrence.objects.filter(id=occurrence_id).exists():  # if occurrence_id is duplicate
            print("Warning, Occurrence id %s already exists" % occurrence_id)   # print warning
            return False  # return a failed validation
        else:  # if occurrence_id not null and not duplicate then return True
            return True

    else:
        print("Missing or non-positive occurrence ID!")
        return False


def valid_coordinates(row):
    """
    Validate coordinates if they exist. Checks that the coordinates are in the correct range for HRP
    :param row:
    :return: Returns True if coords are valid, returns False if an error is detected and prints a message
    """
    occurrence_id = row[occurrence_field_list.index('CatalogNumberNumeric')]  # read id from row data
    # read coordinates from POINT_X and POINT_Y in row data
    coordinates_list = row[occurrence_field_list.index('POINT_X'):occurrence_field_list.index('POINT_Y') + 1]
    # Validate that UTM coordinates are proper size
    if coordinates_list and coordinates_list[0] > 100000 and coordinates_list[1] > 1000000:
        return True
    elif len(coordinates_list) == 2 and (coordinates_list[0] is None or coordinates_list[1] is None):
        return True
    else:
        print("Error validating coordinates for Occurrence %s" % occurrence_id)
        return False


def valid_item_scientific_name(row):
    item_scientific_name = row[occurrence_field_list.index('ItemScientificName')]
    occurrence_id = row[occurrence_field_list.index('CatalogNumberNumeric')]
    if item_scientific_name and item_scientific_name != '':  # if field value exists and not empty string...
        return True
    else:
        print("Invalid ItemScientificName %s for Occurrence %s" % (item_scientific_name, occurrence_id))
        return False


# Occurrence validation function
def validate_row(row):
    """
    Validate row data, convert data types where necessary and
    return a dictionary of cleaned, validated data.
    :param row:
    :return False or row_dict:
    """
    row_dict = {}  # dictionary of row converted and clean row data

    # Validate occurrence id
    occurrence_id = row[occurrence_field_list.index('CatalogNumberNumeric')]  # read id from row data
    if valid_occurrence_id(row):
        row_dict['occurrence_id'] = occurrence_id
    else:
        return False

    # Validate coordinates
    if valid_coordinates(row):
        pt = transform_point(row)
        row_dict['geom'] = pt

    # Validate basis of record
    basis_of_record = row[occurrence_field_list.index('BasisOfRecord')]
    if basis_of_record in ("Collection", "Observation"):
        row_dict['basis_of_record'] = basis_of_record
    else:
        print("Invalid Basis %s for Occurrence %s" % (basis_of_record, occurrence_id))
        return False

    # Validate item type
    item_type = row[occurrence_field_list.index('ItemType')]
    if item_type in ("Faunal", "Floral", "Artifactual", "Geological"):
        row_dict['item_type'] = item_type
    else:
        print("Invalid item type %s for Occurrence %s" % (item_type, occurrence_id))
        return False

    # Validate collection code
    collection_code = row[occurrence_field_list.index('CollectionCode')]
    if (basis_of_record == "Collection" and collection_code == 'A.L.') or \
            (basis_of_record == "Observation" and not collection_code):
        row_dict['collection_code'] = collection_code
    else:
        print("Invalid Collection Code %s for Occurrence %s" % (collection_code, occurrence_id))
        return False

    # Validate PaleoLocalityNumber
    locality_number = row[occurrence_field_list.index('PaleoLocalityNumber')]
    if basis_of_record == 'Collection' and int(locality_number) > 0:
        row_dict['locality_number'] = int(locality_number)
    elif basis_of_record == 'Observation' and not locality_number:
        row_dict['locality_number'] = None
    else:
        print("Invalid locality number %s for Occurrence %s" % (locality_number, occurrence_id))
        return False

    # Validate sublocality
    sublocality = row[occurrence_field_list.index('PaleoSubLocality')]
    if sublocality and not locality_number:
        print("Invalid sublocality %s for Occurrence %s" % (sublocality, occurrence_id))
        return False
    else:
        row_dict['sublocality'] = sublocality

    # Validate item number
    item_number = row[occurrence_field_list.index('ItemNumber')]
    if item_number and not locality_number:
        print("Invalid item number %s for Occurrence %s" % (item_number, occurrence_id))
        return False
    else:
        row_dict['item_number'] = item_number

    # Validate item part
    item_part = row[occurrence_field_list.index('ItemPart')]
    if item_part and not item_number:
        print("Invalid item part %s for Occurrence %s" % (item_part, occurrence_id))
        return False
    else:
        row_dict['item_part'] = item_part

    # Validate Drainage Region
    row_dict['drainage_region'] = row[occurrence_field_list.index('DrainageRegion')]

    # Validate Remarks
    row_dict['remarks'] = row[occurrence_field_list.index('GeneralRemarks')]

    # Validate Item Scientific Name
    item_scientific_name = row[occurrence_field_list.index('ItemScientificName')]
    if valid_item_scientific_name(row):
        row_dict['item_scientific_name'] = item_scientific_name  # add scientific_name to dictionary

    # Validate Item Description
    row_dict['item_description'] = row[occurrence_field_list.index('ItemDescription')]

    # Validate Georeference Remarks
    row_dict['georeference_remarks'] = row[occurrence_field_list.index('GeoreferenceRemarks')]

    # Validate Collecting Method
    collecting_method = row[occurrence_field_list.index('CollectingMethod')]
    if collecting_method in ('Crawl Survey', 'dryscreen5mm', 'Dry Screen', 'Excavation', 'Survey',
                             'Transect Survey', 'Wet Screen', 'wetscreen1mm', None):
        row_dict['collecting_method'] = collecting_method
    else:
        print("Invalid Collecting Method %s for Occurrence %s" % (collecting_method, occurrence_id))
        return False

    # Validate Related Catalog Items
    row_dict['related_catalog_items'] = row[occurrence_field_list.index('RelatedCatalogItems')]

    # Validate Field Number
    row_dict['field_number'] = row[occurrence_field_list.index('FieldNumber')]

    # Validate Collector
    collector = row[occurrence_field_list.index('Collector')]
    if not collector or (collector in HRP_collector_list):
        row_dict['collector'] = collector
    else:
        print("Invalid Collector %s for Occurrence %s" % (collector, occurrence_id))
        return False

    # Validate Finder
    row_dict['finder'] = row[occurrence_field_list.index('Finder')]

    # Validate Disposition
    row_dict['disposition'] = row[occurrence_field_list.index('Disposition')]

    # Validate Collection Remarks
    row_dict['collection_remarks'] = row[occurrence_field_list.index('CollectionRemarks')]

    # Validate date_recorded. Check that entries are either Null, Date, or DateTime
    date_recorded = convert_date_recorded(row)
    row_dict['date_recorded'] = date_recorded

    # Validate year collected
    year_collected_string = row[occurrence_field_list.index('YearCollected')]
    year_collected = None
    try:
        year_collected = int(year_collected_string)  # try converting year collected from str to int
        if date_recorded and (int(date_recorded.year) != year_collected):
            print("Year collected %s does not match date_recorded %s for Occurrence %s" % (year_collected,
                                                                                           date_recorded, occurrence_id))
            return False
        if 1970 < year_collected <= datetime.datetime.now().year:
            row_dict['year_collected'] = year_collected
        else:
            print("Invalid year collected %s for Occurrence %s" % (year_collected, occurrence_id))
            return False
    except TypeError:  # Null raises TypeError
        if not year_collected_string:
            print("Warning year collected is Null for Occurrence %s" % occurrence_id)
        else:  # If not null something else bad is happening, print general error
            print("Invalid year collected %s for Occurrnce %s" % (year_collected, occurrence_id))
            return False
    except ValueError:  # If string such as fubar can't be convered raises ValueError
        print("Invalid year collected %s for Occurrence %s" % (year_collected, occurrence_id))
        return False

    # Validate Individual Count
    individual_count = None
    try:
        individual_count = row[occurrence_field_list.index('IndividualCount')]
        row_dict['individual_count'] = individual_count
    except TypeError:
        if not individual_count:
            row_dict['individual_count'] = None
        else:
            print("Invalid individual count %s for Occurrence %s" % (individual_count, occurrence_id))
            return False

    # Validate Preparation Status
    row_dict['preparation_status'] = row[occurrence_field_list.index('PreparationStatus')]

    # Validate stratigraphic information
    row_dict['stratigraphic_marker_upper'] = row[occurrence_field_list.index('StratigraphicMarkerUpper')]
    row_dict['distance_from_upper'] = row[occurrence_field_list.index('MetersFromUpper')]
    row_dict['stratigraphic_marker_lower'] = row[occurrence_field_list.index('StratigraphicMarkerLower')]
    row_dict['distance_from_lower'] = row[occurrence_field_list.index('MetersFromLower')]
    row_dict['stratigraphic_marker_found'] = row[occurrence_field_list.index('StratigraphicMarkerFound')]
    row_dict['distance_from_found'] = row[occurrence_field_list.index('DistanceFromFound')]
    row_dict['stratigraphic_marker_likely'] = row[occurrence_field_list.index('StratigraphicMarkerLikely')]
    row_dict['distance_from_likely'] = row[occurrence_field_list.index('DistanceFromLikely')]

    # Validate Stratigraphic Formation
    stratigraphic_formation = row[occurrence_field_list.index('StratigraphicFormation')]
    if (not stratigraphic_formation) or (stratigraphic_formation == ''):
        row_dict['stratigraphic_formation'] = None
    elif stratigraphic_formation in ('Hadar', 'Busidima', 'Hadar-Busidima'):
        row_dict['stratigraphic_formation'] = stratigraphic_formation
    else:
        print("Invalid stratigraphic formation %s for Occcurrence %s" % (stratigraphic_formation, occurrence_id))
        return False

    # Validate Stratigraphic Member
    stratigraphic_member = row[occurrence_field_list.index('StratigraphicMember')]
    if (not stratigraphic_member) or (stratigraphic_member in HRP_strat_member_list):
        row_dict['stratigraphic_member'] = stratigraphic_member
    else:
        print("Invalid stratigraphic member %s for Occcurrence %s" % (stratigraphic_member, occurrence_id))
        return False

    # Validate Analytical Unit
    row_dict['analytical_unit'] = row[occurrence_field_list.index('AnalyticalUnit1')]
    row_dict['analytical_unit_2'] = row[occurrence_field_list.index('AnalyticalUnit2')]
    row_dict['analytical_unit_3'] = row[occurrence_field_list.index('AnalyticalUnit3')]
    row_dict['analytical_unit_found'] = row[occurrence_field_list.index('AnalyticalUnitFound')]
    row_dict['analytical_unit_likely'] = row[occurrence_field_list.index('AnalyticalUnitLikely')]
    row_dict['analytical_unit_simplified'] = row[occurrence_field_list.index('AnalyticalUnitSimplified')]

    # Validate In Situ
    in_situ_float = row[occurrence_field_list.index('Insitu')]
    if in_situ_float in (None, -1.0, 0.0, 1.0):
        row_dict['in_situ'] = convert_in_situ(row)  # pass value to helper function
    else:
        print("Invalid in_situ %s for Occurrence %s" % (in_situ_float, occurrence_id))
        return False

    # Validate Ranked
    ranked_float = row[occurrence_field_list.index('RankedUnit')]
    if ranked_float in (None, -1.0, 0.0, 1.0):
        row_dict['ranked'] = convert_ranked(row)  # pass value to helper function
    else:
        print("Invalid ranked value %s for Occurrence %s" % (ranked_float, occurrence_id))
        return False

    # Validate Weathering
    weathering = row[occurrence_field_list.index('Weathering')]
    if (weathering is None) or (weathering <= 5):
        row_dict['weathering'] = weathering
    else:
        print("Invalid weathering %s for Occurrence %s" % (weathering, occurrence_id))
        return False

    # Validate Surface Modification
    row_dict['surface_modification'] = row[occurrence_field_list.index('SurfaceModification')]

    # Validate Problem
    problem_integer = row[occurrence_field_list.index('Problem')]
    if problem_integer in (None, 1, 0):
        row_dict['problem'] = convert_problem(row)
    else:
        print("Invalid problem %s for Occurrence %s" % (problem_integer, occurrence_id))
        return False

    # Validate Problem Comment
    row_dict['problem_comment'] = row[occurrence_field_list.index('ProblemComment')]

    # Validate barcode
    # Barcodes should exist for all Collected items and not for Observations
    barcode = row[occurrence_field_list.index('Barcode')]
    if basis_of_record == 'Collection':
        if not barcode:
            known_problem_tuple = (9900, 11307, 11310, 11311)
            if occurrence_id not in known_problem_tuple:  # ignore missing barcodes for known problems
                print("Missing barcode for Collection Occurrence %s" % occurrence_id)
                return False
            elif occurrence_id in known_problem_tuple:
                row_dict['barcode'] = None
        elif barcode:
            if len(barcode) != 6 or barcode in barcode_list:
                print("Invalid barcode length  or duplicate barcode %s for Occurrence %s" % (barcode, occurrence_id))
                return False
            elif barcode not in barcode_list:  # check that well formed barcodes are unique
                barcode_list.append(barcode)
                row_dict['barcode'] = barcode
    elif basis_of_record == 'Observation':
        if barcode:
            print("Invalid barcode present for Observation Occurrence %s" % occurrence_id)
            return False
        elif not barcode:
            row_dict['barcode'] = None

    # Validate Date Last Modified
    dlm = convert_date_last_modified(row)
    if not dlm:
        row_dict['date_last_modified'] = None

    elif dlm.year < 1970:
        print("Invalid date last modified %s for Occurrence %s" % (dlm, occurrence_id))
        return False
    else:
        row_dict['date_last_modified'] = dlm

    # Validate length of row dictionary
    if len(list(row_dict.keys())) != 49:
        print("Invalid row dictionary length %s for Occurrence %s" % (len(list(row_dict.keys())), occurrence_id))
        print(list(row_dict.keys()))
    return row_dict


# Biology validation function
def validate_biology(row, brow, pk):
    """
    Validate biology row data, convert data types where necessary and
    return a dictionary of cleaned, validated data.
    :param row:
    :return False or row_dict:
    """
    biology_row_dict = {}  # dictionary of row converted and clean row data

    # print brow
    if brow and len(brow) > 1:

        # Validate taxon
        taxon = get_matching_taxon(brow)
        if not taxon:
            name, rank = get_taxon_name_rank(brow)
            print("No matching taxon found, creating new {}: {}".format(rank, name))
            taxon = create_taxon(brow)
            biology_row_dict['taxon'] = taxon
        else:
            #print "Found matching taxon: ",
            #print taxon
            biology_row_dict['taxon'] = taxon
        # Save original taxon names in color separated string, e.g. 'Animalia:Chrodata:Mammalia:Primates:::Homo:sapeins'
        biology_row_dict['verbatim_taxon'] = get_verbatim_taxon_list(brow)

        # Validate Identification Qualifier
        idq_string = brow[biology_field_list.index('IdentificationQualifier')]
        biology_row_dict['verbatim_identification_qualifier'] = idq_string  # preserve a copy of original idq
        taxon = biology_row_dict['taxon']
        # Exception handling in case Taxonomy Tables not populated
        try:
            cf_obj = IdentificationQualifier.objects.get(name='cf.')
        except ObjectDoesNotExist:
            cf_obj = IdentificationQualifier.objects.create(name='cf.', qualified='True')
        try:
            aff_obj = IdentificationQualifier.objects.get(name='aff.')
        except ObjectDoesNotExist:
            aff_obj = IdentificationQualifier.objects.create(name='aff', qualified='True')
        try:
            sp_nov_obj = IdentificationQualifier.objects.get(name='sp. nov.')
        except ObjectDoesNotExist:
            sp_nov_obj = IdentificationQualifier.objects.create(name='sp. nov.', qualified='True')

        if idq_string is None:
            biology_row_dict['identification_qualifier'] = None
            biology_row_dict['qualifier_taxon'] = None

        # ex ? => cf.
        elif idq_string in ('?', 'cf.'):
            biology_row_dict['identification_qualifier'] = cf_obj
            biology_row_dict['qualifier_taxon'] = taxon  # cf. defaults to lowest id taxon

        # ex aff. => aff.
        elif idq_string == 'aff.':  # if idq_string starts with aff. alone
            biology_row_dict['identification_qualifier'] = aff_obj
            biology_row_dict['qualifier_taxon'] = taxon

        # ex ?Australopithecus => cf. Australopithecus
        elif re.match(r'\?\w+', idq_string):  # if idq_string starts with question mark
            biology_row_dict['identification_qualifier'] = cf_obj
            taxon_name_string = idq_string[1:]  # strip of leading question mark
            biology_row_dict['qualifier_taxon'] = get_qualifier_taxon(taxon, taxon_name_string)

        # ex cf. Australopithecus => cf. Australopithecus
        elif re.match(r'cf\. \w+', idq_string):  # if idq_string starts with cf followed by text
            biology_row_dict['identification_qualifier'] = cf_obj
            taxon_name_string = idq_string[4:]  # strip off leading 'cf. '
            biology_row_dict['qualifier_taxon'] = get_qualifier_taxon(taxon, taxon_name_string)

        # ex aff. Australopithecus => aff. Australopithecus
        elif re.match(r'aff\. \w+', idq_string):  # if idq_string starts with aff. followed by text
            biology_row_dict['identification_qualifier'] = aff_obj
            taxon_name_string = idq_string[5:]  # strip off leading 'aff. '
            biology_row_dict['qualifier_taxon'] = get_qualifier_taxon(taxon, taxon_name_string)

        # ex sp. => None
        elif idq_string in ['sp.', 'Damalborea sp.', 'indet.', 'sp. Indet']:  # of idq_string is other special case
            biology_row_dict['identification_qualifier'] = None
            biology_row_dict['qualifier_taxon'] = None

        # ex sp. nov. => sp. nov.
        elif idq_string == 'sp. nov.':
            biology_row_dict['identification_qualifier'] = sp_nov_obj
            biology_row_dict['qualifier_taxon'] = biology_row_dict['taxon']

        # ex sp. A => sp. nov.
        elif re.match(r'sp. +', idq_string):
            biology_row_dict['identification_qualifier'] = sp_nov_obj
            taxon_name_string = idq_string[4:]
            try:
                taxon = Taxon.objects.get(name=taxon_name_string)
            except ObjectDoesNotExist:
                taxon_string = idq_string[4:]
                taxon = Taxon.objects.create(name=taxon_string, parent=None, rank=TaxonRank.objects.get(name='Species'))
            biology_row_dict['qualifier_taxon'] = taxon

        else:
            print("Unable to validate identification qualifier {}".format(idq_string))
            return False


        # Validate identified by
        biology_row_dict['identified_by'] = brow[biology_field_list.index('IdentifiedBy')]

        # Validate year identified
        year_identified_string = brow[biology_field_list.index('DateIdentified')]
        if year_identified_string:
            year_identified = int(year_identified_string)
            if 1900 < year_identified < 2017:
                biology_row_dict['year_identified'] = int(year_identified_string)
            else:
                print("Invalid year identified for Biology Occurrence {}".format(pk))
                return False
        else:
            biology_row_dict['year_identified'] = None

        # Validate type status
        biology_row_dict['type_status'] = brow[biology_field_list.index('TypeStatus')]

        # Validate taxonomy remarks
        biology_row_dict['taxonomy_remarks'] = brow[biology_field_list.index('TaxonomyRemarks')]

        # Validate element
        element = brow[biology_field_list.index('Element')]
        if (not element) or (element in element_list):
            biology_row_dict['element'] = element
        else:
            print("Invalid element entry {} for biology occurrence {}".format(element, pk))
            return False

        # Validate element portion
        biology_row_dict['element_portion'] = brow[biology_field_list.index('ElementPortion')]

        # Validate Side
        biology_row_dict['side'] = brow[biology_field_list.index(('Side'))]

        # Validate element number
        biology_row_dict['element_number'] = brow[biology_field_list.index('ElementNumber')]

        # Validate element qualifier
        biology_row_dict['element_qualifier'] = brow[biology_field_list.index('ElementQualifier')]

        # Validate size class
        biology_row_dict['size_class'] = brow[biology_field_list.index('SizeClass')]

        # Validate life stage
        biology_row_dict['life_stage'] = brow[biology_field_list.index('LifeStage')]

        # Validate element remarks
        biology_row_dict['element_remarks'] = brow[biology_field_list.index('ElementRemarks')]

        # Validate bioloy remarks
        biology_row_dict['biology_remarks'] = brow[biology_field_list.index('BiologyRemarks')]

        return biology_row_dict

    else:
        print("No matching record found in Biology table for Occurrence {}".format(pk))
        return False


def get_locality(row_dict):
    """
    Fetch the corresponding locality object for an occurrence and create a new one if necessary.
    :param row:
    :return locality_object:
    """

    # Validate and build locality text
    basis_of_record = row_dict['basis_of_record']
    collection_code = row_dict['collection_code']
    locality_number = row_dict['locality_number']
    sublocality = row_dict['sublocality']
    geom = row_dict['geom']
    locality_text = ''

    if basis_of_record == 'Collection':
        if locality_number:
            if sublocality and sublocality != '':
                locality_text = str(int(locality_number)) + sublocality
            else:
                locality_text = str(int(locality_number))

        # Check if Locality exists
        try:
            locality = Locality.objects.get(pk=locality_text)
            return locality
        except ObjectDoesNotExist:
            # If not create a new one and return it
            locality = Locality(id=locality_text,
                                collection_code=collection_code,
                                locality_number=locality_number,
                                sublocality=sublocality,
                                date_last_modified=datetime.datetime.now(),
                                geom=geom)

            locality.save()
            return locality


# Import Functions
# Delete me
def import_collection(row_dict, locality):
    new_occurrence = Occurrence(id=row_dict['occurrence_id'],
                                geom=row_dict['geom'],
                                basis_of_record=row_dict['basis_of_record'],
                                item_type=row_dict['item_type'],
                                collection_code=row_dict['collection_code'],
                                locality=locality,
                                item_number=row_dict['item_number'],
                                item_part=row_dict['item_part'],
                                # catalog_number=row_dict['catalog_number'],
                                remarks=row_dict['remarks'],
                                item_scientific_name=row_dict['item_scientific_name'],
                                item_description=row_dict['item_description'],
                                drainage_region=row_dict['drainage_region'],
                                georeference_remarks=row_dict['georeference_remarks'],
                                collecting_method=row_dict['collecting_method'],
                                related_catalog_items=row_dict['related_catalog_items'],
                                field_number=row_dict['field_number'],
                                collector=row_dict['collector'],
                                finder=row_dict['finder'],
                                disposition=row_dict['disposition'],
                                collection_remarks=row_dict['collection_remarks'],
                                date_recorded=row_dict['date_recorded'],
                                year_collected=row_dict['year_collected'],
                                individual_count=row_dict['individual_count'],
                                preparation_status=row_dict['preparation_status'],
                                analytical_unit=row_dict['analytical_unit'],
                                analytical_unit_2=row_dict['analytical_unit_2'],
                                analytical_unit_3=row_dict['analytical_unit_3'],
                                analytical_unit_found=row_dict['analytical_unit_found'],
                                analytical_unit_likely=row_dict['analytical_unit_likely'],
                                analytical_unit_simplified=row_dict['analytical_unit_simplified'],
                                in_situ=row_dict['in_situ'],
                                ranked=row_dict['ranked'],
                                weathering=row_dict['weathering'],
                                surface_modification=row_dict['surface_modification'],
                                problem=row_dict['problem'],
                                problem_comment=row_dict['problem_comment'],
                                barcode=row_dict['barcode'],
                                date_last_modified=row_dict['date_last_modified'],
                                )
    return new_occurrence


def import_biology_collection(row_dict, bio_dict, locality):
    new_bio_occurrence = Biology(id=row_dict['occurrence_id'])
    for f in new_bio_occurrence.get_all_field_names():
        if f in row_dict:
            setattr(new_bio_occurrence, f, row_dict[f])
        elif f in bio_dict:
            setattr(new_bio_occurrence, f, bio_dict[f])
    new_bio_occurrence.locality = locality
    return new_bio_occurrence


def import_archaeology_collection(row_dict, locality):
    new_arch_occurrence = Archaeology(id=row_dict['occurrence_id'])
    for f in new_arch_occurrence.get_all_field_names():
        if f in row_dict:
            setattr(new_arch_occurrence, f, row_dict[f])
    new_arch_occurrence.locality = locality
    return new_arch_occurrence


def import_geology_collection(row_dict, locality):
    new_geo_occurrence = Geology(id=row_dict['occurrence_id'])
    for f in new_geo_occurrence.get_all_field_names():
        if f in row_dict:
            setattr(new_geo_occurrence, f, row_dict[f])
    new_geo_occurrence.locality = locality
    return new_geo_occurrence


def import_observation(row_dict):
    new_occurrence = Occurrence(id=row_dict['occurrence_id'],
                                geom=row_dict['geom'],
                                basis_of_record=row_dict['basis_of_record'],
                                item_type=row_dict['item_type'],
                                # collection_code=row_dict['collection_code'],
                                # locality=locality,
                                # item_number=row_dict['item_number'],
                                # item_part=row_dict['item_part'],
                                # catalog_number=row_dict['catalog_number'],
                                remarks=row_dict['remarks'],
                                item_scientific_name=row_dict['item_scientific_name'],
                                item_description=row_dict['item_description'],
                                drainage_region=row_dict['drainage_region'],
                                georeference_remarks=row_dict['georeference_remarks'],
                                collecting_method=row_dict['collecting_method'],
                                related_catalog_items=row_dict['related_catalog_items'],
                                field_number=row_dict['field_number'],
                                collector=row_dict['collector'],
                                finder=row_dict['finder'],
                                disposition=row_dict['disposition'],
                                collection_remarks=row_dict['collection_remarks'],
                                date_recorded=row_dict['date_recorded'],
                                year_collected=row_dict['year_collected'],
                                individual_count=row_dict['individual_count'],
                                preparation_status=row_dict['preparation_status'],
                                analytical_unit=row_dict['analytical_unit'],
                                analytical_unit_2=row_dict['analytical_unit_2'],
                                analytical_unit_3=row_dict['analytical_unit_3'],
                                analytical_unit_found=row_dict['analytical_unit_found'],
                                analytical_unit_likely=row_dict['analytical_unit_likely'],
                                analytical_unit_simplified=row_dict['analytical_unit_simplified'],
                                in_situ=row_dict['in_situ'],
                                ranked=row_dict['ranked'],
                                weathering=row_dict['weathering'],
                                surface_modification=row_dict['surface_modification'],
                                problem=row_dict['problem'],
                                problem_comment=row_dict['problem_comment'],
                                barcode=row_dict['barcode'],
                                date_last_modified=row_dict['date_last_modified'],
                                )

    # new_occurrence.save()
    return new_occurrence


def import_biology_observation(row_dict, bio_dict):
    new_bio_occurrence = Biology(id=row_dict['occurrence_id'])
    for f in new_bio_occurrence.get_all_field_names():
        if f in row_dict:
            setattr(new_bio_occurrence, f, row_dict[f])
        elif f in bio_dict:
            setattr(new_bio_occurrence, f, bio_dict[f])
    return new_bio_occurrence


def import_archaeology_observation(row_dict):
    new_arch_occurrence = Archaeology(id=row_dict['occurrence_id'])
    for f in new_arch_occurrence.get_all_field_names():
        if f in row_dict:
            setattr(new_arch_occurrence, f, row_dict[f])
    return new_arch_occurrence


def import_geology_observation(row_dict):
    new_geo_occurrence = Geology(id=row_dict['occurrence_id'])
    for f in new_geo_occurrence.get_all_field_names():
        if f in row_dict:
            setattr(new_geo_occurrence, f, row_dict[f])
    return new_geo_occurrence


def validate_new_record(occurrence_object, row):
    if occurrence_object.id != int(row[occurrence_field_list.index('CatalogNumberNumeric')]):
        print("Problem importing id for Occurrence %s" % occurrence_object.id)
        return False
    if occurrence_object.basis_of_record != row[occurrence_field_list.index('BasisOfRecord')]:
        print("Problem importing basis of record %s for Occurrence %s" % \
              (occurrence_object.basis_of_record,
               occurrence_object.id))
        return False
    if occurrence_object.item_type != row[occurrence_field_list.index('ItemType')]:
        print("Problem importing item type %s for Occurrence %s" % \
              (occurrence_object.basis_of_record, occurrence_object.id))
        return False
    if occurrence_object.collection_code != row[occurrence_field_list.index('CollectionCode')]:
        print("Problem importing collection code %s for Occurrence %s" % \
              (occurrence_object.collection_code, occurrence_object.id))
        return False
    if occurrence_object.catalog_number() != row[occurrence_field_list.index('CatalogNumber')]:
        print("Catalog Number %s does not match CatalogNumber %s for Occurrence %s" % \
              (occurrence_object.catalog_number(), row[occurrence_field_list.index('CatalogNumber')], occurrence_object.id))
        return False
    if occurrence_object.item_scientific_name != row[occurrence_field_list.index('ItemScientificName')]:
        print("Item scientific name %s does not match ItemScientificName %s for Occurrence %s" % \
              (occurrence_object.item_scientific_name, row[occurrence_field_list.index('ItemScientificName')],
               occurrence_object.id))
        return False
    if occurrence_object.item_description != row[occurrence_field_list.index('ItemDescription')]:
        print("Item description %s does not match ItemDescription %s for Occurrence %s" % \
              (occurrence_object.item_description, row[occurrence_field_list.index('ItemDescription')], occurrence_object.id))
        return False
    if occurrence_object.collecting_method != row[occurrence_field_list.index('CollectingMethod')]:
        print("Collecting method %s does not match CollectingMethod %s for Occurrence %s" % \
              (occurrence_object.collecting_method, row[occurrence_field_list.index('CollectingMethod')], occurrence_object.id))
        return False
    if occurrence_object.collector != row[occurrence_field_list.index('Collector')]:
        print("Collector %s does not match Collector %s for Occurrence %s" % \
              (occurrence_object.collector, row[occurrence_field_list.index('Collector')], occurrence_object.id))
        return False
    if int(occurrence_object.year_collected) != int(row[occurrence_field_list.index('YearCollected')]):
        print("Year collected %s does not match YearCollected %s for Occurrence %s" % \
              (occurrence_object.year_collected, row[occurrence_field_list.index('YearCollected')], occurrence_object.id))
        return False
    if occurrence_object.analytical_unit != row[occurrence_field_list.index('AnalyticalUnit1')]:
        print("Analytical Unit %s does not match AnalyticalUnit1 %s for Occurrence %s" % \
              (occurrence_object.analytical_unit, row[occurrence_field_list.index('AnalyticalUnit1')], occurrence_object.id))
        return False
    if occurrence_object.barcode != row[occurrence_field_list.index('Barcode')]:
        print("Barcode %s does not match Barcode %s for Occurrence %s" % \
              (occurrence_object.barcode, row[occurrence_field_list.index('Barcode')], occurrence_object.id))
        return False
    else:
        return True


def validate_new_biology(biology_object, brow):
    if len(biology_object.verbatim_taxon) < 1:
        print("Verbatim Taxon too short")
        return False
    if not biology_object.taxon:
        print("Missing taxon")
        return False
    if biology_object.verbatim_identification_qualifier != brow[biology_field_list.index('IdentificationQualifier')]:
        vidq = biology_object.vertbatim_identification_qualifier
        idq = brow[biology_field_list.index('IdentificationQualifier')]
        print("Verbatim identification qualifier {} does not match IdentificationQualifer {}".format(vidq, idq))
    return True


def main():
    import_count, collection_count, observation_count, row_count, ac, bc, gc, ao, bo, go = [0] * 10
    print("Record limit is set to: %s\n" % record_limit)
    print("Processing records\n\n", end=' ')

    occurrence_recordset = occurrence_cursor.execute('SELECT * FROM Occurrence WHERE ProjectCode = "HRP" LIMIT ?',
                                                     record_limit)
    for row in occurrence_recordset:

        row_count += 1
        #print "Processing record %s" % row_count
        #print row

        # Validate the Occurrence data for the row
        #print "Validating row data ...",
        valid_row_dict = validate_row(row)

        if valid_row_dict:
            #print "valid"
            pk = valid_row_dict['occurrence_id']
            basis_of_record = valid_row_dict['basis_of_record']
            item_type = valid_row_dict['item_type']
            import_count += 1

            # Biology Collection
            if basis_of_record == 'Collection' and item_type in ('Faunal', 'Floral'):
                #print "Processing Biology Collection for occurrence %s" % pk
                brow = biology_cursor.execute('SELECT * FROM Biology WHERE CatalogNumberNumeric = ?',
                                              (str(pk),)).fetchone()
                bc += 1
                locality = get_locality(valid_row_dict)
                valid_biology_dict = validate_biology(row, brow, pk)
                new_bio = import_biology_collection(valid_row_dict, valid_biology_dict, locality)
                collection_count += 1
                if validate_new_record(new_bio, row) and validate_new_biology(new_bio, brow):
                    new_bio.save()

            # Archaeology Collection
            elif basis_of_record == 'Collection' and item_type == 'Artifactual':
                #print "Processing Archaeology Collection for Occurrence {}".format(pk)
                ac += 1
                locality = get_locality(valid_row_dict)
                new_arch = import_archaeology_collection(valid_row_dict, locality)
                collection_count += 1
                if validate_new_record(new_arch, row):
                    new_arch.save()

            # Geology Collection
            elif basis_of_record == 'Collection' and item_type == 'Geological':
                #print "Processing Geological Collection for Occurrence {}".format(pk)
                gc += 1
                collection_count += 1
                locality = get_locality(valid_row_dict)
                new_geo = import_geology_collection(valid_row_dict, locality)
                collection_count += 1
                if validate_new_record(new_geo, row):
                    new_geo.save()

            # Biology Observation
            elif basis_of_record == 'Observation' and item_type in ('Faunal', 'Floral'):
                #print "Processing Biology Observation for Occurrence %s" % pk
                brow = biology_cursor.execute('SELECT * FROM Biology WHERE CatalogNumberNumeric = ?',
                                              (str(pk),)).fetchone()
                bo += 1
                observation_count += 1
                valid_biology_dict = validate_biology(row, brow, pk)
                new_bio = import_biology_observation(valid_row_dict, valid_biology_dict)
                if validate_new_record(new_bio, row) and validate_new_biology(new_bio, brow):
                    new_bio.save()

            # Archaeology Observation
            elif basis_of_record == 'Observation' and item_type == 'Artifactual':
                #print "Processing Archaeology Observation for Occurrence %s" % pk
                ao += 1
                observation_count += 1
                new_arch = import_archaeology_observation(valid_row_dict)
                if validate_new_record(new_arch, row):
                    new_arch.save()

            # Geology Observation
            elif basis_of_record == 'Observation' and item_type == 'Geological':
                #print "Processing Geological Observation for Occurrence %s" % pk
                go += 1
                observation_count += 1
                new_geo = import_geology_observation(valid_row_dict)
                if validate_new_record(new_geo, row):
                    new_geo.save()

        if row_count in range(500, 10000, 500):
            print('.', end=' ')
    print("Number of rows processed: %s \nNumber of records imported: %s" % (row_count, import_count))
    print("Imported %s collections and %s observations" % (collection_count, observation_count))
    print("Processed %s biology, %s archaeology and %s geology collections" % (bc, ac, gc))
    print("Processed %s biology, %s archaeology and %s geology observations" % (bo, ao, go))

# Create a connection to the SQLite DB with HRP data

# Open a connection to the local sqlite database
print("Opening connection to %s" % hrpdb_path)
connection = sqlite3.connect(hrpdb_path)
occurrence_cursor = connection.cursor()  # cursor for reading data in the occurrence table
biology_cursor = connection.cursor()  # cursor for reading data in the biology table

# Fetch data from the database
rs = occurrence_cursor.execute('SELECT * FROM Occurrence WHERE ProjectCode = "HRP";')
record_count = len(rs.fetchall())
print("Database has a total of %s records" % record_count)

main()

connection.close()
