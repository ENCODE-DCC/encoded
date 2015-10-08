'use strict';
var React = require('react');
var color = require('color');
var globals = require('./globals');
var search = require('./search');
var url = require('url');
var _ = require('underscore');

var FacetList = search.FacetList;
var TextFilter = search.TextFilter;


var HIGHLIGHT_COLOR = color('#4e7294');


var Matrix = module.exports.Matrix = React.createClass({

    contextTypes: {
        location_href: React.PropTypes.string,
        navigate: React.PropTypes.func
    },

    render: function() {
        var context = this.props.context;
        var parsed_url = url.parse(this.context.location_href);
        var searchBase = parsed_url.search || '';
        searchBase = searchBase ? searchBase + '&' : searchBase + '?';
        var notification = context['notification'];
        if (context.matrix.y.buckets) {
            var x_facets = _.filter(context.facets, f => _.contains(context.matrix.x.facets, f.field));
            var y_facets = _.filter(context.facets, f => _.contains(context.matrix.y.facets, f.field));
            var x_buckets = context.matrix.x.buckets;
            var y_buckets = context.matrix.y.buckets;
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
                                        <TextFilter filters={context.filters} searchBase={searchBase} onChange={this.onChange} />
                                        {context.filters.length ? <a href={parsed_url.pathname}>
                                            <i className="icon icon-times-circle-o"></i> Clear all filters
                                        </a> : ''}
                                    </div>
                                </div>
                            </div>
                            <div className="col-sm-7 col-md-8 col-lg-9" style={{paddingLeft: 0}}>
                                <FacetList facets={x_facets} filters={context.filters} orientation="horizontal"
                                           searchBase={searchBase} onFilter={this.onFilter} />
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-sm-5 col-md-4 col-lg-3" style={{paddingRight: 0}}>
                                <FacetList facets={y_facets} filters={context.filters}
                                           searchBase={searchBase} onFilter={this.onFilter} />
                            </div>
                            <div className="col-sm-7 col-md-8 col-lg-9" style={{paddingLeft: 0, overflow: 'auto'}}>
                                <table className="matrix">
                                    <tbody>
                                        <tr>
                                            <th style={{width: 20}}></th>
                                            <th colSpan={x_buckets.length + 2}
                                                style={{padding: "5px", borderBottom: "solid 1px #ddd", textAlign: "center"}}>{context.matrix.x.label.toUpperCase()}</th>
                                        </tr>
                                        <tr style={{borderBottom: "solid 1px #ddd"}}>
                                            <th rowSpan={y_buckets.length + 1}
                                                className="rotate90"
                                                style={{width: 25, borderRight: "solid 1px #ddd", borderBottom: "solid 2px transparent", padding: "5px"}}>
                                                <div style={{width: 15}}><span>{context.matrix.y.label.toUpperCase()}</span></div>
                                            </th>
                                            <th style={{border: "solid 1px #ddd", textAlign: "center"}}><h3>{context.matrix.doc_count} results</h3></th>
                                            {x_buckets.map(xb => <th className="rotate30"><div><span>{xb.key}</span></div></th>)}
                                            <th className="rotate30" style={{width: "20%"}}></th>
                                        </tr>
                                        {y_buckets.map(function(yb, i) {
                                            return <tr>
                                                <th style={{backgroundColor: "#ddd", border: "solid 1px white"}}>{yb.key}</th>
                                                {x_buckets.map(function(xb) {
                                                    var value = yb.x[xb.key];
                                                    var color = HIGHLIGHT_COLOR.clone();
                                                    // scale color between white and 60% lightness
                                                    color.lightness(60 + (1 - value / max_count) * 40);
                                                    return <td style={{border: "solid 1px #f9f9f9", backgroundColor: color.hexString()}}>{value || ''}</td>;
                                                })}
                                                <td></td>
                                            </tr>;
                                        })}
                                    </tbody>
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
