'use strict';

// IE11 hack to install promise, despite babel
// issue- https://www.bountysource.com/issues/67086174-ie-support-promise-is-undefined-bundles$
if (window && !window.Promise) {
    window.Promise = require('bluebird');
}

// Read and clear stats cookie
var cookie = require('js-cookie');
window.stats_cookie = cookie.get('X-Stats') || '';
cookie.set('X-Stats', '', {path: '/', expires: new Date(0)});

// Use a separate tracker for dev / test
var ga = require('google-analytics');
var trackers = {'www.encodeproject.org': 'UA-47809317-1'};
var tracker = trackers[document.location.hostname] || 'UA-47809317-2';
ga('create', tracker, {'cookieDomain': 'none', 'siteSpeedSampleRate': 100});
ga('send', 'pageview');

// Need to know if onload event has fired for safe history api usage.
window.onload = function () {
    window._onload_event_fired = true;
};

var $script = require('scriptjs');
$script.path('/static/build/');

// Load the rest of the app as a separate chunk.
require.ensure(['./libs/compat', './browser'], function(require) {
	require('./libs/compat');  // Shims first
	require('./browser');
}, 'bundle');
