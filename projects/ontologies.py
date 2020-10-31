# Vocabularies used in model choice lists
# The tuples for choice lists have two values (value, display_text)
# We define the values using variables so that they can also be called in code
# and a change in the value here will propagate in the code

# Basis of Record Vocabulary
fossil_specimen = 'FossilSpecimen'  # corresponding to Darwin Core classes
human_observation = 'HumanObservation'
BASIS_OF_RECORD_VOCABULARY = ((fossil_specimen, "Fossil"), (human_observation, "Observation"))

# HRP modified Basis of Record Vocabulary
collection = "Collection"
observation = "Observation"
HRP_BASIS_OF_RECORD_VOCABULARY = ((collection, "Collection"), (observation, "Observation"))

# Item Type Vocabulary
artifactual = 'Artifactual'
faunal = 'Faunal'
floral = 'Floral'
geological = 'Geological'
cast = 'Cast'
ITEM_TYPE_VOCABULARY = (
    (artifactual, "Artifactual"),
    (faunal, "Faunal"),
    (floral, "Floral"),
    (geological, "Geological"),
    (cast, 'Cast')
)

# Collecting Method Vocabulary
surface_standard = 'Surface Standard'
surface_intensive = 'Surface Intensive'
surface_complete = "Surface Complete"
exploratory_survey = "Exploratory Survey"
dry_screen_5mm = "Dry Screen 5mm"
dry_screen_2mm = "Dry Screen 2mm"
dry_screen_1mm = "Wet Screen 1mm"
excavation = "Excavation"
COLLECTING_METHOD_VOCABULARY = ((surface_standard, "Surface Standard"),
                                (surface_intensive, "Surface Intensive"),
                                (surface_complete, "Surface Complete"),
                                (exploratory_survey, "Exploratory Survey"),
                                (dry_screen_5mm, "Dry Screen 5mm"),
                                (dry_screen_2mm, "Dry Screen 2mm"),
                                (dry_screen_1mm, "Wet Screen 1mm"),
                                (excavation, "Excavation"))

# Anatomical Side Vocabulary
left = "Left"
right = "Right"
both = "Both"
axial = "Axial"
unknown = "Unknown"
SIDE_VOCABULARY = ((left, "Left"),
                   (right, "Right"),
                   (both, "Both"),
                   (axial, "Axial"),  # a median, unsided element
                   (unknown, "Unknown"))

# North American Land Mammal Ages (NALMA)
bridgerian = 'Bridgerian'
wasatchian = 'Wasatchian'
clarkforkian = 'Clarkforkian'

NALMA_CHOICES = (
    (bridgerian, 'Bridgerian'),
    (wasatchian, 'Wasatchian'),
    (clarkforkian, 'Clarkforkian'))

# NALMA Sub Age Vocabulary
cf1, cf2, cf3 = ['Cf'+str(x) for x in range(1,4)]
wa0, wa1, wa2, wa3, wa4, wa5, wa6, wa7 = ['Wa'+str(x) for x in range(0,8)]
br0, br1a, br1b, br2, br3 = ['Br0', 'Br1a', 'Br1b', 'Br2', 'Br3']
clarkforkian_subages = [cf1, cf2, cf3]
wasatchian_subages = [wa0, wa1, wa2, wa3, wa4, wa5, wa6, wa7]
bridgerian_subages = [br0, br1a, br1b, br2, br3]
NALMA_SUB_AGE_CHOICES = (
    (cf1, 'Cf1'),
    (cf2, 'Cf2'),
    (cf3, 'Cf3'),
    (wa0, 'Wa0'),
    (wa1, 'Wa1'),
    (wa2, 'Wa2'),
    (wa3, 'Wa3'),
    (wa4, 'Wa4'),
    (wa5, 'Wa5'),
    (wa6, 'Wa6'),
    (wa7, 'Wa7'),
    (br0, 'Br0'),
    (br1a, 'Br1a'),
    (br1b, 'Br1b'),
    (br2, 'Br2'),
    (br3, 'Br3'),
)
CLARKFORKIAN_SUB_AGE_CHOICES = (
    (cf1, 'Cf1'),
    (cf2, 'Cf2'),
    (cf3, 'Cf3'),
)
WASATCHIAN_SUB_AGE_CHOICES = (
    (wa0, 'Wa0'),
    (wa1, 'Wa1'),
    (wa2, 'Wa2'),
    (wa3, 'Wa3'),
    (wa4, 'Wa4'),
    (wa5, 'Wa5'),
    (wa6, 'Wa6'),
    (wa7, 'Wa7'),
)
BRIDGERIAN_SUB_AGE_CHOICES = (
    (br0, 'Br0'),
    (br1a, 'Br1a'),
    (br1b, 'Br1b'),
    (br2, 'Br2'),
    (br3, 'Br3'),
)

