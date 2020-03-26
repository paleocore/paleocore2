from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, FieldError
from .models import Fossil, Context
import xlrd
from datetime import datetime
import pytz
import re
from paleocore110.settings import PROJECT_ROOT
import collections
import idigbio
import requests
import string

# Define global variables
FOLDER_PATH = PROJECT_ROOT + '/eppe/fixtures/'
YEARS = (1998, 1999, 2000, 2001, 2003, 2004, 2005, 2012, 2014, 2016)
CSHO_YEARS = YEARS[0:7]  # 1998-2005
file_name = 'laetoli_csho_1998'
verbose_default = False

# A list of lots that need to be split into separate catalog numbers
SPLITS = ['EP 1280/01', 'EP 3129/00', 'EP 1181/00', 'EP 3635/00', 'EP 1177/00']

# Define variables for consistent horizon names
modern = 'Modern'
lower_laetolil = 'Laetolil Beds, Lower Unit'
upper_laetolil = 'Laetolil Beds, Upper Unit'
upper_ngaloba = 'Ngaloba Beds, Upper Unit'
lower_ngaloba = 'Ngaloba Beds, Lower Unit'
upper_ndolanya = 'Ndolanya Beds, Upper Unit'
naibadad = 'Naibadad Beds'

moderns_update_dict = {
        'EP 1074/98': upper_laetolil + ', Below Tuff 2',
        'EP 018/98': lower_laetolil,
        'EP 980/01': upper_laetolil + ', Between Tuffs 6 - 7',
        'EP 981/01': upper_laetolil + ', Between Tuff 7 - 8',
        'EP 1332/01': 'Modern',
        'EP 844/98': upper_laetolil + ', Below Tuff 2',
        'EP 1657/00': 'Modern'
    }

# define horizontal rule
hr = '===================================='


# Functions for opening Excel files and reading headers
def make_file_string(year):
    """
    Create a file name string from the year, e.g. 'laetoli_csho_1998.xls'
    :param year: four digit integer value
    :return: string representation of file name
    """
    return 'laetoli_csho_'+str(year)+'.xls'


def open_book(folder, file):
    """
    Open an Excel workbook
    :param folder: string representing folder path with starting and ending slashes,
    e.g. '/Users/dnr266/Documents/PaleoCore/projects/Laetoli/csho_versions/'
    :param file: string representation of the file name, with no slashes, e.g. 'laetoli_csho_1998.xls'
    :return: Returns an xlrd workbook object
    """
    return xlrd.open_workbook(folder+file)


def get_max_sheet(book):
    """
    Get the sheet in the workbook with the most rows of data
    :param book: An xlrd book object
    :return: Returns an xlrd sheet object
    """
    row_counts = [s.nrows for s in book.sheets()]  # list of row counts for each sheet
    max_sheet_index = row_counts.index(max(row_counts))  # find list index for largest sheet
    sheet = book.sheet_by_index(max_sheet_index)  # return the sheet with the greatest number of rows
    return sheet


def get_header_list(sheet):
    """
    Get a list of header row cell values.
    :param sheet:
    :return: Returns a list of values from the first row in the sheet.
    """
    return [c.value for c in sheet.row(0)]


# The lookup_dict is used to map column names across the different excel files.
lookup_dict = {
    'Specimen Number': 'verbatim_specimen_number',
    'Specimen number': 'verbatim_specimen_number',
    'Date Discovered': 'verbatim_date_discovered',
    'Date discovered': 'verbatim_date_discovered',
    'Storage': 'verbatim_storage',
    'tray': 'verbatim_tray',
    'Tray': 'verbatim_tray',
    'Locality': 'verbatim_locality',
    'Horizon': 'verbatim_horizon',
    'Column22': 'verbatim_horizon',
    'Element': 'verbatim_element',
    'Kingdom:': 'verbatim_kingdom',
    'Kingdom': 'verbatim_kingdom',
    'Phylum': 'verbatim_phylum_subphylum',
    'Phylum/Subphylum:': 'verbatim_phylum_subphylum',
    'Phylum/Subphylum': 'verbatim_phylum_subphylum',
    'Class:': 'verbatim_class',
    'Class': 'verbatim_class',
    'Order:': 'verbatim_order',
    'Order': 'verbatim_order',
    'Family': 'verbatim_family',
    'Tribe': 'verbatim_tribe',
    'Tribe:': 'verbatim_tribe',
    'Genus': 'verbatim_genus',
    'Species': 'verbatim_species',
    'Species:': 'verbatim_species',
    'other': 'verbatim_other',
    'Other': 'verbatim_other',
    'Other:': 'verbatim_other',
    'Comments': 'verbatim_comments',
    'Comment': 'verbatim_comments',
    'Published': 'verbatim_published',
    'published': 'verbatim_published',
    'Problems': 'verbatim_problems',
    'Breakage': 'verbatim_breakage',
    'Weathering': 'verbatim_weathering',
    'Animal Damage': 'verbatim_animal_damage',
    'Animal damage': 'verbatim_animal_damage',
    'NonAnimal Damage': 'verbatim_nonanimal_damage',
    'Nonanimal Damage': 'verbatim_nonanimal_damage',
    'Nonanimal damage': 'verbatim_nonanimal_damage',
}


def validate_header_list(header_list):
    """
    Check that the elements of the header list are present in the lookup dictionary
    :param header_list:
    :return: 1 if all header elements in lookup dict, 0 otherwise
    """
    result = 1
    for i in header_list:
        if lookup_dict[i]:
            pass
        else:
            result = 0
    return result


def validate_all_headers(file_years=YEARS):
    """
    Function to inspect headers rows of all import files.
    :param file_years:
    :return:
    """
    files = [make_file_string(y) for y in file_years]
    for file in files:
        book = open_book(folder=FOLDER_PATH, file=file)
        sheet = book.sheet_by_index(0)
        header = get_header_list(sheet)
        if validate_header_list(header):
            print("Header for {} is valid".format(file))
        else:
            print("Header for {} is NOT valid".format(file))


# Functions for processing and reading data from Excel Files
def convert_date(date_cell, date_mode):
    """
    Convert the dates in the excel spreadsheets into python datetime objects.
    The spreadsheet date columns have mixed values, some are strings and others are dates expressed as integers in
    Excel date format.  This function converts the different formats into a common pythonic representation.
    :param date_cell:
    :param date_mode:
    :return: Returns a python datetime object, with default time.
    """
    date_value = None
    if date_cell.ctype == 1:  # unicode string
        try:
            date_format = '%d/%m/%y'
            date_value = datetime.strptime(date_cell.value, date_format)
        except ValueError:
            date_format = '%d/%m/%Y'
            date_value = datetime.strptime(date_cell.value, date_format)
    elif date_cell.ctype == 3:
        date_value = xlrd.xldate_as_datetime(date_cell.value, date_mode)
    return date_value


def make_row_dict(book, header_list, row_data_cell_list):
    """
    Assumes header row is valid
    :param book: an excel workbook object
    :param header_list: a list of column headings
    :param row_data_cell_list: a list of xl cell data
    :return: returns a dictionary with Fossil model keys and excel row data as values
    """
    cells_dict = dict(zip(header_list, row_data_cell_list))  # dictionary of cell values
    try:
        date_discovered = convert_date(cells_dict['Date Discovered'], book.datemode)  # convert xl dates to datetime
    except KeyError:  # check for alternate capitalization
        date_discovered = convert_date(cells_dict['Date discovered'], book.datemode)  # convert xl dates to datetime
    row_cells_list = list(cells_dict.items())  # list of tuples of dict items
    # use list comprehension to generate tuples of dict items replacing cell instances with cell values
    row_values_list = [(i[0], i[1].value) for i in row_cells_list]
    row_values_dict = dict(row_values_list)  # convert the list back to a dict
    try:
        row_values_dict['Date Discovered'] = date_discovered  # replace cell values (text or float) with datetime
    except KeyError:
        row_values_dict['Date discovered'] = date_discovered  # replace cell values (text or float) with datetime
    occurrence_item_list = [(lookup_dict[i[0]], i[1]) for i in row_values_dict.items()]
    item_dict = dict(occurrence_item_list)
    if item_dict['verbatim_specimen_number']:
        item_dict['catalog_number'] = item_dict['verbatim_specimen_number']
    else:
        item_dict = None  # no verbatim specimen number signals empty row.
    return item_dict


def import_sheet(year, file, book, header, sheet, header_row=True, verbose=verbose_default):
    """
    Import data from an Excel spreadsheet. Skips empty rows.
    :param year: Integer value for the woorkbook year.
    :param file: String value containing file name without leading or trailing slashes.
    :param book: An Excel workbook object
    :param header: A list of column header names
    :param sheet: An Excel spreadsheet object
    :param header_row: header row present or not
    :param verbose: verbose output desired
    :return: returns an integer row count and an integer created count. If all goes well the two should match.
    """
    created_count = 0
    starting_row = 1
    row_count = 0
    if not header_row:
        starting_row = 0
    for row in range(starting_row, sheet.nrows):
        if verbose:
            print("processing row {}".format(row_count))
        row_dict = make_row_dict(book, header, sheet.row(row))
        if row_dict:
            row_dict['verbatim_workbook_name'] = file
            row_dict['verbatim_workbook_year'] = year
            # specimen_number = row_dict['verbatim_specimen_number']
            Fossil.objects.create(**row_dict)
            created_count += 1
            row_count += 1
        else:  # if empty row
            row_count += 1
            print('skipping blank row {}'.format(row_count))
    return row_count, created_count


def import_file(folder, file, year, verbose=verbose_default):
    """
    Procedure to import data from an Excel workbook
    :param folder: Directory path to workbook as string and with trailing slash, e.g. '/eppe/fixtures/'
    :param file: File name of workbook including extension, e.g. 'csho_laetoli_1998.xls'
    :param year: Year of data being imported as integer, e.g. 1998
    :param verbose: True/False for more verbose output
    :return:
    """
    print("\nImporting data from {}".format(file))  # Indicate function has started
    book = open_book(folder, file)  # open the excel workbook
    sheet = get_max_sheet(book)  # get the sheet from the workbook
    header = get_header_list(sheet)  # get the header as a list
    if validate_header_list(header):  # validate the header, make sure all columns are in lookup dictionary
        rc, cc = import_sheet(year, file, book, header, sheet, verbose=verbose)  # import data from the sheet
        print("Processed {rc} rows and created {cc} new Fossil objects.".format(rc=rc, cc=cc))
    else:
        print('Invalid Header List')


# Function to delete duplicate and incorrect records
def delete_records():
    """
    Procedure to delete duplicate and erroneous records.
    :return: Returns an integer count of the number of records deleted.
    """
    count = 0
    # Seven specimens are clones. Delete one of each
    # clones = ['EP 1582b/00', EP 1144/04', 'EP 1173/04', 'EP 1400/04', 'EP 1403/04', 'EP 1542/04', 'EP 515/05']
    # 1. Fix EP 1582b/00. Keep the item with the more complete description.
    fossil = Fossil.objects.get(verbatim_specimen_number='EP 1582B/00', verbatim_element='Dist. M/Podial')
    fossil.delete()
    count += 1

    # 2 - 7.  Fix 6 cloned entries, delete one copy.
    for cn in ['EP 1144/04', 'EP 1173/04', 'EP 1400/04', 'EP 1403/04', 'EP 1542/04', '515/05']:
        fossils = Fossil.objects.filter(verbatim_specimen_number=cn)
        if len(fossils) == 2:
            delete_me = fossils[0]
            delete_me.delete()
            count += 1

    # 8. One item is modern, not fossil. Update: decided to keep modern specimens
    # specimen = Fossil.objects.get(verbatim_specimen_number='EP 1905/00')
    # specimen.delete()
    # count += 1

    # 8. Fix EP 1052/98. The Aves specimen is an inccorrect entry and is deleted.
    fossil = Fossil.objects.get(verbatim_specimen_number='EP 1052/98', verbatim_class='Aves')
    fossil.delete()
    count += 1

    # 9. Fix EP 001/98 Delete the crocodile entry
    fossil = Fossil.objects.get(verbatim_specimen_number='EP 001/98', verbatim_family='Crocodylidae')
    fossil.delete()
    count += 1

    # 10. EP 1477b/00 Delete the suid entry.
    fossil = Fossil.objects.get(verbatim_specimen_number='EP 1477B/00', verbatim_order='Artiodactyla')
    fossil.delete()
    count += 1

    return count


