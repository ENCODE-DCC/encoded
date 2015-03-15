'use strict';
require('jest-runtime').mock('scriptjs');
require('jest-runtime').dontMock('es6-promise');
global.Promise = require('es6-promise').Promise;

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
