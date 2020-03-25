import sqlite3

ITEM_TYPE_VOCABULARY = (("Artifactual", "Artifactual"), ("Faunal", "Faunal"), ("Floral", "Floral"), ("Geological", "Geological"))
LGRP_BASIS_OF_RECORD_VOCABULARY = (("Collection", "Collection"), ("Observation", "Observation"))

LGRP_COLLECTING_METHOD_VOCABULARY = (
    ("Survey", "Survey"),
    ("Wet Screen", "Wet Screen"),
    ("Crawl survey", "Crawl survey"),
    ("Transect survey", "Transect survey"),
    ("Dry Screen", "Dry Screen"),
    ("Excavation", "Excavation"),
)

LGRP_COLLECTOR_CHOICES = (
    ("LGRP Team", "LGRP Team"),
    ("K.E. Reed", "K.E. Reed"),
    ("S. Oestmo", "S. Oestmo"),
    ("L. Werdelin", "L. Werdelin"),
    ("C.J. Campisano", "C.J. Campisano"),
    ("D.R. Braun", "D.R. Braun"),
    ("Tomas", "Tomas"),
    ("J. Rowan", "J. Rowan"),
    ("B. Villamoare", "B. Villamoare"),
    ("C. Seyoum", "C. Seyoum"),
    ("E. Scott", "E. Scott"),
    ("E. Locke", "E. Locke"),
    ("J. Harris", "J. Harris"),
    ("I. Lazagabaster", "I. Lazagabaster"),
    ("I. Smail", "I. Smail"),
    ("D. Garello", "D. Garello"),
    ("E.N. DiMaggio", "E.N. DiMaggio"),
    ("W.H. Kimbel", "W.H. Kimbel"),
    ("J. Robinson", "J. Robinson"),
    ("M. Bamford", "M. Bamford"),
    ("Zinash", "Zinash"),
    ("D. Feary", "D. Feary"),
    ("D. I. Garello", "D. I. Garello"),
)

LGRP_FINDER_CHOICES = LGRP_COLLECTOR_CHOICES + (
    ("Afar", "Afar"),
)

LGRP_IDENTIFIER_CHOICES = (
    ('D. Braun', 'D. Braun'),
    ('J. Thompson', 'J. Thompson'),
    ('E. Scott', 'E. Scott'),
    ('E. Locke', 'E. Locke'),
    ('A.E. Shapiro', 'A.E. Shapiro'),
    ('A.W. Gentry', 'A.W. Gentry'),
    ('B.J. Schoville', 'B.J. Schoville'),
    ('B.M. Latimer', 'B.M. Latimer'),
    ('C. Denys', 'C. Denys'),
    ('C.A. Lockwood', 'C.A. Lockwood'),
    ('D. Geraads', 'D. Geraads'),
    ('D.C. Johanson', 'D.C. Johanson'),
    ('E. Delson', 'E. Delson'),
    ('B. Villmoare', 'B. Villmoare'),
    ('E.S. Vrba', 'E.S. Vrba'),
    ('F.C. Howell', 'F.C. Howell'),
    ('G. Petter', 'G. Petter'),
    ('G. Suwa', 'G. Suwa'),
    ('G.G. Eck', 'G.G. Eck'),
    ('H.B. Krentza', 'H.B. Krentza'),
    ('H.B. Wesselman', 'H.B. Wesselman'),
    ('H.B.S. Cooke', 'H.B.S. Cooke'),
    ('Institute Staff', 'Institute Staff'),
    ('J.C. Rage', 'J.C. Rage'),
    ('K.E. Reed', 'K.E. Reed'), ('L.A. Werdelin', 'L.A. Werdelin'), ('L.J. Flynn', 'L.J. Flynn'),
    ('M. Sabatier', 'M. Sabatier'), ('M.E. Lewis', 'M.E. Lewis'), ('N. Fessaha', 'N. Fessaha'),
    ('P. Brodkorb', 'P. Brodkorb'), ('R. Bobe-Quinteros', 'R. Bobe-Quinteros'), ('R. Geze', 'R. Geze'),
    ('R.L. Bernor', 'R.L. Bernor'), ('S.R. Frost', 'S.R. Frost'), ('T.D. White', 'T.D. White'),
    ('T.K. Nalley', 'T.K. Nalley'), ('V. Eisenmann', 'V. Eisenmann'), ('W.H. Kimbel', 'W.H. Kimbel'),
    ('Z. Alemseged', 'Z. Alemseged'), ('S. Oestmo', 'S. Oestmo'), ('J. Rowan', 'J. Rowan'),
    ('C.J. Campisano', 'C.J. Campisano'), ('J. Robinson', 'J. Robinson'), ('I. Smail', 'I. Smail'),
    ('I. Lazagabaster', 'I. Lazagabaster'), ('A. Rector', 'A. Rector')
)