# Functions to split bulk records
def clone(obj):
    """
    Clone a database object.
    :param obj: Original object to be cloned
    :return: New, saved object. New object is identical to old *except* for id and pk
    Note that id and pk are often the same but can differ when using abstract models or model inheritance.
    """
    from copy import deepcopy
    # Need deepcopy here so that obj become different from c.
    # If we use normal assignment, obj = c, when we change c, obj changes too, and that leads to unexpected behavior.
    c = deepcopy(obj)
    c.id = None
    c.pk = None
    c.save()
    return c


def letter_part(n):  # takes quotient and index
    """
    Function to calculate the lettered part for a given number of parts n
    Eg. letter_part(1) = 'a', letter_part(26) = 'z', letter_part(27) = 'az', letter_part(702) = zz  this is the max
    Values for n > 702 return None
    :param n:number of parts
    :return: returns a string of length 1 or 2 ranging from a to zz. Returns None for values greater than zz
    """
    q, i = divmod(n, 26)  # divmod returns quotient and modulus
    if i == 0:  # Fix special case for z, n=26 returns (1,0), but we want (0,25)
        q -= 1
        i = 25  # convert i to index for az string.
    else:
        i -= 1  # convert i to index for az string.
    result = None  # set default result to None
    az = string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'
    if q == 0:  # quotient is 0, first time through a-z
        result = az[i]  # one letter result, eg. 'a'
    elif 26 >= q >= 1:  # quotient is 1 or more, beyond q=26 we would need three letters.
        result = az[q-1]+az[i]  # two letter result, eg. 'aa'
    elif q > 26:
        pass  # will return default None
    return result


def split2many(obj, no_parts=2):
    """
    Split a Fossil into arbitrary number of parts
    :param obj: original db object to split
    :param no_parts: integer number of parts to split into
    :return: returns a list of db objects, length = no_parts,
    all with uniuqe id,pk. Other attributes will need to be updated.
    """
    cat_re = re.compile(r'EP \d{3,4}/[09][01234589]$')  # regex to test lettered part not already present.
    if type(obj) == Fossil:  # only meant to work on fossil objects.
        if cat_re.match(obj.catalog_number):  # confirm original has no parts
            clone_list = [obj]+[clone(obj) for i in range(1, no_parts)]  # create a list of cloned objects
            lpi = 1  # letter part index
            for c in clone_list:  # for each new object reassign catalog number with part.
                part_string = letter_part(lpi)+'/'  # get incremented letter part string
                c.catalog_number = c.catalog_number.replace('/', part_string)  # insert letter part string
                c.save()
                lpi += 1  # advance letter part index by 1
            return clone_list
        else:
            print("catalog number already has parts")
            return None
    else:
        raise TypeError


def split_records():
    """
    Procedure that splits records into parts. Needed for some bulk items where more than one taxa is
    included in a single item. In these cases taxa appear as a comma separated list in the verbatim taxon
    field, (e.g. tgenus = 'Achatina, Burtoa').
    This procedure splits the single record into to parts, e.g. EP 1280/01 becomes EP 1280a/01 and EP 1280b/01
    One specimen, EP 1177/00 is split to 3 parts, a, b, and c.
    :return:
    """
    count = 0
    # Split 5 bulk samples that contain multiple taxa. See Table 5 in manuscript.
    splits = SPLITS
    for catno in splits:
        if Fossil.objects.filter(verbatim_specimen_number=catno):
            print("Splitting {}".format(catno))
            if catno == 'EP 1177/00':  # split EP 1177/00 into 3 parts
                split2many(Fossil.objects.get(verbatim_specimen_number=catno), no_parts=3)
            else:  # split all others into 2 parts
                split2many(Fossil.objects.get(verbatim_specimen_number=catno), no_parts=2)
            count += 1  # increase counter
    return count  # return number of splits made


# Functions for processing and updating data by field
def update_catalog_number():
    """
    Prodedure to update catalog_number from verbatim_specimen_number and standardize formatting of all
    catalog numbers.
    """
    print("Updating catalog_number from verbatim_specimen_number")

    # Define regex search strings
    ep_re = re.compile(r'EP ')
    cat_re = re.compile(r'EP \d{3,4}[a-zA-Z]?/[089][01234589][a-zA-Z]$')
    cap = re.compile(r'EP \d{3,4}[A-Z]/[089][01234589]$')
    missing_slash = re.compile(r'EP \d{3,4}[a-zA-Z]?[089][01234589]$')
    extra_year = re.compile(r'EP \d{3,4}[a-zA-Z]?/[089][01234589][9]$')
    period = re.compile(r'EP \d{3,4}[a-zA-Z]?/[089][01234589][.]$')
    colon = re.compile(r'EP \d{3,4}[a-zA-Z]?:/[089][01234589]$')

    # update catalog number for all records EXCEPT the splits
    for fossil in Fossil.objects.exclude(verbatim_specimen_number__in=SPLITS):
        # Initial write of verbatim catalog number to catalog number
        # Fix missing EP prefix in 2005 records at the same time.
        if not ep_re.match(fossil.verbatim_specimen_number):  # 2005 catalog numbers missing EP prefix
            fossil.catalog_number = 'EP '+fossil.verbatim_specimen_number
        else:
            fossil.catalog_number = fossil.verbatim_specimen_number
        fossil.save()

        # Fix catalog numbers with trailing letters e.g. EP 001/98A to EP 001a/98
        if cat_re.match(fossil.catalog_number):
            part = fossil.catalog_number[-1:]  # A
            base = fossil.catalog_number[:-1]  # EP 001/98
            slash = base.index('/')
            fossil.catalog_number = base[:slash] + part.lower() + base[slash:]  # 'EP 001' + 'a' + '/98'

        # Fix cat numbers with cap part letters e.g. EP 001A/98 to EP 001a/98
        if cap.match(fossil.catalog_number):
            cn = fossil.catalog_number  # 'EP EP 001A/98'
            ci = cn.index('/')
            pre = cn[:ci-1]  # EP 001
            part = cn[ci-1:ci]  # A
            post = cn[ci:]  # /98
            cn = pre + part.lower() + post  # 'EP 001' + 'a' + '/98'
            fossil.catalog_number = cn

        # Fix cat numbers missing slash, e.g. EP 284100
        if missing_slash.match(fossil.catalog_number):
            cn = fossil.catalog_number  # 'EP 284100'
            cn = cn[:-2] + '/' + cn[-2:]  # 'EP 2841' + '/' + '00'
            fossil.catalog_number = cn

        # Fix cat numbers with extra 9 in year, e.g. EP 265/999
        if extra_year.match(fossil.catalog_number):
            fossil.catalog_number = fossil.catalog_number[:-1]  # EP 265/99

        # Fix cat numbers with trailing periods  e.g. EP 001/98.
        if period.match(fossil.catalog_number):
            fossil.catalog_number = fossil.catalog_number[:-1]

        # Fix cat numbers with colons
        if colon.match(fossil.catalog_number):
            cn = fossil.catalog_number  # 'EP 525:/05'
            ci = cn.index(':')
            cn = cn[:ci] + cn[ci+1:]  # 'EP 525' + '/05'
            fossil.catalog_number = cn
        fossil.save()

    # Fix six (6) errors in catalog numbers, see Table 6 in manuscript
    # 1. Fix EP 120A+B/98, remove parts
    ep120 = Fossil.objects.get(verbatim_specimen_number='EP 120A+B/98')
    ep120.catalog_number = 'EP 120/98'
    comment = 'Catalog number corrected from EP {} to EP 120/98'.format(ep120.verbatim_specimen_number)
    ep120.remarks = (ep120.remarks + " " if ep120.remarks else "") + comment
    ep120.save()

    # 2. Fix EP 507/07
    ep507 = Fossil.objects.get(verbatim_specimen_number='507/07')
    ep507.catalog_number = 'EP 507/05'
    comment = 'Catalog number corrected from {} to EP 507/05'.format(ep507.verbatim_specimen_number)
    ep507.remarks = (ep507.remarks + " " if ep507.remarks else "") + comment
    ep507.save()

    # 3. Fix EP 756/06
    ep756 = Fossil.objects.get(verbatim_specimen_number='756/06')
    ep756.catalog_number = 'EP 756/05'
    ep756_comment = 'Catalog number corrected from {} to EP 756/05'.format(ep756.verbatim_specimen_number)
    ep756.remarks = (ep756.remarks + " " if ep756.remarks else "") + ep756_comment
    ep756.save()

    # 4. Fix EP 1075/03. The Serengetilabus specimen has a typo in the catalog number. Should be EP 1975/03
    ep1975 = Fossil.objects.get(verbatim_specimen_number='EP 1075/03', verbatim_genus='Serengetilagus')
    ep1975.catalog_number = 'EP 1975/03'
    ep1975_comment = 'Catalog number corrected from {} to EP 1975/03'.format(ep1975.verbatim_specimen_number)
    ep1975.remarks = (ep1975.remarks + " " if ep1975.remarks else "") + ep1975_comment
    ep1975.save()

    # 5. Fix EP 348/04. The distal radius specimen has a typo in the catalog number and incorrect date. It should
    # read EP 349/04 and the date should be 29 June 2004
    fossil = Fossil.objects.get(catalog_number='EP 348/04', verbatim_element='Distal radius')
    fossil.catalog_number = 'EP 349/04'
    tz = pytz.timezone('Africa/Dar_es_Salaam')
    fossil.date_recorded = datetime(year=2004, month=6, day=29, tzinfo=tz)
    fossil.save()

    # 6. Fix EP 2188/99, the Bovidae distal humerus is a typo and should be EP 2188/03
    fossil = Fossil.objects.get(catalog_number='EP 2188/99', verbatim_element='distal humerus')
    fossil.catalog_number = 'EP 2188/03'
    fossil.save()

    fossil = Fossil.objects.get(catalog_number='EP 2188/99', verbatim_element='Lumbar Vertebral Centrum')
    fossil.catalog_number = 'EP 2188/00'
    fossil.save()

    # Fix 3 emended taxonomic identifications. See Table 8 in text
    # Fix two pairs of duplicate entries that reflect emended taxonomic identifications of the same specimen.
    # emended_specimens = ['EP 001/98', 'EP 1477b/00']
    # EP 001/98 was emended from crocodile to rhino
    # EP 1477b/00 was emended from suid to felid

    # 1. Fix EP 0001/98, update comments to the rhino entry.
    fossil = Fossil.objects.get(catalog_number='EP 001/98', verbatim_family='Rhinocerotidae')
    if fossil.taxon_remarks:
        fossil.taxon_remarks += ' Identification updated from Animalia:Vertebrata:Reptilia:Crocodilia:Crocodylidae'
        fossil.save()
    else:
        fossil.taxon_remarks = 'Identification updated from Animalia:Vertebrata:Reptilia:Crocodilia:Crocodylidae'
        fossil.save()

    # 2. Fix EP 1477b/00 and also related specimen EP 1477a/00
    # Update comments to the the felid entry.
    fossil = Fossil.objects.get(catalog_number='EP 1477b/00', verbatim_order='Carnivora')
    if fossil.taxon_remarks:
        fossil.taxon_remarks += ' Identification updated from Animalia:Vertebrata:Mammalia:Artiodactyla:cf. Suidae'
        fossil.save()
    else:
        fossil.taxon_remarks = 'Identification updated from Animalia:Vertebrata:Mammalia:Artiodactyla:cf. Suidae'
        fossil.save()
    # Also emend the taxonomic information for related record EP 1477a/00
    fossil = Fossil.objects.get(catalog_number='EP 1477a/00')
    fossil.torder = 'Carnivora'
    fossil.tfamily = 'Felidae'
    fossil.tsubfamily = None
    fossil.tgenus = None
    fossil.ttribe = None
    fossil.trivial = None
    fossil.scientific_name = 'Animalia:Vertebrata:Mammalia:Carnivora:Felidae'
    fossil.save()
    if fossil.taxon_remarks:
        fossil.taxon_remarks += ' Identification updated from ' \
                                'Animalia:Vertebrata:Mammalia:Artiodactyla:Suidae:Kolpochoerus'
        fossil.save()
    else:
        fossil.taxon_remarks = 'Identification updated from ' \
                               'Animalia:Vertebrata:Mammalia:Artiodactyla:Suidae:Kolpochoerus'
        fossil.save()


