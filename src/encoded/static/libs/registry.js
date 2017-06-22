import _ from 'underscore';

export default class Registry {
    static providedBy(obj) {
        return obj['@type'] || [];
    }

    static fallback() {
    }

    constructor(options) {
        // May provide custom providedBy and fallback functions
        this.views = {};
        _.extend(this, options);
    }

    register(view, for_, name) {
        const localName = name || '';
        let views = this.views[localName];
        if (!views) {
            views = {};
            this.views[localName] = views;
        }
        views[for_] = view;
    }

    unregister(for_, name) {
        const views = this.views[name || ''];
        if (views) {
            delete views[for_];
        }
    }

    lookup(obj, name) {
        const views = this.views[name || ''];
        if (!views) {
            return Registry.fallback(obj, name);
        }

        const provided = Registry.providedBy(obj);
        for (let i = 0, len = provided.length; i < len; i += 1) {
            const view = views[provided[i]];
            if (view) {
                return view;
            }
        }
        return Registry.fallback(obj, name);
    }

    getAll(name) {
        const views = this.views[name || ''];
        return views || {};
    }
}