# Project Specific Vocabularies
HRP_COLLECTION_CODES = (("A.L.", "A.L."),)

HRP_COLLECTING_METHOD_VOCABULARY = (("Survey", "Survey"),
                                ("dryscreen5mm", "dryscreen5mm"),
                                ("wetscreen1mm", "wetscreen1mm"))

COLLECTOR_CHOICES = (("Zeresenay Alemseged", "Zeresenay Alemseged"),
                     ("Andrew Barr", "Andrew Barr"),
                     ("Rene Bobe", "Rene Bobe"),
                     ("Denis Geraads", "Denis Geraads"),
                     ("Weldeyared Hailu", "Waldeyared Hailu"),
                     ("Shannon McPherron", "Shannon McPherron"),
                     ("Denne Reed", "Denne Reed"),
                     ("Peter Stamos", "Peter Stamos"),
                     ("Jonathan Wynn", "Jonathan Wynn"))

HRP_COLLECTOR_CHOICES = (("C.J. Campisano", "C.J. Campisano"),
                         ("W.H. Kimbel", "W.H. Kimbel"),
                         ("T.K. Nalley", "T.K. Nalley"),
                         ("D.N. Reed", "D.N. Reed"),
                         ("Kaye Reed", "Kaye Reed"),
                         ("B.J. Schoville", "B.J. Schoville"),
                         ("A.E. Shapiro", "A.E. Shapiro"),
                         ("HFS Student", "HFS Student"),
                         ("HRP Team", "HRP Team")
                         )

SKULL_BONES = (("complete skull", "complete skull"),
                   ("partial skull", "partial skull"),
                   ("temporal", "temporal"),
                   ("frontal", "frontal"),  # a median, unsided element
                   ("occipital", "occipital"),
                   ("parietal", "parietal"))

VERTEBRATE_CLASSES = (("Mammalia", "Mammalia"),
                      ("Reptilia", "Reptilia"),
                      ("Aves", "Aves"),
                      ("Pisces", "Pisces"),
                      ("Amphibia", "Amphibia"),
                      ("Assorted", "Assorted"))

MAMMALIAN_ORDERS = (("Primates", "Primates"),
                   ("Condylarthra", "Condylarthra"),
                   ("Perissodactyla", "Perissodactyla"),
                   ("Artiodactyla", "Artiodactyla"),
                   ("Rodentia", "Rodentia"),
                   ("Carnivora", "Carnivora"),
                   ("Creodonta", "Creodonta"),
                   ("Insectivora", "Insectivora"),
                   ("Lipotyphyla", "Lipotyphyla"),
                   ("Tillodontia", "Tillodontia"),
                   ("Mammalia indet.", "Mammalia indet."),
                   ("Pantodonta", "Pantodonta"),
                   ("Marsupialia", "Marsupialia"),
                   ("Cimolesta", "Cimolesta"),
                   ("Multituberculata", "Multituberculata"))

UPPER_TEETH = (("Incisor/", "Incisor/"),
                   ("I1/", "I1/"),
                   ("I2/", "I2/"),
                   ("I3/", "I3/"),
                   ("I4/", "I4/"),
                   ("Canine/", "Canine/"),
                   ("Premolar/", "Premolar/"),
                   ("P1/", "P1/"),
                   ("P2/", "P2/"),
                   ("P3/", "P3/"),
                   ("P4/", "P4/"),
                   ("Molar/", "Molar/"),
                   ("M1/", "M1/"),
                   ("M2/", "M2/"),
                   ("M2/", "M2/"),
                   ("M3/", "M3/"))

