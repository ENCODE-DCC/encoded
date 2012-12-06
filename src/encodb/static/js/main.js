require.config({
    paths: {
        app: 'app',
        base: 'base',
        home: 'home',

        // Plugins
        text: 'vendor/text',

        // Libraries
        backbone: 'vendor/backbone.min',
        bootstrap: 'vendor/bootstrap.min',
        jquery: 'vendor/jquery.min',
        modernizr: 'vendor/modernizr.min',
        underscore: 'vendor/underscore.min'
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

define(['jquery', 'app', 'bootstrap', 'modernizr'],
function module($, app) {

    // Treat the jQuery ready function as the entry point to the application.
    // Inside this function, kick-off all initialization, everything up to this
    // point should be definitions.
    $(function ready() {
        app.start();

        // Simplify debugging
        window.app = app;
    });
});
