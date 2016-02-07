
var app = app || {};
app.album = {};
app.album.autoplay = false;
app.album.autoplay_delay = 5;

app.album.items = [];
app.album.current_item = 0;
app.album.weekdays = [
    'Sunday',
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday'
];


$(window).resize(function () {
    app.album.position_marker();
});


$(document).ready(function () {
    $.ajax({
        'type': 'GET',
        'url': 'get_album/',
        success: function (album) {
            $('body').css({'background': album.background})
            app.album.autoplay_delay = album.autoplay_delay;
        }
    });

    $.ajax({
        'type': 'GET',
        'url': 'get_items/',
        success: app.album.handle_items
    });

    app.map.resize_map();
    app.map.init_map();

    app.album.bind_navigation();
});

app.album.bind_navigation = function (data) {
    $('#nav-prev').click(function () { app.album.prev_item(); })
    $('#nav-next').click(function () { app.album.next_item(); })
    $('#nav-autoplay').click(app.album.toggle_autoplay);

    $(document).bind('keydown', function (e) {
        if (e.keyCode === 37) { app.album.prev_item(); }
        else if (e.keyCode === 32) { app.album.toggle_autoplay(); }
        else if (e.keyCode === 39) { app.album.next_item(); }
    });
};

app.album.handle_items = function (data) {
    var items = [];
    var sorted_item_list = data.items;
    for (var i=0; i<sorted_item_list.length; i++) {
        var item = sorted_item_list[i];
        var img = $('<img src="' + item.image + '">');
        items.push({
            'img': img,
            'time': item.ts,
            'description': item.description,
            'lat': item.lat,
            'lon': item.lon,
            'zoom': item.zoom
        })
    }
    app.album.items = items;
    app.album.add_timeline_marker();
    app.album.position_marker();

    app.album.switch_to_item(0);
};


app.album.switch_to_item = function (i) {
    var item = app.album.items[i];
    if (item) {
        $('#main-image').html(item.img);
        $('#item-description').html(item.description);
        app.map.set_marker(item);
        app.album.set_date(item.time);
    }
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

app.album.toggle_autoplay = function () {
    app.album.autoplay = !app.album.autoplay;
    if (app.album.autoplay) {
        $('#nav-autoplay span').removeClass('glyphicon-play').addClass('glyphicon-stop');
        app.album.start_autoplay();
    } else {
        $('#nav-autoplay span').removeClass('glyphicon-stop').addClass('glyphicon-play');
        app.album.stop_autoplay();
    }
};

app.album.start_autoplay = function () {
    app.album.autoplay = true;
    var delay = app.album.autoplay_delay * 1000;
    var f = function () {
        if (app.album.autoplay) {
            app.album.next_item();
            window.setTimeout(f, delay);
        }
    };
    window.setTimeout(f, delay);
};

app.album.stop_autoplay = function () {
    app.album.autoplay = false;
}


app.album.add_timeline_marker = function () {
    var m = [];
    for (var i = 0; i < app.album.items.length; i++) {
        var when = new Date(app.album.items[i].time);
        m.push($('<div class="marker" data-img="' + i +
                 '" data-when="' + when +
                 '" title="' + when.toLocaleString() + '"></div>'));
    }
    $('body').append(m);

    $('.marker').click(function () {
        app.album.switch_to_item(parseInt($(this).attr('data-img'), 10));
    });
};

app.album.position_marker = function () {
    // Calculate y-coordinates for each marker individually
    $('.marker').map(function () {
        var when = new Date($(this).attr('data-when'));
        var pos = app.album.calculate_timeline_position(when);
        $(this).css({top: pos});
    });

    // x-coordinates are the same for all marker
    var offset = $('#timeline').offset();
    var posX = offset.left - $(window).scrollLeft();
    var left = posX + ($('#timeline').width() / 2) - ($('.marker').width() / 2);
    $('.marker').css({'left': left + 'px'});
};

app.album.calculate_timeline_position = function (when) {
    var timeStart = new Date(app.album.items[0].time).valueOf();
    var timeEnd = new Date(app.album.items[app.album.items.length - 1].time).valueOf();
    var timeDur = (timeEnd - timeStart);

    var relate_position = (when.valueOf() - timeStart) / timeDur;

    var timeline_height = $('#timeline').height();
    var offset_top = $('#timeline').offset().top;
    var margin = 25;

    return offset_top + (margin / 2) + (relate_position * (timeline_height - margin)) + ($('.marker').height() / 2);
};

app.album.set_date = function (s) {
    var when = new Date(s);
    var pos = app.album.calculate_timeline_position(when);
    var ph = $('#pointer').height();
    $('#pointer').animate({'top': pos - ph});

    // TODO: should be a format_date() function
    var buffer = [app.album.weekdays[when.getDay()], ', ',
                  pad(when.getDate(), 2), '. ', pad(when.getMonth() + 1, 2), '. ', when.getFullYear(), '<br>',
                  pad(when.getHours(), 2), ':', pad(when.getMinutes(), 2)];
    $('#date').html(buffer.join(''));
};


var mod = function (x, n) {
    return ((x % n) + n) % n;
};

var pad = function (num, digits) {
    var buffer = [];
    var cnt = 1;
    if (num > 0) { cnt = digits - Math.floor(Math.log(num) / Math.log(10)) - 1; }
    for (var i = 0; i < cnt; i++) { buffer.push('0'); }
    buffer.push('' + num);
    return buffer.join('');
};
