require.config({
    paths: {
        app: 'modules/app',
        base: 'modules/base',
        home: 'modules/home',

        // Plugins
        text: 'libs/text',

        // Libraries
        backbone: 'libs/backbone.min',
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
