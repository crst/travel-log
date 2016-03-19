
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
app.edit.mark_unsaved_changes = function (reason) {
    //console.log('mark unsaved: ' + reason);
    app.edit.has_unsaved_changes = true;
    $('#last-saved').html('<a href="javascript:app.edit.save();">Save changes</a>');
};
app.edit.mark_everything_saved = function () {
    app.edit.has_unsaved_changes = false;
    $('#last-saved').hide().html('Last saved at ' + app.format_time(new Date())).fadeIn('fast');
};
app.edit.mark_no_changes = function () {
    app.edit.has_unsaved_changes = false;
    $('#last-saved').html('No unsaved changes');
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
    var hash = parseInt(location.hash.replace(/^#/, ''), 10);
    if (hash) {
        app.edit.current_item = hash;
    }

    // Setup map
    app.map.resize_map();
    app.map.init_map({'drag_marker': true});

    // Bind events
    app.edit.bind_events();

    // Update page
    app.edit.update();
    app.edit.mark_no_changes();
});

app.edit.bind_events = function () {
    app.edit.bind_url();
    app.edit.bind_album_events();
    app.edit.bind_item_events();
};
app.edit.unbind_events = function () {
    app.edit.unbind_url();
    app.edit.unbind_album_events();
    app.edit.unbind_item_events();
};

app.edit.bind_url = function () {
    $(window).on('hashchange', function () {
        var hash = location.hash.replace(/^#/, '');
        app.edit.unbind_item_events();
        app.edit.select_item(hash);
        app.edit.bind_item_events();
    });
};
app.edit.unbind_url = function () {
    $(window).off('hashchange');
};

app.edit.bind_item_events = function () {
    app.edit.bind_item_upload();
    app.edit.bind_item_toggle_visibility();
    app.edit.bind_item_timestamp();
    app.edit.bind_item_description();
    app.edit.bind_item_thumbnails();

    app.edit.bind_map_coordinates();
    app.edit.bind_map_zoom();
};
app.edit.unbind_item_events = function () {
    app.edit.unbind_item_upload();
    app.edit.unbind_item_toggle_visibility();
    app.edit.unbind_item_timestamp();
    app.edit.unbind_item_description();
    app.edit.unbind_item_thumbnails();

    app.edit.unbind_map_coordinates();
    app.edit.unbind_map_zoom();
};

app.edit.bind_album_events = function () {
    $('#save').on('click', app.edit.save);

    app.edit.bind_album_background();
    app.edit.bind_album_background_color();
    app.edit.bind_album_description();
    app.edit.bind_album_autoplay_delay();
};
app.edit.unbind_album_events = function () {
    $('#save').off('click');

    app.edit.unbind_album_background();
    app.edit.unbind_album_background_color();
    app.edit.unbind_album_description();
    app.edit.unbind_album_autoplay_delay();
};


app.edit.bind_album_description = function () {
    var elem = $('#album-description');
    elem.on('input', function (e) {
        app.edit.album.description = elem.val();

        app.edit.mark_unsaved_changes('album description');
        app.edit.set_work_in_progress(5);
    });

    app.edit.unbind_album_description = function () {
        elem.off('change');
    };
};

app.edit.bind_album_autoplay_delay = function () {
    var elem = $('#album-autoplay-delay');
    elem.on('change', function (e) {
        var delay = parseInt($(this).val());
        if (isNaN(delay)) {
            delay = 5;
            $(this).val(delay);
        }

        app.edit.album.autoplay_delay = delay;

        app.edit.mark_unsaved_changes('album autoplay delay');
        app.edit.set_work_in_progress(5);
    });

    app.edit.unbind_album_autoplay_delay = function () {
        elem.off('change');
    };
};

app.edit.bind_item_upload = function () {
    var elem = $('#image-file');
    elem.on('change', function (e) {
        $('#item-upload-button-text').button('loading');
        var form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            'type': 'POST',
            'url': 'upload_item/',
            'data': form_data,
            'contentType': false,
            'cache': false,
            'processData': false,
            'async': true,
            'success': function (data) {
                $('#item-upload-button-text').button('reset');
                if (data['success']) {
                    app.edit.update_items();
                }
            }
        });
    });

    app.edit.unbind_item_upload = function () {
        elem.off('change');
    };
};

app.edit.bind_album_background = function () {
    var elem = $('#background-image');
    elem.on('change', function (e) {
        $('#album-background-upload-button-text').button('loading');
        var form_data = new FormData($('#upload-background')[0]);
        $.ajax({
            'type': 'POST',
            'url': 'upload_album_background/',
            'data': form_data,
            'contentType': false,
            'cache': false,
            'processData': false,
            'async': true,
            'success': function (data) {
                $('#album-background-upload-button-text').button('reset');
                if (data['success']) {
                    app.edit.update_album();
                }
            }
        })
    });

    app.edit.unbind_album_background = function () {
        elem.off('change');
    };
};

app.edit.bind_album_background_color = function () {
    var elem = $('#album-background-color');
    elem.change(function (e) {
        app.edit.album.background = $(this).val();

        app.edit.mark_unsaved_changes('album background color');
        app.edit.set_work_in_progress(5);
    });

    app.edit.unbind_album_background_color = function () {
        elem.off('change');
    };
};


