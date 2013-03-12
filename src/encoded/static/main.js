requirejs.config({
    baseUrl: '/static',

    paths: {
        generic: 'modules/generic',
        antibodies: 'modules/antibodies',
        biosamples: 'modules/biosamples',
        targets: 'modules/targets',
        sources: 'modules/sources',
        app: 'modules/app',
        assert: 'modules/assert',
        base: 'modules/base',
        home: 'modules/home',
        navbar: 'modules/navbar',
        login: 'modules/login',

        // Plugins
        text: 'libs/text',

        // Libraries
        backbone: 'libs/backbone',
        'backbone.hal': 'libs/backbone.hal',
        bootstrap: 'libs/bootstrap.min',
        jquery: 'libs/jquery.min',
        jsonform: 'libs/jsonform',
        modernizr: 'libs/modernizr.min',
        underscore: 'libs/underscore.min',
        'navigator': 'libs/include.orig',
        //'navigator': 'https://login.persona.org/include'  // mozilla persona include, this should be fetched remotely
        stickyheader: 'libs/sticky_header',
        table_filter: 'libs/jquery.table_filter',
        table_sorter: 'libs/table_sorter'
    },

    shim: {
        backbone: {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        },

        bootstrap: {
            deps: ['jquery']
        },

        jsonform: {
            deps: ['jquery', 'underscore'],
            exports: 'JSONForm'
        },

        'navigator': {
            exports: 'navigator'
        },
        // Modernizr loads later than normal with Require.js, so don't use the
        // new HTML5 elements in the HTML file itself.
        modernizr: {
            exports: 'Modernizr'
        },

        stickyheader: {
            deps: ['jquery']
        },

        table_filter: {
            deps: ['jquery', 'table_sorter']
        },

        table_sorter: {
            deps: ['jquery']
        },

        underscore: {
            exports: '_'
        }
    }
});

if (!window.TESTRUNNER) require(['jquery', 'app', 'bootstrap', 'modernizr', 'stickyheader', 'jsonform'],
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
