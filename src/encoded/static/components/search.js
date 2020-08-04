import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { Panel, PanelBody } from '../libs/ui/panel';
import QueryString from '../libs/query_string';
import { auditDecor } from './audit';
import { CartToggle, CartSearchControls } from './cart';
import FacetRegistry from './facets';
import * as globals from './globals';
import {
    DisplayAsJson,
    DocTypeTitle,
    singleTreatment,
} from './objectutils';
import { DbxrefList } from './dbxref';
import Status from './status';
import { BiosampleSummaryString, BiosampleOrganismNames } from './typeutils';
import { BatchDownloadControls, ViewControls } from './view_controls';
import { BrowserSelector } from './vis_defines';


// Should really be singular...
const types = {
    annotation: { title: 'Annotation file set' },
    antibody_lot: { title: 'Antibodies' },
    biosample_type: { title: 'Biosample types' },
    biosample: { title: 'Biosamples' },
    computational_model: { title: 'Computational model file set' },
    experiment: { title: 'Experiments' },
    gene: { title: 'Genes' },
    target: { title: 'Targets' },
    dataset: { title: 'Datasets' },
    image: { title: 'Images' },
    matched_set: { title: 'Matched set series' },
    aggregate_series: { title: 'Aggregate series' },
    functional_characterization_series: { title: 'Functional characterization series' },
    single_cell_rna_series: { title: 'Single cell RNA series' },
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
    functional_characterization_experiment: { title: 'Functional characterization experiments' },
    transgenic_enhancer_experiment: { title: 'Transgenic enhancer experiments' },
};

const datasetTypes = {
    Annotation: types.annotation.title,
    Dataset: types.dataset.title,
    MatchedSet: types.matched_set.title,
    OrganismDevelopmentSeries: types.organism_development_series.title,
    Project: types.project.title,
    PublicationData: types.publication_data.title,
    Reference: types.reference.title,
    ComputationalModel: types.computational_model.title,
    ReferenceEpigenome: types.reference_epigenome.title,
    ReplicationTimingSeries: types.replication_timing_series.title,
    TreatmentConcentrationSeries: types.treatment_concentration_series.title,
    TreatmentTimeSeries: types.treatment_time_series.title,
    AggregateSeries: types.aggregate_series.title,
    FunctionalCharacterizationSeries: types.functional_characterization_series.title,
    SingleCellRnaSeries: types.single_cell_rna_series.title,
    UcscBrowserComposite: types.ucsc_browser_composite.title,
    FunctionalCharacterizationExperiment: types.functional_characterization_experiment.title,
    TransgenicEnhancerExperiment: types.transgenic_enhancer_experiment.title,
};

const getUniqueTreatments = treatments => _.uniq(treatments.map(treatment => singleTreatment(treatment)));

// session storage used to preserve opened/closed facets
const FACET_STORAGE = 'FACET_STORAGE';

// marker for determining user just opened the page
const MARKER_FOR_NEWLY_LOADED_FACET_PREFIX = 'MARKER_FOR_NEWLY_LOADED_FACETS_';

/**
 * Maximum  downloadable result count
 */
const MAX_DOWNLOADABLE_RESULT = 500;

// You can use this function to render a listing view for the search results object with a couple
// options:
//   1. Pass a search results object directly in props. listing returns a React component that you
//      can render directly.
//
//   2. Pass an object of the form:
//      {
//          context: context object to render
//          ...any other props you want to pass to the panel-rendering component
//      }
//
// Note: this function really doesn't do much of value, but it does do something and it's been
// around since the beginning of encoded, so it stays for now.

export function Listing(reactProps) {
    // XXX not all panels have the same markup
    let context;
    let viewProps = reactProps;
    if (reactProps['@id']) {
        context = reactProps;
        viewProps = { context, key: context['@id'] };
    }
    const ListingView = globals.listingViews.lookup(viewProps.context);
    return <ListingView {...viewProps} />;
}


/**
 * Generate a CSS class for the <li> of a search result table item.
 * @param {object} item Displayed search result object
 *
 * @return {string} CSS class for this type of object
 */
export const resultItemClass = item => `result-item--type-${item['@type'][0]}`;

export const PickerActions = ({ context }, reactContext) => {
    if (reactContext.actions && reactContext.actions.length > 0) {
        return (
            <div className="result-item__picker">
                {reactContext.actions.map(action => React.cloneElement(action, { key: context.name, id: context['@id'] }))}
            </div>
        );
    }

    // No actions; don't render anything.
    return null;
};

PickerActions.propTypes = {
    context: PropTypes.object.isRequired,
};

PickerActions.contextTypes = {
    actions: PropTypes.array,
};


