'use strict';
var React = require('react');
var color = require('color');
var svgIcon = require('../libs/svg-icons').svgIcon;
var globals = require('./globals');
var search = require('./search');
var url = require('url');
var _ = require('underscore');
var button = require('../libs/bootstrap/button');
var dropdownMenu = require('../libs/bootstrap/dropdown-menu');
var navbar = require('../libs/bootstrap/navbar');
var { BrowserSelector } = require('./objectutils');

var BatchDownload = search.BatchDownload;
var FacetList = search.FacetList;
var TextFilter = search.TextFilter;
var DropdownButton = button.DropdownButton;
var DropdownMenu = dropdownMenu.DropdownMenu;
var NavItem = navbar.NavItem;


var HIGHLIGHT_COLOR = color('#4e7294');
// 9-class pastel Brewer palette from http://colorbrewer2.org/
var COLORS = [
    '#fbb4ae',
    '#b3cde3',
    '#ccebc5',
    '#decbe4',
    '#fed9a6',
    '#ffffcc',
    '#e5d8bd',
    '#fddaec',
    '#f2f2f2'
];



const yGroupLimit = 5; // Maximum number of items in a Y group unless the group is opened.


const GroupMoreButton = React.createClass({
    propTypes: {
        id: React.PropTypes.string, // ID for the handleClick function to know which control was clicked
        handleClick: React.PropTypes.func, // Call this parent function to handle the click in the button
        displayText: React.PropTypes.string, // Text to display in the button while closed
    },

    localHandleClick: function () {
        this.props.handleClick(this.props.id);
    },

    render: function () {
        return <button className="group-more-button" onClick={this.localHandleClick}>{this.props.displayText}</button>;
    },
});


