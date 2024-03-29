// Read and clear stats cookie
const cookie = require('js-cookie');

window.stats_cookie = cookie.get('X-Stats') || '';
cookie.set('X-Stats', '', { path: '/', expires: new Date(0) });

// Use a separate tracker for dev / test
const ga = require('google-analytics');

const trackers = { 'www.encodeproject.org': 'UA-47809317-1' };
const tracker = trackers[document.location.hostname] || 'UA-47809317-2';
ga('create', tracker, { cookieDomain: 'none', siteSpeedSampleRate: 100 });
ga('send', 'pageview');

// Need to know if onload event has fired for safe history api usage.
window.onload = () => {
    window._onload_event_fired = true;
};

const $script = require('scriptjs');

$script.path('/static/build/');

// Load the rest of the app as a separate chunk.
require.ensure(['./libs/compat', './browser'], (require) => {
    require('./libs/compat'); // Shims first
    require('./browser');
}, 'bundle');
