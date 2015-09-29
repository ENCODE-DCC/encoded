'use strict';
require('jest-runtime').mock('scriptjs');
require('jest-runtime').dontMock('es6-promise');
global.Promise = require('es6-promise').Promise;

if (window.DOMParser === undefined) {
    // jsdom
    window.DOMParser = function DOMParser() {};
    window.DOMParser.prototype.parseFromString = function parseFromString(markup, type) {
        var parsingMode = 'auto';
        type = type || '';
        if (type.indexOf('xml') >= 0) {
            parsingMode = 'xml';
        } else if (type.indexOf('html') >= 0) {
            parsingMode = 'html';
        }
        var doc = new document.constructor({parsingMode: parsingMode});
        doc.write(markup);
        doc.close();
        return doc;
    };
}