var Matrix = module.exports.Matrix = React.createClass({
    propTypes: {
        context: React.PropTypes.object,
    },

    contextTypes: {
        location_href: React.PropTypes.string,
        navigate: React.PropTypes.func,
        biosampleTypeColors: React.PropTypes.object // DataColor instance for experiment project
    },

    getInitialState: function () {
        // Make a state for each of the Y groups (each Y group currently shows a biosample type).
        // To do that, we have to get each of the bucket keys, which will be the keys into the
        // object that keeps track of whether the group shows all or not. If a group has fewer than
        // the maximum number of items to show a See More button, then it still get included here,
        // but with a value of `false` that never changes.
        const matrix = this.props.context.matrix;
        const primaryYGrouping = matrix.y.group_by[0];
        const yGroups = matrix.y[primaryYGrouping].buckets;
        const yGroupOpen = {};
        yGroups.forEach((group) => {
            yGroupOpen[group.key] = false;
        });
        return { yGroupOpen: yGroupOpen };
    },

    // Called when the Visualize button dropdown menu gets opened or closed. `dropdownEl` is the DOM node for the dropdown menu.
    // This sets inline CSS to set the height of the wrapper <div> to make room for the dropdown.
    updateElement: function(dropdownEl) {
        var wrapperEl = this.refs.hubscontrols.getDOMNode();
        var dropdownHeight = dropdownEl.clientHeight;
        if (dropdownHeight === 0) {
            // The dropdown menu has closed
            wrapperEl.style.height = 'auto';
        } else {
            // The menu has dropped down
            wrapperEl.style.height = wrapperEl.clientHeight + dropdownHeight + 'px';
        }
    },

    // Handle a click in a See More link within the matrix (not for the facets)
    handleClick: function (groupKey) {
        const groupOpen = _.clone(this.state.yGroupOpen);
        groupOpen[groupKey] = !groupOpen[groupKey];
        this.setState({ yGroupOpen: groupOpen });
    },

    render: function() {
        var context = this.props.context;
        var matrix = context.matrix;
        var parsed_url = url.parse(this.context.location_href);
        var matrix_base = parsed_url.search || '';
        var matrix_search = matrix_base + (matrix_base ? '&' : '?');
        var notification = context['notification'];
        const visualizeLimit = 500;
        if (context.notification == 'Success' || context.notification == 'No results found') {
            var x_facets = matrix.x.facets.map(f => _.findWhere(context.facets, {field: f})).filter(f => f);
            var y_facets = matrix.y.facets.map(f => _.findWhere(context.facets, {field: f})).filter(f => f);
            y_facets = y_facets.concat(_.reject(context.facets, f => _.contains(matrix.x.facets, f.field) || _.contains(matrix.y.facets, f.field)));
            var x_grouping = matrix.x.group_by;
            var primary_y_grouping = matrix.y.group_by[0];
            var secondary_y_grouping = matrix.y.group_by[1];
            var x_buckets = matrix.x.buckets;
            var x_limit = matrix.x.limit || x_buckets.length;
            var y_groups = matrix.y[primary_y_grouping].buckets;
            var y_limit = matrix.y.limit;
            var y_group_facet = _.findWhere(context.facets, {field: primary_y_grouping});
            var y_group_options = y_group_facet ? y_group_facet.terms.map(term => term.key) : [];
            y_group_options.sort();
            var search_base = context.matrix.search_base;
            var visualize_disabled = matrix.doc_count > visualizeLimit;

            var colCount = Math.min(x_buckets.length, x_limit + 1);
            var rowCount = y_groups.length ? y_groups.map(g => Math.min(g[secondary_y_grouping].buckets.length, y_limit ? y_limit + 1 : g[secondary_y_grouping].buckets.length) + 1).reduce((a, b) => a + b) : 0;

            // Get a sorted list of batch hubs keys with case-insensitive sort
            // NOTE: Tim thinks this is overkill as opposed to simple sort()
            var visualizeKeys = [];
            if (context.visualize_batch && Object.keys(context.visualize_batch).length) {
                visualizeKeys = Object.keys(context.visualize_batch).sort((a, b) => {
                    var aLower = a.toLowerCase();
                    var bLower = b.toLowerCase();
                    return (aLower > bLower) ? 1 : ((aLower < bLower) ? -1 : 0);
                });
            }

            // Map view icons to svg icons
            var view2svg = {
                'list-alt': 'search',
                'table': 'table'
            };

            // Make an array of colors corresponding to the ordering of biosample_type
            var biosampleTypeColors = this.context.biosampleTypeColors.colorList(y_groups.map(y_group => y_group.key));

            return (
                <div>
                    <div className="panel data-display main-panel">
                        <div className="row">
                            <div className="col-sm-5 col-md-4 col-lg-3 sm-no-padding" style={{paddingRight: 0}}>
                                <div className="row">
                                    <div className="col-sm-11">
                                        <div>
                                            <h3 style={{marginTop: 0}}>{context.title}</h3>
                                            <div>
                                                <p>Click or enter search terms to filter the experiments included in the matrix.</p>
                                                <TextFilter filters={context.filters} searchBase={matrix_search} onChange={this.onChange} />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-sm-7 col-md-8 col-lg-9 sm-no-padding" style={{paddingLeft: 0}}>
                                <FacetList facets={x_facets} filters={context.filters} orientation="horizontal"
                                           searchBase={matrix_search} onFilter={this.onFilter} />
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-sm-5 col-md-4 col-lg-3 sm-no-padding" style={{paddingRight: 0}}>
                                <FacetList facets={y_facets} filters={context.filters}
                                           searchBase={matrix_search} onFilter={this.onFilter} />
                            </div>
                            <div className="col-sm-7 col-md-8 col-lg-9 sm-no-padding">
                                <div className="matrix-wrapper">
                                    <div className="matrix-group-heading">
                                        <div className="matrix-group-heading__content">
                                            {matrix.y.label.toUpperCase()}
                                        </div>
                                    </div>
                                    <table className="matrix">
                                        <tbody>
                                            <tr style={{borderBottom: "solid 1px #ddd"}}>
                                                <th style={{ textAlign: 'center', width: 200 }}>
                                                    <h3>
                                                      {matrix.doc_count} results
                                                    </h3>
                                                    <div className="btn-attached">
                                                        {matrix.doc_count && context.views ? context.views.map(view => <a href={view.href} key={view.icon} className="btn btn-info btn-sm btn-svgicon" title={view.title}>{svgIcon(view2svg[view.icon])}</a>) : ''}
                                                    </div>
                                                    {context.filters.length ?
                                                        <div className="clear-filters-control-matrix">
                                                            <a href={context.matrix.clear_matrix}>Clear Filters <i className="icon icon-times-circle"></i></a>
                                                        </div>
                                                    : null}
                                                </th>
                                                {x_buckets.map(function(xb, i) {
                                                    if (i < x_limit) {
                                                        var href = search_base + '&' + x_grouping + '=' + globals.encodedURIComponent(xb.key);
                                                        return <th key={i} className="rotate30" style={{width: 10}}><div><a title={xb.key} href={href}>{xb.key}</a></div></th>;
                                                    } else if (i == x_limit) {
                                                        var parsed = url.parse(matrix_base, true);
                                                        parsed.query['x.limit'] = null;
                                                        delete parsed.search; // this makes format compose the search string out of the query object
                                                        var unlimited_href = url.format(parsed);
                                                        return <th key={i} className="rotate30" style={{width: 10}}><div><span><a href={unlimited_href}>...and {x_buckets.length - x_limit} more</a></span></div></th>;
                                                    } else {
                                                        return null;
                                                    }
                                                })}
                                            </tr>
                                            {y_groups.map((group, i) => {
                                                var seriesIndex = y_group_options.indexOf(group.key);
                                                var groupColor = biosampleTypeColors[i];
                                                var seriesColor = color(groupColor);
                                                var parsed = url.parse(matrix_base, true);
                                                parsed.query[primary_y_grouping] = group.key;
                                                parsed.query['y.limit'] = null;
                                                delete parsed.search; // this makes format compose the search string out of the query object
                                                var group_href = url.format(parsed);
                                                var rows = [<tr key={group.key}>
                                                    <th colSpan={colCount + 1} style={{textAlign: 'left', backgroundColor: groupColor}}>
                                                        <a href={group_href} style={{color: '#fff'}}>{group.key}</a>
                                                    </th>
                                                </tr>];
                                                var group_buckets = group[secondary_y_grouping].buckets;
                                                var y_limit = matrix.y.limit || group_buckets.length;

                                                // If this group isn't open (noted by
                                                // this.state.yGroupOpen[key]), extract just the
                                                // group rows that are under the display limit.
                                                const groupRows = this.state.yGroupOpen[group.key] ? group_buckets : group_buckets.slice(0, y_limit);
                                                rows.push.apply(rows, groupRows.map((yb, j) => {
                                                    var href = search_base + '&' + secondary_y_grouping + '=' + globals.encodedURIComponent(yb.key);
                                                    return (
                                                        <tr key={yb.key}>
                                                            <th style={{backgroundColor: "#ddd", border: "solid 1px white"}}><a href={href}>{yb.key}</a></th>
                                                            {x_buckets.map(function(xb, i) {
                                                                if (i < x_limit) {
                                                                    var value = yb[x_grouping][i];
                                                                    var color = seriesColor.clone();
                                                                    // scale color between white and the series color
                                                                    color.lightness(color.lightness() + (1 - value / matrix.max_cell_doc_count) * (100 - color.lightness()));
                                                                    let textColor = color.luminosity() > .5 ? '#000' : '#fff';
                                                                    var href = search_base + '&' + secondary_y_grouping + '=' + globals.encodedURIComponent(yb.key)
                                                                                        + '&' + x_grouping + '=' + globals.encodedURIComponent(xb.key);
                                                                    var title = yb.key + ' / ' + xb.key + ': ' + value;
                                                                    return <td key={xb.key} style={{backgroundColor: color.hexString()}}>
                                                                        {value ? <a href={href} style={{color: textColor}} title={title}>{value}</a> : ''}
                                                                    </td>;
                                                                } else {
                                                                    return null;
                                                                }
                                                            })}
                                                            {x_buckets.length > x_limit && <td></td>}
                                                        </tr>
                                                    );
                                                }));
                                                if (group_buckets.length > y_limit) {
                                                    rows.push(
                                                        <tr>
                                                            <th>
                                                                <GroupMoreButton
                                                                    id={group.key}
                                                                    handleClick={this.handleClick}
                                                                    displayText={this.state.yGroupOpen[group.key] ? '- See fewer' : `+ See ${group_buckets.length - y_limit} more…`}
                                                                />
                                                            </th>
                                                            {_.range(colCount - 1).map(n => <td key={n} />)}
                                                        </tr>
                                                    );
                                                }
                                                return rows;
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                                <div className="hubs-controls" ref="hubscontrols">
                                    {context['batch_download'] ?
                                        <BatchDownload context={context} />
                                    : null}
                                    {' '}
                                    {visualizeKeys.length ?
                                        <BrowserSelector
                                            visualizeCfg={context.visualize_batch}
                                            disabled={visualize_disabled}
                                            title={visualize_disabled ? 'Filter to ' + visualizeLimit + ' to visualize' : 'Visualize'}
                                        />
                                    : null}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            );
        } else {
            return <h4>{context.notification}</h4>;
        }
    },

    onFilter: function(e) {
        var search = e.currentTarget.getAttribute('href');
        this.context.navigate(search);
        e.stopPropagation();
        e.preventDefault();
    },

    onChange: function(href) {
        this.context.navigate(href);
    }

});

globals.content_views.register(Matrix, 'Matrix');
