'use strict';
var ReactForms = require('react-forms');

class JSONNode extends ReactForms.schema.ScalarNode {
    serialize(value) {
        return JSON.stringify(value, null, 4);
    }
    deserialize(value) {
        return (typeof value === 'string') ? JSON.parse(value) : value;
    }
}

module.exports = JSONNode;
