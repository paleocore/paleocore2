__author__ = 'reedd'

from .models import Occurrence, Archaeology, Biology, Geology, Taxon, IdentificationQualifier
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
import collections

import re
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
import calendar
from datetime import datetime
import mlp.ontologies


image_folder_path = "/Users/reedd/Documents/projects/PaleoCore/projects/Omo Mursi/Final_Import/omo_mursi_data/omo_mursi_data/"


def duplicate_barcodes():
    all_occurrences = Occurrence.objects.filter(basis_of_record='FossilSpecimen')
    barcode_list = []
    duplicate_list = []
    for item in all_occurrences:
        try:
            barcode_list.append(item.barcode)
        except:
            print("Error")
    for item, count in list(collections.Counter(barcode_list).items()):
                if count > 1:
                    duplicate_list.append(item)
    return duplicate_list


def report_duplicates():
    dups = duplicate_barcodes()
    for d in dups:
        if d:
            occs = Occurrence.objects.filter(barcode=d)
            for o in occs:
                print_string = "id:{} barcode:{} item_type:{} basis:{} collector:{}".format(
                    o.id, o.barcode, o.item_type, o.basis_of_record, o.collector
                )
                print(print_string)


def missing_barcodes():
    occurrences = Occurrence.objects.filter(basis_of_record='FossilSpecimen')
    missing_list = []


def find_mlp_duplicate_biological_barcodes():
    all_mlp_collected_bio_occurrences = Occurrence.objects.filter(item_type__exact="Faunal").filter(basis_of_record__exact="FossilSpecimen")
    barcode_list = []
    duplicate_list = []
    for item in all_mlp_collected_bio_occurrences:
        try:
            barcode_list.append(item.barcode)
        except:
            print("Error")
    for item, count in list(collections.Counter(barcode_list).items()):
                if count > 1:
                    duplicate_list.append(item)
    return duplicate_list


def find_mlp_duplicate_biological_catalog_numbers():
    all_mlp_collected_bio_occurrences = Occurrence.objects.filter(item_type__exact="Faunal").filter(basis_of_record__exact="FossilSpecimen")
    catalog_list = []
    duplicate_list = []
    for item in all_mlp_collected_bio_occurrences:
        try:
            catalog_list.append(item.catalog_number)
        except:
            print("Error")
    for item, count in list(collections.Counter(catalog_list).items()):
                if count > 1:
                    duplicate_list.append(item)
    return duplicate_list


def find_mlp_missing_coordinates():
    all_mlp_occurrences = Occurrence.objects.all()
    missing_coordinates_id_list=[]
    for o in all_mlp_occurrences:
        try: o.geom.x
        except AttributeError:
            missing_coordinates_id_list.append(o.id)
    return missing_coordinates_id_list


# def update_mlp_bio(updatelist=update_tuple_list):
#     for o in updatelist:  # iterate through record tuples in list
#         cat, tax, des = o  # unpack tuple values
#         #print cat+" "+tax+" "+des  # do something with them
#
#         try:
#             occurrence = Occurrence.objects.get(catalog_number=cat)  # fetch the object with the catalog number
#             occurrence.item_scientific_name = tax  # update item scientific name
#             occurrence.item_description = des  # update item_description
#             occurrence.save()  # save updates
#         except ObjectDoesNotExist:  # handle if object is not found or is duplicate returning more than 1 match
#             print("Does Not Exist or Duplicate:"+cat)


def split_scientific_name(scientific_name):
    # split colon delimited string into list e.g. Rodentia:Muridae to ['Rodentia', 'Muridae']
    clean_name = scientific_name.strip()
    taxon_name_list = re.split('\s|:|_|,', clean_name)  # split using space, colon, underscore or comma delimeters
    taxon_name_list = [i for i in taxon_name_list if i != '']  # remove empty string resulting from extra spaces
    return clean_name, taxon_name_list


def get_identification_qualifier_from_scientific_name(scientific_name):
    clean_name, taxon_name_list = split_scientific_name(scientific_name)
    id_qual_name_list = [i.name for i in IdentificationQualifier.objects.all()]  # list of all IdQal names
    id_qual_name = [val for val in taxon_name_list if val in id_qual_name_list]  # get id_qual from taxon name list
    return IdentificationQualifier.objects.get(name__exact=id_qual_name)


