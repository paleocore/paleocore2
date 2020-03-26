__author__ = 'reedd'

from .models import Occurrence, Biology, Taxon, IdentificationQualifier
from .ontologies import *
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
import collections

import re
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
import calendar
from datetime import datetime

from django.apps import apps

def get_terms(app_name):
    app_models = apps.get_app_config(app_name).get_models()
    terms = ()
    for model in app_models:
        terms += model._meta.fields
    term_list = [term.model._meta.label+'.'+term.name for term in terms]
    return term_list

def get_classes(app_name):
    app_models = apps.get_app_config(app_name).get_models()
    app_models_list = [model._meta.label for model in app_models]
    return app_models_list
