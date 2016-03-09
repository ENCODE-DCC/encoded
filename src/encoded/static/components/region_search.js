'use strict';
var React = require('react');
var globals = require('./globals');
var fetched = require('./fetched');
var TabbedArea = require('react-bootstrap').TabbedArea;
var TabPane = require('react-bootstrap').TabPane;
var url = require('url');
var search = require('./search');
var button = require('../libs/bootstrap/button');
var dropdownMenu = require('../libs/bootstrap/dropdown-menu');

var FacetList = search.FacetList;
var Facet = search.Facet;
var TextFilter = search.TextFilter;
var Listing = search.Listing;
var BatchDownload = search.BatchDownload;
var FetchedData = fetched.FetchedData;
var Param = fetched.Param;
var DropdownButton = button.DropdownButton;
var DropdownMenu = dropdownMenu.DropdownMenu;


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
                        return <li key={term.text} tabIndex="0" onClick={this.props.handleClick.bind(null, term.text, term.payload.id, this.props.name)}>{preText}<b>{matchText}</b>{postText}</li>;
                    }, this)}
                </ul>
            );
        } else {
            return null;
        }
    }
});

var AdvSearch = React.createClass({
    getInitialState: function() {
        return {
            disclosed: false,
            showAutoSuggest: false,
            searchTerm: '',
            terms: {}
        };
    },

    contextTypes: {
        autocompleteTermChosen: React.PropTypes.bool,
        autocompleteHidden: React.PropTypes.bool,
        onAutocompleteHiddenChange: React.PropTypes.func,
        location_href: React.PropTypes.string
    },

    handleDiscloseClick: function(e) {
        this.setState({disclosed: !this.state.disclosed});
    },

    handleChange: function(e) {
        this.setState({showAutoSuggest: true});
        this.newSearchTerm = e.target.value;
    },

    handleAutocompleteClick: function(term, id, name) {

        var newTerms = {};
        var inputNode = this.refs.annotation.getDOMNode();
        inputNode.value = this.newSearchTerm = term;
        newTerms[name] = id;
        this.setState({terms: newTerms});
        this.setState({showAutoSuggest: false});
        inputNode.focus();
        // Now let the timer update the terms state when it gets around to it.
    },

    componentDidMount: function() {
        // Use timer to limit to one request per second
        this.timer = setInterval(this.tick, 1000);
    },

    componentWillUnmount: function() {
        clearInterval(this.timer);
    },

    tick: function() {
        if (this.newSearchTerm !== this.state.searchTerm) {
            this.setState({searchTerm: this.newSearchTerm});
        }
    },

    render: function() {
        var context = this.props.context;
        var id = url.parse(this.context.location_href, true);
        var region = id.query['region'] || '';
        return (
            <div className="adv-search-form">
                <form id="panel1" ref="adv-search" role="form" autoComplete="off" aria-labeledby="tab1">
                    <div className="row">
                        <div className="form-group col-md-8">
                            <input type="hidden" name="genome" value="hg19" />
                            {Object.keys(this.state.terms).map(function(key) {
                                return <input type="hidden" name={key} value={this.state.terms[key]} />;
                            }, this)}
                            <input ref="annotation" defaultValue={region} name="region" type="text" className="form-control" onChange={this.handleChange}
                            
                                placeholder="Enter any one of human Gene name, Symbol, Synonyms, Gene ID, HGNC ID, coordinates, rsid, Ensemble ID" />
                            {(this.state.showAutoSuggest && this.state.searchTerm) ?
                                <FetchedData loadingComplete={true}>
                                    <Param name="auto" url={'/suggest/?q=' + this.state.searchTerm} />
                                    <AutocompleteBox name="annotation" userTerm={this.state.searchTerm} handleClick={this.handleAutocompleteClick} />
                                </FetchedData>
                            : null}
                        </div>
                        <div className="form-group col-md-2">
                            <input type="submit" value="Search" className="btn btn-sm btn-info adv-search-submit" />
                        </div>
                    </div>
                </form>
            </div>
        );
    }
});

