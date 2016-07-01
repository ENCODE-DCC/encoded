'use strict';
var React = require('react');
var cloneWithProps = require('react/lib/cloneWithProps');
var queryString = require('query-string');
var Modal = require('react-bootstrap/lib/Modal');
var OverlayMixin = require('react-bootstrap/lib/OverlayMixin');
var button = require('../libs/bootstrap/button');
var dropdownMenu = require('../libs/bootstrap/dropdown-menu');
var SvgIcon = require('../libs/svg-icons');
var cx = require('react/lib/cx');
var url = require('url');
var _ = require('underscore');
var globals = require('./globals');
var image = require('./image');
var search = module.exports;
var audit = require('./audit');
var objectutils = require('./objectutils');

var AuditIndicators = audit.AuditIndicators;
var AuditDetail = audit.AuditDetail;
var AuditMixin = audit.AuditMixin;
var DropdownButton = button.DropdownButton;
var DropdownMenu = dropdownMenu.DropdownMenu;

// Should really be singular...
var types = {
    image: {title: 'Images'},
    page: {title: 'Web page'},
    snowset: {title: 'Snowsets'},
    snowball: {title: 'Snowballs'},
    snowfort: {title: 'Snowforts'},
    snowflake: {title: 'Snowflakes'}
};

var datasetTypes = {
    snowset: types['snowset'].title,
    snowball: types['snowball'].title,
    snowfort: types['snowfort'].title,
};

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

var PickerActionsMixin = module.exports.PickerActionsMixin = {
    contextTypes: {actions: React.PropTypes.array},
    renderActions: function() {
        if (this.context.actions && this.context.actions.length) {
            return (
                <div className="pull-right">
                    {this.context.actions.map(action => cloneWithProps(action, {id: this.props.context['@id']}))}
                </div>
            );
        } else {
            return <span/>;
        }
    }
};

var Item = module.exports.Item = React.createClass({
    mixins: [PickerActionsMixin, AuditMixin],
    render: function() {
        var result = this.props.context;
        var title = globals.listing_titles.lookup(result)({context: result});
        var item_type = result['@type'][0];
        return (
            <li>
                <div className="clearfix">
                    {this.renderActions()}
                    {result.accession ?
                        <div className="pull-right type sentence-case search-meta">
                            <p>{item_type}: {' ' + result['accession']}</p>
                            <AuditIndicators audits={result.audit} id={this.props.context['@id']} search />
                        </div>
                    : null}
                    <div className="accession">
                        <a href={result['@id']}>{title}</a>
                    </div>
                    <div className="data-row">
                        {result.description}
                    </div>
                </div>
                <AuditDetail context={result} id={this.props.context['@id']} forcedEditLink />
            </li>
        );
    }
});
globals.listing_views.register(Item, 'Item');

// Display one antibody status indicator
var StatusIndicator = React.createClass({
    getInitialState: function() {
        return {
            tipOpen: false,
            tipStyles: {}
        };
    },

    // Display tooltip on hover
    onMouseEnter: function () {
        function getNextElementSibling(el) {
            // IE8 doesn't support nextElementSibling
            return el.nextElementSibling ? el.nextElementSibling : el.nextSibling;
        }

        // Get viewport bounds of result table and of this tooltip
        var whiteSpace = 'nowrap';
        var resultBounds = document.getElementById('result-table').getBoundingClientRect();
        var resultWidth = resultBounds.right - resultBounds.left;
        var tipBounds = _.clone(getNextElementSibling(this.refs.indicator.getDOMNode()).getBoundingClientRect());
        var tipWidth = tipBounds.right - tipBounds.left;
        var width = tipWidth;
        if (tipWidth > resultWidth) {
            // Tooltip wider than result table; set tooltip to result table width and allow text to wrap
            tipBounds.right = tipBounds.left + resultWidth - 2;
            whiteSpace = 'normal';
            width = tipBounds.right - tipBounds.left - 2;
        }

        // Set an inline style to move the tooltip if it runs off right edge of result table
        var leftOffset = resultBounds.right - tipBounds.right;
        if (leftOffset < 0) {
            // Tooltip goes outside right edge of result table; move it to the left
            this.setState({tipStyles: {left: (leftOffset + 10) + 'px', maxWidth: resultWidth + 'px', whiteSpace: whiteSpace, width: width + 'px'}});
        } else {
            // Tooltip fits inside result table; move it to native position
            this.setState({tipStyles: {left: '10px', maxWidth: resultWidth + 'px', whiteSpace: whiteSpace, width: width + 'px'}});
        }

        this.setState({tipOpen: true});
    },

    // Close tooltip when not hovering
    onMouseLeave: function() {
        this.setState({tipStyles: {maxWidth: 'none', whiteSpace: 'nowrap', width: 'auto', left: '15px'}}); // Reset position and width
        this.setState({tipOpen: false});
    },

    render: function() {
        var classes = {tooltipopen: this.state.tipOpen};

        return (
            <span className="tooltip-status-trigger">
                <i className={globals.statusClass(this.props.status, 'indicator icon icon-circle')} ref="indicator" onMouseEnter={this.onMouseEnter} onMouseLeave={this.onMouseLeave}></i>
                <div className={"tooltip-status sentence-case " + cx(classes)} style={this.state.tipStyles}>
                    {this.props.status}<br /><span>{this.props.terms.join(', ')}</span>
                </div>
            </span>
        );
    }
});

