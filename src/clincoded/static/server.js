// Entry point for server rendering subprocess

/* jshint strict: false */
require('source-map-support').install();
require('./libs/react-patches');
var app = require('./libs/react-middleware').build(require('./components'));
var http_stream = require('subprocess-middleware').HTTPStream({app: app, captureConsole: true});
process.stdin.resume();
process.stdin.pipe(http_stream);
http_stream.pipe(process.stdout);
