'use strict';
var React = require('react');
var color = require('color');
var globals = require('./globals');
var search = require('./search');
var url = require('url');
var _ = require('underscore');
var button = require('../libs/bootstrap/button');
var dropdownMenu = require('../libs/bootstrap/dropdown-menu');

var BatchDownload = search.BatchDownload;
var FacetList = search.FacetList;
var TextFilter = search.TextFilter;
var DropdownButton = button.DropdownButton;
var DropdownMenu = dropdownMenu.DropdownMenu;


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
    '#f2f2f2',
];


var Matrix = module.exports.Matrix = React.createClass({

    contextTypes: {
        location_href: React.PropTypes.string,
        navigate: React.PropTypes.func
    },

    render: function() {
        var context = this.props.context;
        var matrix = context.matrix;
        var parsed_url = url.parse(this.context.location_href);
        var matrix_base = parsed_url.search || '';
        var matrix_search = matrix_base + (matrix_base ? '&' : '?');
        var notification = context['notification'];
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
            var search_base = context.matrix.search_base;
            var batch_hub_disabled = matrix.doc_count > 500;

            var colCount = Math.min(x_buckets.length, x_limit + 1);
            var rowCount = y_groups.length ? y_groups.map(g => Math.min(g[secondary_y_grouping].buckets.length, y_limit ? y_limit + 1 : g[secondary_y_grouping].buckets.length) + 1).reduce((a, b) => a + b) : 0;

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
                            <div className="col-sm-7 col-md-8 col-lg-9 sm-no-padding" style={{paddingLeft: 0, overflow: 'auto'}}>
                                <table className="matrix">
                                    <tbody>
                                        {matrix.doc_count ?
                                            <tr>
                                                <th style={{width: 20}}></th>
                                                <th colSpan={colCount + 1}
                                                    style={{padding: "5px", borderBottom: "solid 1px #ddd", textAlign: "center"}}>{matrix.x.label.toUpperCase()}</th>
                                            </tr>
                                        : ''}
                                        <tr style={{borderBottom: "solid 1px #ddd"}}>
                                            {matrix.doc_count ?
                                                <th rowSpan={rowCount + 1}
                                                    className="rotate90"
                                                    style={{width: 25, borderRight: "solid 1px #ddd", borderBottom: "solid 2px transparent", padding: "5px"}}>
                                                    <div style={{width: 15}}><span>{matrix.y.label.toUpperCase()}</span></div>
                                                </th>
                                            : ''}
                                            <th style={{border: "solid 1px #ddd", textAlign: "center", width: 200}}>
                                                <h3>
                                                  {matrix.doc_count} results 
                                                  {matrix.doc_count && context.views ? context.views.map(view => <span> <a href={view.href} title={view.title}><i className={'icon icon-' + view.icon}></i></a></span>) : ''}
                                                </h3>
                                                {context.filters.length ?
                                                    <a href={context.matrix.clear_matrix} className="btn btn-info btn-sm"><i className="icon icon-times-circle-o"></i> Clear all filters</a>
                                                : ''}
                                            </th>
                                            {x_buckets.map(function(xb, i) {
                                                if (i < x_limit) {
                                                    return <th className="rotate30" style={{width: 10}}><div><span title={xb.key}>{xb.key}</span></div></th>;
                                                } else if (i == x_limit) {
                                                    var parsed = url.parse(matrix_base, true);
                                                    parsed.query['x.limit'] = null;
                                                    delete parsed.search; // this makes format compose the search string out of the query object
                                                    var unlimited_href = url.format(parsed);
                                                    return <th className="rotate30" style={{width: 10}}><div><span><a href={unlimited_href}>...and {x_buckets.length - x_limit} more</a></span></div></th>;
                                                } else {
                                                    return null;
                                                }
                                            })}
                                        </tr>
                                        {y_groups.map(function(group, k) {
                                            var seriesColor = color(COLORS[k % COLORS.length]);
                                            var parsed = url.parse(matrix_base, true);
                                            parsed.query[primary_y_grouping] = group.key;
                                            parsed.query['y.limit'] = null;
                                            delete parsed.search; // this makes format compose the search string out of the query object
                                            var group_href = url.format(parsed);
                                            var rows = [<tr>
                                                <th colSpan={colCount + 1} style={{textAlign: 'left', backgroundColor: seriesColor.hexString()}}>
                                                    <a href={group_href} style={{color: '#000'}}>{group.key}</a>
                                                </th>
                                            </tr>];
                                            var group_buckets = group[secondary_y_grouping].buckets;
                                            var y_limit = matrix.y.limit || group_buckets.length;
                                            rows.push.apply(rows, group_buckets.map(function(yb, j) {
                                                if (j < y_limit) {
                                                    return <tr>
                                                        <th style={{backgroundColor: "#ddd", border: "solid 1px white"}}>{yb.key}</th>
                                                        {x_buckets.map(function(xb, i) {
                                                            if (i < x_limit) {
                                                                var value = yb[x_grouping][i];
                                                                var color = seriesColor.clone();
                                                                // scale color between white and the series color
                                                                color.lightness(color.lightness() + (1 - value / matrix.max_cell_doc_count) * (100 - color.lightness()));
                                                                var href = search_base + '&' + secondary_y_grouping + '=' + encodeURIComponent(yb.key)
                                                                                       + '&' + x_grouping + '=' + encodeURIComponent(xb.key);
                                                                var title = yb.key + ' / ' + xb.key + ': ' + value;
                                                                return <td style={{backgroundColor: color.hexString()}}>
                                                                    {value ? <a href={href} style={{color: '#000'}} title={title}>{value}</a> : ''}
                                                                </td>;
                                                            } else {
                                                                return null;
                                                            }
                                                        })}
                                                        {x_buckets.length > x_limit && <td></td>}
                                                    </tr>;
                                                } else if (j == y_limit) {
                                                    return <tr>
                                                        <th style={{backgroundColor: "#ddd", border: "solid 1px white"}}><a href={group_href}>...and {group_buckets.length - y_limit} more</a></th>
                                                        {_.range(colCount - 1).map(n => <td></td>)}
                                                    </tr>;
                                                } else {
                                                    return null;
                                                }
                                            }));
                                            return rows;
                                        })}
                                    </tbody>
                                    <tfoot>
                                        <tr>
                                            <th></th>
                                            <th colSpan={Math.min(x_buckets.length, x_limit + 1) + 1} style={{padding: "10px 0", textAlign: 'left'}}>
                                                {context['batch_download'] ?
                                                    <BatchDownload context={context} />
                                                : null}
                                                {' '}
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
                                            </th>
                                        </tr>
                                    </tfoot>
                                </table>
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
