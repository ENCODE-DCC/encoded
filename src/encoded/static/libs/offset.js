// http://www.quirksmode.org/js/findpos.html
module.exports = function offset(el) {
    let curleft = 0;
    let curtop = 0;
    do {
        curleft += el.offsetLeft;
        curtop += el.offsetTop;
    // eslint-disable-next-line no-cond-assign
    } while (el = el.offsetParent);
    return { left: curleft, top: curtop };
};