// Display the status indicators for one target
var StatusIndicators = React.createClass({
    render: function() {
        var targetTree = this.props.targetTree;
        var target = this.props.target;

        return (
            <span className="status-indicators">
                {Object.keys(targetTree[target]).map(function(status, i) {
                    if (status !== 'target') {
                        return <StatusIndicator key={i} status={status} terms={targetTree[target][status]} />;
                    } else {
                        return null;
                    }
                })}
            </span>
        );
    }
});

var Image = module.exports.Image = React.createClass({
    mixins: [PickerActionsMixin],
    render: function() {
        var result = this.props.context;
        var Attachment = image.Attachment;
        return (
            <li>
                <div className="clearfix">
                    {this.renderActions()}
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Image</p>
                        <AuditIndicators audits={result.audit} id={this.props.context['@id']} search />
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>{result.caption}</a>
                    </div>
                    <div className="data-row">
                        <Attachment context={result} attachment={result.attachment} />
                    </div>
                </div>
                <AuditDetail context={result} id={this.props.context['@id']} forcedEditLink />
            </li>
        );
    }
});
globals.listing_views.register(Image, 'Image');


// If the given term is selected, return the href for the term
function termSelected(term, field, filters) {
    for (var filter in filters) {
        if (filters[filter]['field'] == field && filters[filter]['term'] == term) {
            return url.parse(filters[filter]['remove']).search;
        }
    }
    return null;
}

// Determine whether any of the given terms are selected
function countSelectedTerms(terms, field, filters) {
    var count = 0;
    for(var oneTerm in terms) {
        if(termSelected(terms[oneTerm].key, field, filters)) {
            count++;
        }
    }
    return count;
}

var Term = search.Term = React.createClass({
    render: function () {
        var filters = this.props.filters;
        var term = this.props.term['key'];
        var count = this.props.term['doc_count'];
        var title = this.props.title || term;
        var field = this.props.facet['field'];
        var em = field === 'snowflakes.type';
        var barStyle = {
            width:  Math.ceil( (count/this.props.total) * 100) + "%"
        };
        var selected = termSelected(term, field, filters);
        var href;
        if (selected && !this.props.canDeselect) {
            href = null;
        } else if (selected) {
            href = selected;
        } else {
            href = this.props.searchBase + field + '=' + encodeURIComponent(term).replace(/%20/g, '+');
        }
        return (
            <li id={selected ? "selected" : null} key={term}>
                {selected ? '' : <span className="bar" style={barStyle}></span>}
                <a id={selected ? "selected" : null} href={href} onClick={href ? this.props.onFilter : null}>
                    <span className="pull-right">{count} {selected && this.props.canDeselect ? <i className="icon icon-times-circle-o"></i> : ''}</span>
                    <span className="facet-item">
                        {em ? <em>{title}</em> : <span>{title}</span>}
                    </span>
                </a>
            </li>
        );
    }
});

var TypeTerm = search.TypeTerm = React.createClass({
    render: function () {
        var term = this.props.term['key'];
        var filters = this.props.filters;
        var title;
        try {
            title = types[term];
        } catch (e) {
            title = term;
        }
        var total = this.props.total;
        return <Term {...this.props} title={title} filters={filters} total={total} />;
    }
});


