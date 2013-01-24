requirejs.config({
    baseUrl: '/static',

    paths: {
        antibodies: 'modules/antibodies',
        app: 'modules/app',
        assert: 'modules/assert',
        base: 'modules/base',
        home: 'modules/home',
        navbar: 'modules/navbar',

        // Plugins
        text: 'libs/text',

        // Libraries
        backbone: 'libs/backbone',
        'backbone.hal': 'libs/backbone.hal',
        bootstrap: 'libs/bootstrap.min',
        jquery: 'libs/jquery.min',
        modernizr: 'libs/modernizr.min',
        underscore: 'libs/underscore.min'
    },

    shim: {
        backbone: {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        },

        bootstrap: {
            deps: ['jquery']
        },

        // Modernizr loads later than normal with Require.js, so don't use the
        // new HTML5 elements in the HTML file itself.
        modernizr: {
            exports: 'Modernizr'
        },

        underscore: {
            exports: '_'
        }
    }
});

if (!window.TESTRUNNER) require(['jquery', 'app', 'bootstrap', 'modernizr'],
function main($, app) {

    // Treat the jQuery ready function as the entry point to the application.
    // Inside this function, kick-off all initialization, everything up to this
    // point should be definitions.
    $(function ready() {
        app.start();

        // Simplify debugging
        window.app = app;
    });
});
