
var app = {};

app.format_time = function (date) {
    var hours = date.getHours() > 9 ? date.getHours() : '0' + date.getHours();
    var minutes = date.getMinutes() > 9 ? date.getMinutes() : '0' + date.getMinutes();
    var seconds = date.getSeconds() > 9 ? date.getSeconds() : '0' + date.getSeconds();
    return hours + ':' + minutes + ':' + seconds;
};

app.mod = function (x, n) {
    return ((x % n) + n) % n;
};

app.pad = function (num, digits) {
    var buffer = [];
    var cnt = 1;
    if (num > 0) { cnt = digits - Math.floor(Math.log(num) / Math.log(10)) - 1; }
    for (var i = 0; i < cnt; i++) { buffer.push('0'); }
    buffer.push('' + num);
    return buffer.join('');
};


app.format_date = function (d) {
     var weekdays = [
         'Sunday',
         'Monday',
         'Tuesday',
         'Wednesday',
         'Thursday',
         'Friday',
         'Saturday'
     ];

    var buffer = [weekdays[d.getDay()], ', ',
                  app.pad(d.getDate(), 2), '. ', app.pad(d.getMonth() + 1, 2), '. ', d.getFullYear(), '<br>',
                  app.pad(d.getHours(), 2), ':', app.pad(d.getMinutes(), 2)];

    return buffer.join('');
};
