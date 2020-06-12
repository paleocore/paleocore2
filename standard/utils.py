import csv
import io
import codecs
from urllib import request
from owlready2 import *
import pandas
from standard.models import Term, Project, TermCategory, ProjectTerm, TermStatus
from pygbif import occurrences as occ


class Schema:
    """
    Base class to store a data schema including terms, definitions, versions etc.
    Schemas may come in a variety of formats with different levels of detail and complexity.
    For example Darwin Core is a simple list of terms expressed as string literals whereas
    Uberon in a formal ontology expressed in owl
    """
    def import_schema(self):
        pass

    def export_schema(self):
        pass

    def summary(self):
        pass


class DwcNamespaceError(Exception):
    """Namespace link is not available in the currently provided links"""
    pass


class DwcReader:

    def __init__(self, dwc_build_file):
        """Custom Reader switching between raw Github or local file"""
        self.dwc_build_file = dwc_build_file

    def __enter__(self):
        if "https://raw.github" in self.dwc_build_file:
            self.open_dwc_term = request.urlopen(self.dwc_build_file)
        else:
            self.open_dwc_term = open(self.dwc_build_file, 'rb')
        return self.open_dwc_term

    def __exit__(self, *args):
        self.open_dwc_term.close()


class DwcManager:
    """
    Class to manage the Darwin Core schema in Paleo Core.
    """
    terms_source = 'https://raw.githubusercontent.com/tdwg/dwc/master/vocabulary/term_versions.csv'

    def __init__(self, terms_source=terms_source):
        # Initialize attributes:
        # self.terms_dict - dictionary of term dictionaries
        # self.terms_set - set of term iri values, keys to terms_dict
        # self.terms_source = source file for Darwin Core terms, e.g. github repo or local file
        self.terms_source = terms_source
        self.terms_dict = {}
        self._load_terms()

    def _load_terms(self):
        for term in self.terms_iter():
            self.terms_dict[term["term_iri"]] = term

    def terms_iter(self):
        """
        Iterator that provides the active (i.e. recommended) terms from the term versions source file.
        The term is returned as a dictionary object. An index value is added to the dictionary to
        help with sorting the terms in their original order.
        """
        with DwcReader(self.terms_source) as terms_source:
            term_index = 10
            for vterm in csv.DictReader(io.TextIOWrapper(terms_source), delimiter=','):
                if vterm["status"] == "recommended":
                    vterm['index'] = term_index
                    term_index += 10
                    yield vterm

    @property
    def terms_set(self):
        """
        Creates a set of all the terms as simple term_iri values, e.g. 'http://purl.org/dc/terms/type'
        """
        return set(self.terms_dict.keys())

    @property
    def simple_dwc_list(self):
        """
        Creates a list of simple darwin core terms
        :return: Returns a list of term labels (not iri values)
        """
        return [term['label'] for term in self.terms_iter()]

    @staticmethod
    def get_category(term_dict):
        """
        Function to fetch the appropriate category object from the DB. Categories are matched to term
        classes by the mapping dictionary.
        :param term_dict:
        :return: Returns a Paleo Core category object
        """
        mapping_dict = {
            'http://purl.org/dc/terms/': 'Record',
            'http://rs.tdwg.org/dwc/terms/': 'Record',
            'http://rs.tdwg.org/dwc/terms/Occurrence': 'Occurrence',
            'http://rs.tdwg.org/dwc/terms/Organism': 'Organism',
            'http://rs.tdwg.org/dwc/terms/MaterialSample': 'MaterialSample',
            'http://rs.tdwg.org/dwc/terms/Event': 'Event',
            'http://purl.org/dc/terms/Location': 'Location',
            'http://rs.tdwg.org/dwc/terms/GeologicalContext': 'GeologicalContext',
            'http://rs.tdwg.org/dwc/terms/Identification': 'Identification',
            'http://rs.tdwg.org/dwc/terms/Taxon': 'Taxon',
            'http://rs.tdwg.org/dwc/terms/MeasurementOrFact': 'MeasurementOrFac',
            'http://rs.tdwg.org/dwc/terms/ResourceRelationship': 'ResourceRelationship',
            'http://www.w3.org/2000/01/rdf-schema#Class': 'Class',
            'http://rs.tdwg.org/dwc/terms/attributes/UseWithIRI': 'RDF'
        }
        try:
            category = mapping_dict[term_dict['organized_in']]
        except KeyError:
            if term_dict["rdf_type"] == "http://www.w3.org/2000/01/rdf-schema#Class":
                category = 'Class'
            else:
                category = None
        try:
            category_object = TermCategory.objects.get(name=category)
        except TermCategory.DoesNotExist:
            category_object = None
        return category_object

    def update_term(self, term_iri, term_dict):
        """
        Function to update a Darwin Core term in the Paleo Core database. This function overwrites existing
        attriubtes, excetp the remarks. So remarks will safe during updates, as will many-to-many relationships
        with projects.
        :param term_iri:
        :param term_dict:
        :return: Returns an Paleo Core Term object.
        """
        obj, created = Term.objects.get_or_create(uri=term_iri)
        obj.name = term_dict['label']
        obj.definition = term_dict['definition']
        obj.example = term_dict['examples']
        obj.comments = term_dict['comments']
        obj.version_iri = term_dict['iri']
        obj.iri = term_dict['term_iri']
        obj.issued = term_dict['issued']
        obj.rdf_type = term_dict['rdf_type']
        obj.abcd = term_dict['abcd_equivalence']
        obj.flags = term_dict['flags']
        obj.status = TermStatus.objects.get(name='standard')
        obj.category = self.get_category(term_dict)
        obj.rdf_type = term_dict['rdf_type']
        if obj.rdf_type == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Class':
            obj.is_class = True
        if obj.rdf_type == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property':
            obj.is_class = False
        obj.term_ordering = term_dict['index']
        obj.save()

        project = Project.objects.get(name='dwc')  # Assumes dwc project exists in Paleo Core database
        # use get or create to match incoming terms with existing entries in the database and to
        # create new records for novel Darwin Core terms added to Dwc since last update.
        project_terms, pt_created = ProjectTerm.objects.get_or_create(project=project, term=obj)
        project_terms.save()

        return obj, created

    def update_dwc(self):
        """
        Procedure to update the Darwin Core terms in the Paleo Core database. This procedure overwrites
        the old term names, definitions etc. but does NOT affect remarks, which allows persistance of
        Paleo Core commentary about the terms.
        :return:
        """
        for term in self.terms_set:
            self.update_term(term, self.terms_dict[term])

    @staticmethod
    def get_all_versions_as_df(terms_source):
        return pandas.read_csv(terms_source)

    @staticmethod
    def split_iri(term_iri):
        """
        Split the iri field into the namespace url and the local term name
        """
        prog = re.compile("(.*/)([^/]*$)")
        namespace, local_name = prog.findall(term_iri)[0]
        return namespace, local_name

    @staticmethod
    def resolve_namespace_abbrev(namespace):
        """Using the NAMESPACE constant, get the namespace abbreviation by
        providing the namespace link

        Parameters
        -----------
        namespace : str
            valid key of the NAMESPACES variable
        """
        if namespace not in NAMESPACES.keys():
            raise DwcNamespaceError("The namespace url is currently not supported in NAMESPACES")
        return NAMESPACES[namespace]

    def create_dwc_list(self, file_output="simple_dwc_vertical.csv"):
        """Build a list of simple dwc terms and write it to file

        Parameters
        -----------
        file_output : str
            relative path and filename to write the resulting list
        """
        with codecs.open(file_output, 'w', 'utf-8') as dwc_list_file:
            for term in self.simple_dwc_list:
                dwc_list_file.write(term + "\n")

    def create_dwc_header(self, file_output="../dist/simple_dwc_horizontal.csv"):
        """Build a header of simple dwc terms and write it to file

        Parameters
        -----------
        file_output : str
            relative path and filename to write the resulting list
        """
        with codecs.open(file_output, 'w', 'utf-8') as dwc_header_file:
            properties = self.simple_dwc_list
            dwc_header_file.write(",".join(properties))
            dwc_header_file.write("\n")

    def dwc_export(self, file_output='dwc_export.csv'):
        with codecs.open(file_output, 'w', 'utf-8') as dwc_export:
            header = ['index', 'iri', 'label', 'organized_in',
                      'issued','status','replaces','rdf_type','term_iri','abcd_equivalence','flags',
                      'definition', 'comments', 'examples']
            dwc_export.write(','.join(header) + '\n')
            for term in self.terms_iter():
                row = []
                for t in header:
                    if t not in ('definition','comments', 'examples'):
                        row.append(str(term[t]))
                    else:
                        value = '"' + str(term[t]) + '"'
                        row.append(value)
                dwc_export.write(','.join(row) + '\n')


