/*jshint strict:false */
require("core-js/stable");
require("regenerator-runtime/runtime");

// Chrome 42 fetch does not have abort.
window.fetch = undefined;
require('whatwg-fetch');

(function () {

if (typeof console === 'undefined') {
    window.console = {
        log: function () {}
    };
}
var console_methods = [
    'count',
    'dir',
    'error',
    'group',
    'groupCollapsed',
    'groupEnd',
    'info',
    'time',
    'timeEnd',
    'trace',
    'warn',
    'debug',
    'table',
    'assert'
];
for (var i=0, l=console_methods.length; i < l; i++) {
    var name = console_methods[i];
    if (window.console[name] === undefined) {
        window.console[name] = window.console.log;
    }
}

})();

// https://gist.github.com/elijahmanor/6452535
// https://developer.mozilla.org/en-US/docs/Web/API/Element/matches
if (!Element.prototype.matches) (function () {
    var proto = Element.prototype;
    proto.matches = proto.matchesSelector ||
        proto.mozMatchesSelector || proto.msMatchesSelector ||
        proto.oMatchesSelector || proto.webkitMatchesSelector || (function (selector) {
            var element = this;
            var matches = (element.document || element.ownerDocument).querySelectorAll(selector);
            var i = 0;
            while (matches[i] && matches[i] !== element) {
                i++;
            }
            return matches[i] ? true : false;
        });
})();
