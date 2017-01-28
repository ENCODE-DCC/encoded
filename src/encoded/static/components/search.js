'use strict';
var React = require('react');
var queryString = require('query-string');
var button = require('../libs/bootstrap/button');
var {Modal, ModalHeader, ModalBody, ModalFooter} = require('../libs/bootstrap/modal');
var dropdownMenu = require('../libs/bootstrap/dropdown-menu');
var svgIcon = require('../libs/svg-icons').svgIcon;
var url = require('url');
var _ = require('underscore');
import { auditDecor } from './audit';
var globals = require('./globals');
var image = require('./image');
var search = module.exports;
var { donorDiversity } = require('./objectutils');
var dbxref = require('./dbxref');
var objectutils = require('./objectutils');
var {BiosampleSummaryString, BiosampleOrganismNames} = require('./typeutils');

var DbxrefList = dbxref.DbxrefList;
var statusOrder = globals.statusOrder;
var SingleTreatment = objectutils.SingleTreatment;
var DropdownButton = button.DropdownButton;
var DropdownMenu = dropdownMenu.DropdownMenu;

// Should really be singular...
var types = {
    annotation: {title: 'Annotation file set'},
    antibody_lot: {title: 'Antibodies'},
    biosample: {title: 'Biosamples'},
    experiment: {title: 'Experiments'},
    target: {title: 'Targets'},
    dataset: {title: 'Datasets'},
    image: {title: 'Images'},
    matched_set: {title: 'Matched set series'},
    organism_development_series: {title: 'Organism development series'},
    publication: {title: 'Publications'},
    page: {title: 'Web page'},
    pipeline: {title: 'Pipeline'},
    project: {title: 'Project file set'},
    publication_data: {title: 'Publication file set'},
    reference: {title: 'Reference file set'},
    reference_epigenome: {title: 'Reference epigenome series'},
    replication_timing_series: {title: 'Replication timing series'},
    software: {title: 'Software'},
    treatment_concentration_series: {title: 'Treatment concentration series'},
    treatment_time_series: {title: 'Treatment time series'},
    ucsc_browser_composite: {title: 'UCSC browser composite file set'}
};

var datasetTypes = {
    'Annotation': types['annotation'].title,
    'Dataset': types['dataset'].title,
    'MatchedSet': types['matched_set'].title,
    'OrganismDevelopmentSeries': types['organism_development_series'].title,
    'Project': types['project'].title,
    'PublicationData': types['publication_data'].title,
    'Reference': types['reference'].title,
    'ReferenceEpigenome': types['reference_epigenome'].title,
    'ReplicationTimingSeries': types['replication_timing_series'].title,
    'TreatmentConcentrationSeries': types['treatment_concentration_series'].title,
    'TreatmentTimeSeries': types['treatment_time_series'].title,
    'UcscBrowserComposite': types['ucsc_browser_composite'].title
};

var Listing = module.exports.Listing = function (props) {
    // XXX not all panels have the same markup
    var context;
    if (props['@id']) {
        context = props;
        props = {context: context,  key: context['@id']};
    }
    var ListingView = globals.listing_views.lookup(props.context);
    return <ListingView {...props} />;
};

const PickerActions = module.exports.PickerActions = React.createClass ({
    contextTypes: {
        actions: React.PropTypes.array,
    },

    render: function () {
        if (this.context.actions && this.context.actions.length) {
            return (
                <div className="pull-right">
                    {this.context.actions.map(action => React.cloneElement(action, { id: this.props.context['@id'] }))}
                </div>
            );
        } else {
            return <span />;
        }
    },
});

