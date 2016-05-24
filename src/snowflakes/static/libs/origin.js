/*jshint scripturl:true */
'use strict';
var url = require('url');

function same(from, to) {
    if (typeof to === 'undefined') {
        to = from;
        from = document.location.href;
    }
    if (typeof from === 'string') from = url.parse(from);
    if (typeof to === 'string') to = url.parse(url.resolve(from.href, to));

    if (to.protocol === 'data:' || to.protocol === 'javascript:') return true;
    if (from.protocol !== to.protocol) return false;
    if (from.protocol === 'file:') return from.pathname === to.pathname;
    return from.host === to.host;
}

module.exports.same = same;
