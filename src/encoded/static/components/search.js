'use strict';
var React = require('react');
import PropTypes from 'prop-types';
import createReactClass from 'create-react-class';
var queryString = require('query-string');
var button = require('../libs/bootstrap/button');
var {Modal, ModalHeader, ModalBody, ModalFooter} = require('../libs/bootstrap/modal');
var dropdownMenu = require('../libs/bootstrap/dropdown-menu');
import { TabPanel, TabPanelPane } from '../libs/bootstrap/panel';
var svgIcon = require('../libs/svg-icons').svgIcon;
var url = require('url');
var _ = require('underscore');
import { auditDecor } from './audit';
var globals = require('./globals');
var image = require('./image');
var search = module.exports;
import GenomeBrowser from './genome_browser';
var { donorDiversity, BrowserSelector } = require('./objectutils');
var dbxref = require('./dbxref');
var objectutils = require('./objectutils');
var {BiosampleSummaryString, BiosampleOrganismNames} = require('./typeutils');

var DbxrefList = dbxref.DbxrefList;
var statusOrder = globals.statusOrder;
var SingleTreatment = objectutils.SingleTreatment;
var DropdownButton = button.DropdownButton;
var DropdownMenu = dropdownMenu.DropdownMenu;


// Should really be singular...
const types = {
    annotation: { title: 'Annotation file set' },
    antibody_lot: { title: 'Antibodies' },
    biosample: { title: 'Biosamples' },
    experiment: { title: 'Experiments' },
    target: { title: 'Targets' },
    dataset: { title: 'Datasets' },
    image: { title: 'Images' },
    matched_set: { title: 'Matched set series' },
    organism_development_series: { title: 'Organism development series' },
    publication: { title: 'Publications' },
    page: { title: 'Web page' },
    pipeline: { title: 'Pipeline' },
    project: { title: 'Project file set' },
    publication_data: { title: 'Publication file set' },
    reference: { title: 'Reference file set' },
    reference_epigenome: { title: 'Reference epigenome series' },
    replication_timing_series: { title: 'Replication timing series' },
    software: { title: 'Software' },
    treatment_concentration_series: { title: 'Treatment concentration series' },
    treatment_time_series: { title: 'Treatment time series' },
    ucsc_browser_composite: { title: 'UCSC browser composite file set' },
};

const datasetTypes = {
    Annotation: types.annotation.title,
    Dataset: types.dataset.title,
    MatchedSet: types.matched_set.title,
    OrganismDevelopmentSeries: types.organism_development_series.title,
    Project: types.project.title,
    PublicationData: types.publication_data.title,
    Reference: types.reference.title,
    ReferenceEpigenome: types.reference_epigenome.title,
    ReplicationTimingSeries: types.replication_timing_series.title,
    TreatmentConcentrationSeries: types.treatment_concentration_series.title,
    TreatmentTimeSeries: types.treatment_time_series.title,
    UcscBrowserComposite: types.ucsc_browser_composite.title,
};

const listing = module.exports.listing = function (reactProps) {
    // XXX not all panels have the same markup
    let context;
    let viewProps = reactProps;
    if (reactProps['@id']) {
        context = reactProps;
        viewProps = { context: context, key: context['@id'] };
    }
    const ListingView = globals.listing_views.lookup(viewProps.context);
    return <ListingView {...viewProps} />;
};

const PickerActions = module.exports.PickerActions = createReactClass ({
    contextTypes: {
        actions: PropTypes.array,
    },

    render: function () {
        if (this.context.actions && this.context.actions.length) {
            return (
                <div className="pull-right">
                    {this.context.actions.map(action => React.cloneElement(action, { key: this.props.context.name, id: this.props.context['@id'] }))}
                </div>
            );
        } else {
            return <span />;
        }
    },
});

