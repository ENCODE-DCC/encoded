'use strict';

// Read and clear stats cookie
var cookie = require('js-cookie');
window.stats_cookie = cookie.get('X-Stats') || '';
cookie.remove('X-Stats');

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

// Load the rest of the app as a separate chunk.
require.ensure(['./libs/compat', './browser'], function(require) {
	require('./libs/compat');  // Shims first
	require('./browser');
}, 'bundle');
