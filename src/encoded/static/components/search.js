/** @jsx React.DOM */
'use strict';
var React = require('react');
var url = require('url');
var globals = require('./globals');
var search = module.exports;
var dbxref = require('./dbxref');
var DbxrefList = dbxref.DbxrefList;
var Dbxref = dbxref.Dbxref;

    var Listing = function (props) {
        // XXX not all panels have the same markup
        var context;
        if (props['@id']) {
            context = props;
            props = {context: context,  key: context['@id']};
        }
        return globals.listing_views.lookup(props.context)(props);
    };

    var Antibody = module.exports.Antibody = React.createClass({
        render: function() {
            var result = this.props.context;
            var columns = this.props.columns;
            return (<li>
                        <div>
                            <span className="pull-right type">Antibody: {' ' + result['antibody.accession']}</span>
                            <div className="accession">
                                <a href={result['@id']}>{result['target.label'] + ' (' + result['target.organism.name'] + ')'}</a> 
                            </div>
                        </div>
                        <div className="data-row"> 
                            <strong>{columns['antibody.source.title']}</strong>: {result['antibody.source.title']}<br />
                            <strong>{columns['antibody.product_id']}/{columns['antibody.lot_id']}</strong>: {result['antibody.product_id']} / {result['antibody.lot_id']}<br />
                            <strong>{columns['status']}</strong>: {result['status']}
                        </div>
                </li>
            );
        }
    });
    globals.listing_views.register(Antibody, 'antibody_approval');

    var Biosample = module.exports.Biosample = React.createClass({
        render: function() {
            var result = this.props.context;
            var columns = this.props.columns;
            return (<li>
                        <div>
                            <span className="pull-right type">Biosample: {' ' + result['accession']}</span>
                            <div className="accession">
                                <a href={result['@id']}>{result['biosample_term_name'] + ' (' + result['organism.name'] + ')'}</a> 
                            </div>
                        </div>
                        <div className="data-row">
                            <strong>{columns['biosample_type']}</strong>: {result['biosample_type']}<br />
                            <strong>{columns['source.title']}</strong>: {result['source.title']}
                            {result['life_stage'] ? <br /> : null}
                            {result['life_stage'] ? <strong>{columns['life_stage'] + ': '}</strong> :null}
                            {result['life_stage'] ? result['life_stage'] : null}
                        </div>
                </li>   
            );
        }
    });
    globals.listing_views.register(Biosample, 'biosample');

    var Experiment = module.exports.Experiment = React.createClass({
        render: function() {
            var result = this.props.context;
            var columns = this.props.columns;
            return (<li>
                        <div>
                            <span className="pull-right type">Experiment: {' ' + result['accession']}</span>
                            <div className="accession">
                                <a href={result['@id']}>{result['assay_term_name']+ ' of ' + result['biosample_term_name']}</a> 
                            </div>
                        </div>
                        <div className="data-row">
                            {result['target.label'] ? <strong>{columns['target.label'] + ': '}</strong>: null}
                            {result['target.label'] ? result['target.label'] : null}
                            {result['target.label'] ? <br /> : null}
                            <strong>{columns['lab.title']}</strong>: {result['lab.title']}<br />
                            <strong>{columns['award.rfa']}</strong>: {result['award.rfa']}
                        </div>
                </li>
            );
        }
    });
    globals.listing_views.register(Experiment, 'experiment');

    var Target = module.exports.Target = React.createClass({
        render: function() {
            var result = this.props.context;
            var columns = this.props.columns;
            return (<li>
                        <div>
                            <span className="pull-right type">Target</span>
                            <div className="accession">
                                <a href={result['@id']}>{result['label'] + ' (' + result['organism.name'] + ')'}</a> 
                            </div>
                        </div>
                        <div className="data-row">
                            <strong>{columns['dbxref']}</strong>: 
                            {result.dbxref.length ?
                                <DbxrefList values={result.dbxref} target_gene={result.gene_name} />
                                : <em>None submitted</em> }
                        </div>
                </li>
            );
        }
    });
    globals.listing_views.register(Target, 'target');

    var FacetBuilder = search.FacetBuilder = React.createClass({
        render: function() {
            var context = this.props.context;
            var result_count = context['@graph'].length;
            var facets = context['facets'];
            var href_search = url.parse(this.props.href).search || '';
            var counter, counter1 = 0;
            var field = '';
            var buildTerms = function(map) {
                var id;
                var count;
                counter = counter + 1;
                for (var j in map) {
                    id = j;
                    count = map[j];
                }
                if(counter < 4) {
                    return <li><a href={href_search+'&'+field+'='+id}>{id}<span className="pull-right">{count}</span></a></li>
                } 
            };
            var buildCollapsingTerms = function(map) {
                var id;
                var count;
                counter1 = counter1 + 1;
                for (var j in map) {
                    id = j;
                    count = map[j];
                }
                if (counter1 >= 4) {
                    return <li><a href={href_search+'&'+field+'='+id}>{id}<span className="pull-right">{count}</span></a></li>
                }
            };
            var buildSection = function(facet) {
                counter = 0;
                counter1 = 0;
                var termID = '';
                var terms = [];
                var term = '';
                for (var f in facet) {
                    if(f  != 'field') {
                        term = f;
                        termID = f.replace(/\s+/g, '');
                        terms = facet[f];
                    } else {
                        field = facet[f];
                    }
                }
                return <div className="facet">
                        <h5>{term}</h5>
                        <ul className="facet-list nav">
                            <div>
                                {terms.length ?
                                    terms.map(buildTerms)
                                : null}
                            </div>
                            {terms.length > 3 ?
                                <div id={termID} className="collapse">
                                    {terms.length ?
                                        terms.map(buildCollapsingTerms)
                                    : null}
                                </div>
                            : null}
                            {terms.length > 3 ?
                                <label className="pull-right">
                                        <small>
                                            <button type="button" className="btn btn-link collapsed" data-toggle="collapse" data-target={'#'+termID} />
                                        </small>
                                </label>
                            : null}
                        </ul>
                    </div>
            };
            return (
                <div className="box facets">
                    {facets.length ?
                        facets.map(buildSection)
                    : null}
                </div>
            );
        }
    });
    
    var ResultTable = search.ResultTable = React.createClass({
        render: function() {
            var context = this.props.context;
            var results = context['@graph'];
            var href_search = url.parse(this.props.href).search || '';
            var facets = context['facets'];
            var count = context['count'];
            var columns = context['columns'];
            var filters = context['filters'];
            var search_id = context['@id']

            var unfacetButtons = function(filter) {
                for (var key in filter) {
                    var unfacet_url = '';
                    var args = href_search.split('&');
                    for(var prop in args) {
                        if(args[prop].indexOf(key) !== -1) {
                            unfacet_url = '&' + unfacet_url + args[prop]
                        }
                    }
                    var url_unfacet = href_search.replace(unfacet_url, "");
                    return <a className="btn btn-small btn-info" href={url_unfacet}>{filter[key] + ' '}<i className="icon-remove-sign"></i></a>
                }
            };
            return (
                    <div>
                        {results.length ?
                            <div className="row">
                                <div className="span3">
                                    <div>
                                        <ul className="nav nav-tabs nav-stacked">
                                            {search_id.indexOf("type=antibody_approval") > 0 ?
                                                <li><a href={search_id.replace("type=antibody_approval", "")}>Antibodies<span className="pull-right"><i className="icon-remove-sign"></i></span></a></li>
                                            : (count['antibodies'] ? 
                                                    <li><a href={search_id+'&type=antibody_approval'}>Antibodies<span className="pull-right">{count['antibodies']}</span></a></li> 
                                                : null)
                                            }
                                            
                                            {search_id.indexOf("type=biosample") > 0 ?
                                                <li><a href={search_id.replace("type=biosample", "")}>Biosamples<span className="pull-right"><i className="icon-remove-sign"></i></span></a></li>
                                            : (count['biosamples'] ?
                                                    <li><a href={search_id+'&type=biosample'}>Biosamples<span className="pull-right">{count['biosamples']}</span></a></li>
                                                : null)
                                            }
                                            
                                            {search_id.indexOf("type=experiment") > 0 ?
                                                <li><a href={search_id.replace("type=experiment", "")}>Experiments<span className="pull-right"><i className="icon-remove-sign"></i></span></a></li>
                                            : (count['experiments'] ?
                                                    <li><a href={search_id+'&type=experiment'}>Experiments<span className="pull-right">{count['experiments']}</span></a></li>
                                                : null)
                                            }
                                            
                                            {search_id.indexOf("type=target") > 0 ?
                                                <li><a href={search_id.replace("type=target", "")}>Targets<span className="pull-right"><i className="icon-remove-sign"></i></span></a></li>
                                            : (count['targets'] ?
                                                    <li><a href={search_id+'&type=target'}>Targets<span className="pull-right">{count['targets']}</span></a></li>
                                                : null)
                                            }
                                        </ul>
                                    </div>
                                    {facets.length ?
                                        this.transferPropsTo(<FacetBuilder />)
                                    :null}
                                </div>

                                <div className="span8">
                                    <h4>Showing {results.length} of {(count['antibodies'] ? parseInt(count['antibodies']) : 0) + 
                                            (count['biosamples'] ? parseInt(count['biosamples']) : 0) + 
                                            (count['targets'] ? parseInt(count['targets']) : 0) + 
                                            (count['experiments'] ? parseInt(count['experiments']) : 0)}
                                            {((count['antibodies'] ? parseInt(count['antibodies']) : 0) + 
                                                (count['biosamples'] ? parseInt(count['biosamples']) : 0) + 
                                                (count['targets'] ? parseInt(count['targets']) : 0) + 
                                                (count['experiments'] ? parseInt(count['experiments']) : 0)) > 100 ?
                                                <span className="pull-right">
                                                    {search_id.indexOf('&limit=all') !== -1 ? 
                                                        <a className="btn btn-info btn-small" href={search_id.replace("&limit=all", "")}>View 100</a>
                                                    : <a className="btn btn-info btn-small" href={search_id+ '&limit=all'}>View All</a>}
                                                </span>
                                            : null }
                                    </h4>
                                            
                                           
                                    {filters.length ?
                                        <div className="btn-group"> 
                                            {filters.map(unfacetButtons)}
                                        </div>
                                    : null}
                                    <hr />
                                    <ul className="nav result-table">
                                        {results.length ?
                                            results.map(function (result) {
                                                return Listing({context:result, columns: columns});
                                            })
                                        : null}
                                    </ul>
                                </div>
                            </div>
                        : null }
                    </div>  
                );
            }
        }
    );


    var Search = search.Search = React.createClass({
        clearFilter: function (event) {
            this.refs.searchTerm.getDOMNode().value = '';
            this.submitTimer = setTimeout(this.submit);
        }, 
        render: function() {
            var context = this.props.context;
            var results = context['@graph'];
            var notification = context['notification']
            var id = url.parse(this.props.href, true);
            var searchTerm = id.query['searchTerm'] || '';
            return (
                <div>
                    <div className="three-d-box">
                        <form className="input-prepend">
                            <input id='inputValidate' className="input-lg" type="text" placeholder="Search examples: skin, &quot;len pennacchio&quot;, chip-seq etc" 
                                ref="searchTerm" name="searchTerm" defaultValue={searchTerm} />
                        </form>
                    </div>
                    {notification === 'Success' ?
                        <div className="panel data-display"> 
                            {this.transferPropsTo(<ResultTable />)}
                        </div>
                    : <h4>{notification}</h4>}
                </div>
            );
        }
    });

    globals.content_views.register(Search, 'search');
