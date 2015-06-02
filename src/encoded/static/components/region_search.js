'use strict';
var React = require('react');
var globals = require('./globals');
var fetched = require('./fetched');
var browser = require('./browser');
var TabbedArea = require('react-bootstrap').TabbedArea;
var TabPane = require('react-bootstrap').TabPane;
var url = require('url');

var GenomeBrowser = browser.GenomeBrowser;
var FetchedData = fetched.FetchedData;
var Param = fetched.Param;

var Listing = module.exports.Listing = function (props) {
    // XXX not all panels have the same markup
    var context;
    if (props['@id']) {
        context = props;
        props = {context: context,  key: context['@id']};
    }
    var ListingView = globals.listing_views.lookup(props.context);
    return <ListingView {...props} />;
};

var AutocompleteBox = React.createClass({
    render: function() {
        var terms = this.props.auto['@graph']; // List of matching terms from server
        var userTerm = this.props.userTerm && this.props.userTerm.toLowerCase(); // Term user entered

        if (!this.props.hide && userTerm && userTerm.length && terms && terms.length) {
            return (
                <ul className="adv-search-autocomplete">
                    {terms.map(function(term) {
                        var matchStart, matchEnd;
                        var preText, matchText, postText;

                        // Boldface matching part of term
                        matchStart = term.text.toLowerCase().indexOf(userTerm);
                        if (matchStart >= 0) {
                            matchEnd = matchStart + userTerm.length;
                            preText = term.text.substring(0, matchStart);
                            matchText = term.text.substring(matchStart, matchEnd);
                            postText = term.text.substring(matchEnd);
                        } else {
                            preText = term.text;
                        }
                        return <li key={term.payload.id} tabIndex="0" onClick={this.props.handleClick.bind(null, term.text, term.payload.id, this.props.name)}>{preText}<b>{matchText}</b>{postText}</li>;
                    }, this)}
                </ul>
            );
        } else {
            return null;
        }
    }
});

var SearchForm = React.createClass({
    getInitialState: function() {
        return {
            disclosed: false,
            searchTerm: '',
            terms: {}
        };
    },

    contextTypes: {
        autocompleteTermChosen: React.PropTypes.bool,
        onAutocompleteChosenChange: React.PropTypes.func,
        onAutocompleteFocusChange: React.PropTypes.func,
        autocompleteHidden: React.PropTypes.bool,
        onAutocompleteHiddenChange: React.PropTypes.func
    },

    handleChange: function(e) {
        this.newSearchTerm = e.target.value;
        this.context.onAutocompleteHiddenChange(false);
        this.context.onAutocompleteChosenChange(false);
        // Now let the timer update the search terms state when it gets around to it.
    },

    handleAutocompleteClick: function(term, id, name) {
        var newTerms = {};
        var inputNode = this.refs.regionid.getDOMNode();

        inputNode.value = this.newSearchTerm = term;
        newTerms[name] = id;
        this.setState({terms: newTerms});
        this.context.onAutocompleteHiddenChange(true);
        this.context.onAutocompleteChosenChange(true);
        inputNode.focus();
        // Now let the timer update the terms state when it gets around to it.
    },

    handleFocus: function(focused) {
        this.context.onAutocompleteFocusChange(focused);
    },

    componentDidMount: function() {
        // Use timer to limit to one request per second
        this.timer = setInterval(this.tick, 1000);
    },

    componentWillUnmount: function() {
        clearInterval(this.timer);
    },

    tick: function() {
        if (!this.context.autocompleteHidden && (this.newSearchTerm !== this.state.searchTerm)) {
            this.setState({searchTerm: this.newSearchTerm});
        }
    },

    render: function() {
        var id = url.parse(this.props.href, true);
        var region = id.query['region'] || '';
        return (
            <div className="adv-search-form">
                <form role="form" autoComplete="off" aria-labeledby="tab1">
                    <div className="form-group col-md-4">
                        <input type="hidden" name="genome" value="hg19" />
                        {Object.keys(this.state.terms).map(function(key) {
                            return <input type="hidden" name={key} value={this.state.terms[key]} />;
                        }, this)}
                        <input type="text" className="form-control" placeholder="Enter coordinates in the format: chrx:start-end"
                            ref="region" name="region" defaultValue={region} key={region} />
                    </div>
                    <div className="form-group col-md-2">
                        <input type="submit" value="Search" className="btn btn-sm btn-info adv-search-submit" />
                    </div>
                </form>
            </div>
        );
    }
});

var RegionSearch = module.exports.RegionSearch = React.createClass({
    render: function() {
        var context = this.props.context;
        var results = context['@graph'];
        var columns = context['columns'];
        var notification = context['notification'];
        var assembly = ['hg19'];
        var files = [];
        return (
          <div>
              <h3>Search ENCODE data by region</h3>
              <SearchForm {...this.props} />
              {results.length ?
                <div className="panel data-display main-panel">
                    <h4>Showing {results.length} of {context.total}</h4>
                    <TabbedArea defaultActiveKey={1} animation={false}>
                        <TabPane eventKey={1} tab='List view'>
                            <ul className="nav result-table" id="result-table">
                                {results.map(function (result) {
                                    return Listing({context:result, columns: columns, key: result['@id']});
                                })}
                            </ul>
                        </TabPane>
                        <TabPane eventKey={2} tab='Browser view'>
                            {results.map(function(result){
                                  files.push.apply(files, result['files'])
                            })}
                            <GenomeBrowser files={files} assembly={assembly} />
                        </TabPane>
                    </TabbedArea>
                  </div>
              :<h4>{notification}</h4>}
          </div>
        );
    }
});

globals.content_views.register(RegionSearch, 'region-search');
