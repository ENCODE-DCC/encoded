// Entry point for browser
import React from 'react';
import ReactDOM from 'react-dom';
import domready from 'domready';
import App from './components';

// Treat domready function as the entry point to the application.
// Inside this function, kick-off all initialization, everything up to this
// point should be definitions.
if (!window.TEST_RUNNER) {
    domready(() => {
        console.log('ready');
        // Set <html> class depending on browser features
        const BrowserFeat = require('./components/browserfeat').BrowserFeat;
        BrowserFeat.setHtmlFeatClass();
        const props = App.getRenderedProps(document);
        const serverStats = require('querystring').parse(window.stats_cookie);
        App.recordServerStats(serverStats, 'html');

        ReactDOM.render(<App {...props} />, document);
    });
}