LGRP_COLLECTION_CODES = (
    ("AA", "AA"),
    ("AM", "AM"),
    ("AM12", "AM12"),
    ("AS", "AS"),
    ("AT", "AT"),
    ("BD", "BD"),
    ("BG", "BG"),
    ("BR", "BR"),
    ("DK", "DK"),
    ("FD", "FD"),
    ("GR", "GR"),
    ("HD", "HD"),
    ("HS", "HS"),
    ("KG", "KG"),
    ("KL", "KL"),
    ("KT", "KT"),
    ("LD", "LD"),
    ("LG", "LG"),
    ("LN", "LN"),
    ("LS", "LS"),
    ("MF", "MF"),
    ("NL", "NL"),
    ("OI", "OI"),
    ("SS", "SS"),
)

LGRP_ELEMENT_CHOICES = (
    ('astragalus', 'astragalus'),
    ('bacculum', 'bacculum'),
    ('bone (indet.)', 'bone (indet.)'),
    ('calcaneus', 'calcaneus'),
    ('canine', 'canine'),
    ('capitate', 'capitate'),
    ('carapace', 'carapace'),
    ('carpal (indet.)', 'carpal (indet.)'),
    ('carpal/tarsal', 'carpal/tarsal'),
    ('carpometacarpus', 'carpometacarpus'),
    ('carpus', 'carpus'),
    ('chela', 'chela'),
    ('clavicle', 'clavicle'),
    ('coccyx', 'coccyx'),
    ('coprolite', 'coprolite'),
    ('cranium', 'cranium'),
    ('cranium w/horn core', 'cranium w/horn core'),
    ('cuboid', 'cuboid'),
    ('cubonavicular', 'cubonavicular'),
    ('cuneiform', 'cuneiform'),
    ('dermal plate', 'dermal plate'),
    ('egg shell', 'egg shell'),
    ('endocast', 'endocast'),
    ('ethmoid', 'ethmoid'),
    ('femur', 'femur'),
    ('fibula', 'fibula'),
    ('frontal', 'frontal'),
    ('hamate', 'hamate'),
    ('horn core', 'horn core'),
    ('humerus', 'humerus'),
    ('hyoid', 'hyoid'),
    ('Ilium', 'Ilium'),
    ('incisor', 'incisor'),
    ('innominate', 'innominate'),
    ('ischium', 'ischium'),
    ('lacrimal', 'lacrimal'),
    ('long bone ', 'long bone '),
    ('lunate', 'lunate'),
    ('mandible', 'mandible'),
    ('manus', 'manus'),
    ('maxilla', 'maxilla'),
    ('metacarpal', 'metacarpal'),
    ('metapodial', 'metapodial'),
    ('metatarsal', 'metatarsal'),
    ('molar', 'molar'),
    ('nasal', 'nasal'),
    ('navicular', 'navicular'),
    ('naviculocuboid', 'naviculocuboid'),
    ('occipital', 'occipital'),
    ('ossicone', 'ossicone'),
    ('parietal', 'parietal'),
    ('patella', 'patella'),
    ('pes', 'pes'),
    ('phalanx', 'phalanx'),
    ('pisiform', 'pisiform'),
    ('plastron', 'plastron'),
    ('premaxilla', 'premaxilla'),
    ('premolar', 'premolar'),
    ('pubis', 'pubis'),
    ('radioulna', 'radioulna'),
    ('radius', 'radius'),
    ('rib', 'rib'),
    ('sacrum', 'sacrum'),
    ('scaphoid', 'scaphoid'),
    ('scapholunar', 'scapholunar'),
    ('scapula', 'scapula'),
    ('scute', 'scute'),
    ('sesamoid', 'sesamoid'),
    ('shell', 'shell'),
    ('skeleton', 'skeleton'),
    ('skull', 'skull'),
    ('sphenoid', 'sphenoid'),
    ('sternum', 'sternum'),
    ('talon', 'talon'),
    ('talus', 'talus'),
    ('tarsal (indet.)', 'tarsal (indet.)'),
    ('tarsometatarsus', 'tarsometatarsus'),
    ('tarsus', 'tarsus'),
    ('temporal', 'temporal'),
    ('tibia', 'tibia'),
    ('tibiotarsus', 'tibiotarsus'),
    ('tooth (indet.)', 'tooth (indet.)'),
    ('trapezium', 'trapezium'),
    ('trapezoid', 'trapezoid'),
    ('triquetrum', 'triquetrum'),
    ('ulna', 'ulna'),
    ('vertebra', 'vertebra'),
    ('vomer', 'vomer'),
    ('zygomatic', 'zygomatic'),
)

