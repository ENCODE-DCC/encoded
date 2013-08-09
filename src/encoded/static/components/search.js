/** @jsx React.DOM */
define(['exports', 'jquery', 'react', 'globals'],
function (search, $, React, globals) {
    'use strict';

    var FacetBuilder = search.FacetBuilder = React.createClass({
        render: function() {
            var context = this.props.context;
            var facets = context['@graph']['facets'];
            var terms = [];
            var url = (this.props.location)['search'];
            for (var i in facets) {
                terms.push(i);
            }
            var buildTerms = function(map) {
                console.log(map);
                var id;
                var count;
                var field;
                for (var j in map) {
                    if(j == "field") {
                        field = map[j];
                    }else {
                        id = j;
                        count = map[j];
                    }
                }
                return <li>
                        <span class="badge pull-right">{count}</span>
                        <a href = {'/search'+url+'&'+field+'='+id}><small>{id}</small></a>
                    </li>
            };
            var buildSection = function(term) {
                return <div>
                            <legend><small>{term}</small></legend>
                            <ul class="facet-list">
                                {facets[term].length ?
                                    facets[term].map(buildTerms)
                                : null}
                            </ul>
                        </div>
            };
            return (
                <div>
                    {Object.keys(facets).length ?
                        terms.map(buildSection)
                    : null}
                </div>
            );
        }
    });

    var ResultTable = search.ResultTable = React.createClass({
        render: function() {
            var context = this.props.context;
            var results = context['@graph'];
            var url = (this.props.location)['search'];
            var resultsView = function(result) {
                switch (result['@type'][0]) {
                    case "biosample":
                        return <li>
                                <h6>Biosample</h6>
                                <div>
                                    <h4><a href={result['@id']}>{result['accession']}</a></h4>
                                    <i>{result['biosample_term_name']} - {result['biosample_term_id']} - {result['lab']['name']}</i>
                                </div>
                                <hr></hr>
                            </li>
                        break;
                    case "experiment":
                        return <li>
                                <h6>Experiment</h6>
                                <div>
                                    <h4><a href={result['@id']}>{result['accession']}</a></h4>
                                    <i>{result['description']} - {result['assay_term_name']} - {result['lab']['title']}</i>
                                </div>
                                <hr></hr>
                            </li>
                        break;
                    case "antibody_approval":
                        return <li>
                                <h6>Antibody</h6>
                                <div>
                                    <h4><a href={result['@id']}>{result['antibody']['accession']}</a></h4>
                                    <i>{result['target']['name']} - {result['target']['lab']['title']}</i>
                                </div>
                                <hr></hr>
                            </li>
                        break;
                    case "target":
                        return <li>
                                <h6>Target</h6>
                                <div>
                                    <h4><a href={result['@id']}>{result['name']}</a></h4>
                                    <i>{result['organism']['name']} - {result['lab']['title']}</i>
                                </div>
                                <hr></hr>
                            </li>
                        break;
                }
            };  
            return (
                <div class="panel data-display">
                    <div class="row">
                        <div class="span3" id="facets">
                            <h4>Filter Results</h4>
                            <section class="facet wel box">
                                <div>
                                    <legend><small>Data Type</small></legend>
                                    <ul class="facet-list">
                                        {results['count']['antibodies'] ?
                                            <li>
                                                <span class="badge pull-right">{results['count']['antibodies']}</span>
                                                <a href={'/search'+ url+'&type=antibodies'}><small>Antibodies</small></a>
                                            </li>
                                        : null}
                                        {results['count']['biosamples'] ?
                                            <li>
                                                <span class="badge pull-right">{results['count']['biosamples']}</span>
                                                <a href={'/search'+ url+'&type=biosamples'}><small>Biosamples</small></a>
                                            </li>
                                        : null}
                                        {results['count']['experiments'] ?
                                            <li>
                                                <span class="badge pull-right">{results['count']['experiments']}</span>
                                                <a href={'/search'+ url+'&type=experiments'}><small>Experiments</small></a>
                                            </li>
                                        : null}
                                        {results['count']['targets'] ?
                                            <li>
                                                <span class="badge pull-right">{results['count']['targets']}</span>
                                                <a href={'/search'+ url+'&type=targets'}><small>Targets</small></a>
                                            </li>
                                        : null}
                                    </ul>
                                </div>
                                {Object.keys(results['facets']).length ?
                                    <FacetBuilder location={this.props.location} context={this.props.context} />
                                :null }
                            </section>
                        </div>
                        <div class="span8">
                            <legend>{results['results'].length} Results Found</legend>
                            <ul class="nav nav-tabs nav-stacked">
                                {results['results'].length ?
                                    results['results'].map(resultsView)
                                : null}
                            </ul>
                        </div>
                    </div>
                </div>
            );
        }
    });

    var Search = search.Search = React.createClass({
        getInitialState: function() {
            return {items: [], text: ''};
        },
        render: function() {
            var context = this.props.context;
            var results = context['@graph'];
            return (
                <div >
                    <form class="input-prepend">
                        <span class="add-on"><i class="icon-search"></i></span>
                        <input class="input-xxlarge" type="text" placeholder="Search ENCODE" name="searchTerm" defaultValue={this.state.text} />
                    </form>
                    {Object.keys(results).length ?
                        <ResultTable location={this.props.location} context={this.props.context} />
                    :null }
                </div>
            );
        }
    });

    globals.content_views.register(Search, 'search');
    return search;
});
