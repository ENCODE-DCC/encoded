// Entry point for browser
import ReactDOM from 'react-dom';
import domready from 'domready';
import ga from 'google-analytics';
import App from './components';

function getRenderedProps(document) {
    const props = {};
    // Ensure the initial render is exactly the same
    props.href = document.querySelector('link[rel="canonical"]').getAttribute('href');
    props.styles = document.querySelector('link[rel="stylesheet"]').getAttribute('href');
    const scriptProps = document.querySelectorAll('script[data-prop-name]');
    for (let i = 0; i < scriptProps.length; i += 1) {
        const elem = scriptProps[i];
        let value = elem.text;
        const elemType = elem.getAttribute('type') || '';
        if (elemType === 'application/json' || elemType.slice(-5) === '+json') {
            value = JSON.parse(value);
        }
        props[elem.getAttribute('data-prop-name')] = value;
    }
    return props;
}

function recordServerStats(serverStats, timingVar) {
    // serverStats *_time are microsecond values...
    Object.keys(serverStats).forEach((name) => {
        if (name.indexOf('_time') === -1) return;
        ga('send', 'timing', {
            timingCategory: name,
            timingVar,
            timingValue: Math.round(serverStats[name] / 1000),
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
        const props = getRenderedProps(document);
        const serverStats = require('querystring').parse(window.stats_cookie);
        recordServerStats(serverStats, 'html');

        ReactDOM.hydrate(<App {...props} />, document);
    });
}
