/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('./globals');


var Block = module.exports.Block = React.createClass({
    render: function() {
        return (
            <div dangerouslySetInnerHTML={{__html: this.props.data.body}} />
        );
    }
});


var Row = module.exports.Row = React.createClass({
    render: function() {
        var blocks = this.props.blocks.map(function(block) {
            return <Block data={block.data} />;
        });
        return (
            <div class="row">
                {blocks}
            </div>
        );
    }
});


var Page = module.exports.Page = React.createClass({
    render: function() {
        var rows = this.props.context.layout.map(function(row) {
            return <Row blocks={row.blocks} />;
        });
        return <div>{rows}</div>;
    }
});


globals.content_views.register(Page, 'page');
