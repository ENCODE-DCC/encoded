/** @jsx React.DOM */
'use strict';
var _ = require('underscore');

class Registry {
    constructor(options) {
        // May provide custom providedBy and fallback functions
        this.views = {};
        _.extend(this, options);
    }

    providedBy(obj) {
        return obj['@type'] || [];
    }

    register(view, for_, name) {
        name = name || '';
        var views = this.views[name];
        if (!views) {
            this.views[name] = views = {};
        }
        views[for_] = view;
    }

    unregister(for_, name) {
        var views = this.views[name || ''];
        if (!views) {
            return;
        }
        delete views[for_];
    }

    lookup(obj, name) {
        var views = this.views[name || ''];
        if (!views) {
            return this.fallback(obj, name);
        }

        var provided = this.providedBy(obj);
        for (var i = 0, len = provided.length; i < len; i++) {
            var view = views[provided[i]];
            if (view) {
                return view;
            }
        }
        return this.fallback(obj, name);
    }

    getAll(name) {
        var views = this.views[name || ''];
        return views || {};
    }

    fallback(obj, name) {
        return;
    }
}

module.exports = Registry;