var ItemComponent = createReactClass({
    render: function() {
        var result = this.props.context;
        var title = globals.listing_titles.lookup(result)({context: result});
        var itemType = result['@type'][0];
        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    {result.accession ?
                        <div className="pull-right type sentence-case search-meta">
                            <p>{itemType}: {` ${result.accession}`}</p>
                            <AuditIndicators audits={result.audit} id={this.props.context['@id']} search />
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
    },
});

const Item = module.exports.Item = auditDecor(ItemComponent);

globals.listing_views.register(Item, 'Item');


// Display one antibody status indicator
const StatusIndicator = createReactClass({
    propTypes: {
        status: PropTypes.string,
        terms: PropTypes.array,
    },

    getInitialState: function () {
        return {
            tipOpen: false,
            tipStyles: {},
        };
    },

    // Display tooltip on hover
    onMouseEnter: function () {
        function getNextElementSibling(el) {
            // IE8 doesn't support nextElementSibling
            return el.nextElementSibling ? el.nextElementSibling : el.nextSibling;
        }

        // Get viewport bounds of result table and of this tooltip
        let whiteSpace = 'nowrap';
        const resultBounds = document.getElementById('result-table').getBoundingClientRect();
        const resultWidth = resultBounds.right - resultBounds.left;
        const tipBounds = _.clone(getNextElementSibling(this.refs.indicator.getDOMNode()).getBoundingClientRect());
        const tipWidth = tipBounds.right - tipBounds.left;
        let width = tipWidth;
        if (tipWidth > resultWidth) {
            // Tooltip wider than result table; set tooltip to result table width and allow text to wrap
            tipBounds.right = (tipBounds.left + resultWidth) - 2;
            whiteSpace = 'normal';
            width = tipBounds.right - tipBounds.left - 2;
        }

        // Set an inline style to move the tooltip if it runs off right edge of result table
        const leftOffset = resultBounds.right - tipBounds.right;
        if (leftOffset < 0) {
            // Tooltip goes outside right edge of result table; move it to the left
            this.setState({ tipStyles: { left: `${leftOffset + 10}px`, maxWidth: `${resultWidth}px`, whiteSpace: whiteSpace, width: `${width}px` } });
        } else {
            // Tooltip fits inside result table; move it to native position
            this.setState({ tipStyles: { left: '10px', maxWidth: `${resultWidth}px`, whiteSpace: whiteSpace, width: `${width}px` } });
        }

        this.setState({ tipOpen: true });
    },

    // Close tooltip when not hovering
    onMouseLeave: function () {
        this.setState({ tipStyles: { maxWidth: 'none', whiteSpace: 'nowrap', width: 'auto', left: '15px' } }); // Reset position and width
        this.setState({ tipOpen: false });
    },

    render: function() {
        const classes = `tooltip-status sentence-case${this.state.tipOpen ? ' tooltipopen' : ''}`;

        return (
            <span className="tooltip-status-trigger">
                <i className={globals.statusClass(this.props.status, 'indicator icon icon-circle')} ref="indicator" onMouseEnter={this.onMouseEnter} onMouseLeave={this.onMouseLeave} />
                <div className={classes} style={this.state.tipStyles}>
                    {this.props.status}<br /><span>{this.props.terms.join(', ')}</span>
                </div>
            </span>
        );
    },
});

// Display the status indicators for one target
const StatusIndicators = createReactClass({
    propTypes: {
        targetTree: PropTypes.object,
        target: PropTypes.string,
    },

    render: function () {
        const targetTree = this.props.targetTree;
        const target = this.props.target;

        return (
            <span className="status-indicators">
                {Object.keys(targetTree[target]).map((status, i) => {
                    if (status !== 'target') {
                        return <StatusIndicator key={i} status={status} terms={targetTree[target][status]} />;
                    }
                    return null;
                })}
            </span>
        );
    },
});

var AntibodyComponent = createReactClass({
    render: function() {
        var result = this.props.context;

        // Sort the lot reviews by their status according to our predefined order
        // given in the statusOrder array.
        const lotReviews = _.sortBy(result.lot_reviews, lotReview => _.indexOf(globals.statusOrder, lotReview.status)); // Use underscore indexOf so that this works in IE8

        // Build antibody display object as a hierarchy: target=>status=>biosample_term_names
        const targetTree = {};
        lotReviews.forEach((lotReview) => {
            lotReview.targets.forEach((target) => {
                // If we haven't seen this target, save it in targetTree along with the
                // corresponding target and organism structures.
                if (!targetTree[target.name]) {
                    targetTree[target.name] = { target: target };
                }
                const targetNode = targetTree[target.name];

                // If we haven't seen the status, save it in the targetTree target
                if (!targetNode[lotReview.status]) {
                    targetNode[lotReview.status] = [];
                }
                const statusNode = targetNode[lotReview.status];

                // If we haven't seen the biosample term name, save it in the targetTree target status
                if (statusNode.indexOf(lotReview.biosample_term_name) === -1) {
                    statusNode.push(lotReview.biosample_term_name);
                }
            });
        });

        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Antibody</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <p className="type meta-status">{` ${result.status}`}</p>
                        {this.props.auditIndicators(result.audit, result['@id'], { search: true })}
                    </div>
                    <div className="accession">
                        {Object.keys(targetTree).map(target =>
                            <div key={target}>
                                <a href={result['@id']}>
                                    {targetTree[target].target.label}
                                    {targetTree[target].target.organism ? <span>{' ('}<i>{targetTree[target].target.organism.scientific_name}</i>{')'}</span> : ''}
                                </a>
                                <StatusIndicators targetTree={targetTree} target={target} />
                            </div>
                        )}
                    </div>
                    <div className="data-row">
                        <div><strong>Source: </strong>{result.source.title}</div>
                        <div><strong>Product ID / Lot ID: </strong>{result.product_id} / {result.lot_id}</div>
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { except: result['@id'], forcedEditLink: true })}
            </li>
        );
    },
});

const Antibody = module.exports.Antibody = auditDecor(AntibodyComponent);

globals.listing_views.register(Antibody, 'AntibodyLot');


