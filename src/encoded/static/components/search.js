/** @jsx React.DOM */
define(['exports', 'jquery', 'react', 'globals'],
function (search, $, React, globals) {
    'use strict';

    var ResultTable = search.ResultTable = React.createClass({
        render: function() {
            var results = this.props.context.items;
            var url = (this.props.location)['search'];
            console.log(location);
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
                                    <h4><a href={result['@id']}>{result['dataset_accession']}</a></h4>
                                    <i>{result['dataset_description']} - {result['lab']['name']}</i>
                                </div>
                                <hr></hr>
                            </li>
                        break;
                    case "antibody_approval":
                        return <li>
                                <h6>Antibody</h6>
                                <div>
                                    <h4><a href={result['@id']}>{result['antibody_lot']['antibody_accession']}</a></h4>
                                    <i>{result['target']['target_label']} - {result['target']['organism']['organism_name']} - {result['target']['lab']['name']}</i>
                                </div>
                                <hr></hr>
                            </li>
                        break;
                    case "target":
                        return <li>
                                <h6>Target</h6>
                                <div>
                                    <h4><a href={result['@id']}>{result['target_label']}</a></h4>
                                    <i>{result['organism']['organism_name']} - {result['lab']['name']}</i>
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
                                <h4>Data Type</h4>
                                <ul class="facet-list">
                                    {results['count']['antibodies'] ?
                                        <li>
                                            <span class="badge pull-right">{results['count']['antibodies']}</span>
                                            <a href={'/search'+ url+'&index=antibodies'}>Antibodies</a>
                                        </li>
                                    : null}
                                    {results['count']['biosamples'] ?
                                        <li>
                                            <span class="badge pull-right">{results['count']['biosamples']}</span>
                                            <a href={'/search'+ url+'&index=biosamples'}>Biosamples</a>
                                        </li>
                                    : null}
                                    {results['count']['experiments'] ?
                                        <li>
                                            <span class="badge pull-right">{results['count']['experiments']}</span>
                                            <a href={'/search'+ url+'&index=experiments'}>Experiments</a>
                                        </li>
                                    : null}
                                    {results['count']['targets'] ?
                                        <li>
                                            <span class="badge pull-right">{results['count']['targets']}</span>
                                            <a href={'/search'+ url+'&index=targets'}>Targets</a>
                                        </li>
                                    : null}
                                </ul>
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
            var results = this.props.context.items;
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
