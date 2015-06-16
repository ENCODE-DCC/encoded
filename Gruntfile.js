'use strict';
var reactify = require('./reactify');

module.exports = function(grunt) {
    var path = require('path');

    function compressPath(p) {
        var src = 'src/clincoded/static/';
        p = path.relative(__dirname, p);
        if (p.slice(0, src.length) == src) {
            return '../' + p.slice(src.length);
        }
        return '../../' + p;
    }

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        browserify: {
            brace: {
                dest: './src/clincoded/static/build/brace.js',
                require: [
                    'brace',
                    'brace/mode/json',
                    'brace/theme/solarized_light',
                ],
                plugin: [
                    ['minifyify', {
                        map: 'brace.js.map',
                        output: './src/clincoded/static/build/brace.js.map',
                        compressPath: compressPath,
                        uglify: {mangle: process.env.NODE_ENV == 'production'},
                    }],
                ],
            },
            inline: {
                dest: './src/clincoded/static/build/inline.js',
                src: [
                    './src/clincoded/static/inline.js',
                ],
                require: [
                    'scriptjs',
                    'google-analytics',
                ],
                transform: [
                    [{harmony: true, sourceMap: true, target: 'es3'}, reactify],
                    'brfs',
                    'envify',
                ],
                plugin: [
                    ['minifyify', {
                        map: '/static/build/inline.js.map',
                        output: './src/clincoded/static/build/inline.js.map',
                        compressPath: compressPath,
                        uglify: {mangle: process.env.NODE_ENV == 'production'},
                    }],
                ],
            },
            browser: {
                dest: './src/clincoded/static/build/bundle.js',
                src: [
                    './src/clincoded/static/libs/compat.js', // The shims should execute first
                    './src/clincoded/static/libs/sticky_header.js',
                    './src/clincoded/static/libs/respond.js',
                    './src/clincoded/static/browser.js',
                ],
                external: [
                    'brace',
                    'brace/mode/json',
                    'brace/theme/solarized_light',
                    'scriptjs',
                    'google-analytics',
                ],
                transform: [
                    [{harmony: true, sourceMap: true, target: 'es3'}, reactify],
                    'brfs',
                    'envify',
                ],
                plugin: [
                    ['minifyify', {
                        map: 'bundle.js.map',
                        output: './src/clincoded/static/build/bundle.js.map',
                        compressPath: compressPath,
                        uglify: {mangle: process.env.NODE_ENV == 'production'},
                    }],
                ],
            },
            server: {
                dest: './src/clincoded/static/build/renderer.js',
                src: ['./src/clincoded/static/server.js'],
                options: {
                    builtins: false,
                    detectGlobals: false,
                },
                transform: [
                    [{harmony: true, sourceMap: true}, reactify],
                    'brfs',
                    'envify',
                ],
                plugin: [
                    ['minifyify', {map:
                        'renderer.js.map',
                        output: './src/clincoded/static/build/renderer.js.map',
                        compressPath: compressPath,
                        uglify: {mangle: process.env.NODE_ENV == 'production'},
                    }],
                ],
                external: [
                    'assert',
                    'brace',
                    'brace/mode/json',
                    'brace/theme/solarized_light',
                    'source-map-support',
                ],
                ignore: [
                    'jquery',
                    'scriptjs',
                    'google-analytics',
                    'ckeditor',
                ],
            },
        },
        copy: {
            ckeditor: {
                expand: true,
                cwd: 'node_modules/node-ckeditor',
                src: 'ckeditor/**',
                dest: 'src/clincoded/static/build/',
            }
        },
    });

    grunt.registerMultiTask('browserify', function (watch) {
        var browserify = require('browserify');
        var watchify = require('watchify');
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
            b = watchify(b);
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

    grunt.loadNpmTasks('grunt-contrib-copy');

    grunt.registerTask('default', ['browserify', 'copy']);
    grunt.registerTask('watch', ['browserify:*:watch', 'wait']);
};
