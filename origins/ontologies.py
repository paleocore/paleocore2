# Origins Project Choice Lists, Vocabularies, Ontologies
# choice lists and vocabularies are defined with the following design template:

# variable_label1 = value   # variable_labels are lowercase, values can be strings or numbers or codes
# variable_label2 = value
# CHOICES = (
#   (variable_label1, 'string_representation')
#   (variable_label2, 'string_representation')

# The design allows use of the variable_labels in code. Changes to the value applies automatically then in code and
# in what is written to database.


# Continents of the World
africa = 'Africa'
antarctica = 'Antarctica'
asia = 'Asia'
australia = 'Australia'
europe = 'Europe'
north_america = 'North America'
south_america = 'South America'

CONTINENT_CHOICES = (
    (africa, 'Africa'),
    (antarctica, 'Antarctica'),
    (asia, 'Asia'),
    (australia, 'Australia'),
    (europe, 'Europe'),
    (north_america, 'North America'),
    (south_america, 'South America')
)


# helper functions
def choices2list(choices_tuple):
    """
    Helper function that returns a choice list tuple as a simple list of stored values
    :param choices_tuple:
    :return:
    """
    return [c[0] for c in choices_tuple]