def get_identification_qualifier_from_string(id_qual_string):
    """
    Function to get the id qualifier based on a string value.  Returning None as default is the wrong option here. If
    no match is found need to raise an error.
    :param id_qual_string:
    :return:
    """
    if id_qual_string in ['', ' ', None]:
        return None
    elif id_qual_string in ['cf.', 'cf', 'c.f.']:
        return IdentificationQualifier.objects.get(name='cf.')  # some fault tolerance for punctuation
    elif id_qual_string in ['aff.', 'aff', 'a.f.f.']:
        return IdentificationQualifier.objects.get(name='aff.')
    else:
        return IdentificationQualifier.objects.get(name=id_qual_string)  # last change to match novel idq
    # If no match is found ObjectDoesNotExist error is raised.


def get_taxon_from_scientific_name(scientific_name):
    """
    Function retrieves a taxon object from a colon delimited item_scientific_name string
    :param scientific_name: colon delimited item_scientific_name string, e.g. 'Rodentia:Muridae:Golunda gurai'
    :return: returns a taxon object.
    """
    clean_name, taxon_name_list = split_scientific_name(scientific_name)
    taxon_name_list_length = len(taxon_name_list)
    taxon = Taxon.objects.get(name__exact='Life')  # default taxon
    id_qual_names = [i.name for i in IdentificationQualifier.objects.all()]  # get list of id qualifier names
    # If there is no scientific name, the taxon name list will be empty and default, 'Life' will be returned
    if taxon_name_list_length >= 1:  # if there is a scientific name...
        taxon_string = taxon_name_list[-1]  # get the last element
        try:
            # This method of getting the taxon risks matching the wrong species name
            # If the taxonomy table only inlcudes Mammalia:Suidae:Kolpochoeris afarensis
            # trying to match Mammalia:Primates:Australopithecus afarensis will succeed in error
            taxon = Taxon.objects.get(name__exact=taxon_string)
        except MultipleObjectsReturned:  # if multiple taxa match a species name
            index = -2
            parent_name = taxon_name_list[index]  # get the next name in the list
            while parent_name in id_qual_names:  # if the name is an id qualifier ignore it and advance to next item
                index -=1
                parent_name = taxon_name_list[index]  # get first parent item in list that is not an id qualifier
            parent = Taxon.objects.get(name__exact=parent_name)  # find the matching parent object
            taxon = Taxon.objects.filter(name__exact=taxon_string).filter(parent=parent)[0]
        except ObjectDoesNotExist:
            print("No taxon found to match {}".format(taxon_string))
    return taxon


# def test_get_taxon_from_scientific_name(test_list=id_test_list):
#     count=0
#     for i in test_list:
#         try:
#             taxon = get_taxon_from_scientific_name(i)
#             #print '{}, {} = {}'.format(count, i, taxon)
#         except ObjectDoesNotExist:
#             print('{}, {} = {}'.format(count, i, "Does Not Exist"))
#         except MultipleObjectsReturned:
#             '{}, {} = {}'.format(count, i, 'Multiple Objects Returned')
#         count+=1


def mlp_missing_biology_occurrences():
    """
    Function to identify occurrences that should also be biology but are missing from biology table
    :return: returns a list of occurrence object ids.
    """
    result_list = []  # Initialize result list
    # Biology occurrences should be all occurrences that are item_type "Faunal" or "Floral"
    biology_occurrences = Occurrence.objects.filter(item_type__in=['Faunal', 'Floral'])
    for occurrence in biology_occurrences:
        try: Biology.objects.get(occurrence_ptr_id__exact=occurrence.id)  # Find matching occurrence in bio
        except ObjectDoesNotExist:
            result_list.append(occurrence.id)
    return result_list


