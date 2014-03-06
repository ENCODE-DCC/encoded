require('es5-shim');
require('es5-shim/es5-sham');

(function () {

if (typeof console === 'undefined') {
    window.console = {};
    window.console.log = function () {};
}

// These are only required for the case when React wants to reset the HTML element,
// which fails because it cannot set node.innerHTML on IE8
var ElementPrototype = window.Element.prototype;
if (!ElementPrototype.getAttributeNS) {
    ElementPrototype.getAttributeNS = function getAttributeNS (namespace, name) {
        if (namespace) throw new Error("Unsupported getAttributeNS with namespace");
        return this.getAttribute(name);
    };
    ElementPrototype.setAttributeNS = function setAttributeNS (namespace, name, value) {
        if (namespace) throw new Error("Unsupported setAttributeNS with namespace");
        return this.setAttribute(name, value);
    };
    ElementPrototype.removeAttributeNS = function removeAttributeNS (namespace, name) {
        if (namespace) throw new Error("Unsupported removeAttributeNS with namespace");
        return this.removeAttribute(name);
    };
    ElementPrototype.hasAttributeNS = function hasAttributeNS (namespace, name) {
        if (namespace) throw new Error("Unsupported hasAttributeNS with namespace");
        return this.hasAttribute(name);
    };
}

})();