def update_institution():
    Fossil.objects.all().update(institution='NMT')


def update_remarks():
    print("Updating remarks")
    for f in Fossil.objects.all():
        f.remarks = f.verbatim_comments
        f.save()


def update_date_recorded():
    """
    date_recorded = verbatim_date_discovered
    Function to copy dates to date_recorded field and add timezone info.
    Note that times are meaningless here because only dates were recorded in original catalog.
    :return:
    """
    print("Updating date_recorded from verbatim_date_discovered")
    tz = pytz.timezone('Africa/Dar_es_Salaam')
    for s in Fossil.objects.all():
        if s.verbatim_date_discovered:
            s.date_recorded = datetime.combine(s.verbatim_date_discovered, datetime.min.time(), tzinfo=tz)
            s.save()
        else:
            s.date_recorded = None


def update_locality():
    """
    Update locality_name from verbatim_locality. Clean entries and standardize to Laetoli locality vocabulary.
    :return:
    """
    print("Updating Locality")

    # Define dictionary of replacement values to be used in multi-replace function
    rep = {
        '1NW': '1 Northwest',
        '2 (NW)': '2 Northwest',
        '2 (?West)': '2 ?West',
        '2 (West)': '2 West',
        '(S)': 'South',
        '(South)': 'South',
        '22S': '22 South',
        '7E': '7 East',
        '7 E': '7 East',
        '9S': '9 South',
        '9 S': '9 South',
        '10 E': '10 East',
        '10E': '10 East',
        '10 W': '10 West',
        '10W': '10 West',
        '10 Ne': '10 Northeast',
        '12 E': '12 East',
        '12E': '12 East',
        '13 E': '13',
        '13E': '13',
        '13/14': '13',
        '21E': '21 East',
        '22E': '22 East',
        '22 E': '22 East',
        '(Nenguruk Hill)': 'Nenguruk Hill',
        'Gulley': 'Gully',
        'Lobeleita': 'Lobileita',
        'Olesuisu': 'Oleisusu',
        'Laetolil': 'Laetoli',
        'snake gully': 'Snake Gully',
        '#': '',
        '.': '',
        ',': ' ',
    }

    # Compile regular expressions outside loop
    loc = re.compile(r'^Loc[.]* \d{1,2}\w*')  # All cases beginning with 'Loc
    l9s = re.compile(r'^Laetoli Loc.[\s]*9[\s]*')
    l22s = re.compile(r'22 S[\s]*$')
    esere = re.compile(r'^Esere$')
    garusi = re.compile(r'Garusi R  Sw Of Norsigidok$')
    l18 = re.compile(r'18.*')
    l2 = re.compile(r'[\s]2[\s].*')
    noiti = re.compile(r'^Noiti$')

    # iterate through all records
    for f in Fossil.objects.all():
        ln = f.verbatim_locality     
        if loc.match(ln):
            ln = ln.replace('Loc', 'Laetoli')  # If entry begins with Loc.

        ln = multireplace(ln, rep)

        ln = ln.replace('Loc', '')  # remove any remaining Loc
        ln = ln.replace(' Upper Laetoli Beds between Tuffs 5 +7', '')
        ln = ln.replace('Laetoli 95', 'Laetoli 9 South')
        ln = l22s.sub('22 South', ln)
        ln = esere.sub('Esere 1', ln)
        ln = garusi.sub('Garusi Southwest', ln)
        ln = l18.sub('18', ln)
        ln = l2.sub(' 2 ', ln)
        ln = noiti.sub('Noiti 1', ln)
        ln = ln.replace('   ', ' ')  # remove triple spaces
        ln = ln.strip().replace('  ', ' ')  # remove all extraneous whitespaces
        ln = ln.replace('Gully 05 km north of 5', 'Laetoli 5')

        # Convert all versions of blank to None
        if ln in ['', ' ', None]:
            ln = None

        # Assign and save
        f.locality_name = ln
        if f.verbatim_horizon == 'South Below Tuff 2' and l9s.match(f.verbatim_locality):
            f.locality_name = 'Laetoli 9 South'
        f.save()

    # Fix three specimens that have incorrect geological context and locality info
    # ['EP 900/98', 'EP 901/98', 'EP 902/98']
    fossils = Fossil.objects.filter(catalog_number__in=['EP 900/98', 'EP 901/98', 'EP 902/98'])
    if fossils.count() == 3:  # should have three matches
        fossils.update(locality_name='Laetoli 9 South')  # update does not require save

    # Fix two specimens that are missing locality information.
    # ['EP 1308/04', 'EP 1309/04']
    fossils = Fossil.objects.filter(catalog_number__in=['EP 1308/04', 'EP 1309/04'])
    if fossils.count() == 2:
        fossils.update(locality_name='Laetoli 5')

    # Fix 12 specimens with incorrect locality information','
    specimen_list = ['EP 807/04', 'EP 808/04', 'EP 809/04', 'EP 810/04', 'EP 811/04', 'EP 812/04', 'EP 813/04',
                     'EP 814/04', 'EP 815/04', 'EP 816/04', 'EP 817/04', 'EP 818/04']
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=specimen_list)
    fossils.update(locality_name='Laetoli 7')


def update_area():
    """
    Assumes upldate locality
    :return:
    """
    emboremony = re.compile('Emboremony')
    engesha = re.compile('Engesha')
    esere = re.compile('Esere')
    kakesio = re.compile('Kakesio')
    garusi = re.compile('Garusi')
    lobileita = re.compile('Lobileita')
    ndoroto = re.compile('Ndoroto')
    noiti = re.compile('Noiti')
    olaltanaudo = re.compile('Olaltanaudo')
    oleisusu = re.compile('Oleisusu')

    for f in Fossil.objects.all():
        if emboremony.search(f.locality_name):
            f.area_name = 'Kakesio'
        elif engesha.search(f.locality_name):
            f.area_name = 'Esere-Noiti'
        elif esere.search(f.locality_name):
            f.area_name = 'Esere-Noiti'
        elif garusi.search(f.locality_name):
            f.area_name = 'Laetoli'
        elif kakesio.search(f.locality_name):
            f.area_name = 'Kakesio'
        elif lobileita.search(f.locality_name):
            f.area_name = 'Kakesio'
        elif garusi.search(f.locality_name):
            f.area_name = 'Laetoli'
        elif noiti.search(f.locality_name):
            f.area_name = 'Esere-Noiti'
        elif olaltanaudo.search(f.locality_name):
            f.area_name = 'Olaltanaudo'
        elif ndoroto.search(f.locality_name):
            f.area_name = 'Ndoroto'
        elif oleisusu.search(f.locality_name):
            f.area_name = 'Oleisusu'
        else:
            f.area_name = 'Laetoli'
        f.save()


def create_geological_context_dictionary():
    gcn_dict = {
        "?Laetolil Beds, Upper Unit": lower_laetolil,
        "?Mbuga Clay": upper_ngaloba,
        "?Ndolanya Beds": upper_ndolanya,
        "?Upper Ndolanya Beds": upper_ndolanya,
        "?Ngaloba Beds": upper_ngaloba,
        "Ngaloba Beds?": upper_ngaloba,
        "Upper Ngaloba Beds?": upper_ngaloba,
        "?Olpiro Beds": lower_ngaloba,
        "?Pleistocene": upper_ngaloba,
        "Basal Pale Yellow-Brown Tuff": lower_laetolil,
        "Below Ogol Lava": lower_laetolil,
        "Laetolil Beds, ?Lower Unit": lower_laetolil,
        "Laetolil Beds, ?Lower Unit Or Mbuga Clay Horizon": lower_laetolil,
        "Laetolil Beds, Lower Unit": lower_laetolil,
        "Lower Laetolil Beds": lower_laetolil,
        "Laetolil Beds, Lower Unit, Tuff 8": upper_laetolil+", Between Tuff 8 - Yellow Marker Tuff",  # Fix 001/99
        "Laetolil Beds, Upper Unit": upper_laetolil,
        upper_laetolil+", @ Base Of Yellow Marker Tuff": upper_laetolil+", Yellow Marker Tuff",
        upper_laetolil+", Above Tuff 7": upper_laetolil+", Between Tuffs 7 - 8",
        upper_laetolil+", Above Tuff 8": upper_laetolil+", Between Tuff 8 - Yellow Marker Tuff",
        upper_laetolil+", Augite-Biotite Tuff Of Tuff 7": upper_laetolil+", Augite-Biotite Tuff of Tuff 7",
        upper_laetolil+", Below Tuff 2": upper_laetolil+", Below Tuff 2",
        upper_laetolil+", Below Tuff 3": upper_laetolil+", Below Tuff 3",
        upper_laetolil+", Below Tuff 5": upper_laetolil+", Below Tuff 5",
        upper_laetolil+", Below Tuff 7": upper_laetolil+", Between Tuffs 6 - 7",
        upper_laetolil+", Below Tuff 8 To Just Below Tuff 7": upper_laetolil+", Below Tuff 8 To Just Below Tuff 7",
        upper_laetolil+", Below Tuffs 7 - 8": upper_laetolil+", Between Tuffs 7 - 8",
        upper_laetolil+", Between Tuff 6 - Just Above Tuff 7": upper_laetolil+", Between Tuff 6 - Just Above Tuff 7",
        upper_laetolil+", Between Tuff 6 - Just Above Tuff 8": upper_laetolil+", Between Tuff 6 - Just Above Tuff 8",
        upper_laetolil+", Between Tuff 7 - 2M Above Tuff 8": upper_laetolil+", Between Tuff 7 - 2M Above Tuff 8",
        upper_laetolil+", Between Tuff 7 - Just Above Tuff 8": upper_laetolil+", Between Tuff 7 - Just Above Tuff 8",
        upper_laetolil+", Between Tuff 7 - Yellow Marker Tuff": upper_laetolil+", Between Tuff 7 - Yellow Marker Tuff",
        upper_laetolil+", Between Tuff 8 - Yellow Marker Tuff": upper_laetolil+", Between Tuff 8 - Yellow Marker Tuff",
        upper_laetolil+", Between Tuffs 1 - 2": upper_laetolil+", Below Tuff 2",
        upper_laetolil+", Between Tuffs 2 - 3 - Tuffs 5 - 7": upper_laetolil+", Between Tuffs 2 - 3 and Tuffs 5 - 7",
        upper_laetolil+", Between Tuffs 3 - 5": upper_laetolil+", Between Tuffs 3 - 5",
        upper_laetolil+", Between Tuffs 3 - 7": upper_laetolil+", Between Tuffs 3 - 7",
        upper_laetolil+", Between Tuffs 3 - 8": upper_laetolil+", Between Tuffs 3 - 8",
        upper_laetolil+", Between Tuffs 4 - 5": upper_laetolil+", Between Tuffs 4 - 5",
        upper_laetolil+", Between Tuffs 5 - 6": upper_laetolil+", Between Tuffs 5 - 6",
        upper_laetolil+", Between Tuffs 5 - 6, Calcrete Layer": upper_laetolil+", Between Tuffs 5 - 6",
        upper_laetolil+", Between Tuffs 5 - 7": upper_laetolil+", Between Tuffs 5 - 7",
        upper_laetolil+", Between Tuffs 5 - 8": upper_laetolil+", Between Tuffs 5 - 8",
        upper_laetolil+", Between Tuffs 6 - 7": upper_laetolil+", Between Tuffs 6 - 7",
        upper_laetolil+", 2 M Below Tuff 7": upper_laetolil+", Between Tuffs 6 - 7",
        "Laetolil Beds Between Tuffs 6 - 7": upper_laetolil+", Between Tuffs 6 - 7",
        upper_laetolil+", Between Tuffs 6 - 8": upper_laetolil+", Between Tuffs 6 - 8",
        upper_laetolil+", Between Tuffs 7 - 8": upper_laetolil+", Between Tuffs 7 - 8",
        upper_laetolil+", 1 M Above Tuff 7": upper_laetolil+", Between Tuffs 7 - 8",
        upper_laetolil+", Just Below Tuff 7": upper_laetolil+", Between Tuffs 6 - 7",
        upper_laetolil+", Level Unknown": upper_ngaloba,
        upper_laetolil+", Lower Part Of Tuff 7": upper_laetolil+", Tuff 7",
        upper_laetolil+", South Below Tuff 2": upper_laetolil+", Below Tuff 2",
        upper_laetolil+", Surface Below Tuff 7": upper_laetolil+", Between Tuffs 6 - 7",
        upper_laetolil+", Top Part Of Tuff 8": upper_laetolil+", Tuff 8",
        upper_laetolil+", Uppermost Tuff": lower_laetolil,
        upper_laetolil+", Within Tuff 7": upper_laetolil+", Tuff 7",
        upper_laetolil+", Yellow Marker Tuff": upper_laetolil+", Yellow Marker Tuff",
        "Lava Below Laetolil Beds": lower_laetolil,
        "Mbuga Clay": upper_ngaloba,
        "Mbuga Clay - Alluvium (Late Quaternary)": upper_ngaloba,
        "Modern": "Modern",
        "Ndolanya Beds": upper_ndolanya,
        "Ndolanya Beds, Upper Unit": upper_ndolanya,
        "Upper Ndolanya Beds": upper_ndolanya,
        "Ndolanya Beds, Upper Unit, Above Tuff 8": upper_laetolil+", Between Tuff 8 - Yellow Marker Tuff",
        "Ngaloba Beds": upper_ngaloba,
        "Ngaloba Beds, Upper Unit": upper_ngaloba,
        "Ngaloba Beds/Ndolanya Beds": upper_ngaloba,
        "Lower Ngaloba Beds": lower_ngaloba,
        "Olpiro Beds": "Olpiro Beds",
        "Surface Find": upper_laetolil,
        None: None,
    }
    return gcn_dict


