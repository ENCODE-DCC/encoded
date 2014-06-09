/** @jsx React.DOM */
'use strict';
var React = require('react');
var FetchedData = require('../fetched').FetchedData;
var globals = require('../globals');


var ItemBlockView = React.createClass({
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
        if (url.indexOf('/') !== 0) {
            url = '/' + url;
        }
        return <FetchedData url={url} Component={ItemBlockView} loadingComplete={true} />;
    }
});


globals.blocks.register({
    label: 'item block',
    icon: 'icon-file',
    view: FetchedItemBlockView
}, 'itemblock');
