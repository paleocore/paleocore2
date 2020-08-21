from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, FieldError
from .models import CollectionCode
import xlrd
from datetime import datetime
import pytz


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


lookup_dict = {
    'Code': 'code',
    'Institution': 'institution',
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
