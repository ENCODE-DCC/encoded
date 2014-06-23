'use strict';

require('jest-runtime').mock('scriptjs');
window.$script = require('scriptjs');

if (window.DOMParser === undefined) {
    // jsdom
    window.DOMParser = function DOMParser() {};
    window.DOMParser.prototype.parseFromString = function parseFromString(markup, type) {
        var doc = new document.constructor();
        doc.write(markup);
        doc.close();
        return doc;
    };
}