def update_geological_context():
    """
    Clean up and consolidate entries in the Horizon field and copy to geological_context_name
    :return:
    """
    print("Updating Geological Context")

    # Define dictionary of replacement values to be used in multi-replace function
    rep = {
        'And': '-',
        'and': '-',
        '+': '-',
        '&': '-',
        '? ': '?',
        'T1 - T2': 'Tuffs 1 - 2',
        'T2 - T3': 'Tuffs 2 - 3',
        'T3 - T5': 'Tuffs 3 - 5',
        'T4 - T5': 'Tuffs 4 - 5',
        'T5 - T6': 'Tuffs 5 - 6',
        'T5 - T7': 'Tuffs 5 - 7',
        'T6 - T7': 'Tuffs 6 - 7',
        'T6 - T8': 'Tuffs 6 - 8',
        'T7 - T8': 'Tuffs 7 - 8',
        'Below T2': 'Below Tuff 2',
        'Below T3': 'Below Tuff 3',
        'Above T7': 'Above Tuff 7',
        '5-7': '5 - 7',
        '6-7': '6 - 7',
        '5 -7': '5 - 7',
        'Btw': 'Between',
        'Ymt': 'Yellow Marker Tuff',
        'Laeotolil': 'Laetolil',
        'Laetoli ': 'Laetolil ',
    }

    # Compile regular expressions outside loop
    lb_re = re.compile(r'^Upper Laetoli[l]*.*(Be.*)')  # All cases beginning with 'Upper Laetoli' or 'Upper Laetolil'
    bt_re = re.compile(r'^Below Tuff.*|^Between Tuff.*')  # All cases beginning w/ 'Below Tuff' or 'Between Tuff'
    ub_re = re.compile(r'^Upper Beds (Between Tuff[s]* [\d] - .*)')  # Upper Beds Betwee ...
    so_re = re.compile(r'^South Below Tuff 2')  # All cases beginning with 'South Below Tuff 2'
    ab_re = re.compile(r'^Above Tuff 8$')  # All cases beginning with 'Above Tuff 8'
    ue_re = re.compile(r'^[?]Upper Ndolanya$')  # All cases beginning with '? Upper Ndolanya'

    # Compile regex for auto sequence error.
    tf_re = re.compile(r'.*Tuffs 6 - [\d]{2,2}$')  # DO NOT PUT space after comma! This will break regex functionality.

    # Define a standard prefix string for Laetoli Upper Beds
    prefix = upper_laetolil+', '

    # Define lookup dictionary outside loop
    gcn_dict = create_geological_context_dictionary()

    # Iterate through all records and update
    for f in Fossil.objects.all():
        gcn = f.verbatim_horizon.title()  # Make all cases consistent

        # Standardize symbols and expand abbreviations
        gcn = multireplace(gcn, rep)  # Fix abbreviations
        gcn = multireplace(gcn, rep)  # Need to run 2x to catch changes from first round

        # These lines use the regex defined above to update and standardize entries.
        # E.g. The first one converts 'Upper Laetolil' -> 'Laetolil Beds, Upper Unit'
        # Substitute matching strings with groups, group 0 is whole string, group 1 is partial string in parentheses
        gcn = re.sub(lb_re, prefix+'\g<1>', gcn)
        gcn = re.sub(bt_re, prefix+'\g<0>', gcn)
        gcn = re.sub(ub_re, prefix+'\g<1>', gcn)
        gcn = re.sub(so_re, prefix+'\g<0>', gcn)  # These localities should also be updated to 9S
        gcn = re.sub(ab_re, upper_ndolanya + ', Above Tuff 8', gcn)
        gcn = re.sub(ue_re, upper_ndolanya, gcn)

        # Fix auto sequence error. A sequence of entries have incrementing tuff intervals,
        # e.g.
        # Laetolil Beds, Upper Unit, Between Tuffs 6 - 8'
        # Laetolil Beds, Upper Unit, Between Tuffs 6 - 9'
        # Laetolil Beds, Upper Unit, Between Tuffs 6 - 10'
        # Laetolil Beds, Upper Unit, Between Tuffs 6 - 11' ... all the way to 6 - 24
        # My guess is that at some point someone updating the XL sheets selected a range of cells and
        # drag filled below them which created an automatic sequence.
        gcn = tf_re.sub(upper_laetolil + ', Between Tuffs 6 - 7', gcn)
        gcn = gcn.replace('Between Tuffs 6 - 9', 'Between Tuffs 6 - 7')

        # Fix remaining oddballs
        gcn = gcn.replace(' T7', ' Tuff 7 ')
        gcn = gcn.replace('T8', 'Tuff 8')
        gcn = gcn.replace('Tuff 8V', 'Tuff 8')
        gcn = gcn.replace('Between 5 - 7', 'Between Tuffs 5 - 7')
        gcn = gcn.replace('Tuffs 6 - Just Above Tuff 7', 'Tuff 6 - Just Above Tuff 7')
        gcn = gcn.replace('Tuffs 6 - Just Above Tuff 8', 'Tuff 6 - Just Above Tuff 8')

        gcn = gcn.replace('Tuffs 7 Just Above Tuff 8', 'Tuff 7 - Just Above Tuff 8')
        gcn = gcn.replace('Tuff 7 Just Above Tuff 8', 'Tuff 7 - Just Above Tuff 8')
        gcn = gcn.replace('Tuffs 7 - Just Above 8', 'Tuff 7 - Just Above Tuff 8')
        gcn = gcn.replace('Tuffs 7 - Just Above Tuff 8', 'Tuff 7 - Just Above Tuff 8')
        gcn = gcn.replace('Tuffs 7 - Yellow Marker Tuff', 'Tuff 7 - Yellow Marker Tuff')

        gcn = gcn.replace('Horizon Unknown ', '')
        gcn = gcn.replace('(Th)', '')
        gcn = gcn.strip().replace('  ', ' ')  # remove any extraneous spaces

        # Convert all versions of blank to None
        if gcn in ['', ' ', None]:
            gcn = None

        # Simplify and merge gcn values using lookup dictionary
        # This step uses the gcn_dictionary to further clean entries and to merge several unique entries together
        # For example all entries of "?Laetolil Beds, Upper Unit" -> lower_laetolil
        # Note that lower_laetolil is a variable pointing to "Laetolil Beds, Lower Unit". If we decided it is better
        # to label this level "Lower Laetolil Beds" we can simply update the variable.
        try:
            gcn = gcn_dict[gcn]
        except KeyError:  # If the value in gcn is not in the dictionary we just move on.
            pass

        # Assign to field and save
        f.geological_context_name = gcn
        f.save()

    # Fix three specimens that have incorrect geological context and locality info
    # ['EP 900/98', 'EP 901/98', 'EP 902/98']
    fossils = Fossil.objects.filter(catalog_number__in=['EP 900/98', 'EP 901/98', 'EP 902/98'])
    if fossils.count() == 3:  # should have three matches
        fossils.update(geological_context_name=upper_ngaloba)  # update does not require save

    # Fix one specimen with incorrect geological context info
    # EP EP 4337/00
    ep433700 = Fossil.objects.get(verbatim_specimen_number='EP 4337/00')
    ep433700.geological_context_name = upper_laetolil+", Between Tuffs 6 - 7"
    ep433700.save()

    # Fix three specimens with incorrect geological context info
    # EP 717/01 - 719/01
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=['EP 717/01', 'EP 718/01', 'EP 719/01'])
    if fossils.count() == 3:  # should have three matches
        fossils.update(geological_context_name=upper_laetolil+", Between Tuffs 5 - 7")  # update does not require save

    # Fix one specimen with incorrect gcn
    # EP 080/05
    fossil = Fossil.objects.get(verbatim_specimen_number='080/05')
    fossil.geological_context_name = upper_laetolil+", Between Tuff 7 - Just Above Tuff 8"
    fossil.save()

    # Fix two specimens with incorrect gcn
    fossils_list = ['EP 949/01', 'EP 950/01']
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=fossils_list)
    fossils.update(geological_context_name=upper_laetolil+", Between Tuffs 7 - 8")

    # Fix three specimens EP 717-719/01
    fossils_list = ['EP 717/01', 'EP 718/01', 'EP 719/01']
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=fossils_list)
    fossils.update(geological_context_name=upper_laetolil + ", Between Tuffs 5 - 7")

    # Fix two specimens with imprecise geological context
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=['EP 2025/00', 'EP 2026/00'])
    if fossils.count() == 2:
        fossils.update(geological_context_name=lower_laetolil)

    # Fix specimens with verbatim horizon == 'Modern'
    for k in moderns_update_dict.keys():  # modern_update_dict defined at top of file
        if moderns_update_dict[k] != 'Modern':
            f = Fossil.objects.get(catalog_number=k)
            comment = 'Restored verbatim horizon from hard copy catalog to geological context. Possibly modern?'
            f.remarks = (f.remarks + " " if f.remarks else "") + comment
            f.geological_context_name = moderns_update_dict[k]
        f.save()

    # Fix specimens from Emboremony 1
    emb_specimens = ['EP 1545/00', 'EP 1539/00', 'EP 1540/00', 'EP 1541/00', 'EP 1542/00', 'EP 1543/00', 'EP 1544/00']
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=emb_specimens)
    fossils.update(geological_context_name=lower_laetolil)

    fossils = Fossil.objects.filter(locality_name='Emboremony 1').filter(geological_context_name=upper_ndolanya)
    fossils.update(geological_context_name=upper_ngaloba)

    # Fix specimen from Emboremony 2
    # All specimens from Laetolil Beds are Lower Laetolil.
    fossils = Fossil.objects.filter(locality_name='Emboremony 2').filter(geological_context_name=upper_laetolil)
    fossils.update(geological_context_name=lower_laetolil)

    fossils_list = ['EP 358/99', 'EP 360/99', 'EP 361/99', 'EP 362/99']
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=fossils_list)
    fossils.update(geological_context_name=upper_ngaloba)

    # Update specimens from Locality 17
    # All specimens from Locality 17 are from Laetolil Beds, Upper Unit, Between Tuffs 7 - 8
    fossils = Fossil.objects.filter(locality_name='laetoli 17')
    fossils.update(geological_context_name=upper_laetolil+", Between Tuffs 7 - 8")

    # Update specimens from Locality 10E NE
    fossil_list = ['EP 404 / 98', 'EP 405 / 98', 'EP 406 / 98', 'EP 407 / 98', 'EP 408 / 98', 'EP 409 / 98',
                   'EP 410 / 98', 'EP 411 / 98']
    loc10 = Fossil.objects.filter(verbatim_specimen_number__in=fossil_list)
    loc10.update(geological_context_name=upper_laetolil+", Between Tuffs 5 - 7")

    # Fix specimens from Naibadad Beds
    nb_specimens = ['EP 1123/03', 'EP 1124/03', 'EP 1125/03', 'EP 1503/98', 'EP 1529/04', 'EP 1530/04',
                    'EP 1531/04', 'EP 1641/98', 'EP 2348/03', 'EP 2349/03', 'EP 2350/03', 'EP 2351/03',
                    'EP 2352/03', '249/05', '250/05', 'EP 493/01', 'EP 931/04', 'EP 932/04', 'EP 933/04',
                    'EP 934/04', 'EP 935/04', 'EP 936/04', 'EP 937/04', 'EP 938/04', 'EP 939/04', 'EP 940/04',
                    'EP 941/04', 'EP 942/04', 'EP 943/04', 'EP 944/04', 'EP 945/04', 'EP 946/04', 'EP 947/04',
                    'EP 948/04', 'EP 949/04', 'EP 950/04', 'EP 951/04', 'EP 952/04', 'EP 953/04', 'EP 954/04',
                    'EP 955/04']+['EP 2145/00', 'EP 2061/00', 'EP 2061B/00', 'EP 2062/00', '1163/05', '1164/05',
                                  '1172/05', '1173/05', '1174/05']
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=nb_specimens)
    fossils.update(geological_context_name=naibadad)

    # Create or link to Context objects
    for f in Fossil.objects.all():
        c, created = Context.objects.get_or_create(name=f.geological_context_name)
        f.context = c
        f.save()


