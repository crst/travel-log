
// ----------------------------------------------------------------------------
// Module app.edit

var app = app || {};
app.edit = {};

// Module state
// ------------
app.edit.album = {};

// All item data by `id_item`.
app.edit.items = {};

app.edit.current_item = undefined;
app.edit.get_current_item = function () {
    return app.edit.items[app.edit.current_item];
};


// ----------------------------------------------------------------------------
// Saving edits

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
        app.edit.save();
    }
};
window.setInterval(app.edit.handle_changes, 5 * 1000);
app.edit.mark_unsaved_changes = function () {
    app.edit.has_unsaved_changes = true;
    $('#last-saved').html('<a href="javascript:app.edit.save();">Save changes</a>');
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


// ----------------------------------------------------------------------------
// Initialize module

$(document).ready(function () {
    // Bind event handlers
    $('#save').click(app.edit.save);

    app.edit.bind_album_description();
    app.edit.bind_album_autoplay_delay();

    app.edit.bind_item_upload();
    app.edit.bind_item_toggle_visibility();
    app.edit.bind_item_timestamp();
    app.edit.bind_item_description();

    // Setup map
    app.map.resize_map();
    app.map.init_map({'drag_marker': true});
    app.edit.bind_map_coordinates();
    app.edit.bind_map_zoom();

    // Update page
    app.edit.update();
});


app.edit.bind_album_description = function () {
    $('#album-description').change(function (e) {
        app.edit.album.description = $('#album-description').val();

        app.edit.mark_unsaved_changes();
        app.edit.set_work_in_progress(5);
    });
};

app.edit.bind_album_autoplay_delay = function () {
    $('#album-autoplay-delay').change(function (e) {
        var delay = parseInt($(this).val());
        if (isNaN(delay)) {
            delay = 5;
            $(this).val(delay);
        }

        app.edit.album.autoplay_delay = delay;

        app.edit.mark_unsaved_changes();
        app.edit.set_work_in_progress(5);

    });
};

app.edit.bind_item_upload = function () {
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

app.edit.bind_item_toggle_visibility = function () {
    $('#toggle-current-item').click(function () {
        var item = app.edit.get_current_item();
        $.ajax({
            'type': 'POST',
            'url': 'set-item-visibility/',
            'data': JSON.stringify({'item-id': app.edit.current_item, 'item-visibility': !item.is_visible}),
            'contentType': false,
            'cache': false,
            'processData': false,
            'async': true,
            'success': function (data) {
                if (data['success']) {
                    app.edit.update_items();
                }
            }
        })
    });
};

app.edit.save = function () {
    if (app.edit.validate_input()) {
        app.edit.save_album();
        app.edit.save_items();

        // TODO: bind_map_coordinates should not cause a call from the
        // marker to mark_unsaved_changes
        window.setTimeout(function () {
            app.edit.mark_everything_saved();
        }, 100);
    }
};

app.edit.validate_input = function () {
    for (var key in app.edit.items) {
        var item = app.edit.items[key];
        if (item.ts && new Date(item.ts) == 'Invalid Date') {
            $('#item-timestamp').addClass('has-error');
            // TODO: this might be quite annoying.
            app.edit.select_item(key);
            app.edit.set_work_in_progress(60);
            return false;
        }
    }
    $('#item-timestamp').removeClass('has-error');
    return true;
};

app.edit.save_album = function () {
    $.ajax({
        'type': 'POST',
        'url': 'save_album/',
        'data': JSON.stringify(app.edit.album),
        'contentType': 'application/json',
        'cache': false,
        'processData': false,
        'async': true,
        'success': function (data) {
            if (data['success']) {
                app.edit.update_album();
            }
        }
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

app.edit.update = function () {
    app.edit.update_album();
    app.edit.update_items();
};

app.edit.update_album = function () {
    var handle_album = function (album) {
        $('#album-description').val(album.description);
        $('body').css({'background': album.background});
        $('#album-autoplay-delay').val(album.autoplay_delay);

        app.edit.album = album;
    }
    $.ajax({
        'type': 'GET',
        'url': 'get_album/',
        success: handle_album
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
                '<a href="javascript:void(0);" class="thumbnail item-thumbnail" data-item="', current_item_key, '">',
                '<img src="', cur_item.image, '">',
                '</a>',
                '</div>'
            );
        }
        app.edit.items = item_buffer;
        $('#thumbnail-list').html(thumbnail_buffer.join(''));
        app.edit.bind_item_thumbnails();
        app.edit.select_item(app.edit.current_item);
    };
    $.ajax({
        'type': 'GET',
        'url': 'get_items/',
        success: handle_items
    });
};

app.edit.bind_item_thumbnails = function () {
    $('.item-thumbnail').click(function () {
        var id = $(this).attr('data-item');
        app.edit.select_item(id);
    });
};

app.edit.select_item = function (id) {
    app.edit.current_item = id;
    var item = app.edit.items[id];
    if (item) {
        $('#current-item').html('<img src="' + item.image + '">');
        $('#item-timestamp').val(new Date(item.ts).toLocaleString());
        $('#item-description').val(item.description);
        $('#delete-current-item').attr('href', 'delete/' + item.id);
        if (item.is_visible) {
            $('#toggle-current-item')
                .removeClass('btn-warning').addClass('btn-success')
                .attr('title', 'Item is visible. Click to hide.')
                .children('span')
                .removeClass('glyphicon-eye-close').addClass('glyphicon-eye-open');
        } else {
            $('#toggle-current-item')
                .removeClass('btn-success').addClass('btn-warning')
                .attr('title', 'Item is not visible. Click to show.')
                .children('span')
                .removeClass('glyphicon-eye-open').addClass('glyphicon-eye-close');
        }
        app.map.set_marker(item);
    }
};

app.edit.bind_item_timestamp = function () {
    // TODO: should be on focus change instead of input
    $('#item-timestamp').on('input', function () {
        var item = app.edit.get_current_item();
        item.ts = $(this).val();
        app.edit.mark_unsaved_changes();
        app.edit.set_work_in_progress(5);
    });
};

app.edit.bind_item_description = function () {
    $('#item-description').on('input', function () {
        var item = app.edit.get_current_item();
        item.description = $(this).val();
        app.edit.mark_unsaved_changes();
        app.edit.set_work_in_progress(5);
    });
};

app.edit.bind_map_coordinates = function () {
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

app.edit.bind_map_zoom = function () {
    var view = app.map.map.getView();
    view.on('change:resolution', function () {
        var item = app.edit.get_current_item();
        item.zoom = view.getZoom();
        app.edit.mark_unsaved_changes();
        app.edit.set_work_in_progress(5);
    });
};