LGRP_ELEMENT_PORTION_CHOICES = (
    ('almost complete', 'almost complete'),
    ('anterior', 'anterior'),
    ('basal', 'basal'),
    ('complete', 'complete'),
    ('diaphysis', 'diaphysis'),
    ('diaphysis+distal', 'diaphysis+distal'),
    ('diaphysis+proximal', 'diaphysis+proximal'),
    ('distal', 'distal'),
    ('dorsal', 'dorsal'),
    ('epiphysis', 'epiphysis'),
    ('fragment', 'fragment'),
    ('fragments', 'fragments'),
    ('indeterminate', 'indeterminate'),
    ('lateral', 'lateral'),
    ('medial', 'medial'),
    ('midsection', 'midsection'),
    ('midsection+basal', 'midsection+basal'),
    ('midsection+distal', 'midsection+distal'),
    ('posterior', 'posterior'),
    ('proximal', 'proximal'),
    ('symphysis', 'symphysis'),
    ('ventral', 'ventral'),
)

LGRP_ELEMENT_NUMBER_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('3(medial)', '3(medial)'),
    ('4', '4'),
    ('4(lateral)', '4(lateral)'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
    ('2-7', '2-7'),
    ('8-12', '8-12'),
    ('indeterminate', 'indeterminate'),
)

LGRP_ELEMENT_MODIFIER_CHOICES = (
    ('articulated', 'articulated'),
    ('caudal', 'caudal'),
    ('cervical', 'cervical'),
    ('coccygeal', 'coccygeal'),
    ('distal', 'distal'),
    ('intermediate', 'intermediate'),
    ('lower', 'lower'),
    ('lumbar', 'lumbar'),
    ('manual', 'manual'),
    ('manual distal', 'manual distal'),
    ('manual intermediate', 'manual intermediate'),
    ('manual proximal', 'manual proximal'),
    ('pedal', 'pedal'),
    ('pedal distal', 'pedal distal'),
    ('pedal intermediate', 'pedal intermediate'),
    ('pedal proximal', 'pedal proximal'),
    ('proximal', 'proximal'),
    ('sacral', 'sacral'),
    ('thoracic', 'thoracic'),
    ('upper', 'upper'),
    ('indeterminate', 'indeterminate')
)

LGRP_SIDE_CHOICES = (
    ('L', 'L'),
    ('R', 'R'),
    ('Indeterminate', 'Indeterminate'),
    ('L+R', 'L+R')
)

LGRP_WEATHERING_CHOICES = (
    (0, '0 - unweathered'),
    (1, '1 - parallel cracking'),
    (2, '2 - flaking'),
    (3, '3 - rough'),
    (4, '4 - fibrous'),
    (5, '5 - crumbling')
)

lgrp_db_path = '/Users/reedd/Documents/projects/PaleoCore/projects/LGRP/LGRP_Paleobase4_2016.sqlite'
def import_vocabulary(column_name, path=lgrp_db_path):
    connection = sqlite3.connect(lgrp_db_path)
    cursor = connection.cursor()
    colrs = cursor.execute("SELECT {} FROM LookUpTable WHERE {} IS NOT NULL".format(column_name, column_name))
    column_names = [c[0] for c in cursor.description]
    col_list = []
    for row in colrs:
        l = list(row)
        l.append(row[0])
        col_list.append(tuple(l))
    return tuple(col_list)
