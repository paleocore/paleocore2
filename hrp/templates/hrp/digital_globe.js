/**
 * Created by reedd on 12/28/16.
 */
{% extends "gis/admin/openlayers.js" %}
{% block base_layer %}
        new OpenLayers.Layer.XYZ(
            "Imagery",
            [
                'http://api.tiles.mapbox.com/v4/digitalglobe.nal0mpda/${z}/${x}/${y}.png?access_token=pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNpeDl2eDlwdDAwMzAyeWxmbGw0dnAzdncifQ.kzw2UmbmVEtecHgFxMDENw', // You will need to replace the 'access_token' and 'Map ID' values with your own. http://developer.digitalglobe.com/docs/maps-api

            ],
            {
                attribution: "Tiles Courtesy of <a href='http://mapsapidocs.digitalglobe.com/' target='_blank'>© DigitalGlobe, Inc</a>.",
                transitionEffect: "resize"
            }
        )
{% endblock %}
