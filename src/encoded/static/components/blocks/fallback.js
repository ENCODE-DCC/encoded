'use strict';
var React = require('react');
var globals = require('../globals');
var item = require('../item');

var FallbackBlockView = React.createClass({
    render: function() {
        var Panel = item.Panel;
        return (
            <div>
            <h2>{this.props.blocktype.label}</h2>
                <Panel context={this.props.value} />
            </div>
        );
    }
});

var FallbackBlockEdit = module.exports.FallbackBlockEdit = React.createClass({
    render: function() {
        var ReactForms = require('react-forms');
        return <ReactForms.Form {...this.props} defaultValue={this.props.value} />;
    }
});


// Use this as a fallback for any block we haven't registered
globals.blocks.fallback = function (obj) {
    return {
        label: obj['@type'].join(','),
        schema: function() {
            var JSONNode = require('../form').JSONNode;
            return JSONNode.create({
                label: 'JSON',
                input: <textarea rows="15" cols="80" />,
            });
        },
        view: FallbackBlockView
    };
};
