/* jshint strict:false */
require('core-js/stable');
require('regenerator-runtime/runtime');

// Chrome 42 fetch does not have abort.
window.fetch = undefined;
require('whatwg-fetch');
