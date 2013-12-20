// Require all components to ensure javascript load ordering
require('./antibody');
require('./app');
require('./biosample');
require('./collection');
require('./dbxref');
require('./errors');
require('./experiment');
require('./footer');
require('./globals');
require('./home');
require('./item');
require('./mixins');
require('./navbar');
require('./platform');
require('./search');
require('./target');
require('./testing');

var React = require('react');
var App = require('./app');
module.exports = App;

var ReactMount = require('react/lib/ReactMount');
ReactMount.allowFullPageRender = true;


// Treat domready function as the entry point to the application.
// Inside this function, kick-off all initialization, everything up to this
// point should be definitions.
if (typeof window != 'undefined' && !window.TEST_RUNNER) {
    var domready = require('domready');
    domready(function ready() {
        "use strict";
        console.log('ready');
        var props = {};
        // Ensure the initial render is exactly the same
        props.href = document.querySelector('link[rel="canonical"]').href;
        var script_props = document.querySelectorAll('script[data-prop-name]');
        for (var i = 0; i < script_props.length; i++) {
            var elem = script_props[i];
            props[elem.getAttribute('data-prop-name')] = JSON.parse(elem.text);
        }

        var app= App(props);
        React.renderComponent(app, document);

        // Simplify debugging
        window.app = app;
    });
}
