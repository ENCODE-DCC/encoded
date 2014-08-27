/** @jsx React.DOM */
'use strict';
var React = require('react');
var cloneWithProps = require('react/lib/cloneWithProps');
var url = require('url');
var _ = require('underscore');
var globals = require('./globals');
var image = require('./image');
var search = module.exports;
var dbxref = require('./dbxref');
var DbxrefList = dbxref.DbxrefList;
var Dbxref = dbxref.Dbxref;

    // Should readlly be singular...
    var types = {
        antibody_lot: {title: 'Antibodies'},
        biosample: {title: 'Biosamples'},
        experiment: {title: 'Experiments'},
        target: {title: 'Targets'},
        dataset: {title: 'Datasets'},
        image: {title: 'Images'},
        publication: {title: 'Publications'},
        page: {title: 'Web page'},
        software: {title: 'Software'}
    };

    var Listing = module.exports.Listing = function (props) {
        // XXX not all panels have the same markup
        var context;
        if (props['@id']) {
            context = props;
            props = {context: context,  key: context['@id']};
        }
        return globals.listing_views.lookup(props.context)(props);
    };

    var PickerActionsMixin = module.exports.PickerActionsMixin = {
        contextTypes: {actions: React.PropTypes.array},
        renderActions: function() {
            if (this.context.actions && this.context.actions.length) {
                return (
                    <div className="pull-right">
                        {this.context.actions.map(action => cloneWithProps(action, {id: this.props.context['@id']}))}
                    </div>
                );
            } else {
                return <span/>;
            }
        }
    };

    var Item = module.exports.Item = React.createClass({
        mixins: [PickerActionsMixin],
        render: function() {
            var result = this.props.context;
            var title = globals.listing_titles.lookup(result)({context: result});
            var item_type = result['@type'][0];
            return (<li>
                        <div>
                            {this.renderActions()}
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
        mixins: [PickerActionsMixin],
        render: function() {
            var result = this.props.context;
            var columns = this.props.columns;

            // Build antibody display object as a hierarchy: target=>status=>biosample_term_names
            var targetTree = {};
            result.lot_reviews.forEach(function(lot_review) {
                lot_review.targets.forEach(function(target) {
                    // Get the organism object for this target
                    var targetOrganism = _(lot_review.organisms).find(function(organism) {
                        return organism['@id'] === target.organism;
                    });

                    // If we haven't seen this target, save it in targetTree along with the
                    // corresponding target and organism structures.
                    if (!targetTree[target.name]) {
                        targetTree[target.name] = {target: target, organism: targetOrganism};
                    }
                    var targetNode = targetTree[target.name];

                    // If we haven't seen the status, save it in the targetTree target
                    if (!targetNode[lot_review.status]) {
                        targetNode[lot_review.status] = [];
                    }
                    var statusNode = targetNode[lot_review.status];

                    // If we haven't seen the biosample term name, save it in the targetTree target status
                    statusNode.push(lot_review.biosample_term_name);
                });
            });

            return (
                <div>
                    {Object.keys(targetTree).map(function(target) {
                        return (
                            <li>
                                <div>
                                    {this.renderActions()}
                                    <div className="pull-right search-meta">
                                        <p className="type meta-title">Antibody</p>
                                        <p className="type">{' ' + result.accession}</p>
                                        <div className="type meta-status clearfix">
                                            {Object.keys(targetTree[target]).map(function(status) {
                                                return (
                                                    <div className="status-dots">
                                                        {(status !== 'target' && status !== 'organism') ?
                                                            <div className="tooltip-trigger">
                                                                <i className={globals.statusClass(status, 'indicator icon icon-circle')}></i>
                                                                <div className="tooltip sentence-case">
                                                                    {status}<br /><span>{targetTree[target][status].join(', ')}</span>
                                                                </div>
                                                            </div>
                                                        : ''}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                    <div className="accession">
                                        <a href={result['@id']}>
                                            {targetTree[target].target.label}
                                            {targetTree[target].organism ? <span>{' ('}<i>{targetTree[target].organism.scientific_name}</i>{')'}</span> : ''}
                                        </a> 
                                    </div>
                                </div>
                                <div className="data-row"> 
                                    <strong>{columns['source.title']['title']}</strong>: {result['source.title']}<br />
                                    <strong>{columns.product_id.title}/{columns.lot_id.title}</strong>: {result.product_id} / {result.lot_id}<br />
                                </div>
                            </li>
                        );
                    }.bind(this))}
                </div>
            );
        }
    });
    globals.listing_views.register(Antibody, 'antibody_lot');

    var Biosample = module.exports.Biosample = React.createClass({
        mixins: [PickerActionsMixin],
        render: function() {
            var result = this.props.context;
            var columns = this.props.columns;
            var lifeStage = (result['life_stage'] && result['life_stage'] != 'unknown') ? ' ' + result['life_stage'] : '';
            var age = (result['age'] && result['age'] != 'unknown') ? ' ' + result['age'] : '';
            var ageUnits = (result['age_units'] && result['age_units'] != 'unknown' && age) ? ' ' + result['age_units'] : '';
            var separator = (lifeStage || age) ? ',' : '';
            var rnais = (result.rnais[0] && result.rnais[0].target && result.rnais[0].target.label) ? result.rnais[0].target.label : '';
            var constructs = (result.constructs[0] && result.constructs[0].target && result.constructs[0].target.label) ? result.constructs[0].target.label : '';
            var treatment = (result.treatments[0] && result.treatments[0].treatment_term_name) ? result.treatments[0].treatment_term_name : '';
            return (<li>
                        <div>
                            {this.renderActions()}
                            <div className="pull-right search-meta">
                                <p className="type meta-title">Biosample</p>
                                <p className="type">{' ' + result['accession']}</p>
                                <p className="type meta-status">{' ' + result['status']}</p>
                            </div>
                            <div className="accession">
                                <a href={result['@id']}>
                                    {result['biosample_term_name'] + ' ('}
                                    <em>{result['organism.scientific_name']}</em>
                                    {separator + lifeStage + age + ageUnits + ')'}
                                </a> 
                            </div>
                        </div>
                        <div className="data-row">
                            <div><strong>{columns['biosample_type']['title']}</strong>: {result['biosample_type']}</div>
                            {rnais ?
                                <div>
                                    <strong>{columns['rnais.target.label']['title'] + ': '}</strong>
                                    {rnais}
                                </div>
                            : null}
                            {constructs ?
                                <div>
                                    <strong>{columns['constructs.target.label']['title'] + ': '}</strong>
                                    {constructs}
                                </div>
                            : null}
                            {treatment ?
                                <div>
                                    <strong>{columns['treatments.treatment_term_name']['title'] + ': '}</strong>
                                    {treatment}
                                </div>
                            : null}
                            <div><strong>{columns['source.title']['title']}</strong>: {result['source.title']}</div>
                        </div>
                </li>   
            );
        }
    });
    globals.listing_views.register(Biosample, 'biosample');


    var Experiment = module.exports.Experiment = React.createClass({
        mixins: [PickerActionsMixin],
        render: function() {
            var result = this.props.context;
            var columns = this.props.columns;

            // Make array of scientific names from replicates; remove all duplicates
            var names = _.uniq(result.replicates.map(function(replicate) {
                return (replicate.library && replicate.library.biosample && replicate.library.biosample.organism &&
                        replicate.library.biosample.organism) ? replicate.library.biosample.organism.scientific_name : undefined;
            }));
            var name = (names.length === 1 && names[0] && names[0] !== 'unknown') ? names[0] : '';

            // Make array of life stages from replicates; remove all duplicates
            var lifeStages = _.uniq(result.replicates.map(function(replicate) {
                return (replicate.library && replicate.library.biosample) ? replicate.library.biosample.life_stage : undefined;
            }));
            var lifeStage = (lifeStages.length === 1 && lifeStages[0] && lifeStages[0] !== 'unknown') ? ' ' + lifeStages[0] : '';

            // Make array of ages from replicates; remove all duplicates
            var ages = _.uniq(result.replicates.map(function(replicate) {
                return (replicate.library && replicate.library.biosample) ? replicate.library.biosample.age : undefined;
            }));
            var age = (ages.length === 1 && ages[0] && ages[0] !== 'unknown') ? ' ' + ages[0] : '';

            // Make array of age units from replicates; remove all duplicates
            var ageUnit = '';
            if (age) {
                var ageUnits = _.uniq(result.replicates.map(function(replicate) {
                    return (replicate.library && replicate.library.biosample) ? replicate.library.biosample.age_units : undefined;
                }));
                ageUnit = (ageUnits.length === 1 && ageUnits[0] && ageUnits[0] !== 'unknown') ? ' ' + ageUnits[0] : '';
            }

            // If we have life stage or age, need to separate from scientific name with comma
            var separator = (lifeStage || age) ? ', ' : '';

            // Get the first treatment if it's there
            var treatment = (result.replicates[0] && result.replicates[0].library && result.replicates[0].library.biosample &&
                    result.replicates[0].library.biosample.treatments[0]) ? result.replicates[0].library.biosample.treatments[0].treatment_term_name : '';

            return (<li>
                        <div>
                            {this.renderActions()}
                            <div className="pull-right search-meta">
                                <p className="type meta-title">Experiment</p>
                                <p className="type">{' ' + result['accession']}</p>
                                <p className="type meta-status">{' ' + result['status']}</p>
                            </div>
                            <div className="accession">
                                <a href={result['@id']}>
                                    {result['assay_term_name']}<span>{result['biosample_term_name'] ? ' of ' + result['biosample_term_name'] : ''}</span>
                                    {name || lifeStage || age || ageUnit ?
                                        <span>
                                            {' ('}
                                            {name ? <em>{name}</em> : ''}
                                            {separator + lifeStage + age + ageUnit + ')'}
                                        </span>
                                    : ''}
                                </a>
                            </div>
                        </div>
                        <div className="data-row">
                            {result['target.label'] ?
                                <div>
                                    <strong>{columns['target.label']['title'] + ': '}</strong>
                                    {result['target.label']}
                                </div>
                            : null}
                            {treatment ?
                                <div>
                                    <strong>{columns['replicates.library.biosample.treatments.treatment_term_name']['title'] + ': '}</strong>
                                    {treatment}
                                </div>
                            : null}
                            <div><strong>{columns['lab.title']['title']}</strong>: {result['lab.title']}</div>
                            <div><strong>{columns['award.project']['title']}</strong>: {result['award.project']}</div>
                        </div>
                </li>
            );
        }
    });
    globals.listing_views.register(Experiment, 'experiment');

    var Dataset = module.exports.Dataset = React.createClass({
        mixins: [PickerActionsMixin],
        render: function() {
            var result = this.props.context;
            var columns = this.props.columns;
            return (<li>
                        <div>
                            {this.renderActions()}
                            <div className="pull-right search-meta">
                                <p className="type meta-title">Dataset</p>
                                <p className="type">{' ' + result['accession']}</p>
                            </div>
                            <div className="accession">
                                <a href={result['@id']}>{result['description']}</a> 
                            </div>
                        </div>
                        <div className="data-row">
                            {result['dataset_type'] ?
                                <div>
                                    <strong>{columns['dataset_type']['title'] + ': '}</strong>
                                    {result['dataset_type']}
                                </div>
                            : null}
                            <strong>{columns['lab.title']['title']}</strong>: {result['lab.title']}<br />
                            <strong>{columns['award.project']['title']}</strong>: {result['award.project']}
                        </div>
                </li>
            );
        }
    });
    globals.listing_views.register(Dataset, 'dataset');

    var Target = module.exports.Target = React.createClass({
        mixins: [PickerActionsMixin],
        render: function() {
            var result = this.props.context;
            var columns = this.props.columns;
            return (<li>
                        <div>
                            {this.renderActions()}
                            <div className="pull-right search-meta">
                                <p className="type meta-title">Target</p>
                            </div>
                            <div className="accession">
                                <a href={result['@id']}>
                                    {result['label'] + ' ('}
                                    <em>{result['organism.scientific_name']}</em>
                                    {')'}
                                </a> 
                            </div>
                        </div>
                        <div className="data-row">
                            <strong>{columns['dbxref']['title']}</strong>: 
                            {result.dbxref && result.dbxref.length ?
                                <DbxrefList values={result.dbxref} target_gene={result.gene_name} />
                                : <em> None submitted</em> }
                        </div>
                </li>
            );
        }
    });
    globals.listing_views.register(Target, 'target');


    var Image = module.exports.Image = React.createClass({
        mixins: [PickerActionsMixin],
        render: function() {
            var result = this.props.context;
            var Attachment = image.Attachment;
            return (<li>
                        <div>
                            {this.renderActions()}
                            <div className="pull-right search-meta">
                                <p className="type meta-title">Image</p>
                            </div>
                            <div className="accession">
                                <a href={result['@id']}>{result.caption}</a>
                            </div>
                        </div>
                        <div className="data-row">
                            <Attachment context={result} />
                        </div>
                </li>
            );
        }
    });
    globals.listing_views.register(Image, 'image');


    // If the given term is selected, return the href for the term
    function termSelected(term, field, filters) {
        for (var filter in filters) {
            if (filters[filter]['field'] == field && filters[filter]['term'] == term) {
                return url.parse(filters[filter]['remove']).search;
            }
        }
        return null;
    }

    // Determine whether any of the given terms are selected
    function anyTermSelected(terms, field, filters) {
        for(var oneTerm in terms) {
            if(termSelected(terms[oneTerm].term, field, filters)) {
                return true;
            }
        }
        return false;
    }

    var Term = search.Term = React.createClass({
        render: function () {
            var filters = this.props.filters;
            var term = this.props.term['term'];
            var count = this.props.term['count'];
            var title = this.props.title || term;
            var field = this.props.facet['field'];
            var em = field === 'target.organism.scientific_name' ||
                     field === 'organism.scientific_name' ||
                     field === 'replicates.library.biosample.donor.organism.scientific_name';
            var barStyle = {
                width:  Math.ceil( (count/this.props.total) * 100) + "%"
            };
            var link = termSelected(term, field, filters);
            if(link) {
                return (
                    <li id="selected" key={term}>
                        <a id="selected" href={link} onClick={this.props.onFilter}>
                            <span className="pull-right">{count} <i className="icon icon-times-circle-o"></i></span>
                            <span className="facet-item">
                                {em ? <em>{title}</em> : <span>{title}</span>}
                            </span>
                        </a>
                    </li>
                );
            }else {
                return (
                    <li key={term}>
                        <span className="bar" style={barStyle}></span>
                        <a href={this.props.searchBase + field + '=' + term} onClick={this.props.onFilter}>
                            <span className="pull-right">{count}</span>
                            <span className="facet-item">
                                {em ? <em>{title}</em> : <span>{title}</span>}
                            </span>
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
            var title;
            try {
                title = types[term];
            } catch (e) {
                title = term;
            }
            var total = this.props.total;
            return this.transferPropsTo(<Term title={title} filters={filters} total={total} />);
        }
    });


    var Facet = search.Facet = React.createClass({
        getInitialState: function () {
            return {
                facetOpen: false
            };
        },

        handleClick: function () {
            this.setState({facetOpen: !this.state.facetOpen});
        },

        render: function() {
            var facet = this.props.facet;
            var filters = this.props.filters;
            var terms = facet['terms'].filter(function (term) {
                if (term.term) {
                    for(var filter in filters) {
                        if(filters[filter].term === term.term) {
                            return true;
                        }
                    }
                    return term.count > 0;
                } else {
                    return false;
                }
            });
            var moreTerms = terms.slice(5);
            var title = facet['title'];
            var field = facet['field'];
            var total = facet['total'];
            var termID = title.replace(/\s+/g, '');
            var TermComponent = field === 'type' ? TypeTerm : Term;
            var moreTermSelected = anyTermSelected(moreTerms, field, filters);
            var moreSecClass = 'collapse' + ((moreTermSelected || this.state.facetOpen) ? ' in' : '');
            var seeMoreClass = 'btn btn-link' + ((moreTermSelected || this.state.facetOpen) ? '' : ' collapsed');
            return (
                <div className="facet" hidden={terms.length === 0}>
                    <h5>{title}</h5>
                    <ul className="facet-list nav">
                        <div>
                            {terms.slice(0, 5).map(function (term) {
                                return this.transferPropsTo(<TermComponent key={term.term} term={term} filters={filters} total={total} />);
                            }.bind(this))}
                        </div>
                        {terms.length > 5 ?
                            <div id={termID} className={moreSecClass}>
                                {moreTerms.map(function (term) {
                                    return this.transferPropsTo(<TermComponent key={term.term} term={term} filters={filters} total={total} />);
                                }.bind(this))}
                            </div>
                        : null}
                        {(terms.length > 5 && !moreTermSelected) ?
                            <label className="pull-right">
                                    <small>
                                        <button type="button" className={seeMoreClass} data-toggle="collapse" data-target={'#'+termID} onClick={this.handleClick} />
                                    </small>
                            </label>
                        : null}
                    </ul>
                </div>
            );
        }
    });

    var TextFilter = React.createClass({

        getValue: function(props) {
            var filter = this.props.filters.filter(function(f) {
                return f.field == 'searchTerm';
            });
            return filter.length ? filter[0].term : '';
        },

        shouldUpdateComponent: function(nextProps) {
            return (this.getValue(this.props) != this.getValue(nextProps));
        },

        render: function() {
            return (
                <div className="facet">
                    <input ref="input" type="search" className="form-control search-query"
                           placeholder="Enter search term(s)"
                           defaultValue={this.getValue(this.props)}
                           onChange={this.onChange} onBlur={this.onBlur} onKeyPress={this.onKeyPress} />
                </div>
            );
        },

        onChange: function(e) {
            e.stopPropagation();
            return false;
        },

        onBlur: function(e) {
            var search = this.props.searchBase.replace(/&?searchTerm=[^&]*/, '');
            var value = e.target.value;
            if (value) {
                search += 'searchTerm=' + e.target.value;
            } else {
                search = search.substring(0, search.length - 1);
            }
            this.props.onChange(search);
        },

        onKeyPress: function(e) {
            if (e.keyCode == 13) {
                this.onBlur(e);
                return false;                
            }
        }
    });

    var FacetList = search.FacetList = React.createClass({
        render: function() {
            var term = this.props.term;
            var facets = this.props.facets;
            var filters = this.props.filters;
            if (!facets.length) return <div />;
            var hideTypes;
            if (this.props.mode == 'picker') {
                hideTypes = false;
            } else {
                hideTypes = filters.filter(function(filter) {
                    return filter.field == 'type';
                }).length;
            }
            return (
                <div className="box facets">
                    {this.props.mode === 'picker' ? this.transferPropsTo(<TextFilter filters={filters} />) : ''}
                    {facets.map(function (facet) {
                        if (hideTypes && facet.field == 'type') {
                            return <span key={facet.field} />;
                        } else {
                            return this.transferPropsTo(<Facet key={facet.field} facet={facet} filters={filters} />);
                        }
                    }.bind(this))}
                </div>
            );
        }
    });

    var ResultTable = search.ResultTable = React.createClass({

        getDefaultProps: function() {
            return {searchBase: ''};
        },

        childContextTypes: {actions: React.PropTypes.array},
        getChildContext: function() {
            return {
                actions: this.props.actions
            };
        },

        render: function() {
            var context = this.props.context;
            var results = context['@graph'];
            var facets = context['facets'];
            var total = context['total'];
            var columns = context['columns'];
            var filters = context['filters'];
            var searchBase = this.props.searchBase;
            searchBase += searchBase ? '&' : '?';
            
            return (
                    <div>
                        <div className="row">
                            <div className="col-sm-5 col-md-4 col-lg-3">
                                {this.transferPropsTo(
                                    <FacetList facets={facets} filters={filters}
                                               searchBase={searchBase} onFilter={this.onFilter} />
                                )}
                            </div>
                            <div className="col-sm-7 col-md-8 col-lg-9">
                                {context['notification'] === 'Success' ?
                                    <h4>
                                        Showing {results.length} of {total} 
                                        {total > results.length ?
                                            <span className="pull-right">
                                                {searchBase.indexOf('&limit=all') !== -1 ? 
                                                    <a className="btn btn-info btn-sm"
                                                       href={searchBase.replace("&limit=all", "")}
                                                       onClick={this.onFilter}>View 25</a>
                                                : <a rel="nofollow" className="btn btn-info btn-sm"
                                                     href={searchBase+ '&limit=all'}
                                                     onClick={this.onFilter}>View All</a>}
                                            </span>
                                        : null}
                                    </h4>
                                : <h4>{context['notification']}</h4>}
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
                    </div>  
            );
        },

        onFilter: function(e) {
            var search = e.currentTarget.getAttribute('href');
            this.props.onChange(search);
            e.stopPropagation();
            return false;
        }
    });

    var Search = search.Search = React.createClass({
        render: function() {
            var context = this.props.context;
            var results = context['@graph'];
            var notification = context['notification'];
            var searchBase = url.parse(this.props.href).search || '';
            var facetdisplay = context.facets.some(function(facet) {
                return facet.total > 0;
            });
            return (
                <div>
                    {facetdisplay ?
                        <div className="panel data-display main-panel"> 
                            {this.transferPropsTo(<ResultTable key={undefined} searchBase={searchBase} onChange={this.props.navigate} />)}
                        </div>
                    : <h4>{notification}</h4>}
                </div>
            );
        }
    });

    globals.content_views.register(Search, 'search');
