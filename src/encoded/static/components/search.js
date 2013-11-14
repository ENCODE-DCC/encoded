/** @jsx React.DOM */
'use strict';
var React = require('react');
var url = require('url');
var globals = require('./globals');
var search = module.exports;

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
                    if(count == result_count) {
                        return <li>{id}<span className="pull-right">{count}</span></li>
                    }else {
                        return <li><a href={href_search+'&'+field+'='+id}>{id}<span className="pull-right">{count}</span></a></li>
                    }
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
                   if(count == result_count) {
                        return <li>{id}<span className="pull-right">{count}</span></li>
                    }else {
                        return <li><a href={href_search+'&'+field+'='+id}>{id}<span className="pull-right">{count}</span></a></li>
                    }
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
                <div>
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

            var resultsView = function(result) {
                var highlight = result['highlight'];
                switch (result['@type'][0]) {
                    case "biosample":
                        return <li className="post">
                                    <h4><a href={result['@id']}>{result['accession']}</a></h4>
                                    <div className="well">
                                        <strong>{columns['biosample_term_name']}</strong>: {result['biosample_term_name']}
                                        <span className="pull-right"><strong>{columns['biosample_type']}</strong>: {result['biosample_type']}</span><br />
                                        <strong>{columns['organism.name']}</strong>: {result['organism.name']}
                                        <span className="pull-right"><strong>{columns['source.title']}</strong>: {result['source.title']}</span><br />
                                        <strong>{columns['lab.title']}</strong>: {result['lab.title']}
                                    </div>
                            </li>
                        break;
                    case "experiment":
                        return <li className="post">
                                    <h4><a href={result['@id']}>{result['accession']}</a></h4>
                                    <div className="well">
                                        <strong>{columns['assay_term_name']}</strong>: {result['assay_term_name']}
                                        <span className="pull-right"><strong>{columns['target.label']}</strong>: {result['target.label']}</span><br />
                                        <strong>{columns['biosample_term_name']}</strong>: {result['biosample_term_name']}
                                        <span className="pull-right"><strong>{columns['lab.title']}</strong>: {result['lab.title']}</span><br />
                                        <strong>{columns['award.rfa']}</strong>: {result['award.rfa']}
                                    </div>
                            </li>
                        break;
                    case "antibody_approval":
                        return <li className="post">
                                    <h4><a href={result['@id']}>{result['antibody.accession']}</a></h4>
                                    <div className="well">
                                        <strong>{columns['target.label']}</strong>: {result['target.label']}
                                        <span className="pull-right"><strong>{columns['target.organism.name']}</strong>: {result['target.organism.name']}</span><br />
                                        <strong>{columns['antibody.source.title']}</strong>: {result['antibody.source.title']}
                                        <span className="pull-right"><strong>{columns['antibody.product_id']}</strong>: {result['antibody.product_id']}</span><br />
                                        <strong>{columns['antibody.lot_id']}</strong>: {result['antibody.lot_id']}
                                        <span className="pull-right"><strong>{columns['status']}</strong>: {result['status']}</span>
                                    </div>
                            </li>
                        break;
                    case "target":
                        return <li className="post">
                                    <h4><a href={result['@id']}>{result['label']}</a></h4>
                                    <div className="well">
                                        <strong>{columns['organism.name']}</strong>: {result['organism.name']}<br />
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
                                                    <a href={href_search+'&type=antibodies'}>Antibodies<span className="pull-right">{count['antibodies']}</span></a>
                                                </li>
                                            : null}
                                            {count['biosamples'] ?
                                                <li>
                                                    <a href={href_search+'&type=biosamples'}>Biosamples<span className="pull-right">{count['biosamples']}</span></a>
                                                </li>
                                            : null}
                                            {count['experiments'] ?
                                                <li>
                                                    <a href={href_search+'&type=experiments'}>Experiments<span className="pull-right">{count['experiments']}</span></a>
                                                </li>
                                            : null}
                                            {count['targets'] ?
                                                <li>
                                                    <a href={href_search+'&type=targets'}>Targets<span className="pull-right">{count['targets']}</span></a>
                                                </li>
                                            : null}
                                        </ul>
                                    </div>
                                    <div className="box">
                                        {facets.length ?
                                            this.transferPropsTo(<FacetBuilder />)
                                        :null }
                                    </div>
                                </div>
                                <div className="span8">
                                    <ul className="nav">
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
