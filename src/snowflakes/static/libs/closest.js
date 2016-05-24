'use strict';
module.exports = function closest(el, selector) {
    while (el) {
        if (el.matches(selector)) return el; 
        el = el.parentElement;
    }
};