def update_description():
    """
    description and item count = verbatim_element
    starting with ca 4000 unique entries
    :return:
    """
    print("Updating description and item_count")
    # Many entries are suffixed with (N) indicating the number of items. Since N differs each is uniuqe.
    # Start by splitting out item counts
    ic_re = re.compile(r'(?P<desc>[\w\s./+-]*)(?P<count>[(]\d{1,3}[)])\s*$')
    for f in Fossil.objects.all():
        m = ic_re.match(f.verbatim_element)
        if m:
            c = m.group('count')  # (14)
            f.item_count = c.replace('(', '').replace(')', '')
            d = m.group('desc')  # shells
            f.description = d
        else:
            f.description = f.verbatim_element
            f.item_count = 1
        f.description = f.description.strip().lower()
        f.description = f.description.replace('w/', ' ')
        f.description = f.description.replace('with', ' ')
        f.description = f.description.replace('m/', 'meta')
        f.description = f.description.replace('mandibular fragment', 'mandible fragment')
        f.description = f.description.replace('max fragment', 'maxilla fragment')
        f.description = f.description.replace('prox ', 'proximal ')
        f.description = f.description.replace('dist ', 'distal ')
        f.description = f.description.replace('frag ', 'fragment ')
        f.description = f.description.replace(' frag', ' fragment')
        f.description = f.description.replace('mand ', 'mandible ')
        f.description = f.description.replace('vert ', 'vertebra ')
        f.description = f.description.replace('centra', 'centrum')
        f.description = f.description.replace('tust ', 'tusk ')
        f.description = f.description.replace('rightupper', 'right upper')
        f.description = f.description.replace('rightlower', 'right lower')
        f.description = f.description.replace('leftupper', 'left upper')
        f.description = f.description.replace('leftlower', 'left lower')
        f.description = f.description.replace('.', '')
        f.description = f.description.replace('   ', ' ')
        f.description = f.description.replace('  ', ' ')
        f.description = f.description.strip()
        f.save()


def update_taxon_fields(qs=Fossil.objects.all(), verbose=True):
    """
    Function to read values from verbatim taxon field (e.g. verbatim_kingdom, etc.) clean the entries and
    write them to the taxonomic fields (e.g. tkingdom). All taxon fields start with 't' to avoid conflicts
    with python keywords (e.g. class, order). The function also updates the
    identification_qualifier field.
    :return:
    """
    print("Updating taxonomic fields")
    krep = {
        # Kingdom
        'Animaliav': 'Animalia',
        'Animvalia': 'Animalia',
        # Phylum
        'Vertebratav': 'Vertebrata',
        'Mollosca': 'Mollusca',
        # Class
        'INSECTA': 'Insecta',
        'insecta': 'Insecta',
        # Order
        'Perrisodactyla': 'Perissodactyla',
        'Perrissodactyla': 'Perissodactyla',
        'cf. Reptilia': '',
        'Cricetidae': 'Rodentia',
    }

    frep = {
        '----': '',
        'Boidae': 'Bovidae',
        'Cercopithecidae - Colobinae': 'Cercopithecidae',
        'Chameleonidae': 'Chamaeleonidae',
        'Colobinae': 'Cercopithecidae',
        'Deinotherium': 'Deinotheriidae',
        'Endiae': 'Enidae',
        'Gerbilinae': 'Muridae',
        'Hyaendae': 'Hyaenidae',
        'Hyaneidae': 'Hyaenidae',
        'Orycteropidae': 'Orycteropodidae',
        'Proboscidean': 'Proboscidea',
        'Rhioncerotidae': 'Rhinocerotidae',
        'Scarabeidae': 'Scarabaeidae',
        'Suidea': 'Suidae',
        'Testudinae': 'Testudinidae',
        'Thryonomidae': 'Thryonomyidae',
        'Urocylidae': 'Urocyclidae',
        'Not Bovidae': '',
        'See Below': '',
        'unknown': '',
    }

    trep = {
        'Alcelapini': 'Alcelaphini',
        'Neortragini': 'Neotragini',
        'HIppotragini': 'Hippotragini',
        'Hippogtragini': 'Hippotragini',
        'Hipportagini': 'Hippotragini',
        'Hippotragin': 'Hippotragini',
        'Not Alcelaphini': '',
        'AWG': '',
        'Probably': '',
        'probably': '',
        'see below': '',
    }

    grep = {
        # remove id quals.
        'Cf.': 'cf.',
        ',': '',
        'Sp.': '',
        'Gen. Et': '',
        'Incertae': '',
        'As On Bag Label': '',
        'Large Mammal': '',
        'probably': '',
        'see below': '',
        'See Comments': '',
        'see comments': '',
        'Serpentes': '',
        'small sp.': '',
        # corrections
        'Awg - Probably Gazella Kohllarseni': 'Gazella',
        'Aepyceros probably': 'Aepyceros',
        'Aepyceros probably ': 'Aepyceros',
        'Anacus': 'Anancus',
        'Antidorcus': 'Antidorcas',
        'Antidorcas Or Gazella': 'Antidorcas or Gazella',
        'Connohaetes': 'Connochaetes',
        'Euonyma Leakey 1': 'Euonyma',
        'Eurgynathohippus': 'Eurygnathohippus',
        '"Gazella"': 'Gazella',
        '"Gazella "': 'Gazella',
        'Geochelonel': 'Geochelone',
        'Girafffa': 'Giraffa',
        'Hipportagus': 'Hippotragus',
        'Loxondonta': 'Loxodonta',
        'Orcyteropus': 'Orycteropus',
        'oryx': 'Oryx',
        'Parmualarius': 'Parmularius',
        'Parmualrius': 'Parmularius',
        'Parmularis': 'Parmularius',
        'Scaraboidea': '',
        'Sergetilagus': 'Serengetilagus',
        'serengetilagus': 'Serengetilagus',
        'Sublona': 'Subulona',
        'Trochananina': 'Trochonanina',
        'Rhynchocyon pliocaenicus': 'Rhynchocyon',
    }

    srep = {
        'Cf.': 'cf.',
        'no det.': 'indet.',
        'probably': '',
        '-': '',
        's[/': '',
        'Indet..': 'indet.',
        'large mammal': '',
        'sedis': '',
        'aviflumminis': 'avifluminis',
        'brachygularis': 'brachygularius',
        'cf maurusium': 'cf. maurusium',
        'exopata': 'exoptata',
        'gambaszoegensis': 'gombaszoegensis',
        'janenshchi': 'janenschi',
        'janeschi': 'janenschi',
        'kohlarseni': 'kohllarseni',
        'kohllarseni V': 'kohllarseni',
        'laeotoliensis': 'laetoliensis',
        'laeotolilensis': 'laetoliensis',
        'laetolilensis': 'laetoliensis',
        'palaegracilis': 'palaeogracilis',
        'paleogracilis': 'palaeogracilis',
        'serpentes': '',
        'small mammal': '',
        'small rodent': '',

    }

    p_re = re.compile(r'[(].+[)]')  # matches anything in parentheses

    def clean_taxon_field(obj, verbatim_taxon_field_name, rep_dict):
        if verbose:
            print("Cleaning {}".format(verbatim_taxon_field_name))
        fs = getattr(obj, verbatim_taxon_field_name)  # get value for taxon field
        if fs:
            fs = fs.strip()  # get verbatim value, remove leading and trailing spaces
            fs = p_re.sub('', fs)  # remove parenthetical
            fs = multireplace(fs, rep_dict)  # fix random misspellings and typos
            fs, idq = update_idq(fs)  # parse entries for identification qualifiers.
            if idq:  # if ident. qualifiers are found, update record.
                setattr(obj, 'identification_qualifier', idq)
            # clean any excess whitespace
            fs = fs.replace('   ', ' ')  # remove triple spaces
            fs = fs.replace('  ', ' ')  # remove double spaces
            fs = fs.strip()  # remove leading and trailing spaces

        if fs in ['', ' ', None]:  # convert any blanks to None
            fs = None
        return fs

    def update_tsubphylum(obj):
        if obj.tphylum == 'Vertebrata':
            obj.tsubphylum = obj.tphylum
            obj.tphylum = 'Chordata'
        elif obj.tphylum == 'Hexapoda':
            obj.tsubphylum = obj.tphylum
            obj.tphylum = 'Arthropoda'

    def clean_higher_taxonomy():
        if verbose:
            print("Fixing higher taxonomic entries")

        # Update Subfamily entries recorded in Family column
        fossils = Fossil.objects.filter(verbatim_family__contains='inae')
        for f in fossils:
            f.tsubfamily = f.verbatim_family
            f.tsubfamily = f.tsubfamily.replace('Cercopithecidae - Colobinae', 'Colobinae')
            f.taxon_rank = "subfamily"
            f.save()

        # Fix phylum, subphylum for Insectivora
        fixes = Fossil.objects.filter(verbatim_class='Mammalia').filter(verbatim_phylum_subphylum='Arthropoda')
        fixes.update(tphylum='Chordata')
        fixes.update(tsubphylum='Vertebrata')

        # Fix vertebrate gastropods
        fixes = Fossil.objects.filter(verbatim_class='Gastropoda').filter(verbatim_phylum_subphylum='Vertebrata')
        fixes.update(tphylum='Mollusca')
        fixes.update(tsubphylum=None)

        # Fix missing Order
        fixes = Fossil.objects.filter(verbatim_order='').filter(verbatim_family='Bovidae')
        fixes.update(torder='Artiodactyla')

        # Fix Canis missing familly
        fixes = Fossil.objects.filter(verbatim_family=None, verbatim_species='brevirostris')
        fixes.update(tfamily='Canidae')

        # Fix mammal coleoptera
        fixes = Fossil.objects.filter(verbatim_class='Mammalia', verbatim_order='Coleoptera')
        fixes.update(tphylum='Arthropoda')
        fixes.update(tsubphylum='Hexapoda')
        fixes.update(tclass='Insecta')

        # Update bovid tribes where absent
        fixes = Fossil.objects.filter(verbatim_genus__contains='Connochaetes', verbatim_tribe__in=['', ' ', None])
        fixes.update(ttribe='Alcelaphini')

        fixes = Fossil.objects.filter(verbatim_genus__contains='Gazella', verbatim_tribe__in=['', ' ', None])

    def fix_unique():
        if verbose:
            print("Fixing unique problems in taxoomic fields")

        # Fix EP 297/05  verbatim_class = 'Mammalia' but verbatim_order = 'Reptilia ?'
        # Move order entry to taxonomic notes
        f = Fossil.objects.get(catalog_number='EP 297/05')
        if f.taxon_remarks:
            f.taxon_remarks += ' ' + f.verbatim_order  # copy order entry to taxonomic remarks
        else:
            f.taxon_remarks = f.verbatim_order
        if f.torder:
            f.torder = None  # remove from torder field
        f.save()

        # Fix EP 3613/00 verbatim_order='Equidae (Th)' and verbatim_family is ''. Move entry to tfamily
        f = Fossil.objects.get(catalog_number='EP 3613/00')
        f.torder = 'Perissodactyla'
        f.tfamily = 'Equidae'
        f.save()

        # Fix EP 008/03 verbatim_order = 'Reptilia'
        f = Fossil.objects.get(catalog_number='EP 008/03')
        f.torder = None
        f.save()

        # Fix EP 1548/98, EP 2265/00  ttribe = 'Hippotragini Or Alcelaphini'
        fossils = Fossil.objects.filter(ttribe='Hippotraginii Or Alcelaphini')
        for f in fossils:
            # move tribe to taxon_remarks
            if f.taxon_remarks:
                f.taxon_remarks += ' ' + f.ttribe
            else:
                f.taxon_remarks = f.ttribe
            # clear tribe
            f.ttribe = None
            f.save()

        # Fix EP 2045/00 ttribe = 'Not Neotragini'
        fossils = Fossil.objects.filter(ttribe='Not Neotragini')
        for f in fossils:
            # move tribe to taxon_remarks
            if f.taxon_remarks:
                f.taxon_remarks += ' ' + f.ttribe
            else:
                f.taxon_remarks = f.ttribe
            # clear tribe
            f.ttribe = None
            f.save()

        # Fix 5 items with tgenus = 'Antidorcas or Gazella'
        fossils = Fossil.objects.filter(tgenus='Antidorcas or Gazella')
        for f in fossils:
            # move genus to taxon_remarks
            if f.taxon_remarks:
                f.taxon_remarks += ' ' + f.tgenus
            else:
                f.taxon_remarks = f.tgenus
            # clear genus
            f.tgenus = None
            f.save()

        # Fix EP 575/00 genus = Machairodontinae
        ep575 = Fossil.objects.get(catalog_number='EP 575/00')
        ep575.tsubfamily = ep575.tgenus
        ep575.tgenus = None
        ep575.save()

        # Fix frame shift error for EP 243/05
        ep243 = Fossil.objects.get(catalog_number='EP 243/05')
        ep243.order = 'Rodentia'
        ep243.family = 'Cricetidae'
        ep243.subfamily = 'Gerbillinae'
        ep243.save()

        # Fix taxon comments and species for EP 688/98
        f = Fossil.objects.get(catalog_number='EP 688/98')
        f.tspecies = 'kohllarseni'
        remark_string = 'Awg - Probably Gazella Kohllarseni'
        if f.taxon_remarks:
            f.taxon_remarks += ' ' + remark_string
        else:
            f.taxon_remarks = remark_string
        f.save()

        # Fix taxon field for EP 1542/00. Verbatim taxon fields show mix of Urocyclidaae and Achatinidae
        # Urocyclidae was moved to EP 1543/00, need  to fix taxon field for EP 1542/00
        ep1542 = Fossil.objects.get(catalog_number='EP 1542/00')
        update_dict_1542_achatina = {
            'item_count': 2,
            'tfamily': 'Achatinidae',
            'tgenus': 'Achatina',
            'tspecies': 'zanzibarica',
            'scientific_name': 'Achatina zanzibarica',
            'taxon_rank': 'species',
        }
        ep1542 = update_from_dict(ep1542, update_dict_1542_achatina)
        remark_string = 'Urocyclidae moved to 1543/00'
        if ep1542.remarks:
            ep1542.remarks += ' ' + remark_string
        else:
            ep1542.remarks = remark_string
        ep1542.save()

        # Fix species and genus names for EP 1406/98 verbatim species is cf. lycaeon
        ep1406 = Fossil.objects.get(catalog_number='EP 1406/98')
        ep1406.tgenus = 'Lycaon'
        ep1406.tspecies = None
        ep1406.identification_qualifier = 'cf. Lycaon'
        ep1406.save()

        # Fix genus and species names for EP 529/03
        ep529 = Fossil.objects.get(catalog_number='EP 529/03')
        ep529.tgenus = None
        ep529.tspecies = None
        ep529.save()

        # Fix EP 1905/00, has verbatim genus = Modern Hartebeest
        # This is a comment added by Alan Gentry and needs to be moved to the Taxon remarks field.
        ep1905 = Fossil.objects.get(verbatim_specimen_number='EP 1905/00')
        tr = ep1905.taxon_remarks
        vg = ep1905.verbatim_genus
        if vg:
            # append vg if prior remarks present, add vg if no prior remarks
            ep1905.taxon_remarks = (tr + " " if tr else "") + vg
            # update genus
            ep1905.tgenus = None
        ep1905.save()

        # Fix Taxon fields for splits
        update_dict = {
            'EP 1280a/01': {
                'item_count': 2,
                'tfamily': 'Achatinidae',
                'tgenus': 'Achatina',
                'tspecies': 'zanzibarica',
                'scientific_name': 'Achatina zanzibarica',
                'taxon_rank': 'species',
            },
            'EP 1280b/01': {
                'item_count': 5,
                'tfamily': 'Subulinidae',
                'tgenus': 'Pseudoglessula',
                'tspecies': 'gibbonsi',
                'scientific_name': 'Pseudoglessula gibbonsi',
                'identification_qualifier': 'cf. gibbonsi',
                'taxon_rank': 'species',
            },
            'EP 3129a/00': {
                'item_count': 8,
                'tfamily': 'Achatinidae',
                'tgenus': 'Achatina',
                'tspecies': 'zanzibarica',
                'scientific_name': 'Achatina zanzibarica',
                'taxon_rank': 'species',
            },
            'EP 3129b/00': {
                'item_count': 1,
                'tfamily': 'Subulinidae',
                'tgenus': 'Pseudoglessula',
                'tspecies': 'gibbonsi',
                'scientific_name': 'Pseudoglessula gibbonsi',
                'identification_qualifier': 'cf. Pseudoglessula gibbonsi',
                'taxon_rank': 'species',
            },
            'EP 1181a/00': {
                'item_count': 1,
                'tgenus': 'Achatina',
                'tspecies': 'zanzibarica',
                'scientific_name': 'Achatina zanzibarica',
                'taxon_rank': 'species',
            },
            'EP 1181b/00': {
                'item_count': 1,
                'tgenus': 'Burtoa',
                'tspecies': 'nilotica',
                'scientific_name': 'Burtoa nilotica',
                'taxon_rank': 'species',
            },
            'EP 3635a/00': {
                'item_count': 1,
                'tgenus': 'Achatina',
                'tspecies': 'zanzibarica',
                'scientific_name': 'Achatina zanzibarica',
                'taxon_rank': 'species',
            },
            'EP 3635b/00': {
                'item_count': 8,
                'tgenus': 'Limicolaria',
                'tspecies': 'martensiana',
                'scientific_name': 'Limicolaria martensiana',
                'taxon_rank': 'species',
            },
            'EP 1177a/00': {
                'item_count': 1,
                'tgenus': 'Stigmochelys',
                'tspecies': 'brachygularis',
                'scientific_name': 'Stigmochelys brachygularis',
                'taxon_rank': 'species',
                'description': 'nuchal bone',
            },
            'EP 1177b/00': {
                'item_count': 1,
                'tgenus': 'Stigmochelys',
                'tspecies': 'brachygularis',
                'scientific_name': 'Stigmochelys brachygularis',
                'taxon_rank': 'species',
                'description': 'xiphiplastron',
            },
            'EP 1177c/00': {
                'item_count': 1,
                'tgenus': 'Stigmochelys',
                'tspecies': 'brachygularis',
                'scientific_name': 'Stigmochelys brachygularis',
                'taxon_rank': 'species',
                'description': 'fragment of carapace',
            }
        }
        for catno in update_dict.keys():
            if Fossil.objects.filter(catalog_number=catno):
                fossil = Fossil.objects.get(catalog_number=catno)
                fossil = update_from_dict(fossil, update_dict[fossil.catalog_number])
                fossil.save()

    # Update taxon columns
    for record in qs:  # cleans only records in qs
        if verbose:
            print("cleaning taxon fields for {}".format(record.catalog_number))
        record.tkingdom = clean_taxon_field(record, 'verbatim_kingdom', krep)
        record.tphylum = clean_taxon_field(record, 'verbatim_phylum_subphylum', krep)
        update_tsubphylum(record)
        record.tclass = clean_taxon_field(record, 'verbatim_class', krep)
        record.torder = clean_taxon_field(record, 'verbatim_order', krep)
        record.tfamily = clean_taxon_field(record, 'verbatim_family', frep)
        record.ttribe = clean_taxon_field(record, 'verbatim_tribe', trep)
        record.tgenus = clean_taxon_field(record, 'verbatim_genus', grep)
        record.tspecies = clean_taxon_field(record, 'verbatim_species', srep)
        record.save()
    clean_higher_taxonomy()
    fix_unique()  # works on entire DB and fixes specific records


