from django.shortcuts import render
from django.views import generic
from .forms import UpdateSitesForm, UpdateSitesModelForm
from .models import Fossil, Site
from django.contrib import messages
from djgeojson.views import GeoJSONLayerView, GeoJSONResponseMixin
from djgeojson.serializers import Serializer as GeoJSONSerializer
from django.contrib.auth.mixins import LoginRequiredMixin


class UpdateSites(generic.FormView):
    template_name = 'admin/origins/site/update_sites.html'
    form_class = UpdateSitesModelForm
    context_object_name = 'upload'
    success_url = '../'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        idstring = self.request.GET['ids']
        idlist = idstring.split(',')
        new_site = form.cleaned_data['site']
        update_count = 0
        for fossil_id in idlist:
            fossil = Fossil.objects.get(pk=fossil_id)
            fossil.site = new_site
            fossil.save()
            update_count += 1
        if update_count == 1:
            count_string = '1 record'
        if update_count > 1:
            count_string = '{} records'.format(update_count)
        messages.add_message(self.request, messages.INFO, 'Successfully updated {}'.format(count_string))
        return super(UpdateSites, self).form_valid(form)


class MyGeoJSONLayerView(GeoJSONLayerView):

    crs = False

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        serializer = GeoJSONSerializer()
        response = self.response_class(**response_kwargs)
        queryset = self.get_queryset()

        options = dict(properties=self.properties,
                       precision=self.precision,
                       simplify=self.simplify,
                       srid=self.srid,
                       geometry_field=self.geometry_field,
                       force2d=self.force2d,
                       bbox=self.bbox,
                       bbox_auto=self.bbox_auto,
                       use_natural_keys=self.use_natural_keys)
        serializer.serialize(queryset, stream=response, ensure_ascii=False,
                             crs=self.crs,  # in geoJSON crs is deprecated, raises error 36 in ol.source
                             **options)
        return response
