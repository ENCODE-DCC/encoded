'use strict';
// http://www.quirksmode.org/js/findpos.html
module.exports = function offset(el) {
    var curleft = 0;
    var curtop = 0;
    do {
        curleft += el.offsetLeft;
        curtop += el.offsetTop;
    } while (el = el.offsetParent);
    return {left: curleft, top: curtop};
};
