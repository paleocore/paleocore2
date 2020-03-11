from django.conf.urls import url
from . import views as mlp_views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Project URLs are included by main urls.py

    # /projects/mlp/confirmation/
    url(r'^confirmation/$', mlp_views.Confirmation.as_view(), name="mlp_upload_confirmation"),

    # /projects/mlp/upload/shapefile/
    # url(r'^upload/shapefile/', mlp_views.UploadShapefileView.as_view(), name="mlp_upload_shapefile"),

    # /projects/mlp/change_xy/
    url(r'^change_xy/', mlp_views.change_coordinates_view, name="mlp_change_xy"),

    # /projects/mlp/occurrence2biology/
    url(r'^occurrence2biology/', mlp_views.occurrence2biology_view, name="mlp_occurrence2biology"),

]
