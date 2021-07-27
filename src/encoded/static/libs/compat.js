/* jshint strict:false */
require('core-js/stable');
require('regenerator-runtime/runtime');

// Chrome 42 fetch does not have abort.
window.fetch = undefined;
require('whatwg-fetch');

{
    if (typeof console === 'undefined') {
        window.console = {
            log() {
                //
            },
        };
    }
    const consoleMethods = [
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
        'assert',
    ];
    for (let i = 0, l = consoleMethods.length; i < l; i += 1) {
        const name = consoleMethods[i];
        if (window.console[name] === undefined) {
            window.console[name] = window.console.log;
        }
    }
}
