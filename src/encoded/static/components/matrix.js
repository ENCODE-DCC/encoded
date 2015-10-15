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
var MAX_Y_BUCKETS = 20;


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
        var batch_hub_disabled = context.total > 500;
        if (matrix.y.buckets) {
            var x_facets = _.filter(context.facets, f => _.contains(matrix.x.facets, f.field));
            var y_facets = _.filter(context.facets, f => _.contains(matrix.y.facets, f.field));
            var x_buckets = matrix.x.buckets;
            var y_buckets = matrix.y.buckets;
            // find max bucket count
            var max_count = _.max(y_buckets.map(yb => _.max(_.values(yb.x))));

            return (
                <div>
                    <div className="panel data-display main-panel">
                        <div className="row">
                            <div className="col-sm-5 col-md-4 col-lg-3" style={{paddingRight: 0}}>
                                <div className="row">
                                    <div className="col-sm-11">
                                        <h3>{context.title}</h3>
                                        <TextFilter filters={context.filters} searchBase={matrix_search} onChange={this.onChange} />
                                        {context.filters.length ?
                                            <div className="facet">
                                                <a href={parsed_url.pathname}><i className="icon icon-times-circle-o"></i> Clear all filters</a>
                                            </div>
                                        : ''}
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
                                            <th colSpan={Math.min(x_buckets.length, MAX_X_BUCKETS + 1) + 1}
                                                style={{padding: "5px", borderBottom: "solid 1px #ddd", textAlign: "center"}}>{matrix.x.label.toUpperCase()}</th>
                                        </tr>
                                        <tr style={{borderBottom: "solid 1px #ddd"}}>
                                            <th rowSpan={Math.min(y_buckets.length, MAX_Y_BUCKETS + 1) + 1}
                                                className="rotate90"
                                                style={{width: 25, borderRight: "solid 1px #ddd", borderBottom: "solid 2px transparent", padding: "5px"}}>
                                                <div style={{width: 15}}><span>{matrix.y.label.toUpperCase()}</span></div>
                                            </th>
                                            <th style={{border: "solid 1px #ddd", textAlign: "center", width: 200}}><h3>{matrix.doc_count} results</h3></th>
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
                                        {y_buckets.map(function(yb, j) {
                                            if (j < MAX_Y_BUCKETS) {
                                                return <tr>
                                                    <th style={{backgroundColor: "#ddd", border: "solid 1px white"}}>{yb.key}</th>
                                                    {x_buckets.map(function(xb, i) {
                                                        if (i < MAX_X_BUCKETS) {
                                                            var value = yb.x[xb.key];
                                                            var color = HIGHLIGHT_COLOR.clone();
                                                            // scale color between white and 60% lightness
                                                            color.lightness(60 + (1 - value / max_count) * 40);
                                                            var href = search_base + '&' + matrix.y.group_by + '=' + encodeURIComponent(yb.key)
                                                                                   + '&' + matrix.x.group_by + '=' + encodeURIComponent(xb.key);
                                                            return <td style={{backgroundColor: color.hexString()}}>
                                                                {value ? <a href={href} style={{color: '#000'}}>{value}</a> : ''}
                                                            </td>;
                                                        } else {
                                                            return null;
                                                        }
                                                    })}
                                                    {x_buckets.length > MAX_X_BUCKETS && <td></td>}
                                                </tr>;
                                            } else if (j == MAX_Y_BUCKETS) {
                                                return <tr>
                                                    <th style={{backgroundColor: "#ddd", border: "solid 1px white"}}>...and {y_buckets.length - MAX_Y_BUCKETS} more</th>
                                                    {_.range(Math.min(x_buckets.length, MAX_X_BUCKETS + 1)).map(n => <td></td>)}
                                                </tr>;
                                            } else {
                                                return null;
                                            }
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