def occurrence2biology(oi):
    """
    Procedure to convert an Occurrence instance to a Biology instance. The new Biology instance is given a default
    taxon = Life, and identification qualifier = None.
    :param oi: occurrence instance
    :return: returns nothing.
    """

    if oi.item_type in ['Faunal', 'Floral']:  # convert only faunal or floral items to Biology
        # Initiate variables
        # taxon = get_taxon_from_scientific_name(oi.item_scientific_name)
        taxon = Taxon.objects.get(name__exact='Life')
        id_qual = IdentificationQualifier.objects.get(name__exact='None')
        # Create a new biology object
        new_biology = Biology(barcode=oi.barcode,
                                 item_type=oi.item_type,
                                 basis_of_record=oi.basis_of_record,
                                 collecting_method=oi.collecting_method,
                                 field_number=oi.field_number,
                                 taxon=taxon,
                                 identification_qualifier=id_qual,
                                 geom=oi.geom
                                 )
        for key in list(oi.__dict__.keys()):
            new_biology.__dict__[key]=oi.__dict__[key]

        oi.delete()
        new_biology.save()


def occurrence2archaeology(oi):
    """
    Procedure to convert an Occurrence instance to an Archaeology instance.
    :param oi: occurrence instance
    :return: returns nothing
    """
    if oi.item_type in ['Artifactual']:  # convert only artifactual items to archaeology
        # Create a new archaeology object
        new_archaeology = Archaeology(barcode=oi.barcode,
                                 item_type=oi.item_type,
                                 basis_of_record=oi.basis_of_record,
                                 collecting_method=oi.collecting_method,
                                 field_number=oi.field_number,
                                 geom=oi.geom
                                 )
        for key in list(oi.__dict__.keys()):
            new_archaeology.__dict__[key]=oi.__dict__[key]

        new_archaeology.save()
        #oi.delete()


def find2geo(oi):
    """
    Procedure to convert a Find (formerly Occurrence) to a Geology subclass.
    :param oi: occurrence in stance
    :return:
    """
    if oi.item_type in ['Geological']:  # convert only geological items to Geology subclass
        # Create a new Geology object
        print("Creating a new geo object for pk {}".format(oi.id))
        new_geo = Geology(barcode=oi.barcode,
                          geom=oi.geom)
        print("Copying data")
        for key in list(oi.__dict__.keys()):
            new_geo.__dict__[key]=oi.__dict__[key]
        print("Saving")
        new_geo.save()


def get_finds():
    """
    Get Finds that are not subclassses, e.g. Find but not Biology
    :return: Returns a queryset of Find objects
    """
    all_find_ids = {f.id for f in Occurrence.objects.all()}
    subclass_ids = {f.occurrence_ptr_id for f in Biology.objects.all()} | \
                   {f.occurrence_ptr_id for f in Archaeology.objects.all()} | \
                   {f.occurrence_ptr_id for f in Geology.objects.all()}
    find_ids = all_find_ids.difference(subclass_ids)
    # return list(find_ids)
    return Occurrence.objects.filter(id__in=find_ids)


def subtype_finds():
    untyped_finds = get_finds()
    for f in untyped_finds:
        if f.item_type in ['Faunal', 'Floral'] and f.item_scientific_name!='No Fossils At This Location':
            occurrence2biology(f)
        elif f.item_type in ['Archaeological', 'Artifactual']:
            occurrence2archaeology(f)
        elif f.item_type in ['Geological']:
            find2geo(f)
        else:
            pass



def update_occurrence2biology():
    mlp_fossils = Occurrence.objects.filter(item_type__in=["Faunal", "Floral"])
    print('Processing {} Occurrence records'.format(mlp_fossils.count()))
    count = 0
    existing = []
    converted = []
    for f in mlp_fossils:
        try:
            Biology.objects.get(pk=f.id)
            # print "{}. Occurence {} barcode: {} is already a Biology object.".format(count, f.id, f.barcode)
            existing.append(f.id)
        except ObjectDoesNotExist:
            print("{}. Converting Occurrence id: {} barcode: {} to Biology.".format(count, f.id, f.barcode))
            occurrence2biology(f)
            converted.append(f.id) # f doesn't have id yet!
        count += 1
    print("Run completed. {} occurrences already existed. {} were converted.".format(len(existing), len(converted)))
    return existing, converted


def find_unmatched_barcodes():
    mlp_fossils  = Occurrence.objects.filter(basis_of_record='FossilSpecimen')
    problem_list = []
    for f in mlp_fossils:
        if f.barcode != f.item_number:
            problem_list.append(f.barcode)
    return problem_list


