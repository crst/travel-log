
var app = {};

app.format_time = function (date) {
    var hours = date.getHours() > 9 ? date.getHours() : '0' + date.getHours();
    var minutes = date.getMinutes() > 9 ? date.getMinutes() : '0' + date.getMinutes();
    var seconds = date.getSeconds() > 9 ? date.getSeconds() : '0' + date.getSeconds();
    return hours + ':' + minutes + ':' + seconds;
};
