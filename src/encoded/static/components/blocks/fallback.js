/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('../globals');
var item = require('../item');


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


// Also use this view as a fallback for anything we haven't registered
globals.block_views.fallback = function () {
    return BlockViewFallback;
};