def import_dg_updates(file_path='/Users/reedd/Documents/projects/PaleoCore/projects/mlp/data_cleaining_170412/DG_updates.txt'):
    """
    Function to read data from a delimited text file
    :return: list of header values, list of row data lists
    """
    dbfile = open(file_path)
    data = dbfile.readlines()
    dbfile.close()
    data_list = []
    header_list = data[0][:-1].split('\t')  # list of column headers
    # populate data list
    for row in data[1:]:  # skip header row
        data_list.append(row[:-1].split('\t'))  # remove newlines and split by delimiter
        #data_list.append(row.split('\t'))  # remove newlines and split by delimiter
    print('Importing data from {}'.format(file_path))
    return header_list, data_list


def show_duplicate_rows(data_list):
    print("\nChecking for duplicate records.")
    unique_data_list = []
    duplicates = []
    data_list_set = [list(x) for x in set(tuple(x) for x in data_list)]
    for row in data_list:
        if row not in unique_data_list:
            unique_data_list.append(row)
        else:
            duplicates.append(row)
    rowcount = 0
    for row in unique_data_list:
        row.insert(0, rowcount)
        rowcount += 1
    print("Unique rows: {} ?= Row set: {}\nDuplicate rows: {}".format(len(unique_data_list), len(data_list_set), len(duplicates)))
    return unique_data_list, duplicates, data_list_set


def set_data_list(data_list):
    return [list(x) for x in set(tuple(x) for x in data_list)]


def match_catalog_number(catalog_number_string):
    """
    Function to get occurrence objects from MLP catalog number in the form MLP-001
    the function splits the catalog number at the dash and strips leading zeros from the numberic portion of the
    catalog number. It then searches for a matching catalog number.
    :param catalog_number_string:
    :return:
    """
    cn_split = catalog_number_string.split('-')
    try:
        catalog_number_integer = int(cn_split[1])
        cleaned_catalog_number = 'MLP-' + str(catalog_number_integer)
        try:
            occurrence_obj = Biology.objects.get(catalog_number__exact=cleaned_catalog_number)
            return (True, occurrence_obj)
        except(ObjectDoesNotExist):
            return (False, catalog_number_string)
    except(IndexError):
        return (False, catalog_number_string)


def match_barcode_from_catalog_number(catalog_number_string):
    """
    Function to get occurrence objects from MLP catalog number in the form MLP-001
    the function splits the catalog number at the dash and strips leading zeros from the numberic portion of the
    catalog number. It then searches for a matching barcode number.
    :param catalog_number_string:
    :return:
    """
    cn_split = catalog_number_string.split('-')
    try:
        catalog_number_integer = int(cn_split[1])
        #cleaned_catalog_number = 'MLP-' + str(catalog_number_integer)
        try:
            occurrence_obj = Biology.objects.get(barcode__exact=catalog_number_integer)
            return (True, occurrence_obj)
        except(ObjectDoesNotExist):
            return (False, catalog_number_integer)
    except(IndexError):
        return (False, catalog_number_integer)


def match_coordinates(longitude, latitude):
    """
    Function to match an Occurrence instance given coordinates
    :param longitude: in decimal degrees
    :param latitude: in decimal degrees
    :return: returns a two element tuple. The first element is True/False indicating whether there was a single match
    The second element in None by default, or a list of queryset of matches based on coordinates.
    """

    lon = float(longitude)
    lat = float(latitude)
    pnt = Point(lon, lat)
    result = Biology.objects.filter(geom__distance_lte=(pnt, Distance(m=1)))
    match_result = (False, None)
    if (len(result)) == 1:
        match_result = (True, result)
    elif len(result) >= 1:
        match_result = (False, result)
    elif len(result) == 0:
        match_result = (False, None)
    return match_result


