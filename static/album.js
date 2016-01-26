
var app = app || {};
app.album = {};

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
    $('.marker').map(function () {
        var when = new Date($(this).attr('data-when'));
        var pos = app.album.get_time_line_pos(when);
        $(this).css({top: pos});
    });

    var offset = $('#timeline').offset();
    var posX = offset.left - $(window).scrollLeft();
    var left = posX + ($('#timeline').width() / 2) + 1;
    $('.marker').css({'left': left + 'px'});
};

app.album.get_time_line_pos = function (when) {
    var timeStart = new Date(app.album.items[0].time).valueOf();
    var timeEnd = new Date(app.album.items[app.album.items.length - 1].time).valueOf();
    var timeDur = (timeEnd - timeStart);

    var atp = (when.valueOf() - timeStart) / timeDur;

    var th = $('#timeline').height();
    var to = $('#timeline').offset().top;

    return to + (atp * (th - 20)) + 10;
};

app.album.set_date = function (s) {
    var when = new Date(s);
    var pos = app.album.get_time_line_pos(when);
    var ph = $('#pointer').height();
    $('#pointer').animate({'top': pos - ph});

    var buffer = [app.album.weekdays[when.getDay()], ', ',
                  pad(when.getDate(), 2), '. ', pad(when.getMonth() + 1, 2), '. ', when.getFullYear(), '<br>',
                  pad(when.getHours(), 2), ':', pad(when.getMinutes(), 2), ' Uhr'];
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