def update_scientific_name_taxon_rank(qs=Fossil.objects.all()):
    print("Updating scientific name and taxon rank")
    for f in qs:
        if f.tspecies:
            f.taxon_rank = "species"
            f.scientific_name = str(f.tgenus) + ' ' + f.tspecies  # assumes f.tgenus
        elif f.tgenus:
            f.taxon_rank = "genus"
            f.scientific_name = f.tgenus
        elif f.ttribe:
            f.taxon_rank = "tribe"
            f.scientific_name = f.ttribe
        elif f.tsubfamily:
            f.taxon_rank = "subfamily"
            f.scientific_name = f.tsubfamily
        elif f.tfamily:
            f.taxon_rank = "family"
            f.scientific_name = f.tfamily
        elif f.torder:
            f.taxon_rank = "order"
            f.scientific_name = f.torder
        elif f.tclass:
            f.taxon_rank = "class"
            f.scientific_name = f.tclass
        elif f.tsubphylum:
            f.taxon_rank = "subphylum"
            f.scientific_name = f.tsubphylum
        elif f.tphylum:
            f.taxon_rank = "phylum"
            f.scientific_name = f.tphylum
        elif f.tkingdom:
            f.taxon_rank = "kingdom"
            f.scientific_name = f.tkingdom
        f.save()


def update_idq(rts):
    """
    Function to update the identification qualifier field when appropriate.
    This function searches a taxonomic string for Open Nomenclature abbreviations (e.g. cf. aff. sp. indet.)
    If found the string is excised from the taxon field and the verbatim taxon field is copied to
    the identification qualifier field.
    Darwin Core stipulates that all notations about taxonomic uncertainty are limited to the
    identificationQualifier field.
    Example: if verbatim_genus == cf. Australopithecus,
    tgenus = Australopithecus, identification_qualifier = cf. Australopithecus
    :param rts: The raw taxanomic string, e.g. 'cf. major'
    :return: returns the cleaned taxon string and the identification qualifier string
    """
    idq = None
    ts = rts.strip()
    # regex matches all of the following:
    # test_list = ['? major', '?major', 'aff. major', 'Nov. sp.', 'indet', 'Indet.', 'cf.', 'Cf', 'cf. major', 'sp.',
    #             'Sp.', 'sp', 'Sp', ' sp.', 'major sp. nov.', 'sp. A', 'sp. A, sp. B', 'major']
    idqls = re.compile(r'^large sp.$|^small sp.$|[Ii]ndeterminate')
    ndetre = re.compile(r'[Nn]o [Dd]et[.]*[ her]*')
    noidre = re.compile(r'[nN][oO] [iI][dD]')
    idqre = re.compile(r'[sS]p[.]?.*|[cC]f[.]?|[iI]ndet[.]?|Nov[.]?.*|[Aa]ff[.]? |[?]|no det.')
    if ts:
        if idqls.search(ts):
            idq = ts
            ts = idqls.sub('', ts)
        elif noidre.search(ts):
            idq = ts
            ts = noidre.sub('', ts)
        elif ndetre.search(ts):
            idq = ts
            ts = ndetre.sub('', ts)
        elif idqre.search(ts):
            idq = ts
            ts = idqre.sub('', ts)
    return ts, idq


def test_idq():
    """
    Function to test update_idq
    :return: Prints results to a string for each test case in the test_list.
    """
    test_list = ['? major', '?major', 'aff. major', 'Nov. sp.',
                 'indet', 'Indet.', 'no det.', 'Indeterminate', 'major no det.',
                 'cf.', 'Cf', 'cf. major',
                 'large sp.', 'small sp.',
                 'sp.', 'Sp.', 'sp', 'Sp', ' sp.', 'major sp. nov.', 'sp. A', 'sp. A, sp. B',
                 'major', 'Giraffa', 'spirellia']
    for t in test_list:
        t, i = update_idq(t)
        print(str(t)+' |  '+str(i))


