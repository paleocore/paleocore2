from django.conf.urls import url, include
from projects import views
from projects.models import ProjectPage
from djgeojson.views import GeoJSONLayerView

urlpatterns = [
               #                        # Projects list view
               #                        # ex. /projects/
               #                        url(r'^$', views.ProjectIndexView.as_view(), name='index'),
               #
               #                        # Project detail view
               #                        # ex. /projects/mlp/
               #                        url(r'^(?P<pcoreapp>\w+)/$', views.ProjectDetailView.as_view(), name='detail'),
               #
               #                        # Individual project public data table view
               #                        # ex. /projects/data_table/mlp/
               #                        url(r'^data_table/(?P<pcoreapp>.+)/$', views.projectDataTable, name='data_table'),
               #                        # TODO change url formulation to projects/projects/data_table, e.x. projects/mlp/data_table
               #
               # url to get a geojson representation of all PaleoCore projects
               # ex. /projects/projects.geojson
               url(r'^projects.geojson$',
                   GeoJSONLayerView.as_view(model=ProjectPage, properties=['title', 'slug', 'url_path'], geometry_field=('location')),
                   name='projects_geojson'),
               #
               #                        # ex. /projects/data_json/mlp/
               #                        url(r'^data_json/(?P<pcoreapp>.+)/$', views.ajaxProjectData, name='data_json'),
               #                        # TODO get working tests for this view
               #
               #                        # url(r'^data/(?P<pcoreapp>[^/]+)/$', views.ProjectDataView.as_view(), name='data'),
               #                        url(r'^(?P<pcoreapp>.+)/(?P<occurrence_id>\d+)/$', views.OccurrenceDetailView.as_view(),
               #                            name='occurrence_detail'),
               #                        # TODO get working test for this view
               #
               #                        # mlp project url includes
               #                        # ex. /projects/mlp/upload/
               #                        url(r'^mlp/', include('mlp.urls', namespace='mlp')),
               #
               #                        # san_francisco url includes
               #                        # ex. /projects/san_francisco/upload
               #                        url(r'^san_francisco/', include('san_francisco.urls', namespace='san_francisco')),
               #
               #                        # san_francisco url includes
               #                        # ex. /projects/san_francisco/upload
               #                        url(r'^omo_mursi/', include('omo_mursi.urls', namespace='omo_mursi')),
               #
               #                        # west_turkana url includes
               #                        # ex. /projects/west_turkana/upload
               #                        url(r'^west_turkana/', include('west_turkana.urls', namespace='west_turkana')),
               #
               #                        # lgrp project url includes
               #                        # ex. /projects/lgrp/upload/
               #                        url(r'^lgrp/', include('lgrp.urls', namespace='lgrp')),
               #
               #                        # gdb project url includes
               #                        # ex. /projects/gdb/upload/
               #                        url(r'^gdb/', include('gdb.urls', namespace='gdb')),
               #
               ]
