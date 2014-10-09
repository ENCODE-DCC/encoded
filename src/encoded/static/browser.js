'use strict';
// Entry point for browser
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
    var props = App.getRenderedProps(document);
    var stats_header = document.documentElement.getAttribute('data-stats') || '';
    var server_stats = require('querystring').parse(stats_header);
    App.recordServerStats(server_stats, 'html');

    var app = React.renderComponent(App(props), document);

    // Simplify debugging
    window.app = app;
});