const ItemComponent = ({ context: result, auditIndicators, auditDetail }, reactContext) => {
    const title = globals.listingTitles.lookup(result)({ context: result });
    const itemType = result['@type'][0];
    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">{title}</a>
                    <div className="result-item__data-row">
                        {result.description}
                    </div>
                </div>
                {result.accession ?
                    <div className="result-item__meta">
                        <div className="result-item__meta-title">{itemType}: {` ${result.accession}`}</div>
                        {auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
                    </div>
                : null}
                <PickerActions context={result} />
            </div>
            {auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, except: result['@id'], forcedEditLink: true })}
        </li>
    );
};

ItemComponent.propTypes = {
    context: PropTypes.object.isRequired, // Component to render in a listing view
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ItemComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Item = auditDecor(ItemComponent);

globals.listingViews.register(Item, 'Item');


/* eslint-disable react/prefer-stateless-function */
class BiosampleComponent extends React.Component {
    render() {
        const result = this.props.context;
        const lifeStage = (result.life_stage && result.life_stage !== 'unknown') ? ` ${result.life_stage}` : '';
        const ageDisplay = (result.age_display && result.age_display !== '') ? ` ${result.age_display}` : '';
        const separator = (lifeStage || ageDisplay) ? ',' : '';
        const treatment = (result.treatments && result.treatments.length > 0) ? result.treatments[0].treatment_term_name : '';

        // Calculate genetic modification properties for display.
        const rnais = [];
        const constructs = [];
        const mutatedGenes = [];
        if (result.applied_modifications && result.applied_modifications.length > 0) {
            result.applied_modifications.forEach((am) => {
                // Collect RNAi GM methods.
                if (am.method === 'RNAi' && am.modified_site_by_target_id && am.modified_site_by_target_id.name) {
                    rnais.push(am.modified_site_by_target_id.name);
                }

                // Collect construct GM methods.
                if (am.purpose === 'tagging' && am.modified_site_by_target_id && am.modified_site_by_target_id.name) {
                    constructs.push(am.modified_site_by_target_id.name);
                }

                // Collect mutated gene GM methods.
                if ((am.category === 'deletion' || am.category === 'mutagenesis') && am.modified_site_by_target_id && am.modified_site_by_target_id.name) {
                    mutatedGenes.push(am.modified_site_by_target_id.name);
                }
            });
        }

        // Build the text of the synchronization string
        let synchText;
        if (result.synchronization) {
            synchText = `${result.synchronization}${result.post_synchronization_time ? ` +${ageDisplay}` : ''}`;
        }

        return (
            <li className={resultItemClass(result)}>
                <div className="result-item">
                    <div className="result-item__data">
                        <a href={result['@id']} className="result-item__link">
                            {`${result.biosample_ontology.term_name} (`}
                            <em>{result.organism.scientific_name}</em>
                            {`${separator}${lifeStage}${ageDisplay})`}
                        </a>
                        <div className="result-item__data-row">
                            <div><strong>Type: </strong>{result.biosample_ontology.classification}</div>
                            {result.summary ? <div><strong>Summary: </strong>{BiosampleSummaryString(result)}</div> : null}
                            {rnais.length > 0 ? <div><strong>RNAi targets: </strong>{rnais.join(', ')}</div> : null}
                            {constructs.length > 0 ? <div><strong>Constructs: </strong>{constructs.join(', ')}</div> : null}
                            {treatment ? <div><strong>Treatment: </strong>{treatment}</div> : null}
                            {mutatedGenes.length > 0 ? <div><strong>Mutated genes: </strong>{mutatedGenes.join(', ')}</div> : null}
                            {result.culture_harvest_date ? <div><strong>Culture harvest date: </strong>{result.culture_harvest_date}</div> : null}
                            {result.date_obtained ? <div><strong>Date obtained: </strong>{result.date_obtained}</div> : null}
                            {synchText ? <div><strong>Synchronization timepoint: </strong>{synchText}</div> : null}
                            <div><strong>Source: </strong>{result.source.title}</div>
                        </div>
                    </div>
                    <div className="result-item__meta">
                        <div className="result-item__meta-title">Biosample</div>
                        <div className="result-item__meta-id">{` ${result.accession}`}</div>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, sessionProperties: this.context.session_properties, search: true })}
                    </div>
                    <PickerActions context={result} />
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, sessionProperties: this.context.session_properties })}
            </li>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

