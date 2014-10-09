'use strict';

// ie8 compat.
var tags = [
"article",
"aside",
"figcaption",
"figure",
"footer",
"header",
"hgroup",
"nav",
"section"];
for (var i=0, l=tags.length; i < l; i++) {
    document.createElement(tags[i]);
}

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
