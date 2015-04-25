'use strict';
var sorted_json = module.exports = function (obj) {
    if (obj instanceof Array) {
        return obj.map(function (value) {
            return sorted_json(value);
        });
    } else if (obj instanceof Object) {
        var sorted = {};
        Object.keys(obj).sort().forEach(function (key) {
            sorted[key] = obj[key];
        });
        return sorted;
    } else {
        return obj;
    }
};
