/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('../globals');


var RichTextBlockView = module.exports.RichTextBlockView = React.createClass({
    render: function() {
        return (
            <div dangerouslySetInnerHTML={{__html: this.props.data.body}} />
        );
    }
});


globals.block_views.register(RichTextBlockView, 'richtextblock');
