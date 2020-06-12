import projects.ontologies as ontologies

# Basis of Record Vocabulary
BASIS_OF_RECORD_VOCABULARY = ontologies.BASIS_OF_RECORD_VOCABULARY

# Item Type Vocabulary
ITEM_TYPE_VOCABULARY = ontologies.ITEM_TYPE_VOCABULARY

# Collection Method Vocabulary
COLLECTING_METHOD_VOCABULARY = ontologies.COLLECTING_METHOD_VOCABULARY

# Anatomical Side Vocabulary
SIDE_VOCABULARY = ontologies.SIDE_VOCABULARY

# Collector Vocabulary
Sonia = 'Sonia Harmand'
Jason = 'Jason Lewis'
Helene = 'Helene Roche'
Craig = 'Craig Feibel'
Sandrine = 'Sandrine Prat'
Xavier = 'Xavier Boës'
Nicholas = 'Nicholas Taylor'
Jean_Philip = 'Jean-Philip Brugal'
COLLECTOR_CHOICES = (
    (Sonia, 'Sonia Harmand'),
    (Jason, 'Jason Lewis'),
    (Helene, 'Helene Roche'),
    (Craig, 'Craig Feibel'),
    (Sandrine, 'Sandrine Prat'),
    (Xavier, 'Xavier Boës'),
    (Nicholas, 'Nicholas Taylor'),
    (Jean_Philip, 'Jean-Philip Brugal')
)

# Field Season Vocabulary
jan2014 = 'January 2014'
nov2014 = 'Nov 2014'
nov2015 = 'Nov 2015'
jan2018 = 'Jan 2018'
jan2019 = 'Jan 2019'
jan2020 = 'Jan 2020'
FIELD_SEASON_CHOICES = (
    (jan2014, 'Jan 2014'),
    (nov2014, 'Nov 2014'),
    (nov2015, 'Nov 2015'),
    (jan2018, 'Jan 2018'),
    (jan2019, 'Jan 2019'),
    (jan2020, 'Jan 2020')
)
