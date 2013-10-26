var React = require('react');
var App = require('./app');
var domready = require('domready');

// Treat the jQuery ready function as the entry point to the application.
// Inside this function, kick-off all initialization, everything up to this
// point should be definitions.
console.log('loaded main');
domready(function ready() {
    "use strict";
    console.log('ready');
    var app = App({
        contextDataElement: document.getElementById('data-context'),
        href: window.location.href,
    });
    React.renderComponent(app, document.getElementById('slot-application'));

    // Simplify debugging
    window.app = app;
});
