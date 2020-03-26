from django.conf.urls import url
from hrp import views as hrp_views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Project URLs are included by main urls.py

    # /projects/omo_mursi/upload/
    url(r'^upload/$', login_required(hrp_views.UploadKMLView.as_view(), login_url='/login/'), name="hrp_upload_kml"),

    # /projects/omo_mursi/download/
    url(r'^download/$', hrp_views.DownloadKMLView.as_view(), name="hrp_download_kml"),

    # /projects/omo_mursi/confirmation/
    url(r'^confirmation/$', hrp_views.Confirmation.as_view(), name="hrp_upload_confirmation"),

    # /projects/omo_mursi/upload/shapefile/
    # url(r'^upload/shapefile/', hrp_views.UploadShapefileView.as_view(), name="hrp_upload_shapefile"),

    # /projects/omo_mursi/change_xy/
    url(r'^change_xy/', hrp_views.change_coordinates_view, name="hrp_change_xy"),
]
