module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        browserify: {
            vendor: {
                dest: 'build/vendor.js',
                // The shims should execute first
                src: [
                    'es5-shim',
                    'es5-shim/es5-sham',
                ].map(require.resolve),
                options: {
                    alias: [
                        'react-tools/build/modules/React:react',
                        'underscore:',
                    ],
                    shim: {
                        d3: {
                            path: require.resolve('d3-browser/lib/d3'),
                            exports: 'd3',
                        },
                        jquery: {
                            path: require.resolve('jquery-browser/lib/jquery'),
                            exports: '$',
                        },
                    },
                },
            },
            bootstrap: {
                dest: 'build/bootstrap.js',
                src: ['./src/encoded/static/libs/bootstrap.js'],  // simply requires all bootstrap plugins
                alias: ['./src/encoded/static/libs/bootstrap:bootstrap'],
                options: {
                    external: ['jquery'],
                    shim: {
                        'bootstrap-affix': {path: require.resolve('twitter-bootstrap/js/bootstrap-affix'), exports: null, depends: {jquery: 'jQuery'}},
                        'bootstrap-alert': {path: require.resolve('twitter-bootstrap/js/bootstrap-alert'), exports: null, depends: {jquery: 'jQuery'}},
                        'bootstrap-button': {path: require.resolve('twitter-bootstrap/js/bootstrap-button'), exports: null, depends: {jquery: 'jQuery'}},
                        'bootstrap-carousel': {path: require.resolve('twitter-bootstrap/js/bootstrap-carousel'), exports: null, depends: {jquery: 'jQuery'}},
                        'bootstrap-modal': {path: require.resolve('twitter-bootstrap/js/bootstrap-modal'), exports: null, depends: {jquery: 'jQuery'}},
                        'bootstrap-popover': {path: require.resolve('twitter-bootstrap/js/bootstrap-popover'), exports: null, depends: {jquery: 'jQuery', 'bootstrap-tooltip': null}},
                        'bootstrap-scrollspy': {path: require.resolve('twitter-bootstrap/js/bootstrap-scrollspy'), exports: null, depends: {jquery: 'jQuery'}},
                        'bootstrap-tab': {path: require.resolve('twitter-bootstrap/js/bootstrap-tab'), exports: null, depends: {jquery: 'jQuery'}},
                        'bootstrap-tooltip': {path: require.resolve('twitter-bootstrap/js/bootstrap-tooltip'), exports: null, depends: {jquery: 'jQuery'}},
                        'bootstrap-transition': {path: require.resolve('twitter-bootstrap/js/bootstrap-transition'), exports: null, depends: {jquery: 'jQuery'}},
                        'bootstrap-typeahead': {path: require.resolve('twitter-bootstrap/js/bootstrap-typeahead'), exports: null, depends: {jquery: 'jQuery'}},
                    },
                }
            },
            app: {
                dest: 'build/app.js',
                src: [
                    'src/encoded/static/components/*.js',
                    'src/encoded/static/libs/sticky_header.js',
                ],
                options: {
                    //debug: true,
                    transform: [
                        'reactify',
                        'deamdify',
                    ],
                    alias: [
                        'react-tools/build/modules/React:react',
                        './src/encoded/static/libs/class:class',
                        './src/encoded/static/libs/uri:uri',
                        './src/encoded/static/libs/registry:registry',
                    ],
                    external: [
                        'jquery',
                        'react',
                        'underscore',
                        'd3',
                    ],
                    shims: {
                        stickyheader: {
                            path: './src/encoded/static/libs/sticky_header',
                            exports: null,
                            depends: {jquery: 'jQuery'},
                        },
                    }
                }
            },
        },
        concat: {
            'src/encoded/static/build/bundle.js': [
                'build/vendor.js',
                'build/bootstrap.js',
                'build/app.js',
            ],
        },
    });
    grunt.loadNpmTasks('grunt-browserify');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.registerTask('default', ['browserify', 'concat']);
};
