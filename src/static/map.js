
var app = app || {};
app.map = {};

app.map.map = undefined;
app.map.marker = undefined;


$(window).resize(function () {
    app.map.resize_map();
});

app.map.resize_map = function () {
    var m = $('#map-panel');
    $('#map').width(m.width()).height(m.height());
};

app.map.init_map = function (args) {
    args = args || {};

    var marker_feature = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.transform([13.383, 52.516], 'EPSG:4326', 'EPSG:3857'))
    });

    var drag_interaction = new ol.interaction.Modify({
        features: new ol.Collection([marker_feature]),
        style: null
    });

    var marker_style = new ol.style.Style({
        image: new ol.style.Icon(({
            opacity: 1,
            src: '/static/marker.png' // Maps Icons Collection https://mapicons.mapsmarker.com
        }))
    });
    marker_feature.setStyle(marker_style);

    var marker_layer = new ol.layer.Vector({
        source: new ol.source.Vector({
            features: [marker_feature]
        })
    });

    var map_options = {
        'layers': [
            new ol.layer.Tile({
                source: new ol.source.OSM({
                    crossOrigin: null,
                    //url: 'http://{a-b}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
                    url: 'https://cartodb-basemaps-{a-d}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
                    attributions: [
                        ol.source.OSM.ATTRIBUTION,
                        new ol.Attribution({
                            'html': '<p class="Attribution-text u-left"> <span id="CopyText" class="CopyText">Map tiles by <a href="http://cartodb.com/attributions#basemaps">CartoDB</a>, under <a href="https://creativecommons.org/licenses/by/3.0/" target="_blank">CC BY 3.0</a>. Data by <a href="http://www.openstreetmap.org/" target="_blank">OpenStreetMap</a>, under ODbL.</span> </p>'
                        }),
                    ]
                }),
            }),
            marker_layer,
        ],
        'view': new ol.View({
            'projection': 'EPSG:3857',
            'center': ol.proj.transform([13.383, 52.516], 'EPSG:4326', 'EPSG:3857'),
            'zoom': 10
        }),
        'target': 'map',
    };

    app.map.map = new ol.Map(map_options);
    if (args.drag_marker) {
        app.map.map.addInteraction(drag_interaction);
    }

    app.map.marker = marker_feature;
    app.map.marker_layer = marker_layer;
};

app.map.set_marker = function (item) {
    if (item.lat !== 'None' && item.lon !== 'None') {
        var lat = parseFloat(item.lat);
        var lon = parseFloat(item.lon);
        var proj = ol.proj.transform([lon, lat], 'EPSG:4326', 'EPSG:3857');
        app.map.marker.setGeometry(new ol.geom.Point(proj));
        var view = app.map.map.getView();
        view.setCenter(proj);
        view.setZoom(item.zoom);
        //app.map.marker_layer.setVisible(true);
    }
};
