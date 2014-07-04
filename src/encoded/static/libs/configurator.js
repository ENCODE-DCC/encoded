/** @jsx React.DOM */
'use strict';

module.exports = class Configurator {
    constructor(options) {
        this._seen = [];  // Avoid circular references
    }

    include(obj) {
        if (obj.includeme !== undefined) {
            obj = obj.includeme
        }
        if (this._seen.indexOf(obj) !== -1) {
            return;
        }
        this._seen.push(obj);
        obj(this);
    }
}
