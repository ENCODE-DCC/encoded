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


var ItemPreview = React.createClass({
    render: function() {
        var context = this.props.data;
        var style = {width: '80%'};
        return (
            <ul className="facet-list nav" style={style}>
                <Listing context={context} columns={context.columns} />
            </ul>
        );
    }
});


var ObjectPicker = React.createClass({

    getInitialState: function() {
        return {
            browsing: false,
            search: ''
        };
    },

    render: function() {
        var url = this.props.value;
        if (url.indexOf('/') !== 0) {
            url = '/' + url;
        }
        var searchUrl = '/search' + this.state.search;
        var actions = [
            <button className="btn btn-primary" onClick={this.handleSelect}>Select</button>
        ];
        return (
            <div>
              {this.state.browsing
                ? <FetchedData url={searchUrl} Component={SearchBlockEdit}
                               loadingComplete={true} searchBase={this.state.search}
                               actions={actions} onChange={this.handleFilter} />
                : <div className="clearfix">
                    <button className="btn btn-default pull-right" onClick={this.handleBrowse}>Browse&hellip;</button>
                    {this.transferPropsTo(<FetchedData url={url} Component={ItemPreview} loadingComplete={true} />)}
                  </div>}
            </div>
        );
    },

    handleBrowse: function(e) {
        e.preventDefault();
        this.setState({browsing: true});
    },

    handleFilter: function(href) {
        this.setState({search: href});
    },

    handleSelect: function(e) {
        var value = e.currentTarget.id;
        this.setState({browsing: false});
        this.props.onChange(value);
    }
});


globals.blocks.register({
    label: 'item block',
    icon: 'icon-file',
    schema: (
        <Schema>
          <Property name="item" label="Item" input={<ObjectPicker />} />
        </Schema>
    ),
    view: FetchedItemBlockView
}, 'itemblock');
