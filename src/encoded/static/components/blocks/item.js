/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var FetchedData = require('../fetched').FetchedData;
var globals = require('../globals');
var ObjectPicker = require('../inputs').ObjectPicker;


var ItemBlockView = module.exports.ItemBlockView = React.createClass({
    render: function() {
        var ViewComponent = globals.content_views.lookup(this.props.data);
        return this.transferPropsTo(<ViewComponent context={this.props.data} />);
    }
});


var FetchedItemBlockView = React.createClass({

    shouldComponentUpdate: function(nextProps) {
        return (nextProps.value.item != this.props.value.item);
    },

    render: function() {
        var url = this.props.value.item;
        if (url && url.indexOf('/') !== 0) {
            url = '/' + url;
        }
        return <FetchedData url={url} Component={ItemBlockView} loadingComplete={true} />;
    }
});


globals.blocks.register({
    label: 'item block',
    icon: 'icon icon-paperclip',
    schema: (
        <ReactForms.schema.Schema>
          <ReactForms.schema.Property name="item" label="Item" input={<ObjectPicker />} />
        </ReactForms.schema.Schema>
    ),
    view: FetchedItemBlockView
}, 'itemblock');
