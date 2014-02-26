/** @jsx React.DOM */
'use strict';

// https://github.com/facebook/react/pull/1183
var DefaultDOMPropertyConfig = require('react/lib/DefaultDOMPropertyConfig');
DefaultDOMPropertyConfig.DOMAttributeNames.httpEquiv = 'http-equiv';

// https://github.com/facebook/react/pull/1181
var ReactDOM = require('react/lib/ReactDOM');
ReactDOM.link.type.prototype._tagClose = '';


// Require all components to ensure javascript load ordering
require('./antibody');
require('./app');
require('./biosample');
require('./collection');
require('./dataset');
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
require('./edit');

var React = require('react');
var App = require('./app');
module.exports = App;

var ReactMount = require('react/lib/ReactMount');
ReactMount.allowFullPageRender = true;

var recordServerStats = require('./mixins').recordServerStats;


// Treat domready function as the entry point to the application.
// Inside this function, kick-off all initialization, everything up to this
// point should be definitions.
if (typeof window != 'undefined' && !window.TEST_RUNNER) {
    var $ = require('jquery');
    $(document).ready(function ready() {
        console.log('ready');
        var props = {};
        // Ensure the initial render is exactly the same
        props.href = document.querySelector('link[rel="canonical"]').href;
        var script_props = document.querySelectorAll('script[data-prop-name]');
        for (var i = 0; i < script_props.length; i++) {
            var elem = script_props[i];
            props[elem.getAttribute('data-prop-name')] = JSON.parse(elem.text);
        }

        var stats_header = document.documentElement.getAttribute('data-stats') || '';
        var server_stats = require('querystring').parse(stats_header);
        recordServerStats(server_stats, 'html');

        var app = App(props);
        React.renderComponent(app, document);

        // Simplify debugging
        window.app = app;
    });
}
