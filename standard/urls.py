from django.conf.urls import url
from . import views as standard_views

urlpatterns = [
    # e.g. /standards/
    #url(r'^$', standard_views.index, name="paleocore_terms_index"),
    url(r'^$', standard_views.PaleocoreTermsIndexView.as_view(), name="paleocore_terms_index"),

    # e.g. /standards/dwc
    url(r'^(?P<project_name>\w+)$', standard_views.TermsIndexView.as_view(), name="terms_index"),

]

