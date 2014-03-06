require('es5-shim');
require('es5-shim/es5-sham');

(function () {

if (typeof console === 'undefined') {
    window.console = {};
    window.console.log = function () {};
}

})();
