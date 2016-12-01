// Entry point for server rendering subprocess

/* jshint strict: false */

if (process.env.NODE_ENV === undefined) {
    require("babel-core/register")({
      only: ['src/encoded/static'],
    });
} else {
    require('source-map-support').install();
}

require('./libs/react-patches');

var argv = process.argv.slice(2);
var debug = (argv[0] === '--debug');

var app = require('./libs/react-middleware').build(require('./components'));
var http_stream = require('subprocess-middleware').HTTPStream({app: app, captureConsole: !debug});
http_stream.pipe(process.stdout);
if (debug) {
    var value = argv[1] || '{}';
    if (value.slice(0, 5) === 'file:') {
        value = require('fs').readFileSync(value.slice(5));
    } else {
        value = new Buffer(value, 'utf8');
    }
    http_stream.write('HTTP/1.1 200 OK\r\nX-Request-URL: http://localhost/\r\nContent-Length: ' + value.length + '\r\n\r\n');
    http_stream.write(value);
    http_stream.end();
} else {
    process.stdin.pipe(http_stream);
    process.stdin.resume();
}
