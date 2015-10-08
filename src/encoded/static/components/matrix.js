'use strict';
var React = require('react');
var globals = require('./globals');
var search = require('./search');
var url = require('url');
var _ = require('underscore');

var FacetList = search.FacetList;


var Matrix = module.exports.Matrix = React.createClass({

    contextTypes: {
        location_href: React.PropTypes.string,
        navigate: React.PropTypes.func
    },

    render: function() {
        var context = this.props.context;
        var searchBase = url.parse(this.context.location_href).search || '';
        var notification = context['notification'];
        if (context.matrix.y.buckets) {
            var x_facets = _.filter(context.facets, f => _.contains(context.matrix.x.facets, f.field));
            var y_facets = _.filter(context.facets, f => _.contains(context.matrix.y.facets, f.field));
            var x_buckets = context.matrix.x.buckets;
            var y_buckets = context.matrix.y.buckets;

            return (
                <div>
                    <header className="row">
                        <div className="col-sm-12">
                            <h2>{context.title}</h2>
                        </div>
                    </header>
                    <div className="panel data-display main-panel">
                        <div className="row">
                            <div className="col-sm-5 col-md-4 col-lg-3" style={{paddingRight: 0}}>
                                XXX add text filter
                            </div>
                            <div className="col-sm-7 col-md-8 col-lg-9" style={{paddingLeft: 0}}>
                                <FacetList facets={x_facets} filters={context.filters} orientation="horizontal"
                                           searchBase={searchBase ? searchBase + '&' : searchBase + '?'} onFilter={this.onFilter} />
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-sm-5 col-md-4 col-lg-3" style={{paddingRight: 0}}>
                                <FacetList facets={y_facets} filters={context.filters}
                                           searchBase={searchBase ? searchBase + '&' : searchBase + '?'} onFilter={this.onFilter} />
                            </div>
                            <div className="col-sm-7 col-md-8 col-lg-9" style={{paddingLeft: 0}}>
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
                                                <div><span>{context.matrix.y.label.toUpperCase()}</span></div>
                                            </th>
                                            <th style={{border: "solid 1px #ddd", textAlign: "center"}}><h3>{context.total} results</h3></th>
                                            {x_buckets.map(xb => <th className="rotate30"><div><span>{xb.key}</span></div></th>)}
                                            <th className="rotate30" style={{width: "40%"}}></th>
                                        </tr>
                                        {y_buckets.map(function(yb, i) {
                                            return <tr>
                                                <th style={{backgroundColor: "#ddd", border: "solid 1px white"}}>{yb.key}</th>
                                                {x_buckets.map(xb => <td style={{border: "solid 1px #f9f9f9"}}>{yb.x[xb.key] || ''}</td>)}
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
    }

});

globals.content_views.register(Matrix, 'Matrix');
