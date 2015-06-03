'use strict';
var SUBS = {'&': '\\u0026', '<': '\\u003C', '>': '\\u003E'};
var unsafe_re = /[\<\>\&]/g;


var sub = function (match) {
    return SUBS[match];
};


var jsonScriptEscape = function (json_string) {
    return json_string.replace(unsafe_re, sub);
};


module.exports = jsonScriptEscape;