var ItemComponent = React.createClass({
    render: function() {
        var result = this.props.context;
        var title = globals.listing_titles.lookup(result)({context: result});
        var item_type = result['@type'][0];
        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    {result.accession ?
                        <div className="pull-right type sentence-case search-meta">
                            <p>{item_type}: {' ' + result['accession']}</p>
                            {this.props.auditIndicators(result.audit, result['@id'], { search: true })}
                        </div>
                    : null}
                    <div className="accession">
                        <a href={result['@id']}>{title}</a>
                    </div>
                    <div className="data-row">
                        {result.description}
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
});

const Item = module.exports.Item = auditDecor(ItemComponent);

globals.listing_views.register(Item, 'Item');


// Display one antibody status indicator
var StatusIndicator = React.createClass({
    getInitialState: function() {
        return {
            tipOpen: false,
            tipStyles: {}
        };
    },

    // Display tooltip on hover
    onMouseEnter: function () {
        function getNextElementSibling(el) {
            // IE8 doesn't support nextElementSibling
            return el.nextElementSibling ? el.nextElementSibling : el.nextSibling;
        }

        // Get viewport bounds of result table and of this tooltip
        var whiteSpace = 'nowrap';
        var resultBounds = document.getElementById('result-table').getBoundingClientRect();
        var resultWidth = resultBounds.right - resultBounds.left;
        var tipBounds = _.clone(getNextElementSibling(this.refs.indicator).getBoundingClientRect());
        var tipWidth = tipBounds.right - tipBounds.left;
        var width = tipWidth;
        if (tipWidth > resultWidth) {
            // Tooltip wider than result table; set tooltip to result table width and allow text to wrap
            tipBounds.right = tipBounds.left + resultWidth - 2;
            whiteSpace = 'normal';
            width = tipBounds.right - tipBounds.left - 2;
        }

        // Set an inline style to move the tooltip if it runs off right edge of result table
        var leftOffset = resultBounds.right - tipBounds.right;
        if (leftOffset < 0) {
            // Tooltip goes outside right edge of result table; move it to the left
            this.setState({tipStyles: {left: (leftOffset + 10) + 'px', maxWidth: resultWidth + 'px', whiteSpace: whiteSpace, width: width + 'px'}});
        } else {
            // Tooltip fits inside result table; move it to native position
            this.setState({tipStyles: {left: '10px', maxWidth: resultWidth + 'px', whiteSpace: whiteSpace, width: width + 'px'}});
        }

        this.setState({tipOpen: true});
    },

    // Close tooltip when not hovering
    onMouseLeave: function() {
        this.setState({tipStyles: {maxWidth: 'none', whiteSpace: 'nowrap', width: 'auto', left: '15px'}}); // Reset position and width
        this.setState({tipOpen: false});
    },

    render: function() {
        var classes = this.state.tipOpen ? ' tooltipopen' : '';

        return (
            <span className="tooltip-status-trigger">
                <i className={globals.statusClass(this.props.status, 'indicator icon icon-circle')} ref="indicator" onMouseEnter={this.onMouseEnter} onMouseLeave={this.onMouseLeave}></i>
                <div className={`tooltip-status sentence-case${classes}`} style={this.state.tipStyles}>
                    {this.props.status}<br /><span>{this.props.terms.join(', ')}</span>
                </div>
            </span>
        );
    }
});

// Display the status indicators for one target
var StatusIndicators = React.createClass({
    render: function() {
        var targetTree = this.props.targetTree;
        var target = this.props.target;

        return (
            <span className="status-indicators">
                {Object.keys(targetTree[target]).map(function(status, i) {
                    if (status !== 'target') {
                        return <StatusIndicator key={i} status={status} terms={targetTree[target][status]} />;
                    } else {
                        return null;
                    }
                })}
            </span>
        );
    }
});

var AntibodyComponent = React.createClass({
    render: function() {
        var result = this.props.context;

        // Sort the lot reviews by their status according to our predefined order
        // given in the statusOrder array.
        var lot_reviews = _.sortBy(result.lot_reviews, function(lot_review) {
            return _.indexOf(statusOrder, lot_review.status); // Use underscore indexOf so that this works in IE8
        });

        // Build antibody display object as a hierarchy: target=>status=>biosample_term_names
        var targetTree = {};
        lot_reviews.forEach(function(lot_review) {
            lot_review.targets.forEach(function(target) {
                // If we haven't seen this target, save it in targetTree along with the
                // corresponding target and organism structures.
                if (!targetTree[target.name]) {
                    targetTree[target.name] = {target: target};
                }
                var targetNode = targetTree[target.name];

                // If we haven't seen the status, save it in the targetTree target
                if (!targetNode[lot_review.status]) {
                    targetNode[lot_review.status] = [];
                }
                var statusNode = targetNode[lot_review.status];

                // If we haven't seen the biosample term name, save it in the targetTree target status
                if (statusNode.indexOf(lot_review.biosample_term_name) === -1) {
                    statusNode.push(lot_review.biosample_term_name);
                }
            });
        });
        lot_reviews = null; // Tell GC we're done, just to be sure

        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Antibody</p>
                        <p className="type">{' ' + result.accession}</p>
                        <p className="type meta-status">{' ' + result['status']}</p>
                        {this.props.auditIndicators(result.audit, result['@id'], { search: true })}
                    </div>
                    <div className="accession">
                        {Object.keys(targetTree).map(function(target) {
                            return (
                                <div key={target}>
                                    <a href={result['@id']}>
                                        {targetTree[target].target.label}
                                        {targetTree[target].target.organism ? <span>{' ('}<i>{targetTree[target].target.organism.scientific_name}</i>{')'}</span> : ''}
                                    </a>
                                    <StatusIndicators targetTree={targetTree} target={target} />
                                </div>
                            );
                        })}
                    </div>
                    <div className="data-row">
                        <div><strong>Source: </strong>{result.source.title}</div>
                        <div><strong>Product ID / Lot ID: </strong>{result.product_id} / {result.lot_id}</div>
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
});

const Antibody = module.exports.Antibody = auditDecor(AntibodyComponent);

globals.listing_views.register(Antibody, 'AntibodyLot');


var BiosampleComponent = React.createClass({
    render: function() {
        var result = this.props.context;
        var lifeStage = (result['life_stage'] && result['life_stage'] != 'unknown') ? ' ' + result['life_stage'] : '';
        var age = (result['age'] && result['age'] != 'unknown') ? ' ' + result['age'] : '';
        var ageUnits = (result['age_units'] && result['age_units'] != 'unknown' && age) ? ' ' + result['age_units'] : '';
        var separator = (lifeStage || age) ? ',' : '';
        var rnais = (result.rnais[0] && result.rnais[0].target && result.rnais[0].target.label) ? result.rnais[0].target.label : '';
        var constructs;
        if (result.model_organism_donor_constructs && result.model_organism_donor_constructs.length) {
            constructs = result.model_organism_donor_constructs[0].target.label;
        } else {
            constructs = result.constructs[0] ? result.constructs[0].target.label : '';
        }
        var treatment = (result.treatments[0] && result.treatments[0].treatment_term_name) ? result.treatments[0].treatment_term_name : '';
        var mutatedGenes = result.donor && result.donor.mutated_gene && result.donor.mutated_gene.label;

        // Build the text of the synchronization string
        var synchText;
        if (result.synchronization) {
            synchText = result.synchronization +
                (result.post_synchronization_time ?
                    ' + ' + result.post_synchronization_time + (result.post_synchronization_time_units ? ' ' + result.post_synchronization_time_units : '')
                : '');
        }

        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Biosample</p>
                        <p className="type">{' ' + result['accession']}</p>
                        <p className="type meta-status">{' ' + result['status']}</p>
                        {this.props.auditIndicators(result.audit, result['@id'], { search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {result['biosample_term_name'] + ' ('}
                            <em>{result.organism.scientific_name}</em>
                            {separator + lifeStage + age + ageUnits + ')'}
                        </a>
                    </div>
                    <div className="data-row">
                        <div><strong>Type: </strong>{result['biosample_type']}</div>
                        {result.summary ? <div><strong>Summary: </strong>{BiosampleSummaryString(result)}</div> : null}
                        {rnais ? <div><strong>RNAi target: </strong>{rnais}</div> : null}
                        {constructs ? <div><strong>Construct: </strong>{constructs}</div> : null}
                        {treatment ? <div><strong>Treatment: </strong>{treatment}</div> : null}
                        {mutatedGenes ? <div><strong>Mutated gene: </strong>{mutatedGenes}</div> : null}
                        {result.culture_harvest_date ? <div><strong>Culture harvest date: </strong>{result.culture_harvest_date}</div> : null}
                        {result.date_obtained ? <div><strong>Date obtained: </strong>{result.date_obtained}</div> : null}
                        {synchText ? <div><strong>Synchronization timepoint: </strong>{synchText}</div> : null}
                        <div><strong>Source: </strong>{result.source.title}</div>
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
});

const Biosample = module.exports.Biosample = auditDecor(BiosampleComponent);

globals.listing_views.register(Biosample, 'Biosample');


var ExperimentComponent = React.createClass({
    render: function() {
        var result = this.props.context;

        // Collect all biosamples associated with the experiment. This array can contain duplicate
        // biosamples, but no null entries.
        var biosamples = [];
        if (result.replicates && result.replicates.length) {
            biosamples = _.compact(result.replicates.map(replicate => replicate.library && replicate.library.biosample));
        }

        // Get all biosample organism names
        var organismNames = biosamples.length ? BiosampleOrganismNames(biosamples) : [];

        // Collect synchronizations
        var synchronizations = _.uniq(result.replicates.filter(function(replicate) {
            return (replicate.library && replicate.library.biosample && replicate.library.biosample.synchronization);
        }).map(function(replicate) {
            var biosample = replicate.library.biosample;
            return (biosample.synchronization +
                (biosample.post_synchronization_time ?
                    ' + ' + biosample.post_synchronization_time + (biosample.post_synchronization_time_units ? ' ' + biosample.post_synchronization_time_units : '')
                : ''));
        }));

        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Experiment</p>
                        <p className="type">{' ' + result['accession']}</p>
                        <p className="type meta-status">{' ' + result['status']}</p>
                        {this.props.auditIndicators(result.audit, result['@id'], { search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {result.assay_title ?
                                <span>{result.assay_title}</span>
                            :
                                <span>{result.assay_term_name}</span>
                            }
                            {result['biosample_term_name'] ? <span>{' of ' + result['biosample_term_name']}</span> : null}
                        </a>
                    </div>
                    {result.biosample_summary ?
                        <div className="highlight-row">
                            {organismNames.length ?
                                <span>
                                    {organismNames.map((organism, i) => 
                                        <span key={organism}>
                                            {i > 0 ? <span>and </span> : null}
                                            <i>{organism} </i>
                                        </span>
                                    )}
                                </span>
                            : null}
                            {result.biosample_summary}
                        </div>
                    : null}
                    <div className="data-row">
                        {result.target && result.target.label ?
                            <div><strong>Target: </strong>{result.target.label}</div>
                        : null}

                        {synchronizations && synchronizations.length ?
                            <div><strong>Synchronization timepoint: </strong>{synchronizations.join(', ')}</div>
                        : null}

                        <div><strong>Lab: </strong>{result.lab.title}</div>
                        <div><strong>Project: </strong>{result.award.project}</div>
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
});

const Experiment = module.exports.Experiment = auditDecor(ExperimentComponent);

globals.listing_views.register(Experiment, 'Experiment');


var DatasetComponent =  React.createClass({
    render: function() {
        var result = this.props.context;
        var biosampleTerm, organism, lifeSpec, targets, lifeStages = [], ages = [];

        // Determine whether the dataset is a series or not
        var seriesDataset = result['@type'].indexOf('Series') >= 0;

        // Get the biosample info for Series types if any. Can be string or array. If array, only use iff 1 term name exists
        if (seriesDataset) {
            biosampleTerm = (result.biosample_term_name && typeof result.biosample_term_name === 'object' && result.biosample_term_name.length === 1) ? result.biosample_term_name[0] :
                ((result.biosample_term_name && typeof result.biosample_term_name === 'string') ? result.biosample_term_name : '');
            var organisms = _.uniq(result.organism && result.organism.length && result.organism.map(function(organism) {
                return organism.scientific_name;
            }));
            if (organisms.length === 1) {
                organism = organisms[0];
            }

            // Dig through the biosample life stages and ages
            if (result.related_datasets && result.related_datasets.length) {
                result.related_datasets.forEach(function(dataset) {
                    if (dataset.replicates && dataset.replicates.length) {
                        dataset.replicates.forEach(function(replicate) {
                            if (replicate.library && replicate.library.biosample) {
                                var biosample = replicate.library.biosample;
                                var lifeStage = (biosample.life_stage && biosample.life_stage !== 'unknown') ? biosample.life_stage : '';

                                if (lifeStage) { lifeStages.push(lifeStage); }
                                if (biosample.age_display) { ages.push(biosample.age_display); }
                            }
                        });
                    }
                });
                lifeStages = _.uniq(lifeStages);
                ages = _.uniq(ages);
            }
            lifeSpec = _.compact([lifeStages.length === 1 ? lifeStages[0] : null, ages.length === 1 ? ages[0] : null]);

            // Get list of target labels
            if (result.target) {
                targets = _.uniq(result.target.map(function(target) {
                    return target.label;
                }));
            }
        }

        var haveSeries = result['@type'].indexOf('Series') >= 0;
        var haveFileSet = result['@type'].indexOf('FileSet') >= 0;

        // For ReferenceEpigenome, calculate the donor diversity.
        let diversity = '';
        if (result['@type'][0] === 'ReferenceEpigenome') {
            diversity = donorDiversity(result);
        }

        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">{haveSeries ? 'Series' : (haveFileSet ? 'FileSet' : 'Dataset')}</p>
                        <p className="type">{' ' + result['accession']}</p>
                        <p className="type meta-status">{' ' + result['status']}</p>
                        {this.props.auditIndicators(result.audit, result['@id'], { search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {datasetTypes[result['@type'][0]]}
                            {seriesDataset ?
                                <span>
                                    {biosampleTerm ? <span>{' in ' + biosampleTerm}</span> : null}
                                    {organism || lifeSpec.length > 0 ?
                                        <span>
                                            {' ('}
                                            {organism ? <i>{organism}</i> : null}
                                            {lifeSpec.length > 0 ? <span>{organism ? ', ' : ''}{lifeSpec.join(', ')}</span> : null}
                                            {')'}
                                        </span>
                                    : null}
                                </span>
                            :
                                <span>{result.description ? <span>{': ' + result.description}</span> : null}</span>
                            }
                        </a>
                    </div>
                    <div className="data-row">
                        {result['dataset_type'] ? <div><strong>Dataset type: </strong>{result['dataset_type']}</div> : null}
                        {targets && targets.length ? <div><strong>Targets: </strong>{targets.join(', ')}</div> : null}
                        {diversity ? <div><strong>Donor diversity: </strong>{diversity}</div> : null}
                        <div><strong>Lab: </strong>{result.lab.title}</div>
                        <div><strong>Project: </strong>{result.award.project}</div>
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
});

const Dataset = module.exports.Dataset = auditDecor(DatasetComponent);

globals.listing_views.register(Dataset, 'Dataset');


var TargetComponent = React.createClass({
    render: function() {
        var result = this.props.context;
        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Target</p>
                        {this.props.auditIndicators(result.audit, result['@id'], { search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {result['label']}
                            {result.organism && result.organism.scientific_name ? <em>{' (' + result.organism.scientific_name + ')'}</em> : null}
                        </a>
                    </div>
                    <div className="data-row">
                        <strong>External resources: </strong>
                        {result.dbxref && result.dbxref.length ?
                            <DbxrefList values={result.dbxref} target_gene={result.gene_name} target_ref />
                        : <em>None submitted</em> }
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
});

const Target = module.exports.Target = auditDecor(TargetComponent);

globals.listing_views.register(Target, 'Target');


var Image = module.exports.Image = React.createClass({
    render: function() {
        var result = this.props.context;
        var Attachment = image.Attachment;
        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Image</p>
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>{result.caption}</a>
                    </div>
                    <div className="data-row">
                        <Attachment context={result} attachment={result.attachment} />
                    </div>
                </div>
            </li>
        );
    }
});

globals.listing_views.register(Image, 'Image');


// If the given term is selected, return the href for the term
function termSelected(term, facet, filters) {
    var selected = false;
    var filter;
    for (var filterName in filters) {
        filter = filters[filterName];
        if (facet.type === 'exists') {
            if ((filter.field === facet.field + '!' && term === 'no') ||
                (filter.field === facet.field && term === 'yes')) {
                selected = true; break;
            } 
        } else if (filter.field == facet.field && filter.term == term) {
            selected = true; break;
        }
    }
    if (selected) {
        return url.parse(filter.remove).search;
    } else {
        return null;
    }
}

// Determine whether any of the given terms are selected
function countSelectedTerms(terms, facet, filters) {
    var count = 0;
    for(var oneTerm in terms) {
        if(termSelected(terms[oneTerm].key, facet, filters)) {
            count++;
        }
    }
    return count;
}

var Term = search.Term = React.createClass({
    render: function () {
        var filters = this.props.filters;
        var term = this.props.term['key'];
        var count = this.props.term['doc_count'];
        var title = this.props.title || term;
        var facet = this.props.facet;
        var field = facet['field'];
        var em = field === 'target.organism.scientific_name' ||
                    field === 'organism.scientific_name' ||
                    field === 'replicates.library.biosample.donor.organism.scientific_name';
        var barStyle = {
            width:  Math.ceil( (count/this.props.total) * 100) + "%"
        };
        var selected = termSelected(term, facet, filters);
        var href;
        if (selected && !this.props.canDeselect) {
            href = null;
        } else if (selected) {
            href = selected;
        } else {
            if (facet.type === 'exists') {
                if (term === 'yes') {
                    href = this.props.searchBase + field + '=*';
                } else {
                    href = this.props.searchBase + field + '!=*';
                }
            } else {
                href = this.props.searchBase + field + '=' + globals.encodedURIComponent(term);
            }
        }
        return (
            <li id={selected ? "selected" : null} key={term}>
                {selected ? '' : <span className="bar" style={barStyle}></span>}
                {field === 'lot_reviews.status' ? <span className={globals.statusClass(term, 'indicator pull-left facet-term-key icon icon-circle')}></span> : null}
                <a id={selected ? "selected" : null} href={href} onClick={href ? this.props.onFilter : null}>
                    <span className="pull-right">{count} {selected && this.props.canDeselect ? <i className="icon icon-times-circle-o"></i> : ''}</span>
                    <span className="facet-item">
                        {em ? <em>{title}</em> : <span>{title}</span>}
                    </span>
                </a>
            </li>
        );
    }
});

var TypeTerm = search.TypeTerm = React.createClass({
    render: function () {
        var term = this.props.term['key'];
        var filters = this.props.filters;
        var title;
        try {
            title = types[term];
        } catch (e) {
            title = term;
        }
        var total = this.props.total;
        return <Term {...this.props} title={title} filters={filters} total={total} />;
    }
});


var Facet = search.Facet = React.createClass({
    getDefaultProps: function() {
        return {width: 'inherit'};
    },

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
        var title = facet['title'];
        var field = facet['field'];
        var total = facet['total'];
        var termID = title.replace(/\s+/g, '');
        var terms = facet['terms'].filter(function (term) {
            if (term.key) {
                for(var filter in filters) {
                    if(filters[filter].term === term.key) {
                        return true;
                    }
                }
                return term.doc_count > 0;
            } else {
                return false;
            }
        });
        var moreTerms = terms.slice(5);
        var TermComponent = field === 'type' ? TypeTerm : Term;
        var selectedTermCount = countSelectedTerms(moreTerms, field, filters);
        var moreTermSelected = selectedTermCount > 0;
        var canDeselect = (!facet.restrictions || selectedTermCount >= 2);
        var moreSecClass = 'collapse' + ((moreTermSelected || this.state.facetOpen) ? ' in' : '');
        var seeMoreClass = 'btn btn-link' + ((moreTermSelected || this.state.facetOpen) ? '' : ' collapsed');

        // Handle audit facet titles
        if (field.substr(0, 6) === 'audit.') {
            var titleParts = title.split(': ');
            var fieldParts = field.match(/^audit.(.+).category$/i);
            if (fieldParts && fieldParts.length === 2 && titleParts) {
                var iconClass = 'icon audit-activeicon-' + fieldParts[1].toLowerCase();
                title = <span>{titleParts[0]}: <i className={iconClass}></i></span>;
            } else {
                title = <span>{title}</span>;
            }
        }

        if (terms.length && terms.some(term => term.doc_count)) {
            return (
                <div className="facet">
                    <h5>{title}</h5>
                    <ul className="facet-list nav">
                        <div>
                            {terms.slice(0, 5).map(term =>
                                <TermComponent {...this.props} key={term.key} term={term} filters={filters} total={total} canDeselect={canDeselect} />
                            )}
                        </div>
                        {terms.length > 5 ?
                            <div id={termID} className={moreSecClass}>
                                {moreTerms.map(term =>
                                    <TermComponent {...this.props} key={term.key} term={term} filters={filters} total={total} canDeselect={canDeselect} />
                                )}
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
        return null;
    }
});

var TextFilter = search.TextFilter = React.createClass({

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
                        onChange={this.onChange} onBlur={this.onBlur} onKeyDown={this.onKeyDown} />
            </div>
        );
    },

    onChange: function(e) {
        e.stopPropagation();
        e.preventDefault();
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

    onKeyDown: function(e) {
        if (e.keyCode == 13) {
            this.onBlur(e);
            e.preventDefault();
        }
    }
});

var FacetList = search.FacetList = React.createClass({
    contextTypes: {
        session: React.PropTypes.object,
        hidePublicAudits: React.PropTypes.bool
    },

    getDefaultProps: function() {
        return {orientation: 'vertical'};
    },

    render: function() {
        var {context, term} = this.props;
        var loggedIn = this.context.session && this.context.session['auth.userid'];

        // Get all facets, and "normal" facets, meaning non-audit facets
        var facets = this.props.facets;
        var normalFacets = facets.filter(facet => facet.field.substring(0, 6) !== 'audit.');

        var filters = this.props.filters;
        var width = 'inherit';
        if (!facets.length && this.props.mode != 'picker') return <div />;
        var hideTypes;
        if (this.props.mode == 'picker') {
            hideTypes = false;
        } else {
            hideTypes = filters.filter(filter => filter.field === 'type').length === 1 && normalFacets.length > 1;
        }

        // See if we need the Clear Filters link or not. context.clear_filters 
        var clearButton; // JSX for the clear button
        var searchQuery = context && context['@id'] && url.parse(context['@id']).search;
        if (searchQuery) {
            // Convert search query string to a query object for easy parsing
            var terms = queryString.parse(searchQuery);

            // See if there are terms in the query string aside from `searchTerm`. We have a Clear
            // Filters button if we do
            var nonPersistentTerms = _(Object.keys(terms)).any(term => term !== 'searchTerm');
            clearButton = nonPersistentTerms && terms['searchTerm'];

            // If no Clear Filters button yet, do the same check with `type` in the query string
            if (!clearButton) {
                nonPersistentTerms = _(Object.keys(terms)).any(term => term !== 'type');
                clearButton = nonPersistentTerms && terms['type'];
            }
        }

        return (
            <div className="box facets">
                <div className={`orientation${this.props.orientation === 'horizontal' ? ' horizontal' : ''}`}>
                    {clearButton ?
                        <div className="clear-filters-control">
                            <a href={context.clear_filters}>Clear Filters <i className="icon icon-times-circle"></i></a>
                        </div>
                    : null}
                    {this.props.mode === 'picker' && !this.props.hideTextFilter ? <TextFilter {...this.props} filters={filters} /> : ''}
                    {facets.map(facet => {
                        if ((hideTypes && facet.field == 'type') || (!loggedIn && this.context.hidePublicAudits && facet.field.substring(0, 6) === 'audit.')) {
                            return <span key={facet.field} />;
                        } else {
                            return <Facet {...this.props} key={facet.field} facet={facet} filters={filters}
                                            width={width} />;
                        }
                    })}
                </div>
            </div>
        );
    }
});

var BatchDownload = search.BatchDownload = React.createClass({
    render: function () {
        var link = this.props.context['batch_download'];
        return (
            <Modal actuator={<button className="btn btn-info btn-sm">Download</button>}>
                <ModalHeader title="Using batch download" closeModal />
                <ModalBody>
                    <p>Click the "Download" button below to download a "files.txt" file that contains a list of URLs to a file containing all the experimental metadata and links to download the file.
                    The first line of the file will always be the URL to download the metadata file. <br />
                    Further description of the contents of the metadata file are described in the <a href="/help/batch-download/">Batch Download help doc</a>.</p><br />
                    <p>The "files.txt" file can be copied to any server.<br />
                    The following command using cURL can be used to download all the files in the list:</p><br />
                    <code>xargs -n 1 curl -O -L &lt; files.txt</code><br />
                </ModalBody>
                <ModalFooter closeModal={<a className="btn btn-info btn-sm">Close</a>}
                    submitBtn={<a data-bypass="true" target="_self" className="btn btn-info btn-sm" href={link}>{'Download'}</a>}
                    dontClose />
            </Modal>
        );
    },
});

var ResultTable = search.ResultTable = React.createClass({

    getDefaultProps: function() {
        return {
            restrictions: {},
            searchBase: ''
        };
    },

    childContextTypes: {actions: React.PropTypes.array},
    getChildContext: function() {
        return {
            actions: this.props.actions
        };
    },

    render: function() {
        const batchHubLimit = 100;
        var context = this.props.context;
        var results = context['@graph'];
        var total = context['total'];
        var batch_hub_disabled = total > batchHubLimit;
        var columns = context['columns'];
        var filters = context['filters'];
        var label = 'results';
        var searchBase = this.props.searchBase;
        var trimmedSearchBase = searchBase.replace(/[\?|\&]limit=all/, "");

        var facets = context['facets'].map((facet) => {
            if (this.props.restrictions[facet.field] !== undefined) {
                facet = _.clone(facet);
                facet.restrictions = this.props.restrictions[facet.field];
                facet.terms = facet.terms.filter(term => _.contains(facet.restrictions, term.key));
            }
            return facet;
        });

        // See if a specific result type was requested ('type=x')
        // Satisfied iff exactly one type is in the search
        if (results.length) {
            var specificFilter;
            filters.forEach(function(filter) {
                if (filter.field === 'type') {
                    specificFilter = specificFilter ? '' : filter.term;
                }
            });
        }

        // Get a sorted list of batch hubs keys with case-insensitive sort
        var batchHubKeys = [];
        if (context.batch_hub && Object.keys(context.batch_hub).length) {
            batchHubKeys = Object.keys(context.batch_hub).sort((a, b) => {
                var aLower = a.toLowerCase();
                var bLower = b.toLowerCase();
                return (aLower > bLower) ? 1 : ((aLower < bLower) ? -1 : 0);
            });
        }

        // Map view icons to svg icons
        var view2svg = {
            'table': 'table',
            'th': 'matrix'
        };

        return (
            <div>
                <div className="row">
                    {facets.length ? <div className="col-sm-5 col-md-4 col-lg-3">
                        <FacetList {...this.props} facets={facets} filters={filters}
                                    searchBase={searchBase ? searchBase + '&' : searchBase + '?'} onFilter={this.onFilter} />
                    </div> : ''}
                    <div className="col-sm-7 col-md-8 col-lg-9">
                        {context['notification'] === 'Success' ?
                            <div>
                                <h4>Showing {results.length} of {total} {label}</h4>

                                <div className="results-table-control">
                                    {context.views ?
                                        <div className="btn-attached">
                                            {context.views.map((view, i) =>
                                                <a key={i} className="btn btn-info btn-sm btn-svgicon" href={view.href} title={view.title}>{svgIcon(view2svg[view.icon])}</a>
                                            )}
                                        </div>
                                    : null}

                                    {total > results.length && searchBase.indexOf('limit=all') === -1 ?
                                        <a rel="nofollow" className="btn btn-info btn-sm"
                                                href={searchBase ? searchBase + '&limit=all' : '?limit=all'}
                                                onClick={this.onFilter}>View All</a>
                                    :
                                        <span>
                                            {results.length > 25 ?
                                                <a className="btn btn-info btn-sm"
                                                    href={trimmedSearchBase ? trimmedSearchBase : "/search/"}
                                                    onClick={this.onFilter}>View 25</a>
                                            : null}
                                        </span>
                                    }

                                    {context['batch_download'] ?
                                        <BatchDownload context={context} />
                                    : null}

                                    {batchHubKeys && context.batch_hub ?
                                        <DropdownButton disabled={batch_hub_disabled} label="batchhub" title={batch_hub_disabled ? 'Filter to ' + batchHubLimit + ' to visualize' : 'Visualize'} wrapperClasses="results-table-button">
                                            <DropdownMenu>
                                                {batchHubKeys.map(assembly =>
                                                    <a key={assembly} data-bypass="true" target="_blank" href={context['batch_hub'][assembly]}>
                                                        {assembly}
                                                    </a>
                                                )}
                                            </DropdownMenu>
                                        </DropdownButton>
                                    : null}
                                </div>
                            </div>
                        :
                            <h4>{context['notification']}</h4>
                        }
                        <hr />
                        <ul className="nav result-table" id="result-table">
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
        e.preventDefault();
    }
});

var Search = search.Search = React.createClass({
    contextTypes: {
        location_href: React.PropTypes.string,
        navigate: React.PropTypes.func
    },

    render: function() {
        var context = this.props.context;
        var results = context['@graph'];
        var notification = context['notification'];
        var searchBase = url.parse(this.context.location_href).search || '';
        var facetdisplay = context.facets && context.facets.some(function(facet) {
            return facet.total > 0;
        });
        return (
            <div>
                {facetdisplay ?
                    <div className="panel data-display main-panel">
                        <ResultTable {...this.props} key={undefined} searchBase={searchBase} onChange={this.context.navigate} />
                    </div>
                : <h4>{notification}</h4>}
            </div>
        );
    }
});

globals.content_views.register(Search, 'Search');
