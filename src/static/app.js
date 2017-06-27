
var app = {};


app.mod = function (x, n) {
    return ((x % n) + n) % n;
};

app.log = function (n, base) {
    return Math.log(n) / Math.log(base);
};


app.pad = function (num, digits) {
    var buffer = [];
    var cnt = 1;
    if (num > 0) { cnt = digits - Math.floor(app.log(num, 10)) - 1; }
    for (var i = 0; i < cnt; i++) { buffer.push('0'); }
    buffer.push('' + num);
    return buffer.join('');
};


app.format_date = function (d) {
     var weekdays = [
         'Sun',
         'Mon',
         'Tue',
         'Wed',
         'Thu',
         'Fri',
         'Sat'
     ];

    var buffer = [weekdays[d.getDay()], ', ',
                  d.getFullYear() , '-', app.pad(d.getMonth() + 1, 2), '-', app.pad(d.getDate(), 2), '<br>',
                  app.pad(d.getHours(), 2), ':', app.pad(d.getMinutes(), 2)];

    return buffer.join('');
};

app.format_time = function (date) {
    var hours = date.getHours() > 9 ? date.getHours() : '0' + date.getHours();
    var minutes = date.getMinutes() > 9 ? date.getMinutes() : '0' + date.getMinutes();
    var seconds = date.getSeconds() > 9 ? date.getSeconds() : '0' + date.getSeconds();
    return hours + ':' + minutes + ':' + seconds;
};
