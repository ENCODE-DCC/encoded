'use strict';

// Minimal inline IE8 html5 compatibility
require('shivie8');

// Read and clear stats cookie
var cookie = require('cookie-monster')(document);
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
$script('https://login.persona.org/include.js', 'persona');
