define(['class'],
function (class_) {
    'use strict';
    // Inspired by http://james.padolsey.com/javascript/parsing-urls-with-the-dom/
    // Browser support: IE >= 9
    // Could use an iframe for IE8 and _.each instead of .forEach
    // An html document to resolve the uri against another base
    var resolver_doc = document.implementation.createHTMLDocument('resolver');
    var resolver_base = resolver_doc.createElement('base');
    var resolver_a = resolver_doc.createElement('a');
    var document_a = document.createElement('a');
    resolver_doc.head.appendChild(resolver_base);

    var URI = class_({
        constructor: function (href, base) {
            var a;
            if (typeof href === 'undefined') {
                a = document.location;
            } else if (typeof base === 'undefined') {
                // Use an anchor from the current document
                a = document_a;
                a.href = href;
            } else {
                // Use the special resolver document and set the base
                resolver_base.href = base;
                a = resolver_a;
                a.href = href;
            }
            
            this.hash = a.hash;
            this.host = a.host;
            this.hostname = a.hostname;
            this.href = a.href;
            this.origin = a.origin;
            this.pathname = a.pathname;
            this.port = a.port;
            this.protocol = a.protocol;
            this.search = a.search;

            // Normalize
            if (this.protocol === 'data:') {
                // Chrome gives '' but Firefox gives '#foo'
                this.hash = '';
                // Chrome gives 'text/html;charset=utf-8,value' but Firefox gives ''
                this.pathname = '';
                this.origin = 'null';
            } else if (typeof this.origin === 'undefined') {
                // Firefox does not have a.origin (but FF 21 has location.origin)
                this.origin = this.protocol + '//' + this.host;
            }
        },
        params: function () {
            var params = {};
            if (!this.search) return params;
            this.search.slice(1).split('&').forEach(function (part) {
                var equal = part.indexOf('=');
                if (equal === -1) return;
                var key = decodeURIComponent(part.slice(0, equal).replace(/\+/g, ' '));
                var value = decodeURIComponent(part.slice(equal + 1).replace(/\+/g, ' '));
                params[key] = value;
            });
            return params;
        },
        sameOrigin: function (href) {
            if (!(href instanceof this.constructor)) {
                href = URI(href);
            }
            if (this.protocol !== href.protocol) return false;
            if (this.protocol === 'file:') return this.pathname === href.pathname;
            return this.origin !== 'null' && this.origin === href.origin;
        }
    });

    return URI;
});
