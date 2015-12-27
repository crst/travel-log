
var app = app || {};
app.edit = {};


// All item data by `id_item`.
app.edit.items = {};

app.edit.current_item = undefined;
app.edit.get_current_item = function () {
    return app.edit.items[app.edit.current_item];
};



/* We auto-save under two conditions:
 *   - There are unsaved changes.
 *   - And there is no work in progress.
 *
 * Any edit event can set the work_in_progress timer, which blocks
 * auto-saving for the value set in seconds.
 */
app.edit.has_unsaved_changes = false;
app.edit.handle_changes = function () {
    if (app.edit.has_unsaved_changes && app.edit.work_in_progress <= 0) {
        app.edit.save_items();
        app.edit.mark_everything_saved();
    }
};
window.setInterval(app.edit.handle_changes, 5 * 1000);
app.edit.mark_unsaved_changes = function () {
    app.edit.has_unsaved_changes = true;
    $('#last-saved').html('<a href="javascript:app.edit.save_items();">Save changes</a>');
};
app.edit.mark_everything_saved = function () {
    app.edit.has_unsaved_changes = false;
    $('#last-saved').hide().html('Last saved at ' + app.format_time(new Date())).fadeIn('fast');
};

app.edit.work_in_progress = 0;
app.edit.update_work_in_progress = function () {
    if (app.edit.work_in_progress > 0) {
        app.edit.work_in_progress -= 1;
    }
};
window.setInterval(app.edit.update_work_in_progress, 1 * 1000);
app.edit.set_work_in_progress = function (n) {
    app.edit.work_in_progress = n;
};




$(document).ready(function () {
    $('#save').click(app.edit.save_items);
    app.edit.resize_map();
    app.edit.bind_upload();
    app.edit.bind_description();

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
            'type': 'POST',
            'url': 'upload/',
            'data': form_data,
            'contentType': false,
            'cache': false,
            'processData': false,
            'async': true,
            'success': function (data) {
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


app.edit.save_items = function () {
    $.ajax({
        'type': 'POST',
        'url': 'save_items/',
        'data': JSON.stringify(app.edit.items),
        'contentType': 'application/json',
        'cache': false,
        'processData': false,
        'async': true,
        'success': function (data) {
            if (data['success']) {
                app.edit.mark_everything_saved();
            }
        }
    });
};

app.edit.update_items = function () {
    var handle_items = function (items) {
        app.edit.items = items;

        var thumbnail_buffer = [];
        for (var key in items) {
            if (items.hasOwnProperty(key)) {
                if (!app.edit.current_item) {
                    app.edit.current_item = key;
                }
                var item = items[key];

                thumbnail_buffer.push(
                    '<div class="col-sm-6, col-md-12">',
                    '<a href="#" class="thumbnail item-thumbnail" data-item="', key, '">',
                    '<img src="', item.image, '">',
                    '</a>',
                    '</div>'
                );
            }
        }
        $('#thumbnail-list').html(thumbnail_buffer.join(''));
        app.edit.bind_thumbnails();
        app.edit.select_item(app.edit.current_item);
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
    app.edit.current_item = id;
    var item = app.edit.items[id];
    $('#current-item').html(
        '<img src="' + item.image + '">'
    );

    $('#item-description').val(item.description);
};


app.edit.bind_description = function () {
    $('#item-description').on('input', function () {
        var item = app.edit.get_current_item();
        item.description = $(this).val();
        app.edit.mark_unsaved_changes();
        app.edit.set_work_in_progress(5);
    });
};
