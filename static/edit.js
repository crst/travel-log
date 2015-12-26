
var app = app || {};
app.edit = {};
app.edit.selected_item = undefined;

$(document).ready(function () {
    app.edit.resize_map();
    app.edit.bind_upload();

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

    app.edit.update_items();
});



app.edit.bind_upload = function () {
    $('#image-file').change(function (e) {
        var form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: 'POST',
            url: 'upload/',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                if (data['success']) {
                    app.edit.update_items();
                }
            }
        });
    });
};


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


app.edit.update_items = function () {
    var handle_items = function (items) {
        app.edit.items = items;

        var buffer = [];
        for (var key in items) {
            if (items.hasOwnProperty(key)) {
                if (!app.edit.selected_item) {
                    app.edit.selected_item = key;
                }
                var item = items[key];
                buffer.push(
                    '<div class="col-sm-6, col-md-12">',
                    '<a href="#" class="thumbnail item-thumbnail" data-item="', key, '">',
                    '<img src="', item.image, '">',
                    '</a>',
                    '</div>'
                );
            }
        }
        $('#thumbnail-list').html(buffer.join(''));
        app.edit.bind_thumbnails();
        app.edit.select_item(app.edit.selected_item);
    };
    $.ajax({
        'type': 'GET',
        'url': 'get_items/',
        success: handle_items
    });
};

app.edit.bind_thumbnails = function () {
    $('.item-thumbnail').click(function () {
        var id = $(this).attr('data-item');
        app.edit.select_item(id);
    });
};

app.edit.select_item = function (id) {
    app.edit.selected_item = id;
    var item = app.edit.items[id];
    $('#current-item').html(
        '<img src="' + item.image + '">'
    );
};
