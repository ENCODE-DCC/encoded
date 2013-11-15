/** @jsx React.DOM */
'use strict';
var React = require('react');
var url = require('url');
var globals = require('./globals');
var search = module.exports;
var dbxref = require('./dbxref');

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
                if(terms.length == 1) {
                    return
                }
                return <div>
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
                        <hr />
                    </div>
            };
            return (
                <div className="box">
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

            var unfacetButtons = function(filter) {
                for (var key in filter) {
                    return <a className="btn btn-small btn-success" href="#">{filter[key]} <i className="icon-remove"></i></a>
                }
            };
            var resultsView = function(result) {
                var highlight = result['highlight'];
                switch (result['@type'][0]) {
                    case "biosample":
                        return <li>
                                    <div className="accession">
                                        <span className="pull-right">Biosample - {result['organism.name']}</span>
                                        <a href={result['@id']}>{result['accession']}</a>
                                    </div>
                                    <div className="data-row">
                                        <strong>{columns['biosample_term_name']}</strong>: {result['biosample_term_name']}<br />
                                        <strong>{columns['biosample_type']}</strong>: {result['biosample_type']}<br />
                                        <strong>{columns['source.title']}</strong>: {result['source.title']}<br />
                                        <strong>{columns['lab.title']}</strong>: {result['lab.title']}
                                    </div>
                            </li>
                        break;
                    case "experiment":
                        return <li>
                                    <div className="accession">
                                        <span className="pull-right">Experiment - {result['assay_term_name']}</span>
                                        <a href={result['@id']}>{result['accession']}</a>
                                    </div>
                                    <div className="data-row">
                                        <strong>{columns['biosample_term_name']}</strong>: {result['biosample_term_name']}<br />
                                        <strong>{columns['lab.title']}</strong>: {result['lab.title']}<br />
                                        <strong>{columns['award.rfa']}</strong>: {result['award.rfa']}
                                    </div>
                            </li>
                        break;
                    case "antibody_approval":
                        return <li>
                                    <div className="accession">
                                        <span className="pull-right">Antibody - {result['target.organism.name']}</span>
                                        <a href={result['@id']}>{result['antibody.accession']}</a>
                                    </div>
                                    <div className="data-row"> 
                                        <strong>{columns['target.label']}</strong>: {result['target.label']}<br />
                                        <strong>{columns['antibody.source.title']}</strong>: {result['antibody.source.title']}<br />
                                        <strong>{columns['antibody.product_id']}/{columns['antibody.lot_id']}</strong>: {result['antibody.product_id']} / {result['antibody.lot_id']}<br />
                                        <strong>{columns['status']}</strong>: {result['status']}
                                    </div>
                            </li>
                        break;
                    case "target":
                        return <li>
                                    <div className="accession">
                                        <span className="pull-right">Target - {result['organism.name']}</span>
                                        <a href={result['@id']}>{result['label']}</a>
                                    </div>
                                    <div className="data-row">
                                        <strong>{columns['dbxref']}</strong>: {result['dbxref']}
                                    </div>
                            </li>
                        break;
                }
            };  
            return (
                    <div>
                        {results.length ?
                            <div className="row">
                                <div className="span3">
                                    <div>
                                        <ul className="nav nav-tabs nav-stacked">
                                            {count['antibodies'] ?
                                                <li>
                                                    <a href={href_search+'&type=antibody_approval'}>Antibodies<span className="pull-right">{count['antibodies']}</span></a>
                                                </li>
                                            : null}
                                            {count['biosamples'] ?
                                                <li>
                                                    <a href={href_search+'&type=biosample'}>Biosample<span className="pull-right">{count['biosamples']}</span></a>
                                                </li>
                                            : null}
                                            {count['experiments'] ?
                                                <li>
                                                    <a href={href_search+'&type=experiment'}>Experiments<span className="pull-right">{count['experiments']}</span></a>
                                                </li>
                                            : null}
                                            {count['targets'] ?
                                                <li>
                                                    <a href={href_search+'&type=target'}>Targets<span className="pull-right">{count['targets']}</span></a>
                                                </li>
                                            : null}
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
                                            (count['experiments'] ? parseInt(count['experiments']) : 0)}</h4>
                                    <div className="btn-group">        
                                        {filters.length ?
                                            filters.map(unfacetButtons)
                                        : null}
                                    </div>
                                    <hr />
                                    <ul className="nav result-table">
                                        {results.length ?
                                            results.map(resultsView)
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
        getInitialState: function() {
            return {items: [], text: ''};
        },
        render: function() {
            var context = this.props.context;
            var results = context['@graph'];
            return (
                <div>
                    <form className="input-prepend">
                        <span className="add-on"><i className="icon-search"></i></span>
                        <input id='inputValidate' className="input-xxlarge" type="text" placeholder="Search ENCODE" name="searchTerm" defaultValue={this.state.text} />
                    </form>
                    <div className="panel data-display"> 
                        {Object.keys(results).length ?
                            this.transferPropsTo(<ResultTable />)
                        : <h4>Please enter a search term </h4>}
                    </div>
                </div>
            );
        }
    });

    globals.content_views.register(Search, 'search');
