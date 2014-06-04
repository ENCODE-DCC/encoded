/** @jsx React.DOM */
'use strict';
var React = require('react');
var FetchedData = require('../fetched').FetchedData;
var globals = require('../globals');


var ItemBlockView = React.createClass({
    render: function() {
        var ViewComponent = globals.content_views.lookup(this.props.data);
        return <ViewComponent context={this.props.data} />;
    }
});


var FetchedItemBlock = React.createClass({

    shouldComponentUpdate: function(nextProps) {
        return (this.props.loadingComplete && nextProps.value.uuid != this.props.uuid);
    },

    render: function() {
        var url = '/' + this.props.value.uuid;
        return <FetchedData url={url} Component={ItemBlockView} loadingComplete={true} />;
    }
});

globals.block_views.register(FetchedItemBlock, 'itemblock');