LOWER_TEETH = (("/Incisor", "/Incisor"),
                   ("I/1", "I/1"),
                   ("I/2", "I/2"),
                   ("I/3", "I/3"),
                   ("I/4", "I/4"),
                   ("/Canine", "/Canine"),
                   ("/Premolar", "/Premolar"),
                   ("P/1", "P/1"),
                   ("P/2", "P/2"),
                   ("P/3", "P/3"),
                   ("P/4", "P/4"),
                   ("/Molar", "/Molar"),
                   ("M/1", "M/1"),
                   ("M/2", "M/2"),
                   ("M/2", "M/2"),
                   ("M/3", "M/3"))

FORELIMB_ELEMENTS = (("scapula", "scapula"),
                   ("humerus", "humerus"),
                   ("distal humerus", "distal humerus"),
                   ("proximal humerus", "proximal humerus"),
                   ("humeral shaft", "humeral shaft"),
                   ("radius", "radius"),
                   ("distal radius", "distal radius"),
                   ("proximal radius", "proximal radius"),
                   ("ulna", "ulna"),
                   ("distal ulna", "distal ulna"),
                   ("proximal ulna", "proximal ulna"),
                   ("carpal element", "carpal element"),
                   ("podial", "podial"))

HINDLIMB_ELEMENTS = (("pelvis", "pelvis"),
                   ("ischium", "ischium"),
                   ("ilium", "ilium"),
                   ("pubis", "pubis"),
                   ("femur", "femur"),
                   ("distal femur", "distal femur"),
                   ("proximal femur", "proximal femur"),
                   ("tibia", "tibia"),
                   ("distal tibia", "distal tibia"),
                   ("proiximal tibia", "proiximal tibia"),
                   ("fibula", "fibula"),
                   ("distal fibula", "distal fibula"),
                   ("proximal fibula", "proximal fibula"),
                   ("tarsal element", "tarsal element"),
                   ("astragalus", "astragalus"),
                   ("calcaneus", "calcaneus"),
                   ("cuboid", "cuboid"),
                   ("podial", "podial"))

MANDIBLE = (("edentulous mandible", "edentulous mandible"),
                   ("symphysis", "symphysis"),
                   ("condyle", "condyle"),
                   ("With teeth", "With teeth"))

MAXILLA = (("edentulous", "edentulous"),
                   ("With teeth", "With teeth"))

VERTEBRAE = (("caudal", "caudal"),
                   ("lumbar", "lumbar"),
                   ("thoracic", "thoracic"),
                   ("cervical", "cervical"),
                   ("unidentified", "unidentified"))

MISCELLANEOUS = (("tooth", "tooth"),
                   ("bone", "bone"),
                   ("tooth fragment", "tooth fragment"),
                   ("bone fragment", "bone fragment"),
                   ("cranial fragment", "cranial fragment"),
                   ("carapace", "carapace"),
                   ("dermal element", "dermal element"))

TIME_OF_DAY = (("AM", "AM"),
               ("PM", "PM"))

GNATHIC = (("mandible with teeth", "mandible with teeth"),
                   ("edentulous mandible", "edentulous mandible"),
                   ("maxilla with teeth", "maxilla with teeth"),
                   ("edentulous maxilla", "edentulous maxilla"),
                   ("mandibular symphysis", "mandibular symphysis"),
                   ("mandibular condyle", "mandibular condyle"))


africa = "Africa"
europe = "Europe"
asia = "Asia"
north_america = "North America"
south_america = "South America "
australia = "Australia "
antarctica = "Antarctica"
CONTINENT_CHOICES = (
    (africa, "Africa"),
    (europe, "Europe"),
    (asia, "Asia"),
    (north_america, "North America"),
    (south_america, "South America"),
    (australia, "Australia"), (antarctica, "Antarctica")
)

