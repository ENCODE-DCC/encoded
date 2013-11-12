/** @jsx React.DOM */
define(['exports', 'react', 'url', './globals'],
function (exports, React, url, globals) {
    'use strict';
    var search = exports;

    var FacetBuilder = search.FacetBuilder = React.createClass({
        render: function() {
            var context = this.props.context;
            var result_count = context['@graph'].length;
            var facets = context['facets'];
            var href_search = url.parse(this.props.href).search || '';
            var counter, counter1 = 0;
            var buildTerms = function(map) {
                var id;
                var count;
                var field;
                counter = counter + 1;
                for (var j in map) {
                    if(j == "field") {
                        field = map[j];
                    }else {
                        id = j;
                        count = map[j];
                    }
                }
                if(counter < 4) {
                    if(count == result_count) {
                        return <li>
                                <label><small>{id} ({count})</small></label>
                            </li>
                    }else {
                        return <li>
                                <a href={href_search+'&'+field+'='+id}>
                                    <label><small>{id} ({count})</small></label>
                                </a>
                            </li>
                    }
                } 
            };
            var buildCollapsingTerms = function(map) {
                var id;
                var count;
                var field;
                counter1 = counter1 + 1;
                for (var j in map) {
                    if(j == "field") {
                        field = map[j];
                    }else {
                        id = j;
                        count = map[j];
                    }
                }
                if (counter1 >= 4) {
                   if(count == result_count) {
                        return <li>
                                <label><small>{id} ({count})</small></label>
                            </li>
                    }else {
                        return <li>
                                <a href={href_search+'&'+field+'='+id}>
                                    <label><small>{id} ({count})</small></label>
                                </a>
                            </li>
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
                    }
                }
                return <div>
                        <legend><small>{term}</small></legend>
                        <ul className="facet-list">
                            {terms.length ?
                                terms.map(buildTerms)
                            : null}
                        </ul>
                        {terms.length > 3 ?
                            <ul className="facet-list">
                                <div id={termID} className="collapse">
                                    {terms.length ?
                                        terms.map(buildCollapsingTerms)
                                    : null}
                                </div>
                            </ul>
                        : null}
                        {terms.length > 3 ?
                            <label className="pull-right">
                                    <small>
                                        <button type="button" className="btn btn-link collapsed" data-toggle="collapse" data-target={'#'+termID} />
                                    </small>
                            </label>
                        : null}
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

            var resultsView = function(result) {
                var highlight = result['highlight'];
                switch (result['@type'][0]) {
                    case "biosample":
                        return <li className="post">
                                    <div className="accession"><a href={result['@id']}>{result['accession']}</a></div>
                                    <small>{result['biosample_term_name']} - {result['biosample_term_id']} - {result['lab.title']}
                                        <br />
                                        <div className="highlight"dangerouslySetInnerHTML={{__html: highlight.toString()}} />
                                    </small>
                            </li>
                        break;
                    case "experiment":
                        return <li className="post">
                                    <div className="accession"><a href={result['@id']}>{result['accession']}</a></div>
                                    <small>{result['description']} - {result['assay_term_name']} - {result['lab.title']}
                                        <br />
                                        <div className="highlight" dangerouslySetInnerHTML={{__html: highlight.toString()}} />
                                    </small>
                            </li>
                        break;
                    case "antibody_approval":
                        return <li className="post">
                                <div className="accession"><a href={result['@id']}>{result['antibody.accession']}</a></div>
                                <small>{result['target.label']} - {result['antibody.source.title']}
                                    <br />
                                    <div className="highlight" dangerouslySetInnerHTML={{__html: highlight.toString()}} />
                                </small>
                            </li>
                        break;
                    case "target":
                        return <li className="post">
                                <div className="accession"><a href={result['@id']}>{result['label']}</a></div>
                                <small>{result['organism.name']}
                                    <br />
                                    <div  className="highlight" dangerouslySetInnerHTML={{__html: highlight.toString()}} />
                                </small>
                            </li>
                        break;
                }
            };  
            return (
                    <div>
                        {results.length ?
                            <div className="panel data-display">
                                <div className="row">
                                    <div className="span3" id="facets">
                                        <h4>Filter Results</h4>
                                        <section className="facet box">
                                            <div>
                                                <legend><small>Data Type</small></legend>
                                                <ul className="facet-list">
                                                    {count['antibodies'] ?
                                                        <li>
                                                            <span className="badge pull-right">{count['antibodies']}</span>
                                                            <a href={href_search+'&type=antibodies'}><small>Antibodies</small></a>
                                                        </li>
                                                    : null}
                                                    {count['biosamples'] ?
                                                        <li>
                                                            <span className="badge pull-right">{count['biosamples']}</span>
                                                            <a href={href_search+'&type=biosamples'}><small>Biosamples</small></a>
                                                        </li>
                                                    : null}
                                                    {count['experiments'] ?
                                                        <li>
                                                            <span className="badge pull-right">{count['experiments']}</span>
                                                            <a href={href_search+'&type=experiments'}><small>Experiments</small></a>
                                                        </li>
                                                    : null}
                                                    {count['targets'] ?
                                                        <li>
                                                            <span className="badge pull-right">{count['targets']}</span>
                                                            <a href={href_search+'&type=targets'}><small>Targets</small></a>
                                                        </li>
                                                    : null}
                                                </ul>
                                            </div>
                                            {facets.length ?
                                                this.transferPropsTo(<FacetBuilder />)
                                            :null }
                                        </section>
                                    </div>
                                    <div className="span8">
                                        <legend>{results.length} Results Found</legend>
                                        <div className="results">
                                            <ul className="nav">
                                                {results.length ?
                                                    results.map(resultsView)
                                                : null}
                                            </ul>
                                        </div>
                                    </div>
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
                <div >
                    <form className="input-prepend">
                        <span className="add-on"><i className="icon-search"></i></span>
                        <input id='inputValidate' className="input-xxlarge" type="text" placeholder="Search ENCODE" name="searchTerm" defaultValue={this.state.text} />
                    </form>
                    {Object.keys(results).length ?
                        this.transferPropsTo(<ResultTable />)
                    : <h4>Please enter a search term </h4>}
                </div>
            );
        }
    });

    globals.content_views.register(Search, 'search');
    return search;
});
