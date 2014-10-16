/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var fetched = require('../fetched');
var globals = require('../globals');
var ObjectPicker = require('../inputs').ObjectPicker;


var ItemBlockView = module.exports.ItemBlockView = React.createClass({
    render: function() {
        var ViewComponent = globals.content_views.lookup(this.props.context);
        return this.transferPropsTo(<ViewComponent context={this.props.context} />);
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
        return (
            <fetched.FetchedData>
                <fetched.Param name="context" url={url} />
                <ItemBlockView />
            </fetched.FetchedData>
        );
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
