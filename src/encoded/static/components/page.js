/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var Layout = require('./layout').Layout;
var globals = require('./globals');
var merge = require('react/lib/merge');
var ItemEdit = require('./item').ItemEdit;


var LayoutType = {
    serialize: function(value) {
        var blockMap = {};
        value.blocks.map(function(block) {
            blockMap[block['@id']] = block;
        });
        return merge(value, {blocks: blockMap});
    },
    deserialize: function(value) {
        var blockList = Object.keys(value.blocks).map(function(blockId) {
            return value.blocks[blockId];
        });
        return merge(value, {blocks: blockList});
    },
}


var Page = module.exports.Page = React.createClass({
    render: function() {
        var value = LayoutType.serialize(this.props.context.layout);
        return <div><Layout value={value} /></div>;
    }
});


globals.content_views.register(Page, 'page');

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


var Schema    = ReactForms.schema.Schema;
var Property  = ReactForms.schema.Property;
var PageFormSchema = (
    <Schema>
        <Property name="name" label="Name" />
        <Property name="title" label="Title" />
        <Property name="layout" label="Layout"
                  type={LayoutType}
                  input={Layout({editable: true})}
                  defaultValue={defaultLayout} />
    </Schema>
);


var PageEdit = React.createClass({
    render: function() {
        var defaultValue = {layout: defaultLayout};
        return this.transferPropsTo(<ItemEdit context={this.props.context} schema={PageFormSchema} defaultValue={defaultValue} />);
    }
});

globals.content_views.register(PageEdit, 'page', 'edit');
globals.content_views.register(PageEdit, 'page_collection', 'add');
