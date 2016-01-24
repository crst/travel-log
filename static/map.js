
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

app.map.init_map = function () {
    var markerFeature = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.transform([13.383, 52.516], 'EPSG:4326', 'EPSG:3857'))
    });

    var dragInteraction = new ol.interaction.Modify({
        features: new ol.Collection([markerFeature]),
        style: null
    });

    var markerStyle = new ol.style.Style({
        image: new ol.style.Icon(/* @type {olx.style.IconOptions} */ ({
            opacity: 1,
            src: '/static/marker.png' // Maps Icons Collection https://mapicons.mapsmarker.com
        }))
    });
    markerFeature.setStyle(markerStyle);

    var vectorLayer = new ol.layer.Vector({
        source: new ol.source.Vector({
            features: [markerFeature]
        })
    });

    var map_options = {
        'layers': [
            new ol.layer.Tile({
                source: new ol.source.OSM({
                    crossOrigin: null,
                    //url: 'http://{a-b}.www.toolserver.org/tiles/bw-mapnik/{z}/{x}/{y}.png'
                }),
            }),
            vectorLayer,
        ],
        'view': new ol.View({
            'projection': 'EPSG:3857',
            'center': ol.proj.transform([13.383, 52.516], 'EPSG:4326', 'EPSG:3857'),
            'zoom': 10
        }),
        'target': 'map',
    };

    app.map.map = new ol.Map(map_options);
    app.map.map.addInteraction(dragInteraction);
    app.map.marker = markerFeature;
};


app.map.set_marker = function (item) {
    if (item.lat !== 'None' && item.lon !== 'None') {
        var lat = parseFloat(item.lat);
        var lon = parseFloat(item.lon);
        var point = new ol.geom.Point(ol.proj.transform([lon, lat], 'EPSG:4326', 'EPSG:3857'));
        app.map.marker.setGeometry(point);
    }
};
