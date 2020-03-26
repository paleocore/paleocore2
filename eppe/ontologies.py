# EPPE Areas Vocabulary
laetoli = 'Laetoli'
kakesio = 'Kakesio'
esere = 'Esere'

LAETOLI_AREAS = (
    (laetoli, 'Laetoli'),
    (kakesio, 'Kakesio'),
    (esere, 'Esere-Noiti'),
)

# Laetoli Stratigraphic Units
ngaloba = 'Ngaloba Beds'
upper_ngaloba = "Upper Ngaloba Beds"
lower_ngaloba = "Lower Ngaloba Beds"
qngaloba = '?Ngaloba Beds'
olpiro = 'Olpiro Beds'
naibadad = 'Naibadad Beds'
olgol = 'Olgol Lavas'
ndolanya = 'Ndolanya Beds'
upper_ndolanya = 'Upper Ndolanya Beds'
lower_ndolayna = 'Lower Ndolanya Beds'
laetolil = 'Laetolil Beds'
upper_laetolil = 'Upper Laetolil Beds'
lower_laetolil = 'Lower Laetolil Beds'

LAETOLI_UNITS = (
    (ngaloba, 'Ngaloba Beds'),
    (lower_ngaloba, "Lower Ngaloba Beds"),
    (upper_ngaloba, "Upper Ngaloba Beds"),
    (qngaloba, '?Ngaloba Beds'),
    (olpiro, 'Olpiro Beds'),
    (naibadad, 'Naibadad Beds'),
    (olgol, 'Olgol Lavas'),
    (ndolanya, 'Ndolanya Beds'),
    (upper_ndolanya, 'Upper Ndolanya Beds'),
    (lower_ndolayna, 'Lower Ndolanya Beds'),
    (laetolil, 'Laetolil Beds'),
    (upper_laetolil, 'Upper Laetolil Beds'),
    (lower_laetolil, 'Lower Laetolil Beds'),
)


LIFE_STAGE_CHOICES = (
    ('infant', 'infant'),
    ('juvenile', 'juvenile')
)

SIZE_CLASS_CHOICES = (
    ('indeterminate', 'indeterminate'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5')
)

argon_argon = '40Ar/39Ar dating'
argon_bayes = argon_argon + ', ' + 'bayesian interpolation'
amino_acid = 'Amino acid racimization'
biochrnology = 'Biochronology'
DATING_PROTOCOLS = (
    (amino_acid, 'Amino acid racimization'),
    (argon_argon, '40Ar/39Ar dating'),
    (argon_bayes, '40Ar/39Ar dating, bayesian interpolation'),
    (biochrnology, 'Biochronology')
)

deino_2011 = 'Deino AL. 2011. 40Ar/39Ar Dating of Laetoli, Tanzania. In: Harrison T, editor. ' \
             'Paleontology and Geology of Laetoli: Human Evolution in Context: Volume 1: Geology, ' \
             'Geochronology, Paleoecology and Paleoenvironment. Dordrecht: Springer Netherlands. p 77–97.'
DATING_REFERENCES = (
    (deino_2011, 'Deino et al., 2011'),
)
