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
        var context = this.props.value.item;
        if (typeof context === 'object') {
            return <ItemBlockView context={context} />;
        }
        if (typeof context === 'string') {
            return (
                <fetched.FetchedData>
                    <fetched.Param name="context" url={context} />
                    <ItemBlockView />
                </fetched.FetchedData>
            );
        }
        return null;
    }
});


globals.blocks.register({
    label: 'item block',
    icon: 'icon icon-paperclip',
    schema: ReactForms.schema.Mapping({}, {
        item: ReactForms.schema.Scalar({label: 'Item', input: <ObjectPicker />})
    }),
    view: FetchedItemBlockView
}, 'itemblock');
