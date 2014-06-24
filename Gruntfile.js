'use strict';
module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        browserify: {
            brace: {
                dest: './src/encoded/static/build/brace.js',
                require: [
                    'brace',
                    'brace/mode/json',
                    'brace/theme/solarized_light',
                ],
                bundle: {
                    debug: true,
                },
            },
            scribe: {
                dest: './src/encoded/static/build/scribe.js',
                require: [
                    'scribe-editor',
                ],
                transform: [
                    [{global: true}, 'deamdify'],
                ],
                bundle: {
                    debug: true,
                },
            },
            browser: {
                dest: './src/encoded/static/build/bundle.js',
                src: [
                    './src/encoded/static/libs/compat.js', // The shims should execute first
                    './src/encoded/static/libs/sticky_header.js',
                    './src/encoded/static/libs/respond.js',
                    './src/encoded/static/browser.js',
                ],
                external: [
                    'brace',
                    'brace/mode/json',
                    'brace/theme/solarized_light',
                    'scribe-editor',
                ],
                require: [
                    'domready',
                    'jquery',
                    'react',
                    'underscore',
                    'url',
                ],
                transform: [
                    [{harmony: true}, 'reactify'],
                    'brfs',
                ],
                bundle: {
                    debug: true,
                },
            },
            server: {
                dest: './src/encoded/static/build/renderer.js',
                src: ['./src/encoded/static/server.js'],
                options: {
                    builtins: false,
                },
                bundle: {
                    debug: true,
                    detectGlobals: false,
                },
                transform: [
                    [{harmony: true}, 'reactify'],
                    'brfs',
                ],
                external: [
                    'assert',
                    'brace',
                    'brace/mode/json',
                    'brace/theme/solarized_light',
                ],
                ignore: [
                    'jquery',
                    'd3',
                ],
            },
        },
    });

    grunt.registerMultiTask('browserify', function () {
        var browserify = require('browserify');
        var exorcist = require('exorcist');
        var path = require('path');
        var fs = require('fs');
        var data = this.data;
        var done = this.async();
        var options = data.options || {};
        var bundle = data.bundle || {};

        var b = browserify(options);

        var i;
        var reqs = [];
        (data.src || []).forEach(function (src) {
            reqs.push.apply(reqs, grunt.file.expand({filter: 'isFile'}, src).map(function (f) {
                return [path.resolve(f), {entry: true}];
            }));
        });
        (data.require || []).forEach(function (req) {
            if (typeof req === 'string') req = [req];
            reqs.push(req);
        });

        for (i = 0; i < reqs.length; i++) {
            b.require.apply(b, reqs[i]);
        }

        var external = data.external || [];
        for (i = 0; i < external.length; i++) {
            b.external(external[i]);
        }

        bundle.filter = function (id) {
            return external.indexOf(id) < 0;
        };

        var ignore = data.ignore || [];
        for (i = 0; i < ignore.length; i++) {
            b.ignore(ignore[i]);
        }

        (data.transform || []).forEach(function (args) {
            if (typeof args === 'string') args = [args];
            b.transform.apply(b, args);
        });

        var dest = data.dest;
        grunt.file.mkdir(path.dirname(dest));

        var mapFilePath = dest + '.map';

        b = b.bundle(bundle);
        if (bundle.debug) {
            b = b.pipe(exorcist(mapFilePath));
        }
        b.on('error', function (err) { console.error(err); });
        var out = fs.createWriteStream(dest);

        b = b.pipe(out);
        out.on('close', function () {
            if (data.footer) {
                fs.writeFileSync(dest, '\n' + data.footer, {flag: 'a'});
            }
            console.log('File ' + dest + ' created.');
            done();
        });

    });

    grunt.registerTask('default', ['browserify']);
};