var Facet = search.Facet = React.createClass({
    getDefaultProps: function() {
        return {width: 'inherit'};
    },

    getInitialState: function () {
        return {
            facetOpen: false
        };
    },

    handleClick: function () {
        this.setState({facetOpen: !this.state.facetOpen});
    },

    render: function() {
        var facet = this.props.facet;
        var filters = this.props.filters;
        var title = facet['title'];
        var field = facet['field'];
        var total = facet['total'];
        var termID = title.replace(/\s+/g, '');
        var terms = facet['terms'].filter(function (term) {
            if (term.key) {
                for(var filter in filters) {
                    if(filters[filter].term === term.key) {
                        return true;
                    }
                }
                return term.doc_count > 0;
            } else {
                return false;
            }
        });
        var moreTerms = terms.slice(5);
        var TermComponent = field === 'type' ? TypeTerm : Term;
        var selectedTermCount = countSelectedTerms(moreTerms, field, filters);
        var moreTermSelected = selectedTermCount > 0;
        var canDeselect = (!facet.restrictions || selectedTermCount >= 2);
        var moreSecClass = 'collapse' + ((moreTermSelected || this.state.facetOpen) ? ' in' : '');
        var seeMoreClass = 'btn btn-link' + ((moreTermSelected || this.state.facetOpen) ? '' : ' collapsed');
        return (
            <div className="facet" hidden={terms.length === 0} style={{width: this.props.width}}>
                <h5>{title}</h5>
                <ul className="facet-list nav">
                    <div>
                        {terms.slice(0, 5).map(function (term) {
                            return <TermComponent {...this.props} key={term.key} term={term} filters={filters} total={total} canDeselect={canDeselect} />;
                        }.bind(this))}
                    </div>
                    {terms.length > 5 ?
                        <div id={termID} className={moreSecClass}>
                            {moreTerms.map(function (term) {
                                return <TermComponent {...this.props} key={term.key} term={term} filters={filters} total={total} canDeselect={canDeselect} />;
                            }.bind(this))}
                        </div>
                    : null}
                    {(terms.length > 5 && !moreTermSelected) ?
                        <label className="pull-right">
                                <small>
                                    <button type="button" className={seeMoreClass} data-toggle="collapse" data-target={'#'+termID} onClick={this.handleClick} />
                                </small>
                        </label>
                    : null}
                </ul>
            </div>
        );
    }
});

var TextFilter = search.TextFilter = React.createClass({

    getValue: function(props) {
        var filter = this.props.filters.filter(function(f) {
            return f.field == 'searchTerm';
        });
        return filter.length ? filter[0].term : '';
    },

    shouldUpdateComponent: function(nextProps) {
        return (this.getValue(this.props) != this.getValue(nextProps));
    },

    render: function() {
        return (
            <div className="facet">
                <input ref="input" type="search" className="form-control search-query"
                        placeholder="Enter search term(s)"
                        defaultValue={this.getValue(this.props)}
                        onChange={this.onChange} onBlur={this.onBlur} onKeyDown={this.onKeyDown} />
            </div>
        );
    },

    onChange: function(e) {
        e.stopPropagation();
        e.preventDefault();
    },

    onBlur: function(e) {
        var search = this.props.searchBase.replace(/&?searchTerm=[^&]*/, '');
        var value = e.target.value;
        if (value) {
            search += 'searchTerm=' + e.target.value;
        } else {
            search = search.substring(0, search.length - 1);
        }
        this.props.onChange(search);
    },

    onKeyDown: function(e) {
        if (e.keyCode == 13) {
            this.onBlur(e);
            e.preventDefault();
        }
    }
});

var FacetList = search.FacetList = React.createClass({
    contextTypes: {
        session: React.PropTypes.object,
        hidePublicAudits: React.PropTypes.bool
    },

    getDefaultProps: function() {
        return {orientation: 'vertical'};
    },

    render: function() {
        var {context, term} = this.props;
        var loggedIn = this.context.session && this.context.session['auth.userid'];

        // Get all facets, and "normal" facets, meaning non-audit facets
        var facets = this.props.facets;
        var normalFacets = facets.filter(facet => facet.field.substring(0, 6) !== 'audit.');

        var filters = this.props.filters;
        var width = 'inherit';
        if (!facets.length && this.props.mode != 'picker') return <div />;
        var hideTypes;
        if (this.props.mode == 'picker') {
            hideTypes = false;
        } else {
            hideTypes = filters.filter(filter => filter.field === 'type').length === 1 && normalFacets.length > 1;
        }
        if (this.props.orientation == 'horizontal') {
            width = (100 / facets.length) + '%';
        }

        // See if we need the Clear Filters link or not. context.clear_filters 
        var clearButton; // JSX for the clear button
        var searchQuery = context && context['@id'] && url.parse(context['@id']).search;
        if (searchQuery) {
            // Convert search query string to a query object for easy parsing
            var terms = queryString.parse(searchQuery);

            // See if there are terms in the query string aside from `searchTerm`. We have a Clear
            // Filters button if we do
            var nonPersistentTerms = _(Object.keys(terms)).any(term => term !== 'searchTerm');
            clearButton = nonPersistentTerms && terms['searchTerm'];

            // If no Clear Filters button yet, do the same check with `type` in the query string
            if (!clearButton) {
                nonPersistentTerms = _(Object.keys(terms)).any(term => term !== 'type');
                clearButton = nonPersistentTerms && terms['type'];
            }
        }

        return (
            <div className={"box facets " + this.props.orientation}>
                {clearButton ?
                    <div className="clear-filters-control">
                        <a href={context.clear_filters}>Clear Filters <i className="icon icon-times-circle"></i></a>
                    </div>
                : null}
                {this.props.mode === 'picker' && !this.props.hideTextFilter ? <TextFilter {...this.props} filters={filters} /> : ''}
                {facets.map(facet => {
                    if ((hideTypes && facet.field == 'type') || (!loggedIn && this.context.hidePublicAudits && facet.field.substring(0, 6) === 'audit.')) {
                        return <span key={facet.field} />;
                    } else {
                        return <Facet {...this.props} key={facet.field} facet={facet} filters={filters}
                                        width={width} />;
                    }
                })}
            </div>
        );
    }
});