REGION_CHOICES = (("southern_africa", "southern Africa"), ("eastern_africa", "eastern Africa"),
                 ("northern_africa", "northern Africa"), ("", ""), ("", ""))

COUNTRY_CHOICES = (
    ('United States of America', ('United States of America')),
    ('Afghanistan', ('Afghanistan')),
    ('Aland Islands', ('Aland Islands')),
    ('Albania', ('Albania')),
    ('Algeria', ('Algeria')),
    ('American Samoa', ('American Samoa')),
    ('Andorra', ('Andorra')),
    ('Angola', ('Angola')),
    ('Anguilla', ('Anguilla')),
    ('Antigua and Barbuda', ('Antigua and Barbuda')),
    ('Argentina', ('Argentina')),
    ('Armenia', ('Armenia')),
    ('Aruba', ('Aruba')),
    ('Australia', ('Australia')),
    ('Austria', ('Austria')),
    ('Azerbaijan', ('Azerbaijan')),
    ('Bahamas', ('Bahamas')),
    ('Bahrain', ('Bahrain')),
    ('Bangladesh', ('Bangladesh')),
    ('Barbados', ('Barbados')),
    ('Belarus', ('Belarus')),
    ('Belgium', ('Belgium')),
    ('Belize', ('Belize')),
    ('Benin', ('Benin')),
    ('Bermuda', ('Bermuda')),
    ('Bhutan', ('Bhutan')),
    ('Bolivia', ('Bolivia')),
    ('Bosnia and Herzegovina', ('Bosnia and Herzegovina')),
    ('Botswana', ('Botswana')),
    ('Brazil', ('Brazil')),
    ('British Virgin Islands', ('British Virgin Islands')),
    ('Brunei Darussalam', ('Brunei Darussalam')),
    ('Bulgaria', ('Bulgaria')),
    ('Burkina Faso', ('Burkina Faso')),
    ('Burundi', ('Burundi')),
    ('Cambodia', ('Cambodia')),
    ('Cameroon', ('Cameroon')),
    ('Canada', ('Canada')),
    ('Cape Verde', ('Cape Verde')),
    ('Cayman Islands', ('Cayman Islands')),
    ('Central African Republic', ('Central African Republic')),
    ('Chad', ('Chad')),
    ('Channel Islands', ('Channel Islands')),
    ('Chile', ('Chile')),
    ('China', ('China')),
    ('China - Hong Kong', ('China - Hong Kong')),
    ('China - Macao', ('China - Macao')),
    ('Colombia', ('Colombia')),
    ('Comoros', ('Comoros')),
    ('Congo', ('Congo')),
    ('Cook Islands', ('Cook Islands')),
    ('Costa Rica', ('Costa Rica')),
    ('Cote d\'Ivoire', ('Cote d\'Ivoire')),
    ('Croatia', ('Croatia')),
    ('Cuba', ('Cuba')),
    ('Cyprus', ('Cyprus')),
    ('Czech Republic', ('Czech Republic')),
    ('Democratic People\'s Republic of Korea', ('Democratic People\'s Republic of Korea')),
    ('Democratic Republic of the Congo', ('Democratic Republic of the Congo')),
    ('Denmark', ('Denmark')),
    ('Djibouti', ('Djibouti')),
    ('Dominica', ('Dominica')),
    ('Dominican Republic', ('Dominican Republic')),
    ('Ecuador', ('Ecuador')),
    ('Egypt', ('Egypt')),
    ('El Salvador', ('El Salvador')),
    ('Equatorial Guinea', ('Equatorial Guinea')),
    ('Eritrea', ('Eritrea')),
    ('Estonia', ('Estonia')),
    ('Ethiopia', ('Ethiopia')),
    ('Faeroe Islands', ('Faeroe Islands')),
    ('Falkland Islands (Malvinas)', ('Falkland Islands (Malvinas)')),
    ('Fiji', ('Fiji')),
    ('Finland', ('Finland')),
    ('France', ('France')),
    ('French Guiana', ('French Guiana')),
    ('French Polynesia', ('French Polynesia')),
    ('Gabon', ('Gabon')),
    ('Gambia', ('Gambia')),
    ('Georgia', ('Georgia')),
    ('Germany', ('Germany')),
    ('Ghana', ('Ghana')),
    ('Gibraltar', ('Gibraltar')),
    ('Greece', ('Greece')),
    ('Greenland', ('Greenland')),
    ('Grenada', ('Grenada')),
    ('Guadeloupe', ('Guadeloupe')),
    ('Guam', ('Guam')),
    ('Guatemala', ('Guatemala')),
    ('Guernsey', ('Guernsey')),
    ('Guinea', ('Guinea')),
    ('Guinea-Bissau', ('Guinea-Bissau')),
    ('Guyana', ('Guyana')),
    ('Haiti', ('Haiti')),
    ('Holy See (Vatican City)', ('Holy See (Vatican City)')),
    ('Honduras', ('Honduras')),
    ('Hungary', ('Hungary')),
    ('Iceland', ('Iceland')),
    ('India', ('India')),
    ('Indonesia', ('Indonesia')),
    ('Iran', ('Iran')),
    ('Iraq', ('Iraq')),
    ('Ireland', ('Ireland')),
    ('Isle of Man', ('Isle of Man')),
    ('Israel', ('Israel')),
    ('Italy', ('Italy')),
    ('Jamaica', ('Jamaica')),
    ('Japan', ('Japan')),
    ('Jersey', ('Jersey')),
    ('Jordan', ('Jordan')),
    ('Kazakhstan', ('Kazakhstan')),
    ('Kenya', ('Kenya')),
    ('Kiribati', ('Kiribati')),
    ('Kuwait', ('Kuwait')),
    ('Kyrgyzstan', ('Kyrgyzstan')),
    ('Lao People\'s Democratic Republic', ('Lao People\'s Democratic Republic')),
    ('Latvia', ('Latvia')),
    ('Lebanon', ('Lebanon')),
    ('Lesotho', ('Lesotho')),
    ('Liberia', ('Liberia')),
    ('Libyan Arab Jamahiriya', ('Libyan Arab Jamahiriya')),
    ('Liechtenstein', ('Liechtenstein')),
    ('Lithuania', ('Lithuania')),
    ('Luxembourg', ('Luxembourg')),
    ('Macedonia', ('Macedonia')),
    ('Madagascar', ('Madagascar')),
    ('Malawi', ('Malawi')),
    ('Malaysia', ('Malaysia')),
    ('Maldives', ('Maldives')),
    ('Mali', ('Mali')),
    ('Malta', ('Malta')),
    ('Marshall Islands', ('Marshall Islands')),
    ('Martinique', ('Martinique')),
    ('Mauritania', ('Mauritania')),
    ('Mauritius', ('Mauritius')),
    ('Mayotte', ('Mayotte')),
    ('Mexico', ('Mayotte')),
    ('Micronesia, Federated States of', ('Micronesia, Federated States of')),
    ('Monaco', ('Monaco')),
    ('Mongolia', ('Mongolia')),
    ('Montenegro', ('Montenegro')),
    ('Montserrat', ('Montserrat')),
    ('Morocco', ('Morocco')),
    ('Mozambique', ('Mozambique')),
    ('Myanmar', ('Myanmar')),
    ('Namibia', ('Namibia')),
    ('Nauru', ('Nauru')),
    ('Nepal', ('Nepal')),
    ('Netherlands', ('Netherlands')),
    ('Netherlands Antilles', ('Netherlands Antilles')),
    ('New Caledonia', ('New Caledonia')),
    ('New Zealand', ('New Zealand')),
    ('Nicaragua', ('Nicaragua')),
    ('Niger', ('Niger')),
    ('Nigeria', ('Nigeria')),
    ('Niue', ('Niue')),
    ('Norfolk Island', ('Norfolk Island')),
    ('Northern Mariana Islands', ('Northern Mariana Islands')),
    ('Norway', ('Norway')),
    ('Occupied Palestinian Territory', ('Occupied Palestinian Territory')),
    ('Oman', ('Oman')),
    ('Pakistan', ('Pakistan')),
    ('Palau', ('Palau')),
    ('Panama', ('Panama')),
    ('Papua New Guinea', ('Papua New Guinea')),
    ('Paraguay', ('Paraguay')),
    ('Peru', ('Peru')),
    ('Philippines', ('Philippines')),
    ('Pitcairn', ('Pitcairn')),
    ('Poland', ('Poland')),
    ('Portugal', ('Portugal')),
    ('Puerto Rico', ('Puerto Rico')),
    ('Qatar', ('Qatar')),
    ('Republic of Korea', ('Republic of Korea')),
    ('Republic of Moldova', ('Republic of Moldova')),
    ('Reunion', ('Reunion')),
    ('Romania', ('Romania')),
    ('Russian Federation', ('Russian Federation')),
    ('Rwanda', ('Rwanda')),
    ('Saint-Barthelemy', ('Saint-Barthelemy')),
    ('Saint Helena', ('Saint Helena')),
    ('Saint Kitts and Nevis', ('Saint Kitts and Nevis')),
    ('Saint Lucia', ('Saint Lucia')),
    ('Saint-Martin (French part)', ('Saint-Martin (French part)')),
    ('Saint Pierre and Miquelon', ('Saint Pierre and Miquelon')),
    ('Saint Vincent and the Grenadines', ('Saint Vincent and the Grenadines')),
    ('Samoa', ('Samoa')),
    ('San Marino', ('San Marino')),
    ('Sao Tome and Principe', ('Sao Tome and Principe')),
    ('Saudi Arabia', ('Saudi Arabia')),
    ('Senegal', ('Senegal')),
    ('Serbia', ('Serbia')),
    ('Seychelles', ('Seychelles')),
    ('Sierra Leone', ('Sierra Leone')),
    ('Singapore', ('Singapore')),
    ('Slovakia', ('Slovakia')),
    ('Slovenia', ('Slovenia')),
    ('Solomon Islands', ('Solomon Islands')),
    ('Somalia', ('Somalia')),
    ('South Africa', ('South Africa')),
    ('Spain', ('Spain')),
    ('Sri Lanka', ('Sri Lanka')),
    ('Sudan', ('Sudan')),
    ('Suriname', ('Suriname')),
    ('Svalbard and Jan Mayen Islands', ('Svalbard and Jan Mayen Islands')),
    ('Swaziland', ('Swaziland')),
    ('Sweden', ('Sweden')),
    ('Switzerland', ('Switzerland')),
    ('Syrian Arab Republic', ('Syrian Arab Republic')),
    ('Tajikistan', ('Tajikistan')),
    ('Thailand', ('Thailand')),
    ('Timor-Leste', ('Timor-Leste')),
    ('Togo', ('Togo')),
    ('Tokelau', ('Tokelau')),
    ('Tonga', ('Tonga')),
    ('Trinidad and Tobago', ('Trinidad and Tobago')),
    ('Tunisia', ('Tunisia')),
    ('Turkey', ('Turkey')),
    ('Turkmenistan', ('Turkmenistan')),
    ('Turks and Caicos Islands', ('Turks and Caicos Islands')),
    ('Tuvalu', ('Tuvalu')),
    ('Uganda', ('Uganda')),
    ('Ukraine', ('Ukraine')),
    ('United Arab Emirates', ('United Arab Emirates')),
    ('United Kingdom', ('United Kingdom')),
    ('United Republic of Tanzania', ('United Republic of Tanzania')),
    ('United States of America', ('United States of America')),
    ('United States Virgin Islands', ('United States Virgin Islands')),
    ('Uruguay', ('Uruguay')),
    ('Uzbekistan', ('Uzbekistan')),
    ('Vanuatu', ('Vanuatu')),
    ('Venezuela (Bolivarian Republic of)', ('Venezuela (Bolivarian Republic of)')),
    ('Viet Nam', ('Viet Nam')),
    ('Wallis and Futuna Islands', ('Wallis and Futuna Islands')),
    ('Western Sahara', ('Western Sahara')),
    ('Yemen', ('Yemen')),
    ('Zambia', ('Zambia')),
    ('Zimbabwe', ('Zimbabwe')),
)