var RegionSearch = module.exports.RegionSearch = React.createClass({
    onFilter: function(e) {
        var search = e.currentTarget.getAttribute('href');
        this.props.onChange(search);
        e.stopPropagation();
        e.preventDefault();
    },
    contextTypes: {
        location_href: React.PropTypes.string,
        navigate: React.PropTypes.func
    },
    render: function() {
        const batchHubLimit = 100;
        var context = this.props.context;
        var results = context['@graph'];
        var columns = context['columns'];
        var notification = context['notification'];
        var assembly = ['hg19'];
        var files = [];
        var id = url.parse(this.context.location_href, true);
        var region = context['region'] || '';
        var searchBase = url.parse(this.context.location_href).search || '';
        var trimmedSearchBase = searchBase.replace(/[\?|\&]limit=all/, "");
        var filters = context['filters'];
        var facets = context['facets'];
        var total = context['total'];
        var batch_hub_disabled = total > batchHubLimit;

        // Get a sorted list of batch hubs keys with case-insensitive sort
        var batchHubKeys = [];
        if (context.batch_hub && Object.keys(context.batch_hub).length) {
            batchHubKeys = Object.keys(context.batch_hub).sort((a, b) => {
                var aLower = a.toLowerCase();
                var bLower = b.toLowerCase();
                return (aLower > bLower) ? 1 : ((aLower < bLower) ? -1 : 0);
            });
        }

        return (
          <div>
              <h2>Region search</h2>
              <AdvSearch {...this.props} />
              {results.length ?
                  <div className="panel data-display main-panel">
                      <div className="row">
                          <div className="col-sm-5 col-md-4 col-lg-3">
                              <FacetList {...this.props} facets={facets} filters={filters}
                                  searchBase={searchBase ? searchBase + '&' : searchBase + '?'} onFilter={this.onFilter} />
                          </div>
                          <div className="col-sm-7 col-md-8 col-lg-9 search-list">
                              <h4>
                                  Showing {results.length} of {total}
                                  {total > results.length && searchBase.indexOf('limit=all') === -1 ?
                                      <span className="pull-right">
                                          <a rel="nofollow" className="btn btn-info btn-sm"
                                               href={searchBase ? searchBase + '&limit=all' : '?limit=all'}
                                               onClick={this.onFilter}>View All</a>
                                      </span>
                                  :
                                      <span>
                                          {results.length > 25 ?
                                              <span className="pull-right">
                                                  <a className="btn btn-info btn-sm"
                                                     href={trimmedSearchBase ? trimmedSearchBase : "/region-search/"}
                                                     onClick={this.onFilter}>View 25</a>
                                              </span>
                                          : null}
                                      </span>
                                  }

                                  {context['batch_download'] ?
                                      <span className="pull-right">
                                          <BatchDownload context={context} />&nbsp;
                                      </span>
                                  : null}

                                  {batchHubKeys ?
                                    <DropdownButton disabled={batch_hub_disabled} title={batch_hub_disabled ? 'Filter to ' + batchHubLimit + ' to visualize' : 'Visualize'}>
                                        <DropdownMenu>
                                            {batchHubKeys.map(assembly =>
                                                <a key={assembly} data-bypass="true" target="_blank" private-browsing="true" href={context['batch_hub'][assembly]}>
                                                    {assembly}
                                                </a>
                                            )}
                                        </DropdownMenu>
                                    </DropdownButton>
                                  : null}

                              </h4>
                              <hr />
                              <ul className="nav result-table" id="result-table">
                                  {results.map(function (result) {
                                      return Listing({context:result, columns: columns, key: result['@id']});
                                  })}
                              </ul>
                          </div>
                      </div>
                  </div>
              :<h4>{notification}</h4>}
          </div>
        );
    }
});

globals.content_views.register(RegionSearch, 'region-search');