BiosampleComponent.propTypes = {
    context: PropTypes.object.isRequired, // Biosample search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

BiosampleComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Biosample = auditDecor(BiosampleComponent);

globals.listingViews.register(Biosample, 'Biosample');


/**
 * Renders both Experiment, FunctionalCharacterizationExperiment, TransgenicEnhancerExperiment search results.
 */
const ExperimentComponent = (props, reactContext) => {
    const { context: result, cartControls, mode } = props;
    let synchronizations;

    // Determine whether object is Experiment, FunctionalCharacterizationExperiment, or TransgenicEnhancerExperiment.
    const experimentType = result['@type'][0];
    const isFunctionalExperiment = experimentType === 'FunctionalCharacterizationExperiment';
    const isEnhancerExperiment = experimentType === 'TransgenicEnhancerExperiment';
    let displayType;
    if (isFunctionalExperiment) {
        displayType = 'Functional Characterization Experiment';
    } else if (isEnhancerExperiment) {
        displayType = 'Transgenic Enhancer Experiment';
    } else {
        displayType = 'Experiment';
    }

    // Collect all biosamples associated with the experiment. This array can contain duplicate
    // biosamples, but no null entries.
    let biosamples = [];
    const treatments = [];

    if (isEnhancerExperiment) {
        if (result.biosamples && result.biosamples.length > 0) {
            biosamples = result.biosamples.map(sample => biosamples);
        }
    } else {
        if (result.replicates && result.replicates.length > 0) {
            biosamples = _.compact(result.replicates.map(replicate => replicate.library && replicate.library.biosample));
        }
        // flatten treatment array of arrays
        _.compact(biosamples.map(biosample => biosample.treatments)).forEach(treatment => treatment.forEach(t => treatments.push(t)));
    }

    // Get all biosample organism names
    const organismNames = biosamples.length > 0 ? BiosampleOrganismNames(biosamples) : [];

    // Collect synchronizations
    if (isEnhancerExperiment) {
        if (biosamples && biosamples.length > 0) {
            synchronizations = _.uniq(biosamples.filter(biosample => biosample && biosample.synchronization).map((biosample) => {
                return `${biosample.synchronization}${biosample.post_synchronization_time ? ` + ${biosample.age_display}` : ''}`;
            }));
        }
    } else if (result.replicates && result.replicates.length > 0) {
        synchronizations = _.uniq(result.replicates.filter(replicate =>
            replicate.library && replicate.library.biosample && replicate.library.biosample.synchronization
        ).map((replicate) => {
            const biosample = replicate.library.biosample;
            return `${biosample.synchronization}${biosample.post_synchronization_time ? ` + ${biosample.age_display}` : ''}`;
        }));
    }

    const uniqueTreatments = getUniqueTreatments(treatments);

    // Get a map of related datasets, possibly filtering on their status and
    // categorized by their type.
    let seriesMap = {};
    if (result.related_series && result.related_series.length > 0) {
        seriesMap = _.groupBy(
            result.related_series, series => series['@type'][0]
        );
    }

    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">
                        {result.assay_title ?
                            <span>{result.assay_title}</span>
                        :
                            <span>{result.assay_term_name}</span>
                        }
                        {result.biosample_ontology && result.biosample_ontology.term_name ? <span>{` of ${result.biosample_ontology.term_name}`}</span> : null}
                    </a>
                    {result.biosample_summary ?
                        <div className="result-item__highlight-row">
                            {organismNames.length > 0 ?
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
                    <div className="result-item__data-row">
                        {result.target && result.target.label ?
                            <div><strong>Target: </strong>{result.target.label}</div>
                        : null}

                        {mode !== 'cart-view' ?
                            <React.Fragment>
                                {synchronizations && synchronizations.length > 0 ?
                                    <div><strong>Synchronization timepoint: </strong>{synchronizations.join(', ')}</div>
                                : null}

                                <div><strong>Lab: </strong>{result.lab.title}</div>
                                <div><strong>Project: </strong>{result.award.project}</div>
                                {treatments && treatments.length > 0 ?
                                    <div><strong>Treatment{uniqueTreatments.length !== 1 ? 's' : ''}: </strong>
                                        <span>
                                            {uniqueTreatments.join(', ')}
                                        </span>
                                    </div>
                                : null}
                                {Object.keys(seriesMap).map(seriesType =>
                                    <div key={seriesType}>
                                        <strong>{seriesType.replace(/([A-Z])/g, ' $1')}: </strong>
                                        {seriesMap[seriesType].map(
                                            (series, i) => (
                                                <span key={series.accession}>
                                                    {i > 0 ? ', ' : null}
                                                    <a href={series['@id']}>
                                                        {series.accession}
                                                    </a>
                                                </span>
                                            )
                                        )}
                                    </div>
                                )}
                            </React.Fragment>
                        : null}
                    </div>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">{displayType}</div>
                    <div className="result-item__meta-id">{` ${result.accession}`}</div>
                    {mode !== 'cart-view' ?
                        <React.Fragment>
                            <Status item={result.status} badgeSize="small" css="result-table__status" />
                            {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
                        </React.Fragment>
                    : null}
                </div>
                {cartControls && !(reactContext.actions && reactContext.actions.length > 0) ?
                    <div className="result-item__cart-control">
                        <CartToggle element={result} />
                    </div>
                : null}
                <PickerActions context={result} />
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties })}
        </li>
    );
};

