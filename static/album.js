
var app = app || {};
app.album = {};

app.album.items = [];
app.album.current_item = 0;



$(document).ready(function () {
    $.ajax({
        'type': 'GET',
        'url': 'get_items/',
        success: app.album.handle_items
    });

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
    app.album.map = new ol.Map(map_options);


    app.album.bind_navigation();
});

app.album.bind_navigation = function (data) {
    $('#nav-prev').click(function () { app.album.prev_item(); })
    $('#nav-next').click(function () { app.album.next_item(); })

    $(document).bind('keydown', function (e) {
        if (e.keyCode === 37) { app.album.prev_item(); }
        //else if (e.keyCode === 32) { app.album.toggleAutoplay(); }
        else if (e.keyCode === 39) { app.album.next_item(); }
    });
};

app.album.handle_items = function (data) {
    var items = [];
    for (var key in data) {
        var item = data[key];
        var img = $('<img src="' + item.image + '">');
        items.push({
            'img': img,
            'time': item.ts,
            'description': item.description
        })
    }
    app.album.items = items;

    app.album.switch_to_item(0);
};


app.album.switch_to_item = function (i) {
    var item = app.album.items[i];
    $('#main-image').html(item.img);
    $('#item-description').html(item.description);
};

app.album.skip = function (f) {
    app.album.current_item = mod(f(app.album.current_item), app.album.items.length);
    app.album.switch_to_item(app.album.current_item);
}

app.album.next_item = function () {
    app.album.skip(function (i) { return i + 1; });
}

app.album.prev_item = function () {
    app.album.skip(function (i) { return i - 1; });
};


var mod = function (x, n) {
  return ((x % n) + n) % n;
};
