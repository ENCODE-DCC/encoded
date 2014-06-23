// Entry point for browser

/* jshint strict: false */
require('./libs/react-patches');
var React = require('react');
var ReactMount = require('react/lib/ReactMount');
ReactMount.allowFullPageRender = true;

var App = require('./components');
var domready = require('domready');

// Treat domready function as the entry point to the application.
// Inside this function, kick-off all initialization, everything up to this
// point should be definitions.
if (!window.TEST_RUNNER) domready(function ready() {
    console.log('ready');
    // Set <html> class depending on browser features
    var BrowserFeat = require('./components/mixins').BrowserFeat;
    BrowserFeat.setHtmlFeatClass();
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
    App.recordServerStats(server_stats, 'html');

    var app = React.renderComponent(App(props), document);

    // Simplify debugging
    window.app = app;
});
