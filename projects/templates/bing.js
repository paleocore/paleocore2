/**
 * Created by reedd on 10/5/17.
 */
{% extends "gis/admin/openlayers.js" %}
{% block base_layer %}
        new OpenLayers.Layer.Bing({
            name: "Bing Map",
            type: "Aerial",
            key: "Ar53nx2qnSFcrZZZ4nh6Q_mGb_1BVl3jNP3tldp5lJ8SeUgAnMZGnTCNsTQ7O72e"
        })
{% endblock %}