app.edit.bind_item_toggle_visibility = function () {
    var elem = $('#toggle-current-item');
    elem.click(function () {
        var item = app.edit.get_current_item();
        var token = $('input[name="_csrf_token"]').val();
        $.ajax({
            'type': 'POST',
            'url': 'set-item-visibility/',
            'data': JSON.stringify({
                '_csrf_token': token,
                'item-id': app.edit.current_item,
                'item-visibility': !item.is_visible
            }),
            'contentType': 'application/json;charset=UTF-8',
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
    app.edit.unbind_item_toggle_visibility = function () {
        elem.off('click');
    };
};

app.edit.save = function () {
    if (app.edit.validate_input()) {
        app.edit.save_album();
        app.edit.save_items();

        app.edit.mark_everything_saved();
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
    var data = app.edit.album;
    data['_csrf_token'] = $('input[name="_csrf_token"]').val();

    $.ajax({
        'type': 'POST',
        'url': 'save_album/',
        'data': JSON.stringify(data),
        'contentType': 'application/json;charset=UTF-8',
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
    var data = app.edit.items;
    data['_csrf_token'] = $('input[name="_csrf_token"]').val();

    $.ajax({
        'type': 'POST',
        'url': 'save_items/',
        'data': JSON.stringify(data),
        'contentType': 'application/json;charset=UTF-8',
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
        app.edit.unbind_album_events();

        $('#album-description').val(album.description);
        if (album.background.startsWith('#')) {
            $('body').css({'background': album.background});
            $('#album-background-color').val(album.background);
            $('#background-tabs a[href="#background-color-tab"]').tab('show');
        } else {
            $('body').css({
                'background': 'url(' + album.background + ') no-repeat fixed center center',
                'background-size': 'cover'
            });
            $('#background-tabs a[href="#background-image-tab"]').tab('show');
        }
        $('#album-autoplay-delay').val(album.autoplay_delay);
        app.edit.album = album;

        app.edit.bind_album_events();
    }
    $.ajax({
        'type': 'GET',
        'url': 'get_album/',
        success: handle_album
    });
};

app.edit.update_items = function () {
    var handle_items = function (items) {
        app.edit.unbind_item_events();

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
                '<div id="item-', current_item_key, '"class="col-sm-6 col-md-12">',
                '<a href="javascript:void(0);" class="thumbnail item-thumbnail" data-item="', current_item_key, '">',
                '<img src="', cur_item.image, '">',
                '</a>',
                '</div>'
            );
        }
        app.edit.items = item_buffer;
        $('#thumbnail-list').html(thumbnail_buffer.join(''));
        app.edit.select_item(app.edit.current_item);

        app.edit.bind_item_events();
    };
    $.ajax({
        'type': 'GET',
        'url': 'get_items/',
        success: handle_items
    });
};

app.edit.bind_item_thumbnails = function () {
    var elem = $('.item-thumbnail');
    elem.on('click', function () {
        var id = $(this).attr('data-item');
        app.edit.unbind_events();
        app.edit.select_item(id);
        app.edit.bind_events();
    });

    app.edit.unbind_item_thumbnails = function () {
        elem.off('click');
    };
};

app.edit.select_item = function (id) {
    app.edit.current_item = id;
    var item = app.edit.items[id];
    if (item) {
        location.hash = id;
        var offset = $('#item-' + id).offset().top - $('#thumbnail-list').offset().top + $('#thumbnail-list').scrollTop();
        $('#thumbnail-list').animate({'scrollTop': offset}, 'slow');
        $('#current-item').html('<img src="' + item.image + '">');

        var ts = new Date(item.ts);
        $('#item-date').pickadate().pickadate('picker').set('select', ts);
        $('#item-time').pickatime({'interval': 1}).pickatime('picker').set('select', ts);

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
    } else {
        app.edit.current_item = undefined;
        app.edit.update_items();
    }
};

app.edit.bind_item_timestamp = function () {
    var date_elem = $('#item-date');
    var time_elem = $('#item-time');

    var set_current_timestamp = function () {
        var item = app.edit.get_current_item();
        var ts = new Date(date_elem.val() + ' ' + time_elem.val());
        item.ts = ts.toString();
    };

    date_elem.on('change', function () {
        set_current_timestamp();
        app.edit.mark_unsaved_changes('item date');
        app.edit.set_work_in_progress(5);
    });

    time_elem.on('change', function () {
        set_current_timestamp();
        app.edit.mark_unsaved_changes('item time');
        app.edit.set_work_in_progress(5);
    });

    app.edit.unbind_item_timestamp = function () {
        date_elem.off('change');
        time_elem.off('change');
    };
};

app.edit.bind_item_description = function () {
    var elem = $('#item-description');
    elem.on('input', function () {
        var item = app.edit.get_current_item();
        item.description = $(this).val();

        app.edit.mark_unsaved_changes('item description');
        app.edit.set_work_in_progress(5);
    });

    app.edit.unbind_item_description = function () {
        elem.off('input');
    };
};

app.edit.bind_map_coordinates = function () {
    var marker_change = app.map.marker.on('change', function() {
        var coord = this.getGeometry().getCoordinates();
        coord = ol.proj.transform(coord, 'EPSG:3857', 'EPSG:4326');
        var item = app.edit.get_current_item();
        item.lat = coord[1];
        item.lon = coord[0];

        app.edit.mark_unsaved_changes('map coordinates');
        app.edit.set_work_in_progress(5);
    });

    app.edit.unbind_map_coordinates = function () {
        app.map.marker.unByKey(marker_change);
    };
};

app.edit.bind_map_zoom = function () {
    var view = app.map.map.getView();
    var zoom_change = view.on('change:resolution', function () {
        var item = app.edit.get_current_item();
        item.zoom = view.getZoom();

        app.edit.mark_unsaved_changes('map zoom');
        app.edit.set_work_in_progress(5);
    });

    app.edit.unbind_map_zoom = function () {
        view.unByKey(zoom_change);
    };
};
