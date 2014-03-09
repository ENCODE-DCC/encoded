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

    var Item = module.exports.Item = React.createClass({
        render: function() {
            var result = this.props.context;
            var title = globals.listing_titles.lookup(result)({context: result});
            var item_type = result['@type'][0];
            return (<li>
                        <div>
                            {result.accession ? <span className="pull-right type sentence-case">{item_type}: {' ' + result['accession']}</span> : null}
                            <div className="accession">
                                <a href={result['@id']}>{title}</a>
                            </div>
                        </div>
                        <div className="data-row">
                            {result.description}
                        </div>
                </li>
            );
        }
    });
    globals.listing_views.register(Item, 'item');

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
                            <strong>{columns['award.project']}</strong>: {result['award.project']}
                        </div>
                </li>
            );
        }
    });
    globals.listing_views.register(Experiment, 'experiment');

    var Dataset = module.exports.Dataset = React.createClass({
        render: function() {
            var result = this.props.context;
            var columns = this.props.columns;
            return (<li>
                        <div>
                            <span className="pull-right type">Dataset: {' ' + result['accession']}</span>
                            <div className="accession">
                                <a href={result['@id']}>{result['description']}</a> 
                            </div>
                        </div>
                        <div className="data-row">
                            {result['dataset_type'] ? <strong>{columns['dataset_type'] + ': '}</strong>: null}
                            <strong>{columns['lab.title']}</strong>: {result['lab.title']}<br />
                            <strong>{columns['award.project']}</strong>: {result['award.project']}
                        </div>
                </li>
            );
        }
    });
    globals.listing_views.register(Dataset, 'dataset');

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

    var Term = search.Term = React.createClass({
        render: function () {
            var filters = this.props.filters;
            var term = this.props.term['term'];
            var count = this.props.term['count'];
            var title = this.props.title || term;
            var search_base = this.props.search_base;
            var field = this.props.facet['field'];
            var selected = 0;
            var link = '';
            for (var filter in filters) {
                if (filters[filter]['term'] == term && filters[filter]['field'] == field) {
                    selected = 1;
                    link = filters[filter]['remove'];
                }
            }
            if(selected) {
                return (
                    <li id="selected" key={term}>
                        <a id="selected" href={link}>
                            <span className="pull-right"><i className="icon-remove-sign"></i></span>
                            <span className="facet-item">{title}</span>
                        </a>
                    </li>
                );
            }else {
                return (
                    <li key={term}>
                        <a href={search_base+field+'='+term}>
                            <span className="pull-right">{count}</span>
                            <span className="facet-item">{title}</span>
                        </a>
                    </li>
                );
            }
        }
    });

    var TypeTerm = search.TypeTerm = React.createClass({
        render: function () {
            var term = this.props.term['term'];
            var filters = this.props.filters;
            var title = this.props.portal.types[term];
            return this.transferPropsTo(<Term title={title} filters={filters} />);
        }
    });


    var Facet = search.Facet = React.createClass({
        render: function() {
            var facet = this.props.facet;
            var filters = this.props.filters;
            var terms = facet['terms'];
            var title = facet['title'];
            var field = facet['field'];
            var termID = title.replace(/\s+/g, '');
            var TermComponent = field === 'type' ? TypeTerm : Term;
            return (
                <div className="facet" key={field}>
                    <h5>{title}</h5>
                    <ul className="facet-list nav">
                        <div>
                            {terms.slice(0, 5).map(function (term) {
                                return this.transferPropsTo(<TermComponent term={term} filters={filters} />);
                            }.bind(this))}
                        </div>
                        {terms.length > 5 ?
                            <div id={termID} className="collapse">
                                {terms.slice(5).map(function (term) {
                                    return this.transferPropsTo(<TermComponent term={term} filters={filters} />);
                                }.bind(this))}
                            </div>
                        : null}
                        {terms.length > 5 ?
                            <label className="pull-right">
                                    <small>
                                        <button type="button" className="btn btn-link collapsed" data-toggle="collapse" data-target={'#'+termID} />
                                    </small>
                            </label>
                        : null}
                    </ul>
                </div>
            );
        }
    });

    var FacetList = search.FacetList = React.createClass({
        render: function() {
            var facets = this.props.facets;
            var filters = this.props.filters;
            if (!facets.length) return <div />;
            var search_base = url.parse(this.props.href).search || '';
            search_base += search_base ? '&' : '?';
            return (
                <div className="box facets">
                    {facets.map(function (facet) {
                        return this.transferPropsTo(<Facet facet={facet} filters={filters} search_base={search_base} />);
                    }.bind(this))}
                </div>
            );
        }
    });

    var ResultTable = search.ResultTable = React.createClass({
        render: function() {
            var context = this.props.context;
            var results = context['@graph'];
            var facets = context['facets'];
            var total = context['total'];
            var columns = context['columns'];
            var filters = context['filters'];
            var search_id = context['@id']
            
            return (
                    <div>
                        {results.length ?
                            <div className="row">
                                <div className="span3">
                                    {this.transferPropsTo(
                                        <FacetList facets={facets} filters={filters} />
                                    )}
                                </div>

                                <div className="span8">
                                    <h4>Showing {results.length} of {total} 
                                        {total > results.length ?
                                                <span className="pull-right">
                                                    {search_id.indexOf('&limit=all') !== -1 ? 
                                                        <a className="btn btn-info btn-small" href={search_id.replace("&limit=all", "")}>View 25</a>
                                                    : <a rel="nofollow" className="btn btn-info btn-small" href={search_id+ '&limit=all'}>View All</a>}
                                                </span>
                                            : null}
                                    </h4>
                                    <hr />
                                    <ul className="nav result-table">
                                        {results.length ?
                                            results.map(function (result) {
                                                return Listing({context:result, columns: columns, key: result['@id']});
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
        render: function() {
            var context = this.props.context;
            var results = context['@graph'];
            var notification = context['notification']
            var id = url.parse(this.props.href, true);
            var searchTerm = id.query['searchTerm'] || '';
            return (
                <div>
                    {notification === 'Success' ?
                        <div className="panel data-display"> 
                            {this.transferPropsTo(<ResultTable key={undefined} />)}
                        </div>
                    : <h4>{notification}</h4>}
                </div>
            );
        }
    });

    globals.content_views.register(Search, 'search');
