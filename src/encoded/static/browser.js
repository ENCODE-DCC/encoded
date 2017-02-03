// Entry point for browser
import React from 'react';
import ReactDOM from 'react-dom';
import domready from 'domready';
import ga from 'google-analytics';
import App from './components';

function getRenderedProps (document) {
    var props = {};
    // Ensure the initial render is exactly the same
    props.href = document.querySelector('link[rel="canonical"]').getAttribute('href');
    props.styles = document.querySelector('link[rel="stylesheet"]').getAttribute('href');
    var script_props = document.querySelectorAll('script[data-prop-name]');
    for (var i = 0; i < script_props.length; i++) {
        var elem = script_props[i];
        var value = elem.text;
        var elem_type = elem.getAttribute('type') || '';
        if (elem_type == 'application/json' || elem_type.slice(-5) == '+json') {
            value = JSON.parse(value);
        }
        props[elem.getAttribute('data-prop-name')] = value;
    }
    return props;
}

function recordServerStats (server_stats, timingVar) {
    // server_stats *_time are microsecond values...
    Object.keys(server_stats).forEach(function (name) {
        if (name.indexOf('_time') === -1) return;
        ga('send', 'timing', {
            'timingCategory': name,
            'timingVar': timingVar,
            'timingValue': Math.round(server_stats[name] / 1000)
        });
    });
}

function recordBrowserStats (browser_stats, timingVar) {
    Object.keys(browser_stats).forEach(function (name) {
        if (name.indexOf('_time') === -1) return;
        ga('send', 'timing', {
            'timingCategory': name,
            'timingVar': timingVar,
            'timingValue': browser_stats[name]
        });
    });
}

// Treat domready function as the entry point to the application.
// Inside this function, kick-off all initialization, everything up to this
// point should be definitions.
if (!window.TEST_RUNNER) {
    domready(() => {
        console.log('ready');
        // Set <html> class depending on browser features
        const BrowserFeat = require('./components/browserfeat').BrowserFeat;
        BrowserFeat.setHtmlFeatClass();
        const props = getRenderedProps(document);
        const serverStats = require('querystring').parse(window.stats_cookie);
        recordServerStats(serverStats, 'html');

        ReactDOM.render(<App {...props} />, document);
    });
}