def update_taxon_remarks(verbose=False):
    """
    Procedure to update taxon_remarks
    Copies existing data to taxon_remarks from verbatim_other
    Appends parenthetical comments from verbatim_tribe
    :return:
    """
    print("Updating taxon remarks")
    p_re = re.compile(r'[(].+[)]')  # matches anything in parentheses
    print("Updating taxon_remarks from verbatim_other")
    for f in Fossil.objects.all():
        if f.verbatim_other:
            if verbose:
                print("Updating {}".format(f.catalog_number))
            if f.taxon_remarks:
                f.taxon_remarks += ' ' + f.verbatim_other
            else:
                f.taxon_remarks = f.verbatim_other

        # Check for parenthetical and copy to taxon_remarks
        vt = f.verbatim_tribe
        m = p_re.search(vt)  # check if parenthetical
        if m:  # if entry has parenthetical
            if f.taxon_remarks:
                f.taxon_remarks += ' ' + m.group(0)  # append parenthetical to taxon_remarks
            else:
                f.taxon_remarks = m.group(0)  # append parenthetical to taxon_remarks
        # Move Not bovid remarks
        if f.verbatim_family == 'Not Bovidae (Awg)':
            if f.taxon_remarks:
                f.taxon_remarks += f.verbatim_family
            else:
                f.taxon_remarks = f.verbatim_family

        f.save()


def update_disposition():
    """
    Copy data from verbatim_storage into disposition
    :return:
    """
    print("Updating disposition from verbatim_storage")
    for fossil in Fossil.objects.all():
        fossil.disposition = fossil.verbatim_storage
        fossil.save()


def update_problems():
    print("Updating problems")
    # Get only non empty records and exclude those containing the word duplicate.
    # Duplicates have been cleaned and validated elsewhere.
    for f in Fossil.objects.exclude(verbatim_problems__in=['']).exclude(verbatim_problems__icontains='duplicate'):
        # Must check if problem has been flagged by other import functions
        if f.verbatim_problems and not f.problem:
            f.problem = True
            # append problem comment
            if f.problem_comment:
                f.problem_comment = f.problem_comment + ' ' + f.verbatim_problems
            else:
                f.problem_comment = f.verbatim_problems
        elif f.verbatim_problems and f.problem:
            # append problem comment
            if f.problem_comment:
                f.problem_comment = f.problem_comment + ' ' + f.verbatim_problems  # append comment
            else:
                f.problem_comment = f.verbatim_problems
        else:
            pass  # If no verbatim_problems do nothing
        f.save()


# Functions for validating data
def validate_catalog_number():
    """
    Test that all catalog numbers conform to consistant pattern
    EP NNN/YY or EP NNNp/YY; where NNN is a three-four digit integer specimens number, YY is the year and p is an
    optional part letter. Examples: 001/98, 1774/04, 1232a/99. Specimen number less than 100 all have leading
    zeros to hundreds place.
    """
    print("Validating catalog_number")
    # regular expression to test proper format of catalog numbers
    cat_re = re.compile(r'EP \d{3,4}[a-zA-Z]?/[09][01234589]$')
    # list of catalog_number column in db. The values_list function is built into django
    catalog_list = list(Fossil.objects.values_list('catalog_number', flat=True))
    # Test catalog numbers against re
    re_errors_list = [item for item in catalog_list if not cat_re.match(item)]
    duplicate_list = [item for item, count in collections.Counter(catalog_list).items() if count > 1]

    # Pretty print format errors

    if re_errors_list:
        print("\nFormat Errors\n---------------------")
        for f in re_errors_list:
            print("Format error in catalog number {}".format(f))
    # else:
    #     print("No formatting errors found.")

    # Pretty print duplicates
    if duplicate_list:
        print("\nDuplicate Summary\n---------------------")
        for duplicate_catalog_number in duplicate_list:
            print("Duplicate catalog number {}".format(duplicate_catalog_number))
            duplicate_qs = Fossil.objects.filter(catalog_number=duplicate_catalog_number)
            for d in duplicate_qs:
                print('id:{}  loc:{}  desc:{}  taxon:{}'.format(d.id,
                                                                d.locality_name,
                                                                d.description,
                                                                d.scientific_name))
    # Validate individual changes
    # Check EP 120/98
    ep120 = Fossil.objects.get(verbatim_specimen_number='EP 120A+B/98')
    if ep120.catalog_number != 'EP 120/98':
        print('Update error {}'.format(ep120.catalog_number))

    # Check EP 507/05
    ep507 = Fossil.objects.get(verbatim_specimen_number='507/07')
    if ep507.catalog_number != 'EP 507/05':
        print('Update error {}'.format(ep507.catalog_number))

    # Check EP 756/05
    ep756 = Fossil.objects.get(verbatim_specimen_number='756/06')
    if ep756.catalog_number != 'EP 756/05':
        print('Update error {}'.format(ep756.catalog_number))

    # Check EP 1975/03
    ep1975 = Fossil.objects.get(verbatim_specimen_number='EP 1075/03', verbatim_genus='Serengetilagus')
    if ep1975.catalog_number != 'EP 1975/03':
        print('Update error {}'.format(ep1975.catalog_number))

    # Check EP 348/04
    ep349 = Fossil.objects.get(verbatim_specimen_number='EP 348/04', verbatim_element='Distal radius')
    if ep349.catalog_number != 'EP 349/04':
        print('Update error {}'.format(ep349.catalog_number))

    # Check EP 2188/99 -> 2188/03 and 2188/00
    ep2188_03 = Fossil.objects.get(verbatim_specimen_number='EP 2188/99', verbatim_element='distal humerus')
    if ep2188_03.catalog_number != 'EP 2188/03':
        print('Update error {}'.format(ep2188_03.catalog_number))

    ep2188_00 = Fossil.objects.get(verbatim_specimen_number='EP 2188/99', verbatim_element='Lumbar Vertebral Centrum')
    if ep2188_00.catalog_number != 'EP 2188/00':
        print('Update error {}'.format(ep2188_00.catalog_number))

    # Check EP 1905/00
    ep1905 = Fossil.objects.get(verbatim_specimen_number='EP 1905/00')
    if ep1905.tgenus:
        print('Update error {}'.format(ep1905.catalog_number))
    if ep1905.scientific_name != 'Alcelaphini':
        print('Update error {}'.format(ep1905.catalog_number))
    if not ep1905.taxon_remarks:
        print('Update error {}'.format(ep1905.catalog_number))


def validate_splits():
    """
    Validate correct catalog numbers for splits.
    :return:
    """
    print("Validating catalog numbers for splits")
    splits = SPLITS
    valid = True
    for catno in splits:
        try:
            Fossil.objects.get(catalog_number=catno)  # will raise error if splits don't exist.
        except ObjectDoesNotExist:
            pass
        except MultipleObjectsReturned:
            print("Split error {}".format(catno))
            valid = False
        try:
            catnoa = catno.replace('/', 'a/')
            Fossil.objects.get(catalog_number=catnoa)
        except ObjectDoesNotExist:
            print("Split error {}".format(catnoa))
            valid = False
        try:
            catnob = catno.replace('/', 'b/')
            Fossil.objects.get(catalog_number=catnob)
        except ObjectDoesNotExist:
            print("Split error {}".format(catnob))
            valid = False
    try:
        Fossil.objects.get(catalog_number='EP 1177a/00')
    except ObjectDoesNotExist:
        print("Split error {}".format('EP 1177a/00'))
        valid = False
    try:
        Fossil.objects.get(catalog_number='EP 1177b/00')
    except ObjectDoesNotExist:
        print("Split error {}".format('EP 1177b/00'))
        valid = False
    try:
        Fossil.objects.get(catalog_number='EP 1177c/00')
    except ObjectDoesNotExist:
        print("Split error {}".format('EP 1177c/00'))
        valid = False
    if valid:
        pass
        # print("No split errors found.")


def validate_area():
    kakesio_list = ['Kakesio 1', 'Kakesio 2', 'Kakesio 3', 'Kakesio 4', 'Kakesio 5', 'Kakesio 6', 'Kakesio 7',
                    'Kakesio 8', 'Kakesio 9', 'Kakesio 10', 'Kakesio 1-6', 'Kakesio South', 'Kakesio 2-4',
                    'Lobileita', 'Emboremony 1', 'Emboremony 2', 'Emboremony 3']

    esere_list = ['Engesha', 'Esere 1', 'Esere 2', 'Esere 3', 'Noiti 1', 'Noiti 3']
    laetoli_list = ['Laetoli 1',
                    'Laetoli 1 Northwest',
                    'Laetoli 10',
                    'Laetoli 10 East',
                    'Laetoli 10 Northeast',
                    'Laetoli 10 West',
                    'Laetoli 11',
                    'Laetoli 12',
                    'Laetoli 12 East',
                    'Laetoli 13',
                    'Laetoli 13 "Snake Gully"',
                    'Laetoli 14',
                    'Laetoli 15',
                    'Laetoli 16',
                    'Laetoli 17',
                    'Laetoli 18',
                    'Laetoli 19',
                    'Laetoli 2',
                    'Laetoli 20',
                    'Laetoli 21',
                    'Laetoli 21 And 21 East',
                    'Laetoli 22',
                    'Laetoli 22 East',
                    'Laetoli 22 South',
                    'Laetoli 22 South Nenguruk Hill',
                    'Laetoli 23',
                    'Laetoli 24',
                    'Laetoli 3',
                    'Laetoli 4',
                    'Laetoli 5',
                    'Laetoli 6',
                    'Laetoli 7',
                    'Laetoli 7 East',
                    'Laetoli 8',
                    'Laetoli 9',
                    'Laetoli 9 South', 'Olaitole River Gully', 'Silal Artum', 'Garusi Southwest']

    for f in Fossil.objects.all():
        if f.area_name == 'Kakesio' and f.locality_name not in kakesio_list:
            print('Area missmatch for {}'.format(f.catalog_number))
        elif f.area_name == 'Esere-Noiti' and f.locality_name not in esere_list:
            print('Area missmatch for {}'.format(f.catalog_number))
        elif f.area_name == 'Laetoli' and f.locality_name not in laetoli_list:
            print('Area missmatch for {}'.format(f.catalog_number))
        elif f.area_name == 'Oleisusu' and f.locality_name != 'Oleisusu':
            print('Area missmatch for {}'.format(f.catalog_number))
        elif f.area_name == 'Olaltanaudo' and f.locality_name != 'Olaltanaudo':
            print('Area missmatch for {}'.format(f.catalog_number))
        elif f.area_name == 'Ndoroto' and f.locality_name != 'Ndoroto':
            print('Area missmatch for {}'.format(f.catalog_number))


def validate_date_recorded():
    """
    Function to test that all date_recorded values fall between 1998 and 2005.
    :return:
    """
    print("Validating date_recorded")
    result = 1
    for fossil in Fossil.objects.all():
        if fossil.date_recorded:
            if not 1998 <= fossil.date_recorded.year <= 2005:
                print("Fossil is outside date range 1998-2005.")
                result = 0
        else:
            print("Fossil missing date_recorded")
            result = 0
    return result


def validate_locality(verbose=False):
    """
    Validate locality entries against locality vocabulary.
    :return: Prints a listing of the Laetoli locality vocabulary alongside all the verbatim values matched to the
    standardized vocabulary value.
    """
    print("Validating localities")
    locality_list = field_list('locality_name', report=False)
    i = 1
    for loc in locality_list:
        locality_set = set([l.verbatim_locality for l in Fossil.objects.filter(locality_name=loc[0])])
        locality_string = str(locality_set)[1:-1].replace("', ", "'; ")
        area_set = set([l.area_name for l in Fossil.objects.filter(locality_name=loc[0])])
        area_string = '; '.join(area_set)
        if verbose:
            print("{}\t{}\t{}\t{}\t{}".format(i, loc[0], loc[1], area_string, locality_string))
        i += 1

    # Validate updates to two specimens that are missing locality information.
    # ['EP 1308/04', 'EP 1309/04']
    fossils = Fossil.objects.filter(catalog_number__in=['EP 1308/04', 'EP 1309/04'])
    for f in fossils:
        if f.locality_name != 'Laetoli 5':
            print("Locality update error for {}".format(f.catalog_number))

    # Validate updates to Locality 7
    specimen_list = ['EP 807/04', 'EP 808/04', 'EP 809/04', 'EP 810/04', 'EP 811/04', 'EP 812/04', 'EP 813/04',
                     'EP 814/04', 'EP 815/04', 'EP 816/04', 'EP 817/04', 'EP 818/04']
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=specimen_list)
    for f in fossils:
        if f.locality_name != 'Laetoli 7':
            print("Locality update error for {}".format(f.catalog_number))


