'use strict';
var React = require('react');
var color = require('color');
var globals = require('./globals');
var search = require('./search');
var url = require('url');
var _ = require('underscore');

var BatchDownload = search.BatchDownload;
var FacetList = search.FacetList;
var TextFilter = search.TextFilter;


var HIGHLIGHT_COLOR = color('#4e7294');
var MAX_X_BUCKETS = 20;
var Y_BUCKETS_PER_GROUP = 5;
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
        var matrix_search = parsed_url.search || '';
        matrix_search += matrix_search ? '&' : '?';
        var search_base = context.matrix.search_base;
        var notification = context['notification'];
        var batch_hub_disabled = matrix.doc_count > 500;
        if (context.notification == 'Success') {
            var x_facets = _.filter(context.facets, f => _.contains(matrix.x.facets, f.field));
            var y_facets = _.filter(context.facets, f => _.contains(matrix.y.facets, f.field));
            var x_grouping = matrix.x.group_by;
            var primary_y_grouping = matrix.y.group_by[0];
            var secondary_y_grouping = matrix.y.group_by[1];
            var x_buckets = matrix.x.buckets;
            var y_groups = matrix.y[primary_y_grouping].buckets;

            var colCount = Math.min(x_buckets.length, MAX_X_BUCKETS + 1);
            var rowCount;
            if (y_groups.length > 1) {
                rowCount = y_groups.map(g => Math.min(g[secondary_y_grouping].buckets.length, Y_BUCKETS_PER_GROUP + 1) + 1).reduce((a, b) => a + b);
            } else {
                rowCount = y_groups[0][secondary_y_grouping].buckets.length + 1;
            }

            return (
                <div>
                    <div className="panel data-display main-panel">
                        <div className="row">
                            <div className="col-sm-5 col-md-4 col-lg-3" style={{paddingRight: 0}}>
                                <div className="row">
                                    <div className="col-sm-11">
                                        <div>
                                            <h3 style={{marginTop: 0}}>{context.title}</h3>
                                            <p>Click or enter search terms to filter the experiments included in the matrix.</p>
                                            <TextFilter filters={context.filters} searchBase={matrix_search} onChange={this.onChange} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-sm-7 col-md-8 col-lg-9" style={{paddingLeft: 0}}>
                                <FacetList facets={x_facets} filters={context.filters} orientation="horizontal"
                                           searchBase={matrix_search} onFilter={this.onFilter} />
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-sm-5 col-md-4 col-lg-3" style={{paddingRight: 0}}>
                                <FacetList facets={y_facets} filters={context.filters}
                                           searchBase={matrix_search} onFilter={this.onFilter} />
                            </div>
                            <div className="col-sm-7 col-md-8 col-lg-9" style={{paddingLeft: 0, overflow: 'auto'}}>
                                <table className="matrix">
                                    <tbody>
                                        <tr>
                                            <th style={{width: 20}}></th>
                                            <th colSpan={colCount + 1}
                                                style={{padding: "5px", borderBottom: "solid 1px #ddd", textAlign: "center"}}>{matrix.x.label.toUpperCase()}</th>
                                        </tr>
                                        <tr style={{borderBottom: "solid 1px #ddd"}}>
                                            <th rowSpan={rowCount + 1}
                                                className="rotate90"
                                                style={{width: 25, borderRight: "solid 1px #ddd", borderBottom: "solid 2px transparent", padding: "5px"}}>
                                                <div style={{width: 15}}><span>{matrix.y.label.toUpperCase()}</span></div>
                                            </th>
                                            <th style={{border: "solid 1px #ddd", textAlign: "center", width: 200}}>
                                                <h3>{matrix.doc_count} results</h3>
                                                {context.filters.length ?
                                                    <a href={parsed_url.pathname} className="btn btn-info btn-sm"><i className="icon icon-times-circle-o"></i> Clear all filters</a>
                                                : ''}
                                            </th>
                                            {x_buckets.map(function(xb, i) {
                                                if (i < MAX_X_BUCKETS) {
                                                    return <th className="rotate30" style={{width: 10}}><div><span title={xb.key}>{xb.key}</span></div></th>;
                                                } else if (i == MAX_X_BUCKETS) {
                                                    return <th className="rotate30" style={{width: 10}}><div><span>...and {x_buckets.length - MAX_X_BUCKETS} more</span></div></th>;
                                                } else {
                                                    return null;
                                                }
                                            })}
                                        </tr>
                                        {y_groups.map(function(group, k) {
                                            var seriesColor = color(COLORS[k % COLORS.length]);
                                            var rows = [<tr>
                                                <th colSpan={colCount + 1} style={{textAlign: 'left', backgroundColor: seriesColor.hexString()}}>{group.key} ({group.doc_count})</th>
                                            </tr>];
                                            var group_buckets = group[secondary_y_grouping].buckets;
                                            rows.push.apply(rows, group_buckets.map(function(yb, j) {
                                                if (y_groups.length > 1 && j < Y_BUCKETS_PER_GROUP) {
                                                    return <tr>
                                                        <th style={{backgroundColor: "#ddd", border: "solid 1px white"}}>{yb.key}</th>
                                                        {x_buckets.map(function(xb, i) {
                                                            if (i < MAX_X_BUCKETS) {
                                                                var value = yb[x_grouping][xb.key];
                                                                var color = seriesColor.clone();
                                                                // scale color between white and 60% lightness
                                                                color.lightness(60 + (1 - value / matrix.max_cell_doc_count) * 40);
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
                                                        {x_buckets.length > MAX_X_BUCKETS && <td></td>}
                                                    </tr>;
                                                } else if (j == Y_BUCKETS_PER_GROUP) {
                                                    return <tr>
                                                        <th style={{backgroundColor: "#ddd", border: "solid 1px white"}}>...and {group_buckets.length - Y_BUCKETS_PER_GROUP} more</th>
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
                                            <th colSpan={Math.min(x_buckets.length, MAX_X_BUCKETS + 1) + 1} style={{padding: "10px 0", textAlign: 'left'}}>
                                                {context['batch_download'] ?
                                                    <BatchDownload context={context} />
                                                : null}
                                                {' '}
                                                {context['batch_hub'] ?
                                                    <a disabled={batch_hub_disabled} data-bypass="true" target="_blank" private-browsing="true" className="btn btn-info btn-sm"
                                                       href={context['batch_hub']}>{batch_hub_disabled ? 'Filter to 500 to visualize' :'Visualize'}</a>
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
