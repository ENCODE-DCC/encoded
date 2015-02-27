'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var Layout = require('./layout').Layout;
var globals = require('./globals');
var _ = require('underscore');


var defaultLayout = {
    rows: [
        {
            cols: [
                {
                    blocks: ['#block1']
                }
            ]
        }
    ],
    blocks: [
        {
            "@id": "#block1",
            "@type": "richtextblock",
            "body": "(new layout)"
        }
    ]
};


class LayoutNode extends ReactForms.schema.ScalarNode {
    serialize(value) {
        if (!value) {
            value = defaultLayout;
        }
        var blockMap = {};
        value.blocks.map(function(block) {
            blockMap[block['@id']] = block;
        });
        return _.extend({}, value, {blocks: blockMap});
    }
    deserialize(value) {
        var blockList = Object.keys(value.blocks).map(function(blockId) {
            return value.blocks[blockId];
        });
        return _.extend({}, value, {blocks: blockList});
    }
}


var Page = module.exports.Page = React.createClass({
    render: function() {
        var context = this.props.context;
        var value = LayoutNode.serialize(context.layout);
        return (
            <div>
                <header className="row">
                    <div className="col-sm-12">
                        <h1 className="page-title">{context.title}</h1>
                    </div>
                </header>
                <Layout value={value} />
            </div>
        );
    }
});


globals.content_views.register(Page, 'page');
