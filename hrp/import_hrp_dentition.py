__author__ = 'reedd'
"""
This loader/importer script is designed to read data from a sqlite database storing the Hadar Research Project (HRP)
data, and load those data into the PaleoCore postgres database. It assumes that the occurrence and biology table data
has already been imported. This script reads in the data form the dentition table and adds it to the appropriate
Biology occurrences.

The script:
1)
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

# absolute file path to the HRP sqlite database from whihc we are reading data
hrpdb_path = '/Users/reedd/Documents/projects/PaleoCore/projects/HRP/HRP_Paleobase4_2016.sqlite'
record_limit = ('20000',)  # a limiter setting the maximum number of records to be read from the database, for debugging
# list of fields as they occur in the HRP sqlite database dentition table. The list is used to correctly find
# specific data read in from each row of the occurrence table.
dentition_field_list = ['FaunaAttrbutesID', 'CatalogNumberNumeric', 'CatalogNumberNumberic_OLD', 'Maxilla', 'Mandible',
                     'uli1', 'uli2', 'uli3', 'uri1', 'uri2', 'uri3', 'ulc', 'urc', 'ulp1', 'ulp2', 'ulp3', 'ulp4',
                     'urp1', 'urp2', 'urp3', 'urp4', 'ulm1', 'ulm2', 'ulm3', 'ulm4', 'urm1', 'urm2', 'urm3', 'urm4',
                     'lli1', 'lli2', 'lli3', 'lri1', 'lri2', 'lri3', 'llc', 'lrc', 'llp1', 'llp2', 'llp3', 'llp4',
                     'lrp1', 'lrp2', 'lrp3', 'lrp4', 'llm1', 'llm2', 'llm3', 'llm4', 'lrm1', 'lrm2', 'lrm3', 'lrm4',
                     'indet_incisor', 'indet_canine', 'indet_premolar', 'indet_molar',
                     'indet_Tooth', 'deciduous']

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


def get_dentition_row(obj):
    pk_string = str(obj.id)
    return dentition_cursor.execute('SELECT * FROM dentition WHERE CatalogNumberNumeric = ?', (pk_string,)).fetchone()


def valid_dentition(row):
    if row:  # if there is row data, many will be None
        # perhaps validate dentition data against element data in biology table.
        # if upper teeth only, element = maxilla
        # if lower teeth only, element = mandible
        # if both element is max+man
        return True
    else:
        return None


def add_dentition_data(row, obj):
    obj_field_list = obj.get_all_field_names()
    for f in dentition_field_list:
        if f in obj_field_list:
            if row[dentition_field_list.index(f)]:
                fval = True
            else:
                fval = False
            setattr(obj, f, fval)
    return obj


def main():
    import_count, collection_count, observation_count, row_count, ac, bc, gc, ao, bo, go = [0] * 10
    print("Record limit is set to: %s\n" % record_limit)
    print("Processing records\n\n", end=' ')

    # Fetch all Biology occurrences
    biology_objects_rs = Biology.objects.all()

    for obj in biology_objects_rs:
        # fetch related row from dentition
        dentition_row = get_dentition_row(obj)
        #print dentition_row

        # validate data in the row
        if valid_dentition(dentition_row):
            # add data to object
            updated_obj = add_dentition_data(dentition_row, obj)
        # save object
        #     print obj.id, obj.element, obj.uli1, obj.uli2, obj.uli3, obj.uli4, obj.uli5, obj.uri1, obj.uri2, obj.uri3, obj.uri4, \
        #     obj.ulc, obj.urc, obj.ulp1, obj.ulp2, obj.ulp3, obj.ulp4, obj.urp1, obj.urp2, obj.urp3, obj.urp4, \
        #     obj.ulm1, obj.ulm2, obj.ulm3, obj.urm1, obj.urm2, obj.urm3
            updated_obj.save()
        # print report
            import_count += 1
    print("Completed update of {} biological occurrences".format(import_count))

# Open a connection to the local sqlite database
print("Opening connection to %s" % hrpdb_path)
connection = sqlite3.connect(hrpdb_path)  # open a connection to the HRP sqlite database
dentition_cursor = connection.cursor()  # cursor for reading data in the dentition table

main()  # process data in the sqlite database

connection.close()  # close the connection