# Chronostratigraphic Choices
phanerozoic = "Phanerozoic"
proterozoic = "Proterozoic"
archaen = "Archaen"
EON_CHOICES = (
    (phanerozoic, "Phanerozoic"),
    (proterozoic, "Proterozoic"),
    (archaen, "Archaen")
)

cenozoic = "Cenozoic"
mesozoic = "Mesozoic"
paleozoic = "Paleozoic"
ERA_CHOICES = (
    (cenozoic, "Cenozoic"),
    (mesozoic, "Mesozoic"),
    (paleozoic, "Paleozoic")
)

quaternary = "Quaternary"
neogene = "Neogene"
paleogene = "Paleogene"
cretaceous = "Cretaceous"
PERIOD_CHOICES = (
    (quaternary, "Quaternary"),
    (neogene, "Neogene"),
    (paleogene, "Paleogene"),
    (cretaceous, "Cretaceous"),
)

# Epochs of the Cenozooic
holocene = 'Holocene'
pleistocene = 'Pleistocene'
pliocene = 'Pliocene'
miocene = 'Miocene'
oligocene = 'Oligocene'
eocene = 'Eocene'
paleocene = 'Paleocene'

EPOCH_CHOICES = (
    (holocene, "Holocene"),
    (pleistocene, "Pleistocene"),
    (pliocene, "Pliocene"),
    (miocene, "Miocene"),
    (oligocene, "Oligocene"),
    (eocene, "Eocene"),
    (paleocene, "Paleocene")
)

