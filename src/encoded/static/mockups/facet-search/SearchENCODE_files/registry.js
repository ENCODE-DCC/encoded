define(['class', 'underscore'],
function (class_, _) {
    'use strict';

    var Registry = class_({
        constructor: function (options) {
            // May provide custom providedBy and fallback functions
            this.views = {};
            _.extend(this, options);
        },

        providedBy: function (obj) {
            return obj['@type'] || [];
        },

        register: function (view, for_, name) {
            name = name || '';
            var views = this.views[name];
            if (!views) {
                this.views[name] = views = {};
            }
            views[for_] = view;
        },

        unregister: function (for_, name) {
            var views = this.views[name || ''];
            if (!views) {
                return;
            }
            delete views[for_];
        },

        lookup: function (obj, name) {
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
        },

        fallback: function (obj, name) {
            return;
        }
    });

    return Registry;
});