var BiosampleComponent = createReactClass({
    render: function() {
        const result = this.props.context;
        const lifeStage = (result.life_stage && result.life_stage !== 'unknown') ? ` ${result.life_stage}` : '';
        const age = (result.age && result.age !== 'unknown') ? ` ${result.age}` : '';
        const ageUnits = (result.age_units && result.age_units !== 'unknown' && age) ? ` ${result.age_units}` : '';
        const separator = (lifeStage || age) ? ',' : '';
        const rnais = (result.rnais[0] && result.rnais[0].target && result.rnais[0].target.label) ? result.rnais[0].target.label : '';
        let constructs;

        if (result.model_organism_donor_constructs && result.model_organism_donor_constructs.length) {
            constructs = result.model_organism_donor_constructs[0].target.label;
        } else {
            constructs = result.constructs[0] ? result.constructs[0].target.label : '';
        }
        const treatment = (result.treatments[0] && result.treatments[0].treatment_term_name) ? result.treatments[0].treatment_term_name : '';
        const mutatedGenes = result.donor && result.donor.mutated_gene && result.donor.mutated_gene.label;

        // Build the text of the synchronization string
        let synchText;
        if (result.synchronization) {
            synchText = result.synchronization +
                (result.post_synchronization_time ?
                    ` + ${result.post_synchronization_time}${result.post_synchronization_time_units ? ` ${result.post_synchronization_time_units}` : ''}`
                : '');
        }

        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Biosample</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <p className="type meta-status">{` ${result.status}`}</p>
                        {this.props.auditIndicators(result.audit, result['@id'], { search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {`${result.biosample_term_name} (`}
                            <em>{result.organism.scientific_name}</em>
                            {`${separator}${lifeStage}${age}${ageUnits})`}
                        </a>
                    </div>
                    <div className="data-row">
                        <div><strong>Type: </strong>{result.biosample_type}</div>
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
    },
});

const Biosample = module.exports.Biosample = auditDecor(BiosampleComponent);

globals.listing_views.register(Biosample, 'Biosample');


var ExperimentComponent = createReactClass({
    render: function() {
        var result = this.props.context;

        // Collect all biosamples associated with the experiment. This array can contain duplicate
        // biosamples, but no null entries.
        let biosamples = [];
        if (result.replicates && result.replicates.length) {
            biosamples = _.compact(result.replicates.map(replicate => replicate.library && replicate.library.biosample));
        }

        // Get all biosample organism names
        const organismNames = biosamples.length ? BiosampleOrganismNames(biosamples) : [];

        // Collect synchronizations
        const synchronizations = _.uniq(result.replicates.filter(replicate =>
            replicate.library && replicate.library.biosample && replicate.library.biosample.synchronization
        ).map((replicate) => {
            const biosample = replicate.library.biosample;
            return (biosample.synchronization +
                (biosample.post_synchronization_time ?
                    ` + ${biosample.post_synchronization_time}${biosample.post_synchronization_time_units ? ` ${biosample.post_synchronization_time_units}` : ''}`
                : ''));
        }));

        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Experiment</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <p className="type meta-status">{` ${result.status}`}</p>
                        {this.props.auditIndicators(result.audit, result['@id'], { search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {result.assay_title ?
                                <span>{result.assay_title}</span>
                            :
                                <span>{result.assay_term_name}</span>
                            }
                            {result.biosample_term_name ? <span>{` of ${result.biosample_term_name}`}</span> : null}
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
    },
});

const Experiment = module.exports.Experiment = auditDecor(ExperimentComponent);

globals.listing_views.register(Experiment, 'Experiment');


var DatasetComponent =  createReactClass({
    render: function() {
        const result = this.props.context;
        let biosampleTerm;
        let organism;
        let lifeSpec;
        let targets;
        let lifeStages = [];
        let ages = [];

        // Determine whether the dataset is a series or not
        const seriesDataset = result['@type'].indexOf('Series') >= 0;

        // Get the biosample info for Series types if any. Can be string or array. If array, only use iff 1 term name exists
        if (seriesDataset) {
            biosampleTerm = (result.biosample_term_name && typeof result.biosample_term_name === 'object' && result.biosample_term_name.length === 1) ? result.biosample_term_name[0] :
                ((result.biosample_term_name && typeof result.biosample_term_name === 'string') ? result.biosample_term_name : '');
            const organisms = _.uniq(result.organism && result.organism.length && result.organism.map(resultOrganism => resultOrganism.scientific_name));
            if (organisms.length === 1) {
                organism = organisms[0];
            }

            // Dig through the biosample life stages and ages
            if (result.related_datasets && result.related_datasets.length) {
                result.related_datasets.forEach((dataset) => {
                    if (dataset.replicates && dataset.replicates.length) {
                        dataset.replicates.forEach((replicate) => {
                            if (replicate.library && replicate.library.biosample) {
                                const biosample = replicate.library.biosample;
                                const lifeStage = (biosample.life_stage && biosample.life_stage !== 'unknown') ? biosample.life_stage : '';

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
                targets = _.uniq(result.target.map(target => target.label));
            }
        }

        const haveSeries = result['@type'].indexOf('Series') >= 0;
        const haveFileSet = result['@type'].indexOf('FileSet') >= 0;

        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">{haveSeries ? 'Series' : (haveFileSet ? 'FileSet' : 'Dataset')}</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <p className="type meta-status">{` ${result.status}`}</p>
                        {this.props.auditIndicators(result.audit, result['@id'], { search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {datasetTypes[result['@type'][0]]}
                            {seriesDataset ?
                                <span>
                                    {biosampleTerm ? <span>{` in ${biosampleTerm}`}</span> : null}
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
                                <span>{result.description ? <span>{`: ${result.description}`}</span> : null}</span>
                            }
                        </a>
                    </div>
                    <div className="data-row">
                        {result.dataset_type ? <div><strong>Dataset type: </strong>{result.dataset_type}</div> : null}
                        {targets && targets.length ? <div><strong>Targets: </strong>{targets.join(', ')}</div> : null}
                        <div><strong>Lab: </strong>{result.lab.title}</div>
                        <div><strong>Project: </strong>{result.award.project}</div>
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { except: result['@id'], forcedEditLink: true })}
            </li>
        );
    },
});

const Dataset = module.exports.Dataset = auditDecor(DatasetComponent);

globals.listing_views.register(Dataset, 'Dataset');


var TargetComponent = createReactClass({
    render: function() {
        const result = this.props.context;
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
                            {result.label}
                            {result.organism && result.organism.scientific_name ? <em>{` (${result.organism.scientific_name})`}</em> : null}
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
    },
});

const Target = module.exports.Target = auditDecor(TargetComponent);

globals.listing_views.register(Target, 'Target');


const Image = module.exports.Image = createReactClass({
    render: function() {
        const result = this.props.context;
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
    },
});

globals.listing_views.register(Image, 'Image');


// If the given term is selected, return the href for the term
function termSelected(term, facet, filters) {
    let matchingFilter;

    const selected = Object.keys(filters).some((filterKey) => {
        const filter = filters[filterKey];
        if (facet.type === 'exists') {
            if ((filter.field === `${facet.field}!` && term === 'no') ||
                (filter.field === facet.field && term === 'yes')) {
                matchingFilter = filter;
                return true;
            }
        } else if (filter.field === facet.field && filter.term === term) {
            matchingFilter = filter;
            return true;
        }
        return false;
    });
    if (selected) {
        return url.parse(matchingFilter.remove).search;
    }
    return null;
}

// Determine whether any of the given terms are selected
function countSelectedTerms(terms, facet, filters) {
    let count = 0;
    Object.keys(terms).forEach((termKey) => {
        if (termSelected(terms[termKey].key, facet, filters)) {
            count += 1;
        }
    });
    return count;
}

const Term = search.Term = createReactClass({
    propTypes: {
        filters: PropTypes.array,
        term: PropTypes.object,
        title: PropTypes.string,
        facet: PropTypes.object,
        total: PropTypes.number,
        canDeselect: PropTypes.bool,
        searchBase: PropTypes.string,
        onFilter: PropTypes.func,
    },

    render: function () {
        const filters = this.props.filters;
        const term = this.props.term.key;
        const count = this.props.term.doc_count;
        const title = this.props.title || term;
        const facet = this.props.facet;
        const field = facet.field;
        const em = field === 'target.organism.scientific_name' ||
                    field === 'organism.scientific_name' ||
                    field === 'replicates.library.biosample.donor.organism.scientific_name';
        const barStyle = {
            width: `${Math.ceil((count / this.props.total) * 100)}%`,
        };
        const selected = termSelected(term, facet, filters);
        let href;
        if (selected && !this.props.canDeselect) {
            href = null;
        } else if (selected) {
            href = selected;
        } else if (facet.type === 'exists') {
            if (term === 'yes') {
                href = `${this.props.searchBase}${field}=*`;
            } else {
                href = `${this.props.searchBase}${field}!=*`;
            }
        } else {
            href = `${this.props.searchBase}${field}=${globals.encodedURIComponent(term)}`;
        }
        return (
            <li id={selected ? 'selected' : null} key={term}>
                {selected ? '' : <span className="bar" style={barStyle} />}
                {field === 'lot_reviews.status' ? <span className={globals.statusClass(term, 'indicator pull-left facet-term-key icon icon-circle')} /> : null}
                <a id={selected ? 'selected' : null} href={href} onClick={href ? this.props.onFilter : null}>
                    <span className="pull-right">{count} {selected && this.props.canDeselect ? <i className="icon icon-times-circle-o" /> : ''}</span>
                    <span className="facet-item">
                        {em ? <em>{title}</em> : <span>{title}</span>}
                    </span>
                </a>
            </li>
        );
    },
});

const TypeTerm = search.TypeTerm = createReactClass({
    propTypes: {
        term: PropTypes.object,
        filters: PropTypes.array,
        total: PropTypes.number,
    },

    render: function () {
        const term = this.props.term.key;
        const filters = this.props.filters;
        let title;
        try {
            title = types[term];
        } catch (e) {
            title = term;
        }
        const total = this.props.total;
        return <Term {...this.props} title={title} filters={filters} total={total} />;
    },
});


const Facet = search.Facet = createReactClass({
    propTypes: {
        facet: PropTypes.object,
        filters: PropTypes.array,
        width: PropTypes.string,
    },

    getDefaultProps: function () {
        return { width: 'inherit' };
    },

    getInitialState: function () {
        return {
            facetOpen: false,
        };
    },

    handleClick: function () {
        this.setState({ facetOpen: !this.state.facetOpen });
    },

    render: function () {
        const facet = this.props.facet;
        const filters = this.props.filters;
        let title = facet.title;
        const field = facet.field;
        const total = facet.total;
        const termID = title.replace(/\s+/g, '');
        const terms = facet.terms.filter((term) => {
            if (term.key) {
                const found = Object.keys(filters).some(filterKey => filters[filterKey].term === term.key);
                if (!found) {
                    return term.doc_count > 0;
                }
                return found;
            }
            return false;
        });
        const moreTerms = terms.slice(5);
        const TermComponent = field === 'type' ? TypeTerm : Term;
        const selectedTermCount = countSelectedTerms(moreTerms, field, filters);
        const moreTermSelected = selectedTermCount > 0;
        const canDeselect = (!facet.restrictions || selectedTermCount >= 2);
        const moreSecClass = `collapse${(moreTermSelected || this.state.facetOpen) ? ' in' : ''}`;
        const seeMoreClass = `btn btn-link${(moreTermSelected || this.state.facetOpen) ? '' : ' collapsed'}`;

        // Handle audit facet titles
        if (field.substr(0, 6) === 'audit.') {
            const titleParts = title.split(': ');
            const fieldParts = field.match(/^audit.(.+).category$/i);
            if (fieldParts && fieldParts.length === 2 && titleParts) {
                const iconClass = `icon audit-activeicon-${fieldParts[1].toLowerCase()}`;
                title = <span>{titleParts[0]}: <i className={iconClass} /></span>;
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


const TextFilter = search.TextFilter = createReactClass({
    propTypes: {
        filters: PropTypes.array,
        searchBase: PropTypes.string,
        onChange: PropTypes.func,
    },

    onChange: function (e) {
        e.stopPropagation();
        e.preventDefault();
    },

    onBlur: function (e) {
        let searchStr = this.props.searchBase.replace(/&?searchTerm=[^&]*/, '');
        const value = e.target.value;
        if (value) {
            searchStr += `searchTerm=${e.target.value}`;
        } else {
            searchStr = searchStr.substring(0, searchStr.length - 1);
        }
        this.props.onChange(searchStr);
    },

    onKeyDown: function (e) {
        if (e.keyCode === 13) {
            this.onBlur(e);
            e.preventDefault();
        }
    },

    getValue: function () {
        const filter = this.props.filters.filter(f => f.field === 'searchTerm');
        return filter.length ? filter[0].term : '';
    },

    shouldUpdateComponent: function (nextProps) {
        return (this.getValue(this.props) !== this.getValue(nextProps));
    },

    render: function () {
        return (
            <div className="facet">
                <input
                    ref="input" type="search" className="form-control search-query"
                    placeholder="Enter search term(s)"
                    defaultValue={this.getValue(this.props)}
                    onChange={this.onChange} onBlur={this.onBlur} onKeyDown={this.onKeyDown}
                />
            </div>
        );
    },
});

const FacetList = search.FacetList = createReactClass({
    propTypes: {
        context: PropTypes.object,
        facets: PropTypes.oneOfType([
            PropTypes.array,
            PropTypes.object,
        ]),
        filters: PropTypes.array,
        mode: PropTypes.string,
        orientation: PropTypes.string,
        hideTextFilter: PropTypes.bool,
    },

    contextTypes: {
        session: PropTypes.object,
    },

    getDefaultProps: function () {
        return { orientation: 'vertical' };
    },

    render: function () {
        const { context } = this.props;
        const loggedIn = this.context.session && this.context.session['auth.userid'];

        // Get all facets, and "normal" facets, meaning non-audit facets
        const facets = this.props.facets;
        const normalFacets = facets.filter(facet => facet.field.substring(0, 6) !== 'audit.');

        const filters = this.props.filters;
        let width = 'inherit';
        if (!facets.length && this.props.mode !== 'picker') return <div />;
        let hideTypes;
        if (this.props.mode === 'picker') {
            hideTypes = false;
        } else {
            hideTypes = filters.filter(filter => filter.field === 'type').length === 1 && normalFacets.length > 1;
        }
        if (this.props.orientation === 'horizontal') {
            width = `${100 / facets.length}%`;
        }

        // See if we need the Clear Filters link or not. context.clear_filters
        let clearButton; // JSX for the clear button
        const searchQuery = context && context['@id'] && url.parse(context['@id']).search;
        if (searchQuery) {
            // Convert search query string to a query object for easy parsing
            const terms = queryString.parse(searchQuery);

            // See if there are terms in the query string aside from `searchTerm`. We have a Clear
            // Filters button if we do
            let nonPersistentTerms = _(Object.keys(terms)).any(term => term !== 'searchTerm');
            clearButton = nonPersistentTerms && terms.searchTerm;

            // If no Clear Filters button yet, do the same check with `type` in the query string
            if (!clearButton) {
                nonPersistentTerms = _(Object.keys(terms)).any(term => term !== 'type');
                clearButton = nonPersistentTerms && terms.type;
            }
        }

        return (
            <div className="box facets">
                <div className={`orientation${this.props.orientation === 'horizontal' ? ' horizontal' : ''}`}>
                    {clearButton ?
                        <div className="clear-filters-control">
                            <a href={context.clear_filters}>Clear Filters <i className="icon icon-times-circle" /></a>
                        </div>
                    : null}
                    {this.props.mode === 'picker' && !this.props.hideTextFilter ? <TextFilter {...this.props} filters={filters} /> : ''}
                    {facets.map((facet) => {
                        if ((hideTypes && facet.field === 'type') || (!loggedIn && facet.field.substring(0, 6) === 'audit.')) {
                            return <span key={facet.field} />;
                        }
                        return <Facet {...this.props} key={facet.field} facet={facet} filters={filters} width={width} />;
                    })}
                </div>
            </div>
        );
    },
});

const BatchDownload = search.BatchDownload = createReactClass({
    propTypes: {
        context: PropTypes.object,
    },

    render: function () {
        const link = this.props.context.batch_download;
        return (
            <Modal actuator={<button className="btn btn-info btn-sm">Download</button>}>
                <ModalHeader title="Using batch download" closeModal />
                <ModalBody>
                    <p>Click the &ldquo;Download&rdquo; button below to download a &ldquo;files.txt&rdquo; file that contains a list of URLs to a file containing all the experimental metadata and links to download the file.
                    The first line of the file will always be the URL to download the metadata file. <br />
                    Further description of the contents of the metadata file are described in the <a href="/help/batch-download/">Batch Download help doc</a>.</p><br />
                    <p>The &ldquo;files.txt&rdquo; file can be copied to any server.<br />
                    The following command using cURL can be used to download all the files in the list:</p><br />
                    <code>xargs -n 1 curl -O -L &lt; files.txt</code><br />
                </ModalBody>
                <ModalFooter
                    closeModal={<a className="btn btn-info btn-sm">Close</a>}
                    submitBtn={<a data-bypass="true" target="_self" className="btn btn-info btn-sm" href={link}>{'Download'}</a>}
                    dontClose
                />
            </Modal>
        );
    },
});


const ResultTable = search.ResultTable = createReactClass({
    propTypes: {
        context: PropTypes.object,
        actions: PropTypes.array,
        restrictions: PropTypes.object,
        assemblies: PropTypes.array, // List of assemblies of all 'File' objects in search results
        searchBase: PropTypes.string,
        onChange: PropTypes.func,
        mode: PropTypes.string,
        currentRegion: PropTypes.func,
    },

    childContextTypes: { actions: PropTypes.array },

    contextTypes: {
        session: React.PropTypes.object,
    },

    getDefaultProps: function () {
        return {
            restrictions: {},
            searchBase: '',
        };
    },

    getInitialState: function () {
        return {
            browserAssembly: this.props.assemblies && this.props.assemblies[0], // Currently selected assembly for the browser
            selectedTab: '',
        };
    },

    getChildContext: function () {
        return {
            actions: this.props.actions,
        };
    },

    componentDidMount: function () {
        if (window !== undefined) {
            // Determining this in componentDidMount to avoid server/client reactJS conflict.
            if (window.location.hash === '#browser') {
                this.setState({ selectedTab: 'browserpane' });
            }
        }
    },

    onFilter: function (e) {
        const searchStr = e.currentTarget.getAttribute('href');
        this.props.onChange(searchStr);
        e.stopPropagation();
        e.preventDefault();
        this.setState({ selectedTab: 'listpane' });  // Always return to listpane so that browser can rerender
    },

    // Called when new value chosen from assembly dropdown.
    assemblyChange: function (e) {
        this.setState({ browserAssembly: e.target.value });
    },

    handleTabClick: function (tab) {
        // Since we force TabPanel tab selection, we need to keep track of selectedTab.
        if (this.state.selectedTab !== tab) {
            this.setState({ selectedTab: tab });
        }
        console.log(`selectedTab: ${tab}`);
    },

    render: function () {
        const visualizeLimit = 100;
        const { context, searchBase, assemblies } = this.props;
        const results = context['@graph'];
        const total = context.total;
        const visualizeDisabled = total > visualizeLimit;
        const columns = context.columns;
        const filters = context.filters;
        const label = 'results';
        const trimmedSearchBase = searchBase.replace(/[\?|&]limit=all/, '');
        const loggedIn = this.context.session && this.context.session['auth.userid'];
        let browseAllFiles = true; // True to pass all files to browser
        let browserAssembly = ''; // Assembly to pass to ResultsBrowser component
        let browserDatasets = []; // Datasets will be used to get vis_json blobs
        let browserFiles = [];   // Files to pass to ResultsBrowser component
        let assemblyChooser;

        const facets = context.facets.map((facet) => {
            if (this.props.restrictions[facet.field] !== undefined) {
                const workFacet = _.clone(facet);
                workFacet.restrictions = this.props.restrictions[workFacet.field];
                workFacet.terms = workFacet.terms.filter(term => _.contains(workFacet.restrictions, term.key));
            }
            return facet;
        });

        // See if a specific result type was requested ('type=x')
        // Satisfied iff exactly one type is in the search
        if (results.length) {
            let specificFilter;
            filters.forEach((filter) => {
                if (filter.field === 'type') {
                    specificFilter = specificFilter ? '' : filter.term;
                }
            });
        }

        // Get a sorted list of batch hubs keys with case-insensitive sort
        // NOTE: Tim thinks this is overkill as opposed to simple sort()
        let visualizeKeys = [];
        if (context.visualize_batch && Object.keys(context.visualize_batch).length) {
            visualizeKeys = Object.keys(context.visualize_batch).sort((a, b) => {
                const aLower = a.toLowerCase();
                const bLower = b.toLowerCase();
                return (aLower > bLower) ? 1 : ((aLower < bLower) ? -1 : 0);
            });
        }

        // Map view icons to svg icons
        const view2svg = {
            table: 'table',
            th: 'matrix',
        };

        // Check whether the search query qualifies for a genome browser display. Start by counting
        // the number of "type" filters exist.
        let typeFilter;
        const counter = filters.reduce((prev, curr) => {
            if (curr.field === 'type') {
                typeFilter = curr;
                return prev + 1;
            }
            return prev;
        }, 0);

        // If we have only one "type" term in the query string and it's for File, then we can
        // display the List/Browser tabs. Otherwise we just get the list.
        let browserAvail = counter === 1 && typeFilter && typeFilter.term === 'File' && assemblies.length === 1 && loggedIn;
        if (browserAvail) {
            // If dataset is in the query string, we can show all files.
            const datasetFilter = filters.find(filter => filter.field === 'dataset');
            if (datasetFilter) {
                browseAllFiles = true;

                // Probably not worth a define in globals.js for visualizable types and statuses.
                browserFiles = results.filter(file => ['bigBed', 'bigWig'].indexOf(file.file_format) > -1);
                if (browserFiles.length > 0) {
                    browserFiles = browserFiles.filter(file =>
                        ['released', 'in progress', 'archived'].indexOf(file.status) > -1
                    );
                }
                browserAvail = (browserFiles.length > 0);

                if (browserAvail) {
                    // Distill down to a list of datasets so they can be passed to genome_browser code.
                    browserDatasets = browserFiles.reduce((datasets, file) => (
                        (!file.dataset || datasets.indexOf(file.dataset) > -1) ? datasets : datasets.concat(file.dataset)
                    ), []);
                }
            } else {
                browseAllFiles = false;
                browserAvail = false;    // NEW: Limit browser option to type=File&dataset=... only!
            }
        }

        if (browserAvail) {
            // Now determine if we have a mix of assemblies in the files, or just one. If we have
            // a mix, we need to render a drop-down.
            if (assemblies.length === 1) {
                // Only one assembly in all the files. No menu needed.
                browserAssembly = assemblies[0];
                // empty div to avoid warning only.
                assemblyChooser = (
                    <div className="browser-assembly-chooser" />
                );
            } else {
                browserAssembly = this.state.browserAssembly;
                assemblyChooser = (
                    <div className="browser-assembly-chooser">
                        <div className="browser-assembly-chooser__title">Assembly:</div>
                        <div className="browser-assembly-chooser__menu">
                            <AssemblyChooser assemblies={assemblies} assemblyChange={this.assemblyChange} />
                        </div>
                    </div>
                );
            }
        }

        return (
            <div>
                <div className="row">
                    {facets.length ? <div className="col-sm-5 col-md-4 col-lg-3">
                        <FacetList
                            {...this.props} facets={facets} filters={filters}
                            searchBase={searchBase ? `${searchBase}&` : `${searchBase}?`} onFilter={this.onFilter}
                        />
                    </div> : ''}
                    <div className="col-sm-7 col-md-8 col-lg-9">

                        {context.notification === 'Success' ?
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
                                        <a
                                            rel="nofollow" className="btn btn-info btn-sm"
                                            href={searchBase ? `${searchBase}&limit=all` : '?limit=all'}
                                            onClick={this.onFilter}
                                        >
                                            View All
                                        </a>
                                    :
                                        <span>
                                            {results.length > 25 ?
                                                <a
                                                    className="btn btn-info btn-sm"
                                                    href={trimmedSearchBase || '/search/'}
                                                    onClick={this.onFilter}
                                                >
                                                    View 25
                                                </a>
                                            : null}
                                        </span>
                                    }

                                    {context.batch_download ?
                                        <BatchDownload context={context} />
                                    : null}

                                    {visualizeKeys && context.visualize_batch ?
                                        <BrowserSelector
                                            visualizeCfg={context.visualize_batch}
                                            disabled={visualizeDisabled}
                                            title={visualizeDisabled ? `Filter to ${visualizeLimit} to visualize` : 'Visualize'}
                                        />
                                    : null}
                                </div>
                                <hr />
                                {browserAvail ?
                                    <TabPanel tabs={{ listpane: 'List', browserpane: <BrowserTabQuickView /> }} selectedTab={this.state.selectedTab} handleTabClick={this.handleTabClick} tabFlange>
                                        <TabPanelPane key="listpane">
                                            <ResultTableList results={results} columns={columns} tabbed />
                                        </TabPanelPane>
                                        <TabPanelPane key="browserpane">
                                            {assemblyChooser}
                                            <ResultBrowser files={results} assembly={browserAssembly} datasets={browserDatasets} limitFiles={!browseAllFiles} currentRegion={this.props.currentRegion} />
                                        </TabPanelPane>
                                    </TabPanel>
                                :
                                    <ResultTableList results={results} columns={columns} />
                                }
                            </div>
                        :
                            <h4>{context.notification}</h4>
                        }
                    </div>
                </div>
            </div>
        );
    },
});


const BrowserTabQuickView = React.createClass({
    render: function () {
        return <div>Quick View <span className="beta-badge">BETA</span></div>;
    },
});


const ResultTableList = createReactClass({
    propTypes: {
        results: PropTypes.array.isRequired, // Array of search results to display
        columns: PropTypes.object.isRequired, // Columns from search results
        tabbed: PropTypes.bool, // True if table is in a tab
    },

    render: function () {
        const { results, columns, tabbed } = this.props;
        return (
            <ul className={`nav result-table${tabbed ? ' result-table-tabbed' : ''}`} id="result-table">
                {results.length ?
                    results.map(result => listing({ context: result, columns: columns, key: result['@id'] }))
                : null}
            </ul>
        );
    },
});


// Display a local genome browser in the ResultTable where search results would normally go. This
// only gets displayed if the query string contains only one type and it's "File."
const ResultBrowser = createReactClass({
    propTypes: {
        files: PropTypes.array, // Array of files whose browser we're rendering
        assembly: PropTypes.string, // Filter `files` by this assembly
        datasets: PropTypes.array, // One or more '/dataset/ENCSRnnnXXX/' that files belong to
        limitFiles: PropTypes.bool, // True to limit browsing to 20 files
        currentRegion: PropTypes.func,
    },

    render: function () {
        let visUrl = '';
        const datasetCount = this.props.datasets.length;
        let region;  // optionally make a persistent region
        const lastRegion = this.props.currentRegion();
        if (lastRegion && lastRegion.assembly === this.props.assembly) {
            region = lastRegion.region;
            console.log('found region %s', region);
        }
        if (datasetCount === 1) {
            // /datasets/{ENCSR000AEI}/@@hub/{hg19}/jsonout/trackDb.txt
            visUrl = `${this.props.datasets[0]}/@@hub/${this.props.assembly}/jsonout/trackDb.txt`;
        } else if (datasetCount > 1) {
            // /batch_hub/type%3DExperiment%2C%2Caccession%3D{ENCSR000AAA}%2C%2Caccession%3D{ENCSR000AEI}%2C%2Caccjson/{hg19}/trackDb.txt
            for (let ix = 0; ix < datasetCount; ix += 1) {
                const accession = this.props.datasets[ix].split('/')[2];
                visUrl += `accession=${accession}%2C%2C`;
            }
            visUrl = `batch_hub/type=Experiment/${visUrl}&accjson/${this.props.assembly}/trackDb.txt`;
        }
        if (datasetCount > 0) {
            return (
                <FetchedData ignoreErrors>
                    <Param name="visBlobs" url={visUrl} />
                    <GenomeBrowser files={this.props.files} assembly={this.props.assembly} limitFiles={this.props.limitFiles} region={region} currentRegion={this.props.currentRegion} />
                </FetchedData>
            );
        }
        return (
            <div>
                <GenomeBrowser files={this.props.files} assembly={this.props.assembly} limitFiles={this.props.limitFiles} region={region} currentRegion={this.props.currentRegion} />
            </div>
        );
    },
});


// Display a dropdown menu of the given assemblies.
const AssemblyChooser = createReactClass({
    propTypes: {
        assemblies: PropTypes.array, // Array of assemblies to include in the dropdown
        currentAssembly: PropTypes.string, // Currently selected assembly
        assemblyChange: PropTypes.func, // Function to call when the user chooses a new assembly
    },

    render: function () {
        const { assemblies, currentAssembly, assemblyChange } = this.props;

        return (
            <select className="form-control" value={currentAssembly} onChange={assemblyChange}>
                {assemblies.map((assembly, i) =>
                    <option key={i} value={assembly}>{assembly}</option>
                )}
            </select>
        );
    },
});


const Search = search.Search = createReactClass({
    propTypes: {
        context: PropTypes.object,
    },

    contextTypes: {
        location_href: PropTypes.string,
        navigate: PropTypes.func,
    },

    // optionally make a persistent region
    lastRegion: {
        assembly: React.PropTypes.string,
        region: React.PropTypes.string,
    },

    currentRegion: function (assembly, region) {
        if (assembly && region) {
            this.lastRegion = {
                assembly: assembly,
                region: region,
            };
        }
        return this.lastRegion;
    },

    render: function () {
        const context = this.props.context;
        const notification = context.notification;
        const searchBase = url.parse(this.context.location_href).search || '';
        const facetdisplay = context.facets && context.facets.some(facet => facet.total > 0);
        let assemblies = [];

        // Make an array of all assemblies found in all files in the search results.
        const results = this.props.context['@graph'];
        const files = results.length ? results.filter(result => result['@type'][0] === 'File') : [];
        if (files.length) {
            // Reduce all found file assemblies so we don't have duplicates in the 'assemblies' array.
            assemblies = files.reduce((assembliesAcc, file) => ((!file.assembly || assembliesAcc.indexOf(file.assembly) > -1) ? assembliesAcc : assembliesAcc.concat(file.assembly)), []);
        }

        return (
            <div>
                {facetdisplay ?
                    <div className="panel data-display main-panel">
                        <ResultTable {...this.props} key={undefined} searchBase={searchBase} assemblies={assemblies} onChange={this.context.navigate} currentRegion={this.currentRegion} />
                    </div>
                : <h4>{notification}</h4>}
            </div>
        );
    },
});

globals.content_views.register(Search, 'Search');
