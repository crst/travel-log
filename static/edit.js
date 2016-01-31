
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
    // Bind event handlers
    $('#save').click(app.edit.save_items);
    app.edit.bind_upload();
    app.edit.bind_timestamp();
    app.edit.bind_description();

    // Setup map
    app.map.resize_map();
    app.map.init_map({'drag_marker': true});
    app.edit.bind_coordinates();
    app.edit.bind_zoom();

    // Update page
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
                app.edit.update_items();
            }
        }
    });
};

app.edit.update_items = function () {
    var handle_items = function (items) {
        var sorted_item_list = items.items;
        var item_buffer = {};


        var thumbnail_buffer = [];
        for (var i=0; i<sorted_item_list.length; i++) {
            var cur_item = sorted_item_list[i];
            item_buffer[cur_item.id] = cur_item;
            var current_item_key = cur_item.id;
            if (!app.edit.current_item) {
                app.edit.current_item = current_item_key;
            }
            var item = items[current_item_key];

            thumbnail_buffer.push(
                '<div class="col-sm-6, col-md-12">',
                '<a href="#" class="thumbnail item-thumbnail" data-item="', current_item_key, '">',
                '<img src="', cur_item.image, '">',
                '</a>',
                '</div>'
            );
        }
        app.edit.items = item_buffer;
        $('#thumbnail-list').html(thumbnail_buffer.join(''));
        app.edit.bind_thumbnails();
        app.edit.select_item(app.edit.current_item);
        // TODO: select_item should not cause a call from the marker
        // to mark_unsaved_changes
        window.setTimeout(function () {
            app.edit.mark_everything_saved();
        }, 10);
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
    if (item) {
        $('#current-item').html(
            '<img src="' + item.image + '">'
        );

        $('#item-timestamp').val(item.ts);
        $('#item-description').val(item.description);

        app.map.set_marker(item);
    }
};



app.edit.bind_timestamp = function () {
    $('#item-timestamp').on('input', function () {
        var item = app.edit.get_current_item();
        item.ts = $(this).val();
        app.edit.mark_unsaved_changes();
        app.edit.set_work_in_progress(5);
    });
};

app.edit.bind_description = function () {
    $('#item-description').on('input', function () {
        var item = app.edit.get_current_item();
        item.description = $(this).val();
        app.edit.mark_unsaved_changes();
        app.edit.set_work_in_progress(5);
    });
};

app.edit.bind_coordinates = function () {
    app.map.marker.on('change', function() {
        var coord = this.getGeometry().getCoordinates();
        coord = ol.proj.transform(coord, 'EPSG:3857', 'EPSG:4326');
        var item = app.edit.get_current_item();
        item.lat = coord[1];
        item.lon = coord[0];
        app.edit.mark_unsaved_changes();
        app.edit.set_work_in_progress(5);
    });
};

app.edit.bind_zoom = function () {
    var view = app.map.map.getView();
    view.on('change:resolution', function () {
        var item = app.edit.get_current_item();
        item.zoom = view.getZoom();
        app.edit.mark_unsaved_changes();
        app.edit.set_work_in_progress(5);
    });
};
