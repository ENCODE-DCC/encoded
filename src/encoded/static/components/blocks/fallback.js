/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('../globals');
var item = require('../item');


// Fallback block view

var BlockViewFallback = module.exports.BlockViewFallback = React.createClass({
    render: function() {
        var Panel = item.Panel;
        return (
            <div>
            <h2>{this.props.type.join(', ')}</h2>
                <Panel context={this.props.value} />
            </div>
        );
    }
});


// Fallback block edit form

var ReactForms = require('react-forms');
var Form = ReactForms.Form;
var Property = ReactForms.schema.Property;

var JsonType = {
    serialize: function(value) { return JSON.stringify(value, null, 4); },
    deserialize: function(value) { return (typeof value === 'string') ? JSON.parse(value) : value; },
}

var BlockSchema = (
    <Property label="JSON" type={JsonType} input={<textarea rows="15" cols="80" />} />
);

var BlockEditFallback = React.createClass({
    render: function() {
        return this.transferPropsTo(<Form schema={BlockSchema} value={this.props.value} />);
    }
});


// Also use these views as a fallback for anything we haven't registered
globals.block_views.fallback = function (obj, name) {
    return (name == 'edit') ? BlockEditFallback : BlockViewFallback;
};