def old_match(data_list):
    """
    Function to match Biology objects based on barcode or coordinates.
    :param data_list:
    :return:
    """
    counter = 0
    row_counter = 0
    match_list = []
    coordinate_match_list = []
    problem_list = []
    for row in data_list:
        row_counter += 1
        cat_number_string = row[0]
        match_catalog_number_result = match_catalog_number(cat_number_string)  # try to match by catalog number
        if match_catalog_number_result[0]:  # if there is a successful match by catalog number ...
            match_tuple = (row, match_catalog_number_result[1])  # tuple with original row data and matched occur obj
            match_list.append(match_tuple)  # add the row data to the match list
        elif not match_catalog_number_result[0]:  # next try matching by coordinates
            coordinate_match_result = match_coordinates(row[1], row[2])
            if coordinate_match_result[0]:
                coordinate_match_tuple = (row, coordinate_match_result[1])
                coordinate_match_list.append(coordinate_match_tuple)
            elif not coordinate_match_result[0]:
                problem_tuple = (row, coordinate_match_result[1])
                problem_list.append(problem_tuple)
    print('Matched {} records using catalog numbers'.format(len(match_list)))
    print('Matched {} records using coordinates'.format(len(coordinate_match_list)))
    print('There are {} remaining unmatched records\n'.format(len(problem_list)))

    return match_list, coordinate_match_list, problem_list


def match(data_list):
    print('\nMatching {} items in list'.format(len(data_list)))
    full_match_list = []
    coordinate_match_list = []
    bad_match_list = []
    for row in data_list:
        catno = row[1]  # catalog number
        lon = row[2]  # longitude
        lat = row[3]  # latitude
        basis = row[7]  # basis of record
        cat_match_result = match_catalog_number(catno)
        coord_match_result = match_coordinates(lon, lat)
        # catalog match == coordinate match (only one object)
        if cat_match_result[0] and coord_match_result[0] and cat_match_result[1] == coord_match_result[1][0]:
            match_tuple = (row, cat_match_result[1])
            full_match_list.append(match_tuple)
        # coordinate match != catalog match, e.g. because there is an old or erroneous catalog number
        elif coord_match_result[0] and not cat_match_result[0]:
            match_tuple = (row, coord_match_result[1][0])
            coordinate_match_list.append(match_tuple)
        # catalog match in coordinate match list (more than one coordinate match)
        elif cat_match_result[0] and len(coord_match_result[1]) >= 2:
            matched_object = cat_match_result[1]
            if matched_object in coord_match_result[1]:
                match_tuple = (row, matched_object)
                coordinate_match_list.append(match_tuple)
        # No cat match and multiple coord matches, see if one is human observation
        elif (not cat_match_result[0]) and (not coord_match_result[0]) and basis == 'HumanObservation':
            if coord_match_result[1]:  # if there is a coordinate match result
                if len(coord_match_result[1]) >= 2:
                    matched_objects = [i for i in coord_match_result[1] if i.catalog_number == 'MLP-0']
                    if len(matched_objects) == 1:
                        match_tuple = (row, matched_objects[0])
                        coordinate_match_list.append(match_tuple)
        else:
            # print "{}. Catalog number {} and coordinates {} {}, bad match.".format(count, catno, lon, lat)
            match_tuple = (row, None)
            bad_match_list.append(match_tuple)
            #print match_tuple

    print("Matches: {}\nCoordinate Matches: {}\nBad Matches: {}".format(len(full_match_list),
                                                                        len(coordinate_match_list),
                                                                        len(bad_match_list)))
    return full_match_list, coordinate_match_list, bad_match_list


def display_match(match_tuple):
    row, obj = match_tuple[0], match_tuple[1]

    # row data
    id = row[0]
    catalog_number = row[1]
    longitude = float(row[2])
    latitude = float(row[3])
    collector = row[4]
    date_list = row[5].split(' ')
    month = date_list[0]
    year = date_list[1]
    description = row[6]
    basis = row[7]
    sciname = row[8]
    taxon_string = row[11]
    id_qualifier = row[12]
    notes = row[10]
    taxon_obj = get_taxon_from_scientific_name(taxon_string)

    # object data
    omonth = calendar.month_name[obj.field_number.month]
    oyear = obj.field_number.year
    #                   row   id  catno  basis    lon        lat     coll   mo     yr   desc   sci   tname qual
    row_print_string = '{:3}:{:5}  {:8}  {:10}  {:10.10f} {:10.10f}  {:20}  {:8}  {:4}  {:30}  {:30}  {:30} {:5} {}\n'
    #                      bio:  id  catno  basis   lon         lat     coll   mo    yr    desc    sci  tname qual  rem
    object_print_string = '{:3}:{:5}  {:8}  {:10}  {:10.10f} {:10.10f}  {:20}  {:8}  {:4}  {:30}  {:30}  {:30} {:5} {}'

    print(object_print_string.format('bio', obj.id, obj.catalog_number,
                                     obj.basis_of_record,
                                     obj.point_x(), obj.point_y(),
                                     obj.collector, omonth, oyear,
                                     obj.item_description, obj.item_scientific_name, obj.taxon,
                                     obj.identification_qualifier,
                                     obj.remarks))
    print(row_print_string.format('row', id, catalog_number, basis,
                                  longitude, latitude,
                                  collector,
                                  month, year,
                                  description,
                                  taxon_string, taxon_obj,
                                  id_qualifier,
                                  notes))


