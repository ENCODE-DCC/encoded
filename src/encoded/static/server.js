// Entry point for server rendering subprocess

/* jshint strict: false */

if (process.env.NODE_ENV === undefined) {
    require("babel-core/register")({
      only: ['react-forms', 'src/encoded/static'],
    });
} else {
    require('source-map-support').install();
}

require('./libs/react-patches');

var argv = process.argv.slice(process.execArgv.length + 2);
var debug = (argv[0] === '--debug');

var app = require('./libs/react-middleware').build(require('./components'));
var http_stream = require('subprocess-middleware').HTTPStream({app: app, captureConsole: !debug});
http_stream.pipe(process.stdout);
if (debug) {
    var value = argv[1] || '{}';
    http_stream.end('HTTP/1.1 200 OK\r\nX-Request-URL: http://localhost/\r\nContent-Length: ' + value.length + '\r\n\r\n' + value);
} else {
    process.stdin.pipe(http_stream);
    process.stdin.resume();
}