var ResultTable = search.ResultTable = React.createClass({

    getDefaultProps: function() {
        return {
            restrictions: {},
            searchBase: ''
        };
    },

    childContextTypes: {actions: React.PropTypes.array},
    getChildContext: function() {
        return {
            actions: this.props.actions
        };
    },

    render: function() {
        var context = this.props.context;
        var results = context['@graph'];
        var total = context['total'];
        var columns = context['columns'];
        var filters = context['filters'];
        var label = 'results';
        var searchBase = this.props.searchBase;
        var trimmedSearchBase = searchBase.replace(/[\?|\&]limit=all/, "");

        var facets = context['facets'].map(function(facet) {
            if (this.props.restrictions[facet.field] !== undefined) {
                facet = _.clone(facet);
                facet.restrictions = this.props.restrictions[facet.field];
                facet.terms = facet.terms.filter(term => _.contains(facet.restrictions, term.key));
            }
            return facet;
        }.bind(this));

        // See if a specific result type was requested ('type=x')
        // Satisfied iff exactly one type is in the search
        if (results.length) {
            var specificFilter;
            filters.forEach(function(filter) {
                if (filter.field === 'type') {
                    specificFilter = specificFilter ? '' : filter.term;
                }
            });
        }


        // Map view icons to svg icons
        var view2svg = {
            'table': 'table',
            'th': 'matrix'
        };

        return (
            <div>
                <div className="row">
                    {facets.length ? <div className="col-sm-5 col-md-4 col-lg-3">
                        <FacetList {...this.props} facets={facets} filters={filters}
                                    searchBase={searchBase ? searchBase + '&' : searchBase + '?'} onFilter={this.onFilter} />
                    </div> : ''}
                    <div className="col-sm-7 col-md-8 col-lg-9">
                        {context['notification'] === 'Success' ?
                            <div>
                                <h4>Showing {results.length} of {total} {label}</h4>

                                <div className="results-table-control">
                                    {context.views ?
                                        <div className="btn-attached">
                                            {context.views.map((view, i) =>
                                                <a key={i} className="btn btn-info btn-sm btn-svgicon" href={view.href} title={view.title}>{SvgIcon(view2svg[view.icon])}</a>
                                            )}
                                        </div>
                                    : null}

                                    {total > results.length && searchBase.indexOf('limit=all') === -1 ?
                                        <a rel="nofollow" className="btn btn-info btn-sm"
                                                href={searchBase ? searchBase + '&limit=all' : '?limit=all'}
                                                onClick={this.onFilter}>View All</a>
                                    :
                                        <span>
                                            {results.length > 25 ?
                                                <a className="btn btn-info btn-sm"
                                                    href={trimmedSearchBase ? trimmedSearchBase : "/search/"}
                                                    onClick={this.onFilter}>View 25</a>
                                            : null}
                                        </span>
                                    }

                                </div>
                            </div>
                        :
                            <h4>{context['notification']}</h4>
                        }
                        <hr />
                        <ul className="nav result-table" id="result-table">
                            {results.length ?
                                results.map(function (result) {
                                    return Listing({context:result, columns: columns, key: result['@id']});
                                })
                            : null}
                        </ul>
                    </div>
                </div>
            </div>
        );
    },

    onFilter: function(e) {
        var search = e.currentTarget.getAttribute('href');
        this.props.onChange(search);
        e.stopPropagation();
        e.preventDefault();
    }
});

var Search = search.Search = React.createClass({
    contextTypes: {
        location_href: React.PropTypes.string,
        navigate: React.PropTypes.func
    },

    render: function() {
        var context = this.props.context;
        var results = context['@graph'];
        var notification = context['notification'];
        var searchBase = url.parse(this.context.location_href).search || '';
        var facetdisplay = context.facets && context.facets.some(function(facet) {
            return facet.total > 0;
        });
        return (
            <div>
                {facetdisplay ?
                    <div className="panel data-display main-panel">
                        <ResultTable {...this.props} key={undefined} searchBase={searchBase} onChange={this.context.navigate} />
                    </div>
                : <h4>{notification}</h4>}
            </div>
        );
    }
});

globals.content_views.register(Search, 'Search');