class UberonManager:
    """
    Class to manage the Uberon schema in Paleo Core
    """
    pass


NAMESPACES = {
    'http://rs.tdwg.org/dwc/iri/': 'dwciri',
    'http://rs.tdwg.org/dwc/terms/': 'dwc',
    'http://purl.org/dc/elements/1.1/': 'dc',
    'http://purl.org/dc/terms/': 'dcterms',
    'http://rs.tdwg.org/dwc/terms/attributes/': 'tdwgutility'}


term_versions_url = 'https://raw.githubusercontent.com/tdwg/dwc/master/vocabulary/term_versions.csv'


def load_uberon(url='http://purl.obolibrary.org/obo/uberon.owl#'):
    uberon = get_ontology(url)
    uberon.load()
    return uberon


def camel2snake(input_string):
    return ''.join(['_' + i.lower() if i.isupper()
                    else i for i in input_string]).lstrip('_')


gbif_path = '/Users/dreed/Documents/tdwg/gbif_fossil_data_200514.csv'


def get_csv_header():
    with open(gbif_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        header_list = next(reader)
    return header_list


def csv_head(start=1, end=10, verbose=True):
    with open(gbif_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        header_list = next(reader)
        array = [next(reader) for i in list(range(start, end+1))]
        if verbose:
            for r in array:
                print(r)
    return array


def get_api_header():
    o = occ.get(345504339)
    return list(o.keys())


def get_unique(field_name):
    with open(gbif_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
        header_list = next(reader)
        field_index = header_list.index(field_name)
        unique_set = set()
        row_index = 0
        error_count = 0
        while row_index < 11642710:
            row_index += 1
            try:
                row = next(reader)
                unique_set.add(row[field_index])
            except:
                print('error reading row {}'.format(row_index))
                error_count += 1
            print("\r" + str(row_index), end="")
        return unique_set


def get_row(row_number):
    with open(gbif_path, newline='') as csvfile:
        #reader = csv.reader(csvfile, delimiter='\t')
        reader = csv.reader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
        header_list = next(reader)
        row_index = 0
        while row_index < 11642710:
            row = next(reader)
            row_index += 1
            if row_index == row_number:
                print(row)
                break


def get_row_count(path=gbif_path):
    with open(path, newline='') as f:
        return sum(1 for line in f)
