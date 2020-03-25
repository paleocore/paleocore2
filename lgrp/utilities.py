from .models import *
from difflib import SequenceMatcher
from itertools import permutations
import csv
import time


def match_taxon(biology_object):
    """
    find taxon objects from item_scientific_name
    Return: (True/False, match_count, match_list)
    """
    # match, match_count, match_list = (False, 0, None)
    match_list = Taxon.objects.filter(name=biology_object.item_scientific_name)
    if len(match_list) == 1:  # one match
        result_tuple = (True, 1, match_list)
    else:
        result_tuple = (False, len(match_list), match_list)
    return result_tuple


def match_element(biology_object):
    """
    find anatomical element from string in item_description. Returns a result tuple. The first element is true
    only if there is one and only one match
    :param biology_object:
    :return: (True/False, match_count, match_list)
    """
    match, match_count, match_list = (False, 0, None)
    element_list = [e[1] for e in LGRP_ELEMENT_CHOICES]
    description = biology_object.item_description
    if description.lower() in element_list:
        match = True
        match_count = 1
        match_list = description
    result = (match, match_count, match_list)
    return result


def update_taxa():
    bios = Biology.objects.all()
    bios2fix = bios.filter(taxon__name='Life').exclude(item_scientific_name=None)
    for bio in bios2fix:
        if bio.item_scientific_name == 'Mammal':
            bio.item_scientific_name = 'Mammalia'
            bio.taxon = Taxon.objects.get(name='Mammalia')
            print('matching mammal for {}'.format(bio))
        elif bio.item_scientific_name == 'Hippopotomidae':
            bio.item_scientific_name = 'Hippopotamidae'
            bio.taxon = Taxon.objects.get(name='Hippopotamidae')
            print('matching hippo for {}'.format(bio))
        elif bio.item_scientific_name == 'Primate':
            bio.item_scientific_name = 'Primates'
            bio.taxon = Taxon.objects.get(name='Primates')
            print('matching primate for {}'.format(bio))
        elif match_taxon(bio)[0]:
            bio.taxon = match_taxon(bio)[2][0]
            print('found match for {}'.format(bio))
        else:
            print('no match for {}'.format(bio))
            pass
        bio.save()


def similar(t):
    a, b = t
    return SequenceMatcher(None, a, b).ratio()


def get_similar_taxa():
    """
    Get a list of all pairwise permutations of taxa sorted according to similarity
    Useful for detecting duplicate and near-duplicate taxonomic entries
    :return: list of 2-tuples ordered most similar to least
    """
    taxa = Taxon.objects.all()
    taxon_name_set = set([t.name for t in taxa])
    plist = [pair for pair in permutations(taxon_name_set, 2)]
    return sorted(plist, key=similar, reverse=True)


def prune_species():
    """
    Function to remove unused species
    :return:
    """
    species = TaxonRank.objects.get(name='Species')
    for taxon in Taxon.objects.all():
        if Biology.objects.filter(taxon=taxon).count() == 0 and taxon.rank == species:
            taxon.delete()


def export():
    start = time.time()
    with open('lgrp_export_test.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        b = Biology()  # create an empty instance of a biology object
        queryset = Biology.objects.all()

        # Fetch model field names. We need to account for data originating from tables, relations and methods.
        concrete_field_names = b.get_concrete_field_names()  # fetch a list of concrete field names
        method_field_names = b.method_fields_to_export()  # fetch a list for method field names

        fk_fields = [f for f in b._meta.get_fields() if f.is_relation]  # get a list of field objects
        fk_field_names = [f.name for f in fk_fields]  # fetch a list of foreign key field names

        # Concatenate to make a master field list
        field_names = concrete_field_names + method_field_names + fk_field_names
        writer.writerow(field_names)  # write column headers

        def get_fk_values(occurrence, fk):
            """
            Get the values associated with a foreign key relation
            :param occurrence:
            :param fk:
            :return:
            """
            qs = None
            return_string = ''
            try:
                qs = [obj for obj in getattr(occurrence, fk).all()]  # if fk is one to many try getting all objects
            except AttributeError:
                return_string = str(getattr(occurrence, fk))  # if one2one or many2one get single related value

            if qs:
                try:
                    # Getting the name of related objects requires calling the file or image object.
                    # This solution may break if relation is neither file nor image.
                    return_string = '|'.join([str(os.path.basename(p.image.name)) for p in qs])
                except AttributeError:
                    return_string = '|'.join([str(os.path.basename(p.file.name)) for p in qs])

            return return_string

        for occurrence in queryset:  # iterate through the occurrence instances selected in the admin
            # The next line uses string comprehension to build a list of values for each field.
            # All values are converted to strings.
            concrete_values = [getattr(occurrence, field) for field in concrete_field_names]
            # Create a list of values from method calls. Note the parenthesis after getattr in the list comprehension.
            method_values = [getattr(occurrence, method)() for method in method_field_names]
            # Create a list of values from related tables. One to many fields have related values concatenated in str.
            fk_values = [get_fk_values(occurrence, fk) for fk in fk_field_names]

            row_data = concrete_values + method_values + fk_values
            cleaned_row_data = ['' if i in [None, False, 'None', 'False'] else i for i in row_data]  # Replace ''.
            writer.writerow(cleaned_row_data)

    csvfile.close()
    end = time.time()
    return print(end-start)