ExperimentComponent.propTypes = {
    context: PropTypes.object.isRequired, // Experiment search results
    cartControls: PropTypes.bool, // True if displayed in active cart
    mode: PropTypes.string, // Special search-result modes, e.g. "picker"
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired,
};

ExperimentComponent.defaultProps = {
    cartControls: false,
    mode: '',
};

ExperimentComponent.contextTypes = {
    session: PropTypes.object,
    actions: PropTypes.array,
    session_properties: PropTypes.object,
};

const Experiment = auditDecor(ExperimentComponent);

globals.listingViews.register(Experiment, 'Experiment');
globals.listingViews.register(Experiment, 'FunctionalCharacterizationExperiment');
globals.listingViews.register(Experiment, 'TransgenicEnhancerExperiment');


const DatasetComponent = (props, reactContext) => {
    const result = props.context;
    let biosampleTerm;
    let organism;
    let lifeSpec;
    let targets;
    let lifeStages = [];
    let ages = [];
    let treatments = [];

    // Determine whether the dataset is a series or not
    const seriesDataset = result['@type'].indexOf('Series') >= 0;

    // Get the biosample info for Series types if any. Can be string or array. If array, only use iff 1 term name exists
    if (seriesDataset) {
        biosampleTerm = (result.biosample_ontology && Array.isArray(result.biosample_ontology) && result.biosample_ontology.length === 1 && result.biosample_ontology[0].term_name) ? result.biosample_ontology[0].term_name : ((result.biosample_ontology && result.biosample_ontology.term_name) ? result.biosample_ontology.term_name : '');
        const organisms = (result.organism && result.organism.length > 0) ? _.uniq(result.organism.map(resultOrganism => resultOrganism.scientific_name)) : [];
        if (organisms.length === 1) {
            organism = organisms[0];
        }

        // Dig through the biosample life stages and ages
        if (result.related_datasets && result.related_datasets.length > 0) {
            result.related_datasets.forEach((dataset) => {
                if (dataset.replicates && dataset.replicates.length > 0) {
                    dataset.replicates.forEach((replicate) => {
                        if (replicate.library && replicate.library.biosample) {
                            const biosample = replicate.library.biosample;
                            const lifeStage = (biosample.life_stage && biosample.life_stage !== 'unknown') ? biosample.life_stage : '';

                            if (lifeStage) { lifeStages.push(lifeStage); }
                            if (biosample.age_display) { ages.push(biosample.age_display); }
                            if (biosample.treatments) { treatments = [...treatments, ...biosample.treatments]; }
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
    const uniqueTreatments = getUniqueTreatments(treatments);

    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">
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
                    <div className="result-item__data-row">
                        {result.dataset_type ? <div><strong>Dataset type: </strong>{result.dataset_type}</div> : null}
                        {targets && targets.length > 0 ? <div><strong>Targets: </strong>{targets.join(', ')}</div> : null}
                        <div><strong>Lab: </strong>{result.lab.title}</div>
                        <div><strong>Project: </strong>{result.award.project}</div>
                        { treatments && treatments.length > 0 ?
                                <div><strong>Treatment{uniqueTreatments.length !== 1 ? 's' : ''}: </strong>
                                    <span>
                                        {uniqueTreatments.join(', ')}
                                    </span>
                                </div>
                            : null}
                    </div>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">{haveSeries ? 'Series' : (haveFileSet ? 'FileSet' : 'Dataset')}</div>
                    <div className="result-item__meta-id">{` ${result.accession}`}</div>
                    <Status item={result.status} badgeSize="small" css="result-table__status" />
                    {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
                </div>
                <PickerActions context={result} />
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties })}
        </li>
    );
};

DatasetComponent.propTypes = {
    context: PropTypes.object.isRequired, // Dataset search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

DatasetComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Dataset = auditDecor(DatasetComponent);

globals.listingViews.register(Dataset, 'Dataset');


const TargetComponent = ({ context: result, auditIndicators, auditDetail }, reactContext) => (
    <li className={resultItemClass(result)}>
        <div className="result-item">
            <div className="result-item__data">
                <a href={result['@id']} className="result-item__link">
                    {result.label} ({result.organism && result.organism.scientific_name ? <i>{result.organism.scientific_name}</i> : <span>{result.investigated_as[0]}</span>})
                </a>
                <div className="result-item__target-external-resources">
                    <p>External resources:</p>
                    {result.dbxrefs && result.dbxrefs.length > 0 ?
                        <DbxrefList context={result} dbxrefs={result.dbxrefs} />
                    : <em>None submitted</em> }
                </div>
            </div>
            <div className="result-item__meta">
                <div className="result-item__meta-title">Target</div>
                {auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
            </div>
            <PickerActions context={result} />
        </div>
        {auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, except: result['@id'], forcedEditLink: true })}
    </li>
);

TargetComponent.propTypes = {
    context: PropTypes.object.isRequired, // Target search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

TargetComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Target = auditDecor(TargetComponent);

globals.listingViews.register(Target, 'Target');


const Image = (props) => {
    const result = props.context;

    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">{result['@id']}</a>
                    <div className="attachment">
                        <div className="file-thumbnail">
                            <img src={result.thumb_nail} alt="thumbnail" />
                        </div>
                    </div>
                    {result.caption}
                </div>
                <div className="result-item__meta">
                    <p className="type meta-title">Image</p>
                    <Status item={result.status} badgeSize="small" css="result-table__status" />
                </div>
                <PickerActions context={result} />
            </div>
        </li>
    );
};

Image.propTypes = {
    context: PropTypes.object.isRequired, // Image search results
};

globals.listingViews.register(Image, 'Image');


/**
 * Entry field for filtering the results list when search results appear in edit forms.
 *
 * @export
 * @class TextFilter
 * @extends {React.Component}
 */
export class TextFilter extends React.Component {
    constructor() {
        super();

        // Bind `this` to non-React component methods.
        this.performSearch = this.performSearch.bind(this);
        this.onKeyDown = this.onKeyDown.bind(this);
    }

    /**
    * Keydown event handler
    *
    * @param {object} e Key down event
    * @memberof TextFilter
    * @private
    */
    onKeyDown(e) {
        if (e.keyCode === 13) {
            this.performSearch(e);
            e.preventDefault();
        }
    }

    getValue() {
        const filter = this.props.filters.filter(f => f.field === 'searchTerm');
        return filter.length > 0 ? filter[0].term : '';
    }

    /**
    * Makes call to do search
    *
    * @param {object} e Event
    * @memberof TextFilter
    * @private
    */
    performSearch(e) {
        let searchStr = this.props.searchBase.replace(/&?searchTerm=[^&]*/, '');
        const value = e.target.value;
        if (value) {
            searchStr += `searchTerm=${e.target.value}`;
        } else {
            searchStr = searchStr.substring(0, searchStr.length - 1);
        }
        this.props.onChange(searchStr);
    }

    shouldUpdateComponent(nextProps) {
        return (this.getValue(this.props) !== this.getValue(nextProps));
    }

    /**
    * Provides view for @see {@link TextFilter}
    *
    * @returns {object} @see {@link TextFilter} React's JSX object
    * @memberof TextFilter
    * @public
    */
    render() {
        return (
            <div className="facet">
                <input
                    type="search"
                    className="search-query"
                    placeholder="Enter search term(s)"
                    defaultValue={this.getValue(this.props)}
                    onKeyDown={this.onKeyDown}
                    data-test="filter-search-box"
                />
            </div>
        );
    }
}

TextFilter.propTypes = {
    filters: PropTypes.array.isRequired,
    searchBase: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
};


// Displays the entire list of facets. It contains a number of <Facet> components.
export const FacetList = (props) => {
    const { context, facets, filters, mode, orientation, hideTextFilter, addClasses, docTypeTitleSuffix, supressTitle, onFilter, isExpandable } = props;

    const [expandedFacets, setExpandFacets] = React.useState(new Set());

    // Get facets from storage that need to be expanded
    React.useEffect(() => {
        const facetsStorage = sessionStorage.getItem(FACET_STORAGE);
        const facetList = new Set(facetsStorage ? facetsStorage.split(',') : []);

        sessionStorage.setItem(FACET_STORAGE, facetList.size !== 0 ? [...facetList].join(',') : []);
        setExpandFacets(facetList); // initalize facet collapse-state
    }, []);

    // Only on initialize load, get facets from facet-section and schema that need to be expanded
    React.useEffect(() => {
        const facetsStorage = sessionStorage.getItem(FACET_STORAGE);
        const facetList = new Set(facetsStorage ? facetsStorage.split(',') : []);

        facets.forEach((facet) => {
            const field = facet.field;
            const newlyLoadedFacetStorage = `${MARKER_FOR_NEWLY_LOADED_FACET_PREFIX}${field}`;
            const isFacetNewlyLoaded = sessionStorage.getItem(newlyLoadedFacetStorage);

            const relevantFilters = context && context.filters.filter(filter => (
                filter.field === facet.field || filter.field === `${facet.field}!`
            ));

            // auto-open facets based on selected terms (see url) or it set in the schema (open_on_load)
            if (!isFacetNewlyLoaded && ((relevantFilters && relevantFilters.length > 0) || facet.open_on_load === true)) {
                sessionStorage.setItem(newlyLoadedFacetStorage, field); // ensure this is not called again on this active session storage
                facetList.add(facet.field);
            }
        });

        sessionStorage.setItem(FACET_STORAGE, facetList.size !== 0 ? [...facetList].join(',') : []);
        setExpandFacets(facetList); // initalize facet collapse-state
    }, [context, facets]);

    if (facets.length === 0 && mode !== 'picker') {
        return <div />;
    }

    const parsedUrl = context && context['@id'] && url.parse(context['@id']);

    /**
     * Handlers opening or closing a tab
     *
     * @param {event} e React synthetic event
     * @param {bool} status True for open, false for closed
     * @param {string} field Tab name
     */
    const handleExpanderClick = (e, status, field) => {
        let facetList = null;

        if (e.altKey) {
            // user has held down option-key (alt-key in Windows and Linux)
            sessionStorage.removeItem(FACET_STORAGE);
            facetList = new Set(status ? [] : facets.map(f => f.field));
        } else {
            facetList = new Set(expandedFacets);
            facetList[status ? 'delete' : 'add'](field);
        }

        sessionStorage.setItem(FACET_STORAGE, [...facetList].join(',')); // replace rather than update memory
        setExpandFacets(facetList); // controls open/closed facets
    };

    /**
     * Called when user types a key while focused on a facet term. If the user types a space or
     * return we call the term click handler -- needed for a11y because we have a <div> acting as a
     * button instead of an actual <button>.
     *
     * @param {event} e React synthetic event
     * @param {bool} status True for open, false for closed
     * @param {string} field Tab name
    */
    const handleKeyDown = (e, status, field) => {
        if (e.keyCode === 13 || e.keyCode === 32) {
            // keyCode: 13 = enter-key. 32 = spacebar
            e.preventDefault();
            handleExpanderClick(e, status, field);
        }
    };

    // See if we need the Clear filters link based on combinations of query-string parameters.
    let clearButton = false;
    const searchQuery = parsedUrl && parsedUrl.search;
    if (!supressTitle && searchQuery) {
        const querySearchTerm = new QueryString(parsedUrl.query);
        const queryType = querySearchTerm.clone();

        // We have a Clear Filters button if we have "searchTerm" or "advancedQuery" and *anything*
        // else.
        const hasSearchTerm = querySearchTerm.queryCount('searchTerm') > 0 || querySearchTerm.queryCount('advancedQuery') > 0;
        if (hasSearchTerm) {
            querySearchTerm.deleteKeyValue('searchTerm').deleteKeyValue('advancedQuery');
            clearButton = querySearchTerm.queryCount() > 0;
        }

        // If no Clear Filters button yet, do the same check with `type` in the query string.
        if (!clearButton) {
            // We have a Clear Filters button if we have "type" and *anything* else.
            const hasType = queryType.queryCount('type') > 0;
            if (hasType) {
                queryType.deleteKeyValue('type');
                clearButton = queryType.queryCount() > 0;
            }
        }
    }

    return (
        <div className="search-results__facets">
            <div className={`box facets${addClasses ? ` ${addClasses}` : ''}`}>
                <div className={`orientation${orientation === 'horizontal' ? ' horizontal' : ''}`} data-test="facetcontainer">
                    {(!supressTitle || clearButton) ?
                        <div className="search-header-control">
                            <DocTypeTitle searchResults={context} wrapper={children => <h1>{children} {docTypeTitleSuffix}</h1>} />
                            {context.clear_filters ?
                                <ClearFilters searchUri={context.clear_filters} enableDisplay={clearButton} />
                            : null}
                        </div>
                    : null}
                    {mode === 'picker' && !hideTextFilter ? <TextFilter {...props} filters={filters} /> : ''}
                    <div className="facet-wrapper">
                        {facets.map((facet) => {
                            // Filter the filters to just the ones relevant to the current facet,
                            // matching negation filters too.
                            const relevantFilters = context && context.filters.filter(filter => (
                                filter.field === facet.field || filter.field === `${facet.field}!`
                            ));

                            // Look up the renderer registered for this facet and use it to render this
                            // facet if a renderer exists. A non-existing renderer supresses the
                            // display of a facet.
                            const FacetRenderer = FacetRegistry.Facet.lookup(facet.field);
                            const isExpanded = expandedFacets.has(facet.field);
                            return FacetRenderer && <FacetRenderer
                                key={facet.field}
                                facet={facet}
                                results={context}
                                mode={mode}
                                relevantFilters={relevantFilters}
                                pathname={parsedUrl.pathname}
                                queryString={parsedUrl.query}
                                onFilter={onFilter}
                                isExpanded={isExpanded}
                                handleExpanderClick={handleExpanderClick}
                                handleKeyDown={handleKeyDown}
                                isExpandable={isExpandable}
                            />;
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

FacetList.propTypes = {
    context: PropTypes.object.isRequired,
    facets: PropTypes.oneOfType([
        PropTypes.array,
        PropTypes.object,
    ]).isRequired,
    filters: PropTypes.array.isRequired,
    mode: PropTypes.string,
    orientation: PropTypes.string,
    hideTextFilter: PropTypes.bool,
    docTypeTitleSuffix: PropTypes.string,
    addClasses: PropTypes.string, // CSS classes to use if the default isn't needed.
    /** True to supress the display of facet-list title */
    supressTitle: PropTypes.bool,
    /** Special facet-term click handler for edit forms */
    onFilter: PropTypes.func,
    /** True if the collapsible, false otherwise  */
    isExpandable: PropTypes.bool,
};

FacetList.defaultProps = {
    mode: '',
    orientation: 'vertical',
    hideTextFilter: false,
    addClasses: '',
    docTypeTitleSuffix: 'search',
    supressTitle: false,
    onFilter: null,
    isExpandable: true,
};

FacetList.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};


/**
 * Display the "Clear filters" link.
 */
export const ClearFilters = ({ searchUri, enableDisplay }) => (
    <div className="clear-filters-control">
        {enableDisplay ? <div><a href={searchUri}>Clear Filters <i className="icon icon-times-circle" /></a></div> : null}
    </div>
);

ClearFilters.propTypes = {
    /** URI for the Clear Filters link */
    searchUri: PropTypes.string.isRequired,
    /** True to display the link */
    enableDisplay: PropTypes.bool,
};

ClearFilters.defaultProps = {
    enableDisplay: true,
};


/**
 * Display and react to controls at the top of search result output, like the search and matrix
 * pages.
 */
export const SearchControls = ({ context, visualizeDisabledTitle, showResultsToggle, onFilter, hideBrowserSelector, additionalFilters, showDownloadButton }, reactContext) => {
    const results = context['@graph'];
    const searchBase = url.parse(reactContext.location_href).search || '';
    const trimmedSearchBase = searchBase.replace(/[?|&]limit=all/, '');
    const canDownload = context.total <= MAX_DOWNLOADABLE_RESULT;
    const modalText = canDownload ?
        <>
            <p>
                Click the &ldquo;Download&rdquo; button below to download a &ldquo;files.txt&rdquo; file that contains a list of URLs to a file containing all the experimental metadata and links to download the file.
                The first line of the file has the URL or command line to download the metadata file.
            </p>
            <p>
                Further description of the contents of the metadata file are described in the <a href="/help/batch-download/">Batch Download help doc</a>.
            </p>
            <p>
                The &ldquo;files.txt&rdquo; file can be copied to any server.<br />
                The following command using cURL can be used to download all the files in the list:
            </p>
            <code>xargs -L 1 curl -O -J -L &lt; files.txt</code><br />
        </> :
        <>
            <p>
                This search is too large (&gt;{MAX_DOWNLOADABLE_RESULT} datasets) to automatically generate a manifest or metadata file.  We are currently working on methods to download from large searches.
            </p>
            <p>
                You can directly access the files in AWS: <a href="https://registry.opendata.aws/encode-project/" target="_blank" rel="noopener noreferrer">https://registry.opendata.aws/encode-project/</a>
            </p>
        </>;

    let resultsToggle = null;
    if (showResultsToggle) {
        if (context.total > results.length && searchBase.indexOf('limit=all') === -1) {
            resultsToggle = (
                <a
                    rel="nofollow"
                    className="btn btn-info btn-sm"
                    href={searchBase ? `${searchBase}&limit=all` : '?limit=all'}
                    onClick={onFilter}
                >
                    View All
                </a>
            );
        } else {
            resultsToggle = (
                <span>
                    {results.length > 25 ?
                        <a
                            className="btn btn-info btn-sm"
                            href={trimmedSearchBase || '/search/'}
                            onClick={onFilter}
                        >
                            View 25
                        </a>
                    : null}
                </span>
            );
        }
    }

    return (
        <div className="results-table-control">
            <div className="results-table-control__main">
                <ViewControls results={context} additionalFilters={additionalFilters} />
                {resultsToggle}
                {showDownloadButton ? <BatchDownloadControls results={context} additionalFilters={additionalFilters} modalText={modalText} canDownload={canDownload} /> : ''}
                {!hideBrowserSelector ?
                    <BrowserSelector results={context} disabledTitle={visualizeDisabledTitle} additionalFilters={additionalFilters} />
                : null}
            </div>
            <div className="results-table-control__json">
                <DisplayAsJson />
            </div>
        </div>
    );
};

SearchControls.propTypes = {
    /** Search results object that generates this page */
    context: PropTypes.object.isRequired,
    /** True to disable Visualize button */
    visualizeDisabledTitle: PropTypes.string,
    /** True to show View All/View 25 control */
    showResultsToggle: (props, propName, componentName) => {
        if (props[propName] && typeof props.onFilter !== 'function') {
            return new Error(`"onFilter" prop to ${componentName} required if "showResultsToggle" is true`);
        }
        return null;
    },
    /** Function to handle clicks in links to toggle between viewing all and limited */
    onFilter: (props, propName, componentName) => {
        if (props.showResultsToggle && typeof props[propName] !== 'function') {
            return new Error(`"onFilter" prop to ${componentName} required if "showResultsToggle" is true`);
        }
        return null;
    },
    /** True to hide the Visualize button */
    hideBrowserSelector: PropTypes.bool,
    /** Add filters to search links if needed */
    additionalFilters: PropTypes.array,
    /** Determines whether or not download button is displayed */
    showDownloadButton: PropTypes.bool,
};

SearchControls.defaultProps = {
    visualizeDisabledTitle: '',
    showResultsToggle: false,
    onFilter: null,
    hideBrowserSelector: false,
    additionalFilters: [],
    showDownloadButton: true,
};

SearchControls.contextTypes = {
    location_href: PropTypes.string,
};


// Maximum number of selected items that can be visualized.
const VISUALIZE_LIMIT = 100;


export class ResultTable extends React.Component {
    constructor(props) {
        super(props);

        // Bind `this` to non-React moethods.
        this.onFilter = this.onFilter.bind(this);
    }

    getChildContext() {
        return {
            actions: this.props.actions,
        };
    }

    onFilter(e) {
        const searchStr = e.currentTarget.getAttribute('href');
        this.props.onChange(searchStr);
        e.stopPropagation();
        e.preventDefault();
    }

    render() {
        const { context, searchBase, actions } = this.props;
        const { facets } = context;
        const results = context['@graph'];
        const total = context.total;
        const columns = context.columns;
        const filters = context.filters;
        const label = 'results';
        const visualizeDisabledTitle = context.total > VISUALIZE_LIMIT ? `Filter to ${VISUALIZE_LIMIT} to visualize` : '';

        return (
            <div className="search-results">
                <FacetList
                    {...this.props}
                    facets={facets}
                    filters={filters}
                    searchBase={searchBase ? `${searchBase}&` : `${searchBase}?`}
                    onFilter={this.onFilter}
                />
                {context.notification === 'Success' ?
                    <div className="search-results__result-list">
                        <h4>Showing {results.length} of {total} {label}</h4>
                        <SearchControls context={context} visualizeDisabledTitle={visualizeDisabledTitle} onFilter={this.onFilter} showResultsToggle />
                        {!(actions && actions.length > 0) ?
                            <CartSearchControls searchResults={context} />
                        : null}
                        <ResultTableList results={results} columns={columns} cartControls />
                    </div>
                :
                    <h4>{context.notification}</h4>
                }
            </div>
        );
    }
}

ResultTable.propTypes = {
    context: PropTypes.object.isRequired,
    actions: PropTypes.array,
    searchBase: PropTypes.string,
    onChange: PropTypes.func.isRequired,
    currentRegion: PropTypes.func,
};

ResultTable.defaultProps = {
    actions: [],
    searchBase: '',
    currentRegion: null,
};

ResultTable.childContextTypes = {
    actions: PropTypes.array,
};

ResultTable.contextTypes = {
    session: PropTypes.object,
};


// Display the list of search results. `mode` allows for special displays, and supports:
//     picker: Results displayed in an edit form object picker
//     cart-view: Results displayed in the Cart View page.
export const ResultTableList = ({ results, columns, cartControls, mode }) => (
    <ul className="result-table" id="result-table">
        {results.length > 0 ?
            results.map(result => Listing({ context: result, columns, key: result['@id'], cartControls, mode }))
        : null}
    </ul>
);

ResultTableList.propTypes = {
    results: PropTypes.array.isRequired, // Array of search results to display
    columns: PropTypes.object, // Columns from search results
    cartControls: PropTypes.bool, // True if items should display with cart controls
    mode: PropTypes.string, // Special search-result modes, e.g. "picker"
};

ResultTableList.defaultProps = {
    columns: null,
    cartControls: false,
    mode: '',
};


export class Search extends React.Component {
    constructor() {
        super();

        // Bind `this` to non-React methods.
        this.currentRegion = this.currentRegion.bind(this);
    }

    currentRegion(assembly, region) {
        if (assembly && region) {
            this.lastRegion = {
                assembly,
                region,
            };
        }
        return Search.lastRegion;
    }

    render() {
        const context = this.props.context;
        const notification = context.notification;
        const searchBase = url.parse(this.context.location_href).search || '';
        const facetdisplay = context.facets && context.facets.some(facet => facet.total > 0);

        if (facetdisplay) {
            return (
                <Panel>
                    <PanelBody>
                        <ResultTable {...this.props} searchBase={searchBase} onChange={this.context.navigate} currentRegion={this.currentRegion} />
                    </PanelBody>
                </Panel>
            );
        }

        return <h4>{notification}</h4>;
    }
}

Search.propTypes = {
    context: PropTypes.object.isRequired,
};

Search.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};

// optionally make a persistent region
Search.lastRegion = {
    assembly: PropTypes.string,
    region: PropTypes.string,
};

globals.contentViews.register(Search, 'Search');
