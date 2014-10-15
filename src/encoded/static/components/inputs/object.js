/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('../globals');
var FetchedData = require('../fetched').FetchedData;
var ResultTable = require('../search').ResultTable;


var SearchBlockEdit = React.createClass({
    render: function() {
        var styles = {maxHeight: 300, overflow: 'scroll' };
        return (
            <div className="well" style={styles}>
                {this.transferPropsTo(<ResultTable context={this.props.data} mode="picker" />)}
            </div>
        );
    }
});


var ItemPreview = React.createClass({
    render: function() {
        var context = this.props.data['@graph'][0];
        if (context === undefined) return null;
        var style = {width: '80%'};
        var Listing = globals.listing_views.lookup(context);
        return (
            <ul className="nav result-table">
                <Listing context={context} columns={this.props.data.columns} key={context['@id']} />
            </ul>
        );
    }
});


var ObjectPicker = React.createClass({

    getDefaultProps: function() {
        return {
            restrictions: {},
            searchBase: '?mode=picker'
        };
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
                                 loadingComplete={true}
                                 searchBase={this.state.search} restrictions={this.props.restrictions}
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


module.exports = ObjectPicker;