def validate_taxon_name(taxon_name, taxon_rank, verbose=True):
    api = idigbio.json()
    r = api.search_records(rq={taxon_rank: taxon_name})
    if r['itemCount']:
        if verbose:
            print("{} OK {}".format(taxon_name, r['itemCount']))
    else:
        print("{} ERROR".format(taxon_name))


def validate_taxon_field(taxon_name, verbose=True):
    taxon_field_name = 't'+taxon_name
    # print('Validating {}'.format(taxon_field_name))
    api = idigbio.json()  # connection to idigbio db
    tlist = [t[0] for t in field_list(taxon_field_name, report=False) if t[0]]  # list of taxon names excluding None
    for taxon in tlist:
        # print('validating {}'.format(taxon))
        if taxon_field_name == 'tspecies':
            r = api.search_records(rq={'scientificname': taxon})
        else:
            r = api.search_records(rq={taxon_name: taxon})  # search
        if r:
            if r['itemCount']:
                if verbose:
                    print("{} OK {}".format(taxon, r['itemCount']))
            else:
                print("{} ERROR".format(taxon))
        else:
            pass
            # print("{} ERROR".format(taxon))


def validate_geological_context(verbose=False):
    """
    Validate entries for geological context.
    :return:
    """
    print("Validating geological context")
    r1 = re.compile(r'Between Tuffs 6 - [\d]{2}$')
    gcn_list = field_list('geological_context_name', report=False)
    # count=1
    for gcn in gcn_list:
        # print('checking {}'.format(count))
        # count += 1
        gcn_string = gcn[0]
        if gcn_string:
            if r1.search(gcn_string):
                print("Bad entry for Geological Context: {}".format(gcn_string))

    if verbose:
        for g in Context.objects.all():
            # For every entry in the Context table print the name of the Context followed by a list of
            # all the unique values of verbatim_horizon that were matched to that Context.
            fossils = Fossil.objects.filter(context=g)
            fossils_set = set([f.verbatim_horizon for f in fossils])
            fossils_string = str(fossils_set).replace("', ", "'\n\t").replace("{", "\t").replace("}", "\n")
            print("--{}--".format(g.name))
            print("{}".format(fossils_string))

    # Verify updates to 'EP 900/98', 'EP 901/98', 'EP 902/98'
    fossils = Fossil.objects.filter(catalog_number__in=['EP 900/98', 'EP 901/98', 'EP 902/98'])
    for f in fossils:
        if f.geological_context_name != upper_ngaloba:
            print("Update gcn error for {}".format(f.catalog_number))

    # Verify updates to EP 4337/00
    ep433700 = Fossil.objects.get(catalog_number='EP 4337/00')
    if ep433700.geological_context_name != upper_laetolil+", Between Tuffs 6 - 7":
        print("Update gcn error for "+ep433700.catalog_number)

    # Verify updates to EP 717/01 - 719/01
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=['EP 717/01', 'EP 718/01', 'EP 719/01'])
    for f in fossils:
        if f.geological_context_name != upper_laetolil + ", Between Tuffs 5 - 7":
            print("Update gcn error for {}".format(f.catalog_number))

    # Verify updates to EP 2025/00 and 2026/00
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=['EP 2025/00', 'EP 2026/00'])
    for f in fossils:
        if f.geological_context_name != lower_laetolil:
            print("Update gcn error for {}".format(f.catalog_number))

    # Verify updates to EP 080/05
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=['080/05'])
    for f in fossils:
        if f.geological_context_name != upper_laetolil+", Between Tuff 7 - Just Above Tuff 8":
            print("Update gcn error for {}".format(f.catalog_number))

    # Verify updates to EP 949/01 and EP 950/01
    fossils_list = ['EP 949/01', 'EP 950/01']
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=fossils_list)
    for f in fossils:
        if f.geological_context_name != upper_laetolil+", Between Tuffs 7 - 8":
            print("Update gcn error for {}".format(f.catalog_number))

    # Fix three specimens EP 717-719/01
    fossils_list = ['EP 717/01', 'EP 718/01', 'EP 719/01']
    fossils = Fossil.objects.filter(verbatim_specimen_number__in=fossils_list)
    for f in fossils:
        if f.geological_context_name != upper_laetolil+", Between Tuffs 5 - 7":
            print("Update gcn error for {}".format(f.catalog_number))

    # gcn for specimens with verbatim horizon =  Modern
    for k in moderns_update_dict.keys():  # modern_update_dict defined at top of file
        f = Fossil.objects.get(catalog_number=k)
        if f.geological_context_name != moderns_update_dict[k]:
            print("Update gcn error for {}".format(f.catalog_number))

    # Verify updates to Emboremony 1
    emb1 = Fossil.objects.filter(locality_name='Emboremony 1')
    for f in emb1:
        if f.geological_context_name not in [lower_laetolil, upper_ngaloba]:
            print("Update gcn error for {}".format(f.catalog_number))

    # Verify update to Emboremony 2
    # All fossils should be from Lower Laetolil Beds or Upper Ngaloba Beds
    emb2 = Fossil.objects.filter(locality_name='Emboremony 2')
    for f in emb2:
        if f.geological_context_name not in [lower_laetolil, upper_ngaloba]:
            print("Update gcn error for {}".format(f.catalog_number))

    # Verify specimens from Locality 17
    # All specimens from Locality 17 are from Laetolil Beds, Upper Unit, Between Tuffs 7 - 8
    loc17 = Fossil.objects.filter(locality_name='laetoli 17')
    for f in loc17:
        if f.geological_context_name != upper_laetolil+", Between Tuffs 7 - 8":
            print("Update gcn error for {}".format(f.catalog_number))

    # Verify specimens from Locality 10
    # No specimens shoudl be "Upper Laetolil Beds" only
    loc10 = Fossil.objects.filter(locality_name='laetoli 10 Northeast')
    for f in loc10:
        if f.geological_context_name == upper_laetolil:
            print("Update gcn error for {}".format(f.catalog_number))

    # Verify specimens from Locality 13
    # All fossils listed as Ndolanya Beds at loc 13 should be Naibadad
    loc13 = Fossil.objects.filter(locality_name='Laetoli 13')
    for f in loc13:
        if f.geological_context_name in [upper_ndolanya, upper_ngaloba]:
            print("Update gcn error for {}".format(f.catalog_number))

    # Spot checks
    # There should be no gcn with a ?
    if Fossil.objects.filter(geological_context_name__contains='?').count() > 0:
        print("Update gcn error, ? not updated")


# Main import function
def main(year_list=CSHO_YEARS):
    # import data
    print('Importing data from XL spreadsheets...')
    for year in year_list:
        file = make_file_string(year)
        import_file(folder=FOLDER_PATH, file=file, year=year)
    print('{} records imported'.format(Fossil.objects.all().count()))
    print(hr)

    # delete records
    print('\nDeleting duplicate and erroneous records...')
    c = delete_records()
    print('{} records deleted'.format(c))
    print('Current record count: {}'.format(Fossil.objects.all().count()))
    print(hr)

    # split bulk collections
    print('\nSplitting bulk collections...')
    c = split_records()
    print('{} records split'.format(c))
    print('Current record count: {}'.format(Fossil.objects.all().count()))
    print(hr)

    # update data
    print('\nUpdating records from verbatim data...')
    update_catalog_number()
    update_remarks()
    update_date_recorded()
    update_institution()
    update_disposition()
    update_locality()
    update_area()
    update_geological_context()
    update_description()
    update_taxon_fields(verbose=False)
    update_scientific_name_taxon_rank()
    update_taxon_remarks()
    update_problems()
    print('Current record count: {}'.format(Fossil.objects.all().count()))
    print(hr)

    print('\nValidating records')
    validate_date_recorded()
    validate_catalog_number()
    validate_locality()
    validate_splits()
    validate_geological_context()
    print(hr)


# Additional utility functions
def get_max_field_length(field):
    bios = Fossil.objects.all()
    try:
        max_length = max([len(getattr(b, field)) for b in bios])
    except TypeError:
        attribute_list = [getattr(b, field) for b in bios]
        attribute_list = [a for a in attribute_list if a]  # remove None values
        if attribute_list:
            try:
                max_length = max([len(a) for a in attribute_list])
            except TypeError:
                max_length = None
        else:
            max_length = None
    return max_length


def report_max_field_length():
    for f in get_verbatim_fields():
        max_length = get_max_field_length(f)
        print('{} {}'.format(f, max_length))


def get_verbatim_fields():
    return set(list(lookup_dict.values()))


def field_list(field_name, report=True):
    """
    Get the unique values for a field
    :return:
    """
    res_list = []
    try:
        dl = Fossil.objects.distinct(field_name)
        for f in dl:
            n = getattr(f, field_name)
            kwargs = {
                '{0}__{1}'.format(field_name, 'exact'): n
            }
            c = Fossil.objects.filter(**kwargs).count()
            if field_name == 'tspecies':
                g = getattr(f, 'tgenus')
                if g:
                    n = g + ' ' + n
            t = (n, c)
            res_list.append(t)
        if report:
            for i in res_list:
                print("{} {}".format(*i))  # use * to unpack tuple
    except FieldError:  # because field_name is a method not an attribute
        res_list = list(set([getattr(f, field_name)() for f in Fossil.objects.all()]))
        res_list = sorted(res_list)

    return res_list


def multireplace(in_string, replacements):
    """
    Replace multiple matches in a string at once.
    :param in_string: The string to be processed
    :param replacements: a dictionary of replacement values {value to find, value to replace}
    :return: returns string with all matches replaced.
    Credit to bgusach, https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729
    """
    # Place longer ones first to keep shorter substrings from matching where the longer ones should take place
    # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc', it should produce
    # 'hey ABC' and not 'hey ABc'
    sub_strings = sorted(replacements, key=len, reverse=True)

    # Create a big OR regex that matches any of the substrings to replace
    regexp = re.compile('|'.join(map(re.escape, sub_strings)))

    # For each match, look up the new string in the replacements
    return regexp.sub(lambda match: replacements[match.group(0)], in_string)


def q2cf(taxon_string):
    cf_re = re.compile(r'[?]')  # find all cases with '?'
    if cf_re.search(taxon_string):
        if taxon_string.strip() == '?':  # If taxon is just ? replace with None
            taxon_string = ''
        else:
            taxon_string = 'cf. ' + cf_re.sub('', taxon_string)  # If case has ? remove it and prefix with cf.
    return taxon_string


def clear_problem_duplicate(o):
    o.problem = False
    o.problem_comment = o.problem_comment.replace('Duplicate catalog number!', '')
    o.save()


def diff_fossils(catalog_number):
    fossils = Fossil.objects.filter(catalog_number=catalog_number)
    for i in fossils[0].__dict__:
        print(str(fossils[0].__dict__[i])+'     '+str(fossils[1].__dict__[i]))


def import_report(year_list=CSHO_YEARS):
    record_count_list = []
    for year in year_list:
        workbook_name = make_file_string(year)
        count = Fossil.objects.filter(verbatim_workbook_name=workbook_name).count()
        record_count_list.append((year, count))
    return record_count_list


def update_from_dict(obj, update_dict):
    """
    A function to update an object instance with values stored in a dictionary.
    In some cases preferred over calling filter(pk=pk).update(**dict) because update does not send signals.
    :param obj: The object instance to be updated
    :param update_dict: A dictionary of attribute-value pairs to update the object
    :return: Returns the object instance with upated values. But still need to save the changes!
    """
    #
    for attr, value in update_dict.items():
        setattr(obj, attr, value)
    return obj


def get_pbdb_taxon(taxon_name):
    url = 'https://paleobiodb.org/data1.2/taxa/single.txt?name='+taxon_name
    resp = requests.get(url)
    if resp.status_code == 200:
        h, d = resp.content.decode('utf-8').replace('"', '').split('\r\n')[0:2]
        h = h.split(',')
        d = d.split(',')
        result = dict(zip(h, d))
    else:
        result = None
    return result


def get_idigbio_taxon(taxon_name, taxon_rank):
    result = None
    api = idigbio.json()
    taxon_rank.replace('tspecies', 'scientificname')
    r = api.search_records(rq={taxon_rank: taxon_name})
    if r:
        result = r
    return result
