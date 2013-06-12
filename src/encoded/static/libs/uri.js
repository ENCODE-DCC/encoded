define(function () {
    'use strict';
    // Inspired by http://james.padolsey.com/javascript/parsing-urls-with-the-dom/
    // Browser support: IE >= 9
    // Could use an iframe for IE8 and _.each instead of .forEach
    // An html document to resolve the uri against another base
    var resolver_doc = document.implementation.createHTMLDocument();
    var resolver_base = resolver_doc.createElement('base');
    var resolver_a = resolver_doc.createElement('a');
    var document_a = document.createElement('a');
    resolver_doc.head.appendChild(resolver_base);

    // http://www.ianbicking.org/blog/2013/04/new-considered-harmful.html
    var class_ = function (superclass, properties) {
        var prototype;
        if (! properties) {
            // We're creating an object with no superclass
            prototype = superclass;
        } else {
            prototype = Object.create(superclass.prototype);
            for (var a in properties) {
                if (properties.hasOwnProperty(a)) {
                    prototype[a] = properties[a];
                }
            }
        }
        var ClassObject = function () {
            var newObject = Object.create(prototype);
            if (newObject.constructor) {
                newObject.constructor.apply(newObject, arguments);
            }
            return newObject;
        };
        ClassObject.prototype = prototype;
        return ClassObject;
    };

    var URI = class_({
        constructor: function (href, base) {
            var a;
            if (typeof base === 'undefined') {
                // Use an anchor from the current document
                a = document_a;
            } else {
                // Use the special resolver document and set the base
                resolver_base.href = base;
                a = resolver_a;
            }
            a.href = href;
            
            this.hash = a.hash;
            this.host = a.host;
            this.hostname = a.hostname;
            this.href = a.href;
            this.origin = a.origin;
            this.pathname = a.pathname;
            this.port = a.port;
            this.protocol = a.protocol;
            this.search = a.search;
        },
        params: function () {
            var params = {};
            if (!this.search) return params;
            this.search.slice(1).split('&').forEach(function (part) {
                var equal = part.indexOf('=');
                if (equal === -1) return;
                var key = decodeURIComponent(part.slice(0, equal).replace('+', ' '));
                var value = decodeURIComponent(part.slice(equal + 1).replace('+', ' '));
                params[key] = value;
            });
            return params;
        }
    });

    return URI;
});
