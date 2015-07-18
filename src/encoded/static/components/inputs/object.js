'use strict';
var React = require('react');
var globals = require('../globals');
var fetched = require('../fetched');
var ResultTable = require('../search').ResultTable;


var openLinksInNewWindow = function(e) {
    if (e.isDefaultPrevented()) return;

    // intercept links and open in new tab
    var target = e.target;
    while (target && (target.tagName.toLowerCase() != 'a')) {
        target = target.parentElement;
    }
    if (!target) return;

    e.preventDefault();
    window.open(target.getAttribute('href'), '_blank');
};


var SearchBlockEdit = React.createClass({
    render: function() {
        var styles = {maxHeight: 300, overflow: 'scroll', clear: 'both' };
        return (
            <div className="well" style={styles} onClick={openLinksInNewWindow}>
                <ResultTable {...this.props} mode="picker" />
            </div>
        );
    }
});


var ItemPreview = module.exports.ItemPreview = React.createClass({
    render: function() {
        var context = this.props.data;
        if (context === undefined) return null;
        var Listing = globals.listing_views.lookup(context);
        return (
            <ul className="nav result-table" onClick={openLinksInNewWindow}>
                <Listing context={context} columns={this.props.data.columns} key={context['@id']} />
            </ul>
        );
    }
});


var ObjectPicker = module.exports.ObjectPicker = React.createClass({

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
        var previewUrl = url;
        var searchUrl = '/search/' + this.state.search;
        var actions = [
            <button className="btn btn-primary" onClick={this.handleSelect}>Select</button>
        ];
        return (
            <div className="item-picker">
                <button className="btn btn-primary pull-right" onClick={this.handleBrowse}>Browse&hellip;</button>
                <div className="item-picker-preview">
                    {url ? <a className="clear" href="#" onClick={this.handleClear}><i className="icon icon-times"></i></a> : ''}
                    {url ?
                        <fetched.FetchedData>
                            <fetched.Param name="data" url={previewUrl} />
                            <ItemPreview {...this.props} />
                        </fetched.FetchedData> : ''}
                </div>
                {this.state.browsing ? 
                    <fetched.FetchedData>
                        <fetched.Param name="context" url={searchUrl} />
                        <SearchBlockEdit
                            searchBase={this.state.search} restrictions={this.props.restrictions}
                            actions={actions} onChange={this.handleFilter} />
                    </fetched.FetchedData> : ''}
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
        e.preventDefault();
    }
});
