'use strict';

module.exports = function(grunt) {
    var path = require('path');

    function compressPath(p) {
        var src = 'src/encoded/static/';
        p = path.relative(__dirname, p);
        if (p.slice(0, src.length) == src) {
            return '../' + p.slice(src.length);
        }
        return '../../' + p;
    }

    var NODE_ENV = process.env.NODE_ENV || 'development';

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
                plugin: [
                    ['minifyify', {
                        map: 'brace.js.map',
                        output: './src/encoded/static/build/brace.js.map',
                        compressPath: compressPath,
                        uglify: {mangle: NODE_ENV == 'production'},
                    }],
                ],
            },
            dagre: {
                dest: './src/encoded/static/build/dagre.js',
                require: [
                    'dagre-d3',
                    'd3',
                ],
                options: {
                    debug: true,
                },
                plugin: [
                    ['minifyify', {
                        map: 'dagre.js.map',
                        output: './src/encoded/static/build/dagre.js.map',
                        compressPath: compressPath,
                        uglify: {mangle: NODE_ENV == 'production'},
                    }],
                ],
            },
            inline: {
                dest: './src/encoded/static/build/inline.js',
                src: [
                    './src/encoded/static/inline.js',
                ],
                require: [
                    'scriptjs',
                    'google-analytics',
                ],
                transform: [
                    'brfs',
                    'envify',
                ],
                plugin: [
                    ['minifyify', {
                        map: '/static/build/inline.js.map',
                        output: './src/encoded/static/build/inline.js.map',
                        compressPath: compressPath,
                        uglify: {mangle: NODE_ENV == 'production'},
                    }],
                ],
            },
            browser: {
                dest: './src/encoded/static/build/bundle.js',
                src: [
                    './src/encoded/static/libs/compat.js', // The shims should execute first
                    './src/encoded/static/libs/respond.js',
                    './src/encoded/static/browser.js',
                ],
                external: [
                    'brace',
                    'brace/mode/json',
                    'brace/theme/solarized_light',
                    'dagre-d3',
                    'd3',
                    'scriptjs',
                    'google-analytics',
                ],
                transform: [
                    [{sourceMap: true, loose: "all", optional: ["spec.protoToAssign"]}, 'babelify'],
                    [{sourceMap: true, loose: "all", optional: ["spec.protoToAssign"], global: true, only: ['react-forms']}, 'babelify'],
                    'brfs',
                    [require('envify/custom')({NODE_ENV: NODE_ENV})],
                ],
                plugin: [
                    ['minifyify', {
                        map: 'bundle.js.map',
                        output: './src/encoded/static/build/bundle.js.map',
                        compressPath: compressPath,
                        uglify: {mangle: NODE_ENV === 'production'},
                    }],
                ],
            },
            server: {
                dest: './src/encoded/static/build/renderer.js',
                src: ['./src/encoded/static/server.js'],
                options: {
                    builtins: false,
                    detectGlobals: false,
                },
                transform: [
                    [{sourceMap: true}, 'babelify'],
                    [{sourceMap: true, global: true, only: ['react-forms']}, 'babelify'],
                    'brfs',
                    [require('envify/custom')({NODE_ENV: NODE_ENV})],
                ],
                plugin: [
                    ['minifyify', {map:
                        'renderer.js.map',
                        output: './src/encoded/static/build/renderer.js.map',
                        compressPath: compressPath,
                        uglify: {mangle: NODE_ENV === 'production'},
                    }],
                ],
                external: [
                    'assert',
                    'brace',
                    'brace/mode/json',
                    'brace/theme/solarized_light',
                    'dagre-d3',
                    'd3',
                    'source-map-support',
                ],
                ignore: [
                    'scriptjs',
                    'google-analytics',
                    'ckeditor',
                ],
            },
        },
    });

    grunt.registerMultiTask('browserify', function (watch) {
        var browserify = require('browserify');
        var _ = grunt.util._;
        var path = require('path');
        var fs = require('fs');
        var data = this.data;
        var options = _.extend({
            debug: true,
            cache: {},
            packageCache: {},
            fullPaths: watch
        }, data.options);

        var b = browserify(options);
        if (watch) {
            b = require('watchify')(b);
        }

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

        options.filter = function (id) {
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

        (data.plugin || []).forEach(function (args) {
            if (typeof args === 'string') args = [args];
            b.plugin.apply(b, args);
        });

        var dest = data.dest;
        grunt.file.mkdir(path.dirname(dest));

        var bundle = function(done) {
            var out = fs.createWriteStream(dest);
            b.bundle().pipe(out);
            out.on('close', function() {
                grunt.log.write('Wrote ' + dest + '\n');
                if (done !== undefined) done();
            });
        };
        b.on('update', function() { bundle(); });
        var done = this.async();
        bundle(done);
    });

    grunt.registerTask('wait', function() {
        grunt.log.write('Waiting for changes...\n');
        this.async();
    });

    grunt.registerTask('default', ['browserify']);
    grunt.registerTask('watch', ['browserify:*:watch', 'wait']);
};