upper = "Upper"
middle = "Middle"
calabrian = "Calabrian"
gelasian = "Gelasian"
piacenzian = "Piacenzian"
zanclean = "Zanclean"
messinian = "Messinian"
tortonian = "Tortonian"
Serravallian = "Seravallian"
langhian = "Langhian"
burdigalian = "Burdigalian"
aquitanian = "Aquitanian"

AGE_CHOICES = (
    (upper, "Upper"),
    (middle, "Middle"),
    (calabrian, "Calabrian"),
    (gelasian, "Gelasian"),
    (piacenzian, "Piacenzian"),
    (zanclean, "Zanclean"),
    (messinian, "Messinian"),
    (tortonian, "Tortonian"),
    (Serravallian, "Seravallian"),
    (langhian, "Langhian"),
    (burdigalian, "Burdigalian"),
    (aquitanian, "Aquitanian",)
)


# Raw Material Choices - Derived from tDAR
basketry = 'basketry'
building_material = "building material"
ceramic = "ceramic"
chipped_stone = "chipped stone "
dating_sample = "dating sample"
fauna = "fauna "
fire_cracked_rock = "fire-cracked rock "
glass = "glass "
ground_stone = "ground stone "
hide = "hide "
human_remains = "human remains "
macrobotanical = "macrobotanical "
metal = "metal "
mineral = "mineral "
pollen = "pollen "
shell = "shell "
textile = "textile "
wood = "wood"
MATERIAL_CHOICES = (
    (basketry, "basketry"),
    (building_material, "building material"),
    (ceramic, "ceramic"),
    (chipped_stone, "chipped stone"),
    (dating_sample, "dating sample"),
    (fauna, "fauna"),
    (fire_cracked_rock, "fire-cracked rock"),
    (glass, "glass"),
    (ground_stone, "ground stone"),
    (hide, "hide"),
    (human_remains, "human remains"),
    (macrobotanical, "macrobotanical"),
    (metal, "metal"),
    (mineral, "mineral"),
    (pollen, "pollen"),
    (shell, "shell"),
    (textile, "textile"),
    (wood, "wood")
)  # Choice list comes from tDAR"

open_air = "open-air"
cave = "cave"
rockshelter = "rockshelter"
SETTING_CHOICES = (
    (open_air, "open-air"),
    (cave, "cave"),
    (rockshelter, "rockshelter")
)





















