def validate_matches(match_list, coordinate_match_list, problem_match_list):
    print("\n## Summary of Matches ##\n")
    match_no = 1

    # print "\n Catalog Number Matches\n"
    # for p in match_list:
    #     print 'Match {}'.format(match_no)
    #     match_no += 1
    #     display_match(p)
    print("\n Coordinate Matches\n")
    for p in coordinate_match_list:
        print('Match {}'.format(match_no))
        match_no += 1
        display_match(p)


def update_matches(match_list):
    print("\n## Updating Matches ##")
    counter = 0
    for m in match_list:
        row = m[0]
        obj = m[1]
        description = row[6]
        sciname = row[8]
        taxon_string = row[11]
        taxon_obj = get_taxon_from_scientific_name(taxon_string)
        id_qualifier_string = row[12]
        identifier = row[15]
        if id_qualifier_string != '':
            id_qual_obj = IdentificationQualifier.objects.get(name=id_qualifier_string)
        elif id_qualifier_string == '':
            id_qual_obj = IdentificationQualifier.objects.get(name='None')

        obj.item_scientific_name = sciname
        obj.item_description = description
        obj.taxon = taxon_obj
        obj.identification_qualifier = id_qual_obj
        obj.identified_by = identifier
        print("updated match {} cat:{}".format(row[0], row[1]))
        counter += 1
        obj.save()
    print("{} records updated successfully.".format(counter))


def main():
    existing, converted = update_occurrence2biology()  # convert all faunal and floral occurrences to biology
    # import header and data list from file
    hl, dl = import_dg_updates(file_path='/home/dnr266/paleocore/mlp/fixtures/DG_updates.txt')
    # hl, dl = import_dg_updates()  # import header and data list from file
    udl, du, dls = show_duplicate_rows(dl)  # check for duplicates
    ml, cl, pl = match(udl)
    validate_matches(ml, cl, pl)
    update_matches(ml)
    update_matches(cl)

    return existing, converted, hl, dl, udl, du, dls, ml, cl, pl


def find_duplicate_catalog_number(mylist):
    unique_list = []
    duplicate_list = []
    for i in mylist:
        if i not in unique_list:
            unique_list.append(i)
        else:
            duplicate_list.append(i)
    return unique_list, duplicate_list


def get_parent_name(taxon_name_list):
    index = -2
    parent_name = taxon_name_list[index]
    id_qual_names = [i.name for i in IdentificationQualifier.objects.all()]
    while parent_name in id_qual_names:
        index -= 1
        parent_name = taxon_name_list[index]
    return parent_name


def fixpts():
    update_list = [(530, 40.8249787777, 11.5880623344), (650, 40.8157221399, 11.5580415457),
                   (1790, 40.8414173126, 11.5584075832),
                   (1796, 40.8387199127, 11.5635939209),
                   (1800, 40.8396148682, 11.5641256533),
                   (1804, 40.8408664654, 11.563696463),
                   (1805, 40.8411042121, 11.5613672431),
                   (1808, 40.8414761456, 11.5594843559),
                   (1812, 40.8380699158, 11.5653869765),
                   (1886, 40.7597923279, 11.5538666796)]
    for i in update_list:
        pk = i[0]
        x = i[1]
        y = i[2]
        o = Biology.objects.get(pk=pk)
        o.geom = Point(x, y)
        o.save()


