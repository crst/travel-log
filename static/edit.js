
var app = app || {};
app.edit = {};

$(document).ready(function () {
    app.edit.resize_map();

    var map_options = {
        'target': 'map',
        'layers': [
            new ol.layer.Tile({
                source: new ol.source.MapQuest({layer: 'osm'})
            })
        ],
        'view': new ol.View({
            'projection': 'EPSG:3857',
            'center': ol.proj.transform([13.383, 52.516], 'EPSG:4326', 'EPSG:3857'),
            'zoom': 9
        })
    };
    app.edit.init_map(map_options);
});

$(window).resize(function () {
    app.edit.resize_map();
});

app.edit.resize_map = function () {
    var m = $('#map-panel');
    $('#map').width(m.width()).height(m.height());
};

app.edit.init_map = function (map_options) {
    app.edit.map = new ol.Map(map_options);
};
