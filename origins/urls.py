from django.conf.urls import url
from origins.models import SitePage, WorldBorder
from .views import MyGeoJSONLayerView

urlpatterns = [
    # url to get a geojson representation of all Origins sites
    # ex. /origins/origins.geojson  Note no trailing slash!
    url(r'^origins.geojson$',
        MyGeoJSONLayerView.as_view(model=SitePage,
                                   crs=False,
                                   properties=['title', 'slug', 'url_path'],
                                   geometry_field='location'),
        name='sites_geojson'),
url(r'^countries.geojson$',
        MyGeoJSONLayerView.as_view(model=WorldBorder,
                                   crs=False,
                                   properties=['name', 'area', 'pop2005', 'fips'],
                                   geometry_field='mpoly'),
        name='countries_geojson'),
]
