module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        browserify: {
            browser: {
                dest: 'src/encoded/static/build/bundle.js',
                src: [
                    './src/encoded/static/libs/compat.js', // The shims should execute first
                    './src/encoded/static/libs/bootstrap.min.js',
                    './src/encoded/static/components/index.js',

                ],
                root: '.',
                require: [
                    'domready',
                    'jquery',
                    'react',
                    'underscore',
                    'url',

                    ['./src/encoded/static/libs/class', {expose: 'class'}],
                    ['./src/encoded/static/libs/jsonScriptEscape', {expose: 'jsonScriptEscape'}],
                    ['./src/encoded/static/libs/origin' , {expose: 'origin'}],
                    ['./src/encoded/static/libs/registry' , {expose: 'registry'}],
                    ['./src/encoded/static/components', {expose: 'main'}],
                ],
                shim: {
                    stickyheader: {
                        path: './src/encoded/static/libs/sticky_header',
                        exports: null,
                        depends: {jquery: 'jQuery'},
                    },
                    respond: {
                        path: './src/encoded/static/libs/respond',
                        exports: null,
                    }
                },
                transform: [
                    [{es6: true}, 'reactify'],
                ],
                bundle: {
                    debug: true,
                },
            },
            specs: {
                dest: 'src/encoded/tests/js/build/bundle.js',
                src: [
                    'src/encoded/tests/js/specs/*.js',
                    'src/encoded/tests/js/testing.js',
                ],
                bundle: {
                    debug: true,
                },
                external: [
                    'domready',
                    'jquery',
                    'jasmine',
                    'jasmine_html',
                    'underscore',
                    'url',
                    'origin',
                    'registry',
                    'main',
                ],
            },
            server: {
                dest: 'src/encoded/static/build/renderer.js',
                src: ['./src/encoded/static/components/index.js'],
                require: [
                    ['./src/encoded/static/libs/server.js', {expose: 'server'}],
                    ['./src/encoded/static/libs/class', {expose: 'class'}],
                    ['./src/encoded/static/libs/jsonScriptEscape', {expose: 'jsonScriptEscape'}],
                    ['./src/encoded/static/libs/origin' , {expose: 'origin'}],
                    ['./src/encoded/static/libs/registry' , {expose: 'registry'}],
                    ['./src/encoded/static/components', {expose: 'main'}],
                ],
                options: {
                    noParse: ['./src/encoded/static/libs/streams.js'],
                },
                bundle: {
                    debug: true,
                },
                transform: [
                    [{es6: true}, 'reactify'],
                ],
                external: [
                    'assert',
                ],
                ignore: [
                    'jquery',
                    'd3',
                ],
                footer: "require('source-map-support').install();\n" +
                        "require('server').run(require('main'));\n",
            },
        },
    });

    grunt.registerMultiTask('browserify', function () {
        var browserify = require('browserify');
        var shim = require('browserify-shim');
        var mold = require('mold-source-map');
        var path = require('path');
        var fs = require('fs');
        var data = this.data;
        var done = this.async();
        var options = data.options || {};
        var bundle = data.bundle || {};

        var b = browserify(options);

        if (data.shim) {
            b = shim(b, data.shim);
        }

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

        for (var i = 0; i < reqs.length; i++) {
            b.require.apply(b, reqs[i]);
        }

        var external = data.external || [];
        for (var i = 0; i < external.length; i++) {
            b.external(external[i]);
        }

        bundle.filter = function (id) {
            return external.indexOf(id) < 0;
        };

        var ignore = data.ignore || [];
        for (var i = 0; i < ignore.length; i++) {
            b.ignore(ignore[i]);
        }

        (data.transform || []).forEach(function (args) {
            if (typeof args === 'string') args = [args];
            b.transform.apply(b, args);
        });

        var dest = path.resolve(data.dest);
        var root = data.root ? path.resolve(data.root) : path.resolve(path.dirname(dest));

        grunt.file.mkdir(path.dirname(dest));

        var mapFilePath = dest + '.map';

        function mapFileUrlComment(sourcemap) {
            // make source files appear under the following paths:
            // /js
            //    foo.js
            //    main.js
            // /js/wunder
            //    bar.js 

            sourcemap.sourceRoot('file://'); 
            sourcemap.mapSources(mold.mapPathRelativeTo(root));
            // write map file and return a sourceMappingUrl that points to it
            fs.writeFileSync(mapFilePath, sourcemap.toJSON(2), 'utf-8');
            console.log('File ' + mapFilePath + ' created.');

            // Giving just a filename instead of a path will cause the browser to look for the map file 
            // right next to where it loaded the bundle from.
            // Therefore this way the map is found no matter if the page is served or opened from the filesystem.
            return '//# sourceMappingURL=' + path.basename(mapFilePath);
        }

        b = b.bundle(bundle);
        if (bundle.debug) {
            b = b.pipe(mold.transform(mapFileUrlComment));
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
