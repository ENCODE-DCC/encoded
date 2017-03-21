'use strict';
var React = require('react');
var panel = require('../libs/bootstrap/panel');
var globals = require('./globals');
var fetched = require('./fetched');
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
var {Panel, PanelBody, PanelHeading} = panel;


var regionGenomes = [
    {value: 'GRCh37', display: 'hg19'},
    {value: 'GRCh38', display: 'GRCh38'},
    {value: 'GRCm37', display: 'mm9'},
    {value: 'GRCm38', display: 'mm10'}
];


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
            coordinates: '',
            genome: regionGenomes[0].value,
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
        this.setState({showAutoSuggest: true, terms: {}});
        this.newSearchTerm = e.target.value;
    },

    handleAutocompleteClick: function(term, id, name) {
        var newTerms = {};
        var inputNode = this.refs.annotation;
        inputNode.value = term;
        newTerms[name] = id;
        this.setState({terms: newTerms});
        this.setState({showAutoSuggest: false});
        inputNode.focus();
        // Now let the timer update the terms state when it gets around to it.
    },

    handleAssemblySelect: function(event) {
        // Handle click in assembly-selection <select>
        this.setState({genome: event.target.value});
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
            <Panel>
                <PanelBody>
                    <form id="panel1" className="adv-search-form" ref="adv-search" role="form" autoComplete="off" aria-labelledby="tab1">
                        <input type="hidden" name="annotation" value={this.state.terms['annotation']} />
                        <div className="form-group">
                            <label>Enter any one of human Gene name, Symbol, Synonyms, Gene ID, HGNC ID, coordinates, rsid, Ensemble ID</label>
                            <div className="input-group input-group-region-input">
                                <input ref="annotation" defaultValue={region} name="region" type="text" className="form-control" onChange={this.handleChange} />
                                {(this.state.showAutoSuggest && this.state.searchTerm) ?
                                    <FetchedData loadingComplete={true}>
                                        <Param name="auto" url={'/suggest/?genome=' + this.state.genome + '&q=' + this.state.searchTerm  } type="json" />
                                        <AutocompleteBox name="annotation" userTerm={this.state.searchTerm} handleClick={this.handleAutocompleteClick} />
                                    </FetchedData>
                                : null}
                                <div className="input-group-addon input-group-select-addon">
                                    <select value={this.state.genome} name="genome" onChange={this.handleAssemblySelect}>
                                        {regionGenomes.map(genomeId =>
                                            <option key={genomeId.value} value={genomeId.value}>{genomeId.display}</option>
                                        )}
                                    </select>
                                </div>
                                {context.notification ?
                                    <p className="input-region-error">{context.notification}</p>
                                : null}
                            </div>
                        </div>
                        <input type="submit" value="Search" className="btn btn-sm btn-info pull-right" />
                    </form>
                    {context.coordinates ?
                        <p>Searched coordinates: <strong>{context.coordinates}</strong></p>
                    : null}
                </PanelBody>
            </Panel>
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
        const visualizeLimit = 100;
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
        var visualize_disabled = total > visualizeLimit;

        // Get a sorted list of batch hubs keys with case-insensitive sort
        var visualizeKeys = [];
        if (context.visualize_batch && Object.keys(context.visualize_batch).length) {
            visualizeKeys = Object.keys(context.visualize_batch).sort((a, b) => {
                var aLower = a.toLowerCase();
                var bLower = b.toLowerCase();
                return (aLower > bLower) ? 1 : ((aLower < bLower) ? -1 : 0);
            });
        }

        return (
            <div>
                <h2>Region search</h2>
                <AdvSearch {...this.props} />
                    {context['notification'] === 'Success' ?
                        <div className="panel data-display main-panel">
                            <div className="row">
                                <div className="col-sm-5 col-md-4 col-lg-3">
                                    <FacetList {...this.props} facets={facets} filters={filters}
                                        searchBase={searchBase ? searchBase + '&' : searchBase + '?'} onFilter={this.onFilter} />
                                </div>
                                <div className="col-sm-7 col-md-8 col-lg-9">
                                    <div>
                                        <h4>
                                            Showing {results.length} of {total}
                                        </h4>
                                        <div className="results-table-control">
                                            {total > results.length && searchBase.indexOf('limit=all') === -1 ?
                                                    <a rel="nofollow" className="btn btn-info btn-sm"
                                                         href={searchBase ? searchBase + '&limit=all' : '?limit=all'}
                                                         onClick={this.onFilter}>View All</a>
                                            :
                                                <span>
                                                    {results.length > 25 ?
                                                            <a className="btn btn-info btn-sm"
                                                               href={trimmedSearchBase ? trimmedSearchBase : "/region-search/"}
                                                               onClick={this.onFilter}>View 25</a>
                                                    : null}
                                                </span>
                                            }

                                            {context['download_elements'] ?
                                                <DropdownButton title='Download Elements' label="downloadelements" wrapperClasses="results-table-button">
                                                    <DropdownMenu>
                                                        {context['download_elements'].map(link =>
                                                            <a key={link} data-bypass="true" target="_blank" private-browsing="true" href={link}>
                                                                {link.split('.').pop()}
                                                            </a>
                                                        )}
                                                    </DropdownMenu>
                                                </DropdownButton>
                                            : null}

                                            {visualizeKeys ?
                                                <DropdownButton disabled={visualize_disabled} title={visualize_disabled ? 'Filter to ' + visualizeLimit + ' to visualize' : 'Visualize'} label="batchhubs" wrapperClasses="results-table-button">
                                                    <DropdownMenu>
                                                        {visualizeKeys.map(assembly =>
                                                            Object.keys(context.visualize_batch[assembly]).sort().map(browser =>
                                                                <a key={[assembly, '_', browser].join()} data-bypass="true" target="_blank" private-browsing="true" href={context.visualize_batch[assembly][browser]}>
                                                                    {assembly} {browser}
                                                                </a>
                                                            )
                                                        )}
                                                    </DropdownMenu>
                                                </DropdownButton>
                                            : null}

                                        </div>
                                    </div>

                                  <hr />
                                  <ul className="nav result-table" id="result-table">
                                      {results.map(function (result) {
                                          return Listing({context:result, columns: columns, key: result['@id']});
                                      })}
                                  </ul>
                                </div>
                            </div>
                        </div>
                    : null}
            </div>
        );
    }
});

globals.content_views.register(RegionSearch, 'region-search');
