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
    },

    componentDidMount: function() {
        // focus the first "Select" button in the search results
        var button = this.getDOMNode().querySelector('button.btn-primary');
        if (button) {
            button.focus();
        }
    },
});


var ItemPreview = module.exports.ItemPreview = React.createClass({
    render: function() {
        var context = this.props.data;
        if (context === undefined) return null;
        var Listing = globals.listing_views.lookup(context);
        return (
            <ul className="nav result-table" onClick={openLinksInNewWindow}>
                <Listing context={context} key={context['@id']} />
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
            search: '',
        };
    },

    componentDidUpdate: function(prevProps, prevState) {
        if (!this.props.value && !this.state.searchInput && this.state.searchInput != prevState.searchInput) {
            this.refs.input.getDOMNode().focus();
        } else if (this.props.value != prevProps.value) {
            this.refs.clear.getDOMNode().focus();
        }
    },

    render: function() {
        var url = this.props.value;
        var previewUrl = url;
        var searchUrl = '/search/' + this.state.search;
        var actions = [
            <button className="btn btn-primary" onClick={this.handleSelect}>Select</button>
        ];
        var searchParams = this.state.searchParams || this.props.searchBase;
        if (this.state.search) {
            searchParams += '&searchTerm=' + encodeURIComponent(this.state.search);
        }
        return (
            <div className={"item-picker" + (this.props.disabled ? ' disabled' : '')}>
                <div className="item-picker-preview" style={{display: 'inline-block', width: 'calc(100% - 120px)'}}>
                    {url ?
                        <fetched.FetchedData>
                            <fetched.Param name="data" url={previewUrl} />
                            <ItemPreview {...this.props} />
                        </fetched.FetchedData> : ''}
                    {!url ? <input value={this.state.searchInput} ref="input" type="text"
                                   placeholder="Enter a search term (accession, uuid, alias, ...)"
                                   onChange={this.handleInput} onBlur={this.handleSearch} onKeyDown={this.handleInput}
                                   disabled={this.props.disabled} /> : ''}
                    {this.state.error ? <div className="alert alert-danger">{this.state.error}</div> : ''}
                </div>
                {!this.props.disabled &&
                    <div className="pull-right">
                        <a className="clear" href="#" ref="clear" onClick={this.handleClear}><i className="icon icon-times"></i></a>
                        {' '}<button className={"btn btn-primary" + (this.state.browsing ? ' active' : '')} onClick={this.handleBrowse}>Browse&hellip;</button>
                    </div>
                }
                {this.state.browsing ? 
                    <fetched.FetchedData>
                        <fetched.Param name="context" url={'/search/' + searchParams} />
                        <SearchBlockEdit
                            searchBase={searchParams} restrictions={this.props.restrictions}
                            hideTextFilter={!url}
                            actions={actions} onChange={this.handleFilter} />
                    </fetched.FetchedData> : ''}
            </div>
        );
    },

    handleInput: function(e) {
        if (e.keyCode == 13) {
            e.preventDefault();
            this.handleSearch();
        }
        this.setState({searchInput: e.target.value});
    },

    handleSearch: function(e) {
        if (this.state.searchInput) {
            this.setState({search: this.state.searchInput, browsing: true});
        }
        this.props.onBlur();
    },

    handleBrowse: function(e) {
        e.preventDefault();
        this.setState({browsing: !this.state.browsing});
    },

    handleFilter: function(href) {
        this.setState({searchParams: href});
    },

    handleSelect: function(e) {
        var value = e.currentTarget.id;
        this.setState({browsing: false, searchInput: null, search: ''});
        this.props.onChange(value);
    },

    handleClear: function(e) {
        this.props.onBlur();
        this.props.onChange(null);
        this.setState({browsing: false, searchInput: '', search: '', searchParams: null});
        e.preventDefault();
    }
});
