/** @jsx React.DOM */
define(['exports', 'jquery', 'react', 'globals'],
function (search, $, React, globals) {
    'use strict';

    var ResultTable = search.ResultTable = React.createClass({
        render: function() {
            var results = this.props.context.items;
            console.log(results.biosamples.length);
            var createBiosampleTable = function(item) {
                return <tr>
                        <td>{item['accession']}</td>
                        <td>{item['biosample_type']}</td>
                        <td>{item['biosample_term_name']}</td>
                        <td>{item['donor']['organism']['organism_name']}</td>
                        <td>{item['source']['alias']}</td>
                    </tr>
            };
            var createExperimentTable = function(item) {
                return <tr>
                        <td>{item['dataset_accession']}</td>
                        <td>{item['dataset_description']}</td>
                        <td>{item['project']}</td>
                        <td>{item['lab']['name']}</td>
                    </tr>
            };
            var createAntibodyTable = function(item) {
                return <tr>
                        <td>{item['antibody_lot']['antibody_accession']}</td>
                        <td>{item['project']}</td>
                        <td>{item['approval_status']}</td>
                        <td>{item['target']['organism']['organism_name']}</td>
                        <td>{item['antibody_lot']['source']['alias']}</td>
                    </tr>  
            };
            var createTargetTable = function(item) {
                return <tr>
                        <td>{item['target_gene_name']}</td>
                        <td>{item['project']}</td>
                        <td>{item['organism']['organism_name']}</td>
                    </tr>   
            };
            return (
                <div class="panel data-display">
                    {results['biosamples'].length ?
                        <table class="table table-striped">
                            <thead class="sticky-header">
                                <tr><th>Accession</th><th>Biosample Type</th><th>Biosample Term</th><th>Species</th><th>Source</th></tr>
                            </thead>
                            {results['biosamples'].map(createBiosampleTable)}</table>
                    : null}
                    {results['experiments'].length ?  
                        <table class="table table-striped">
                        <thead class="sticky-header">
                            <tr><th>Accession</th><th>Description</th><th>Project</th><th>Lab</th></tr>
                        </thead>
                        {results['experiments'].map(createExperimentTable)}</table>
                    : null}
                    {results['antibodies'].length ?  
                        <table class="table table-striped">
                            <thead class="sticky-header">
                                <tr><th>Accession</th><th>Project</th><th>Approval Status</th><th>Species</th><th>Source</th></tr>
                            </thead>
                            {results['antibodies'].map(createAntibodyTable)}</table>
                    : null}
                    {results['targets'].length ? 
                        <table class="table table-striped">
                            <thead class="sticky-header">
                                <tr><th>Target</th><th>Project</th><th>Species</th></tr>
                            </thead>
                            {results['targets'].map(createTargetTable)}</table>
                    : null}
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
                        <span class="add-on"><i class="icon-search">Search</i></span>
                        <input type="text" class="search-query" placeholder="Search ENCODE" name="searchTerm" defaultValue={this.state.text} />
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
