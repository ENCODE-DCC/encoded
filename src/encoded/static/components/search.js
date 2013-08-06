/** @jsx React.DOM */
define(['exports', 'jquery', 'react', 'globals'],
function (search, $, React, globals) {
    'use strict';

    var ResultTable = search.ResultTable = React.createClass({
        render: function() {
            var results = this.props.context.items;
            var resultsView = function(result) {
                return <li class="result">
                        <h6>BIOSAMPLE</h6>
                        <div class="content">ENCBSRNA000</div>
                    </li>
            };
            return (
                <div class="panel data-display">
                    <div class="row">
                        <div class="span3" id="facets">
                            <h4>Filter Results</h4>
                            <section class="facet wel box">
                                <h4>Data Type</h4>
                                <ul class="facet-list">
                                    <li class="selected"><a href>All</a></li>
                                    <li><a href>Antibodies</a></li>
                                    <li><a href>Biosamples</a></li>
                                    <li><a href>Experiments</a></li>
                                    <li><a href>Targets</a></li>
                                </ul>
                            </section>
                        </div>
                        <div class="span8">
                            <h4>{results['results'].length} Results Found</h4>
                            <ul class="searchResults">
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
                        <ResultTable context={this.props.context} />
                    :null }
                </div>
            );
        }
    });

    globals.content_views.register(Search, 'search');
    return search;
});
