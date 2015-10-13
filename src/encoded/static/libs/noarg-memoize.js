'use strict';
// Exists to work around https://github.com/prometheusresearch/react-forms/issues/70
module.exports = function noarg_memoize(fn) {
    var value;
    return function () {
        if (value === undefined) {
            value = fn();
        }
        return value;
    }
};
