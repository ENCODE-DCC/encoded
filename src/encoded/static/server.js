// Entry point for server rendering subprocess

/* jshint strict: false */

if (process.env.NODE_ENV === undefined) {
    require('babel-core/register')({
        only: ['src/encoded/static'],
    });
} else {
    require('source-map-support').install();
}

require('./libs/react-patches');

const argv = process.argv.slice(2);
const debug = (argv[0] === '--debug');

const app = require('./libs/react-middleware').build(require('./components'));
const httpStream = require('subprocess-middleware').HTTPStream({ app: app, captureConsole: !debug });

httpStream.pipe(process.stdout);
if (debug) {
    let value = argv[1] || '{}';
    if (value.slice(0, 5) === 'file:') {
        value = require('fs').readFileSync(value.slice(5));
    } else {
        value = new Buffer(value, 'utf8');
    }
    httpStream.write(`HTTP/1.1 200 OK\r\nX-Request-URL: http://localhost/\r\nContent-Length: ${value.length}\r\n\r\n`);
    httpStream.write(value);
    httpStream.end();
} else {
    process.stdin.pipe(httpStream);
    process.stdin.resume();
}
