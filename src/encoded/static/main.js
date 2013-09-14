requirejs.config({
    baseUrl: '/static/components',

    paths: {
        // Plugins
        jsx: '../vendor/jsx',

        // Libraries
        bootstrap: '../vendor/bootstrap.min',
        jquery: '../vendor/jquery.min',
        jsonform: '../vendor/jsonform',
        JSXTransformer: '../vendor/JSXTransformer',
        underscore: '../vendor/underscore.min',
        //persona: '../libs/include.orig',
        persona: 'https://login.persona.org/include',  // mozilla persona include, this should be fetched remotely
        react: '../vendor/react',
        stickyheader: '../libs/sticky_header',
        'class': '../libs/class',
        registry: '../libs/registry',
        uri: '../libs/uri',
        d3: '../libs/d3.v3.min'
    },

    shim: {
        bootstrap: {
            deps: ['jquery']
        },

        jsonform: {
            deps: ['jquery', 'underscore'],
            exports: 'JSONForm'
        },

        JSXTransformer: {
            exports: "JSXTransformer"
        },

        persona: {
            exports: 'navigator.id'
        },

        react: {
            exports: 'React'
        },

        stickyheader: {
            deps: ['jquery']
        },

        underscore: {
            exports: '_'
        },

        d3: {
            exports: 'd3'
        }
    }
});

if (!window.TESTRUNNER) require(['jquery', 'react', 'jsx!app', 'bootstrap', 'stickyheader', 'jsonform', 'persona', 'd3',
    'jsx!item', 'jsx!collection', 'jsx!errors', 'jsx!home', 'jsx!antibody', 'jsx!biosample', 'jsx!experiment', 'jsx!platform', 'jsx!target', 'jsx!search'
    ],
function main($, React, App) {
    'use strict';

    // Treat the jQuery ready function as the entry point to the application.
    // Inside this function, kick-off all initialization, everything up to this
    // point should be definitions.
    $(function ready() {
        var app = App({
            contextDataElement: document.getElementById('data-context'),
            href: window.location.href,
        });
        React.renderComponent(app, document.getElementById('slot-application'));

        // Simplify debugging
        window.app = app;
    });
});