def test_taxon_usage(taxon_id):
    uses = Biology.objects.filter(taxon=taxon_id)
    print("mlp has {} Biology instances pointing to taxon {}".format(uses.count(), taxon_id))
    return uses


def create_biology(row):
    catalog_number_match = match_catalog_number(row[0])
    catalog_number = catalog_number_match[1]
    barcode_match = match_barcode_from_catalog_number(row[0])
    barcode = barcode_match[1]
    taxon = get_taxon_from_scientific_name(row[10])
    idq = get_identification_qualifier_from_string(row[11])
    lon = float(row[1])
    lat = float(row[2])
    fn = datetime(year=2014, month=1, day=1)
    if not barcode_match[0]:
        return Biology(catalog_number=catalog_number,
                       barcode=barcode,
                       basis_of_record='FossilSpecimen',
                       item_type='Faunal',
                       collection_code='MLP',
                       item_number=barcode,
                       remarks='Missing data from 2014, added in May 2015.',
                       item_scientific_name=row[10],
                       item_description=row[5],
                       collecting_method='Surface Standard',
                       year_collected=2014,
                       field_number=fn,
                       field_season='Jan 2014',
                       individual_count=1,
                       problem=True,
                       problem_comment='Missing data added in May 2015, verify in museum.',
                       geom=Point(lon, lat, srid=4326),
                       taxon=taxon,
                       identification_qualifier=idq
                       )
    else:
        print("Occurrence {} already exists.".format(barcode))


def update_biology_identifications(header, data, dry_run=False):
    """
    Procedure to update the item_scientific_name, item_description and taxon of data read from
    a text/csv file.
    :param header: data file column header row
    :param data: data rows as a list of lists
    :param dry_run: True for dry_run, False for save
    :return:
    """
    for row in data:
        rowdict = dict(zip(header, row))  # combine header and row data into dictionary for easy reference
        id = int(rowdict['id'])
        bio = Biology.objects.get(pk=id)  # fetch the object from the DB
        bio.item_scientific_name = rowdict['item_scientific_name']  # update item_scientific_name
        bio.item_description = rowdict['item_description']  # update item_description
        print(id)
        try:
            bio.taxon = get_taxon_from_scientific_name(rowdict['taxon']) # find matching taxon and update
        except ObjectDoesNotExist:
            print('no taxon match for id {}').format(id)
        except MultipleObjectsReturned:
            print('multiple taxa match for id {}').format(id)
        try:
            idq = get_identification_qualifier_from_string(rowdict['qualifier'])
            bio.identification_qualifier = idq
        except KeyError:
            pass
        try:
            bio.identification_remarks = rowdict['identification_remarks']
        except KeyError:
            pass
        except IndexError:
            pass
        bio.identified_by = mlp.ontologies.denis_geraads
        print('{} {} {} {} {} {} {}'.format(bio.id, bio.item_description,
                                            bio.item_scientific_name, bio.taxon,
                                            bio.identification_qualifier,
                                            bio.identification_remarks, bio.identified_by))

        if not dry_run:
            bio.save()  # save item


def taxon_count(t):
    try:
        count = Biology.objects.filter(taxon=t).count()
    except:
        count = None
    return count


def get_taxa_counts(rank=None):
    """
    function to generate taxonomic lists based on Biology instances for a project
    :param rank:
    :return: Returns a list of tuples containing the taxon and taxon rank,
    e.g. [(<Life>,<root>), (<Animalia>, <Kingdom>), ... ]
    """

    biology_objects = Biology.objects.all()
    taxon_set = set([b.taxon for b in biology_objects])
    taxon_object_list = [(t, t.rank, taxon_count(t)) for t in taxon_set]
    if rank:
        pass
    return taxon_object_list


def get_taxa():
    """
    Get a list of distinct taxon objects for biology instances
    :return: Returns a list
    """
    return [b.taxon for b in Biology.objects.distinct('taxon')]


html_escape_table = {
    "&": "&amp;",
    # ">": "&gt;",
    # "<": "&lt;",
    # "'": "&apos;",
    # '"': "&quot;",
}


def html_escape(text):
    """
    Escape unsafe characters from text strings and replace with html
    :param text:
    :return:
    """
    return "".join(html_escape_table.get(c, c) for c in text)
