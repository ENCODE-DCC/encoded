/** @jsx React.DOM */
'use strict';
var React = require('react');
var FetchedData = require('../fetched').FetchedData;
var globals = require('../globals');
var search = require('./search');

var ReactForms = require('react-forms');
var Schema = ReactForms.schema.Schema;
var Property = ReactForms.schema.Property;

var Listing = require('../search').Listing;
var SearchBlockEdit = search.SearchBlockEdit;


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


var ItemPreview = React.createClass({
    render: function() {
        var context = this.props.data['@graph'][0];
        var style = {width: '80%'};
        var Listing = globals.listing_views.lookup(context);
        return (
            <ul className="nav result-table">
                <Listing context={context} columns={this.props.data.columns} key={context['@id']} />
            </ul>
        );
    }
});


var ObjectPicker = module.exports.ObjectPicker = React.createClass({

    getDefaultProps: function() {
        return {searchBase: '?mode=picker'};
    },

    getInitialState: function() {
        return {
            browsing: false,
            search: this.props.searchBase
        };
    },

    render: function() {
        var url = this.props.value;
        var previewUrl = '/search?mode=picker&@id=' + url;
        var searchUrl = '/search' + this.state.search;
        var actions = [
            <button className="btn btn-primary" onClick={this.handleSelect}>Select</button>
        ];
        return (
            <div className="item-picker">
                <button className="btn btn-primary pull-right" onClick={this.handleBrowse}>Browse&hellip;</button>
                <div className="item-picker-preview">
                    {url ? <a className="clear" href="#" onClick={this.handleClear}><i className="icon icon-times"></i></a> : ''}
                    {url ? this.transferPropsTo(<FetchedData url={previewUrl} Component={ItemPreview} loadingComplete={true} showSpinnerOnUpdate={false} />) : ''}
                </div>
                {this.state.browsing ? 
                    <FetchedData url={searchUrl} Component={SearchBlockEdit}
                                 loadingComplete={true} searchBase={this.state.search}
                                 actions={actions} onChange={this.handleFilter}
                                 showSpinnerOnUpdate={false} /> : ''}
            </div>
        );
    },

    handleBrowse: function(e) {
        e.preventDefault();
        this.setState({browsing: !this.state.browsing});
    },

    handleFilter: function(href) {
        this.setState({search: href});
    },

    handleSelect: function(e) {
        var value = e.currentTarget.id;
        this.setState({browsing: false});
        this.props.onChange(value);
    },

    handleClear: function(e) {
        this.props.onChange("");
        return false;
    }
});


globals.blocks.register({
    label: 'item block',
    icon: 'icon icon-paperclip',
    schema: (
        <Schema>
          <Property name="item" label="Item" input={<ObjectPicker />} />
        </Schema>
    ),
    view: FetchedItemBlockView
}, 'itemblock');
