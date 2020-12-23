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
    BiosampleType,
    requestSearch,
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
    patient: { title: 'Patients' },
    surgery: { title: 'Surgery and Pathology Reports' },
    annotation: { title: 'Annotation file set' },
    biospecimen: { title: 'Biospecimens' },
    // bioexperiment: { title: 'Bioexperiments' },
    // bioseries: { title: 'Series File set' },
    // biofileSet: { title: 'File set' },
    // bioexperimentSeries: { title: 'Experiment Series'},
    biodataset: { title: 'Biodatasets' },
    bioexperiment: { title: 'Bioexperiments' },
    bioseries: { title: 'Bioserieses' },
    biofileSet: { title: 'BiofileSets' },
    bioexperimentSeries:{title:'BioexperimentSereieses'},
    image: { title: 'Images' },
    publication: { title: 'Publications' },
    page: { title: 'Web page' },
    bioproject: { title: 'Project file set' },
    publication_data: { title: 'Publication file set' },
    bioreference: { title: 'Reference file set' },
};

const datasetTypes = {
};

const biodatasetTypes = {
    Biodataset: types.biodataset.title,
    Bioproject: types.bioproject.title,
    Bioreference: types.bioreference.title,
    Bioseries: types.bioseries.title,
    BiofileSet: types.biofileSet.title,
    BioexperimentSeries:types.bioexperimentSeries.title

}

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
 * Renders both Experiment and FunctionalCharacterizationExperiment search results.
 */
const ExperimentComponent = (props, reactContext) => {
    const { context: result, cartControls, mode } = props;
    let synchronizations;

    // Determine whether object is Experiment or FunctionalCharacterizationExperiment.
    const experimentType = result['@type'][0];
    const isFunctionalExperiment = experimentType === 'FunctionalCharacterizationExperiment';
    const displayType = isFunctionalExperiment ? 'Functional Characterization Experiment' : 'Experiment';

    // Collect all biosamples associated with the experiment. This array can contain duplicate
    // biosamples, but no null entries.
    let biosamples = [];
    const treatments = [];

    if (result.replicates && result.replicates.length > 0) {
        biosamples = _.compact(result.replicates.map(replicate => replicate.library && replicate.library.biosample));
        // flatten treatment array of arrays
        _.compact(biosamples.map(biosample => biosample.treatments)).forEach(treatment => treatment.forEach(t => treatments.push(t)));
    }

    // Get all biosample organism names
    const organismNames = biosamples.length > 0 ? BiosampleOrganismNames(biosamples) : [];

    // Collect synchronizations
    if (result.replicates && result.replicates.length > 0) {
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


/* eslint-disable react/prefer-stateless-function */
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


/* eslint-disable react/prefer-stateless-function */
class PatientComponent extends React.Component {
    render() {
        const { cartControls } = this.props;
        const result = this.props.context;
        let age = result.diagnosis.age;
        const hasAge = (age != "Unknown") ? true : false;
        const ageUnit = (result.diagnosis.age_unit && hasAge && age != "90 or above") ? ` ${result.diagnosis.age_unit}` : '';

        return (
            <li className={resultItemClass(result)}>
                <div className="result-item">
                    <div className="result-item__data">
                        <a href={result['@id']} className="result-item__link">
                            {`${result.accession}`}
                            {hasAge && `(${age}${ageUnit})`}
                        </a>
                        <div className="result-item__data-row">
                            <div><strong>Sex: </strong>{result.sex}</div>
                            <div><strong>Ethnicity: </strong>{result.ethnicity}</div>
                            <div><strong>Race: </strong>{result.race}</div>
                        </div>
                    </div>
                    <div className="result-item__meta">
                        <div className="result-item__meta-title">Patient</div>
                        <div className="result-item__meta-id">{` ${result.accession}`}</div>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}

                    </div>
                    <PickerActions {...this.props} />
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

PatientComponent.propTypes = {
    context: PropTypes.object.isRequired, // Target search results
    cartControls: PropTypes.bool, // True if displayed in active cart
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

PatientComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Patient = auditDecor(PatientComponent);

globals.listingViews.register(Patient, 'Patient');

class PathologyComponent extends React.Component {
    render() {
        const result = this.props.context;

        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Pathology Report</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {`${result.accession} `}
                        </a>
                    </div>
                    <div className="data-row">
                        <div><strong>Tumor Size Range:</strong>{result.tumor_size}{result.tumor_size_units}</div>
                        <div><strong>Histologic Subtype: </strong>{result.histology}</div>
                        <div><strong>Tumor Grade: </strong>{result.grade}</div>
                        <div><strong>pT stage: </strong>{result.ajcc_p_stage}</div>
                        <div><strong>AJCC TNM Stage: </strong>{result.ajcc_tnm_stage}</div>
                        <div><strong>Laterality: </strong>{result.laterality}</div>
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

PathologyComponent.propTypes = {
    context: PropTypes.object.isRequired, // Target search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

PathologyComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const PathologyReport = auditDecor(PathologyComponent);

globals.listingViews.register(PathologyReport, 'PathologyReport');

class SurgeryComponent extends React.Component {
    render() {
        const result = this.props.context;
        const surgeryProcedure = result.surgery_procedure;
        let type1 = [];
        for (let i = 0; i < surgeryProcedure.length; i++) {
            type1.push(<div><strong>Surgery Procedure: </strong>{surgeryProcedure[i].procedure_type}</div>);
        }
        return (
            < li >
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Surgery</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {`${result.accession} `}

                        </a>
                    </div>
                    <div className="data-row">
                        <div><strong>Surgery Date: </strong>{result.date}</div>
                        <div><strong>Hospital Location: </strong>{result.hospital_location} </div>
                        {type1}
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li >
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

SurgeryComponent.propTypes = {
    context: PropTypes.object.isRequired, // Target search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

SurgeryComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Surgery = auditDecor(SurgeryComponent);

globals.listingViews.register(Surgery, 'Surgery');

/* eslint-disable react/prefer-stateless-function */
class BiofileComponent extends React.Component {
    render() {
        const result = this.props.context;
        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Biofile</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {`${result.accession} `}

                        </a>
                    </div>
                    <div className="data-row">
                        <div><strong>File format: </strong>{result.file_format}</div>
                        <div><strong>Output type: </strong>{result.output_type}</div>
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

BiofileComponent.propTypes = {
    context: PropTypes.object.isRequired, // Target search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

BiofileComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Biofile = auditDecor(BiofileComponent);

globals.listingViews.register(Biofile, 'Biofile');

/* eslint-disable react/prefer-stateless-function */
class BiospecimenComponent extends React.Component {
    render() {
        const result = this.props.context;
        const tissueType = (result.tissue_type && result.sample_type == 'Tissue') ? ` ${result.tissue_type}` : '';
        const anatomicSite = (result.anatomic_site && result.sample_type == 'Tissue') ? ` ${result.anatomic_site}` : '';

        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Biospecimen</p>
                        <p className="type">{` ${result.accession}`}</p>

                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {`${result.accession} `}

                        </a>
                    </div>
                    <div className="data-row">
                        <div><strong>Sample type: </strong>{result.sample_type}</div>
                        <div><strong>Tissue derivatives: </strong>{result.tissue_derivatives}</div>
                        <div><strong>Tissue type: </strong>{result.tissue_type}</div>
                        <div><strong>Anatomic site: </strong>{result.anatomic_site}</div>
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }

}
/* eslint-enable react/prefer-stateless-function */

BiospecimenComponent.propTypes = {
    context: PropTypes.object.isRequired, // Biosample search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

BiospecimenComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Biospecimen = auditDecor(BiospecimenComponent);

globals.listingViews.register(Biospecimen, 'Biospecimen');

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



const BioexperimentComponent = (props, reactContext) => {
    const { cartControls } = props;
    const result = props.context;

    return (
        <li>
            <div className="result-item">
                <div className="result-item__data">
                    <PickerActions {...props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Bioexperiment</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {result.assay_term_name ?
                                <span>{result.assay_term_name}</span> : null
                            }
                        </a>
                    </div>

            </div>
            {cartControls ?
                <div className="result-item__cart-control">
                    <CartToggle element={result} />
                </div>
                : null}
            </div>
            { props.auditDetail(result.audit, result['@id'], { session: reactContext.session, except: result['@id'], forcedEditLink: true }) }
        </li >
    );
};

BioexperimentComponent.propTypes = {
    context: PropTypes.object.isRequired, // Experiment search results
    cartControls: PropTypes.bool, // True if displayed in active cart
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired,
};

BioexperimentComponent.defaultProps = {
    cartControls: false,
};

BioexperimentComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Bioexperiment = auditDecor(BioexperimentComponent);

globals.listingViews.register(Bioexperiment, 'Bioexperiment');

const BiodatasetComponent = (props, reactContext) => {
    const result = props.context;
    let biosampleTerm;

    // Determine whether the dataset is a series or not
    const seriesDataset = result['@type'].indexOf('Bioseries') >= 0;
console.log("seriesDataset", seriesDataset);
    // Get the biosample info for Series types if any. Can be string or array. If array, only use iff 1 term name exists
    if (seriesDataset) {
        biosampleTerm = (result.assay_term_name) ? result.assay_term_name : '';
        // biosampleTerm = (result.biospecimen && Array.isArray(result.biospecimen) && result.biospecimen.length === 1 && result.biospecimen[0].sample_type) ? result.biospecimen[0].sample_type : ((result.biospecimen && result.biospecimen.sample_type) ? result.biospecimen.sample_type : '');


    }

    const haveSeries = result['@type'].indexOf('Bioseries') >= 0;
    const haveFileSet = result['@type'].indexOf('BiofileSet') >= 0;
    console.log("haveSeries", result['@type'].indexOf('Bioseries'));

    return (
        <li>
            <div className="result-item">
                <div className="result-item__data">
                    <PickerActions {...props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">{haveSeries ? 'Bioseries' : (haveFileSet ? 'BiofileSet' : 'Biodataset')}</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {biodatasetTypes[result['@type'][0]]}
                            {seriesDataset ?
                                <span>
                                    {biosampleTerm ? <span>{` in ${biosampleTerm}`}</span> : null}

                                </span>
                                :
                                <span>{result.description ? <span>{`: ${result.description}`}</span> : null}</span>
                            }
                        </a>
                    </div>
                    <div className="data-row">
                        {/* <div><strong>Lab: </strong>{result.lab.title}</div>
                        <div><strong>Project: </strong>{result.award.project}</div> */}
                    </div>
                </div>
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, except: result['@id'], forcedEditLink: true })}
        </li>
    );
};

BiodatasetComponent.propTypes = {
    context: PropTypes.object.isRequired, // Dataset search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

BiodatasetComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Biodataset = auditDecor(BiodatasetComponent);

globals.listingViews.register(Biodataset, 'Biodataset');


/* eslint-disable react/prefer-stateless-function */
/**
 *
 * If the given term within the facet is selected, either as a selected term or a negated term,
 * return the href for the term. Don't pass any terms from facets generated by the back end
 * specifically for negation, because they don't get rendered anyway.
 * @param {string} term - Facet term being tested.
 * @param {object} facet - Facet object containing `term`.
 * @param {array} filters - `filters` array directly from search result object.
 * @return (object) - {
 *                        selected: If the term is selected, this returns the href to remove the term from the URL.
 *                        negated: true if the selected term is for negation.
 *                    }
 */
function termSelected(term, facet, filters) {
    let matchingFilter;
    let negated = false;
    const exists = facet.type === 'exists';

    // Run through the search result filters to decide whether the given term is selected.
    const selected = filters.some((filter) => {
        // Determine whether the filter is for negation (ends in a !). If it's a negation filter,
        // strip the final "!" for easier testing.
        negated = filter.field.charAt(filter.field.length - 1) === '!';
        const filterFieldName = negated ? filter.field.slice(0, -1) : filter.field;

        if (exists) {
            // Facets with an "exists" property defined in the schema need special handling to
            // allow for yes/no display.
            if ((filter.field === `${facet.field}!` && term === 'no') ||
                (filter.field === facet.field && term === 'yes')) {
                matchingFilter = filter;
                return true;
            }
        } else if (filterFieldName === facet.field && filter.term === String(term)) {
            // The facet field and the given term match a filter, so save that filter so we can
            // extract its `remove` link.
            matchingFilter = filter;
            return true;
        }

        // Not an "exists" term, and not a selected term.
        return false;
    });

    if (selected) {
        // The given term is selected. Return the href to remove the term from the URI, as well as
        // whether this term was a negation term or not.
        return {
            selected: url.parse(matchingFilter.remove).search,
            negated,
            exists,
        };
    }

    // The given term isn't selected. Return no href (the href will be determined separately), and
    // if the term isn't selected, it can't be a negation term.
    return {
        selected: null,
        negated: false,
        exists,
    };
}

// Determine whether any of the given terms are selected
function countSelectedTerms(terms, facet, filters) {
    let count = 0;
    terms.forEach((term) => {
        const { selected } = termSelected(term.key, facet, filters);
        if (selected) {
            count += 1;
        }
    });
    return count;
}

// Display one term within a facet.
const Term = (props) => {
    const { filters, facet, total, canDeselect, searchBase, onFilter, statusFacet } = props;
    const term = props.term.key;
    const count = props.term.doc_count;
    const title = props.title || term;
    const field = facet.field;
    const em = field === 'target.organism.scientific_name' ||
        field === 'organism.scientific_name' ||
        field === 'replicates.library.biosample.donor.organism.scientific_name';
    const barStyle = {
        width: `${Math.ceil((count / total) * 100)}%`,
    };

    // Determine if the given term should display selected, as well as what the href for the term
    // should be. If it *is* selected, also indicate whether it was selected for negation or not.
    const { selected, negated, exists } = termSelected(term, facet, filters);
    let href;
    let negationHref = '';
    if (selected && !canDeselect) {
        href = null;
    } else if (selected) {
        href = selected;
    } else if (facet.type === 'exists') {
        if (term === 'yes') {
            href = `${searchBase}${field}=*`;
        } else {
            href = `${searchBase}${field}!=*`;
        }
    } else {
        // Term isn't selected. Get the href for the term, and for its negation button.
        href = `${searchBase}${field}=${globals.encodedURIComponent(term)}`;
        negationHref = `${searchBase}${field}!=${globals.encodedURIComponent(term)}`;
    }

    if (facet.appended === 'true') {
        const facetTerm = facet.terms.find(x => x.key === term);
        const isNegated = facetTerm.isEqual === 'false';
        const vfield = filters.find(f => f.term === term);
        const vhref = vfield ? vfield.remove : '';
        return (
            <li className={`facet-term${isNegated ? ' negated-selected' : (selected ? ' selected' : '')}`}>
                {statusFacet ? <Status item={term} badgeSize="small" css="facet-term__status" noLabel /> : null}
                <a className="facet-term__item" href={vhref} onClick={href ? onFilter : null}>
                    <div className="facet-term__text">
                        {em ? <em>{title}</em> : <span>{title}</span>}
                    </div>
                </a>
            </li>
        );
    }

    return (
        <li className={`facet-term${negated ? ' negated-selected' : (selected ? ' selected' : '')}`}>
            {statusFacet ? <Status item={term} badgeSize="small" css="facet-term__status" noLabel /> : null}
            <a className="facet-term__item" href={href} onClick={href ? onFilter : null}>
                <div className="facet-term__text">
                    {em ? <em>{title}</em> : <span>{title}</span>}
                </div>
                {negated ? null : <div className="facet-term__count">{count}</div>}
                {(selected || negated) ? null : <div className="facet-term__bar" style={barStyle} />}
            </a>
            <div className="facet-term__negator">
                {(selected || negated || exists) ? null : <a href={negationHref} title={'Do not include items with this term'}><i className="icon icon-minus-circle" /></a>}
            </div>
        </li>
    );
};

Term.propTypes = {
    filters: PropTypes.array.isRequired, // Search result filters
    term: PropTypes.object.isRequired, // One element of the terms array from a single facet
    title: PropTypes.string, // Optional override for facet title
    facet: PropTypes.object.isRequired, // Search result facet object containing the given term
    total: PropTypes.number.isRequired, // Total number of items this term includes
    canDeselect: PropTypes.bool,
    searchBase: PropTypes.string.isRequired, // Base URI for the search
    onFilter: PropTypes.func,
    statusFacet: PropTypes.bool, // True if the facet displays statuses
};

Term.defaultProps = {
    title: '',
    canDeselect: true,
    onFilter: null,
    statusFacet: false,
};


// Wrapper for <Term> to display the "Data Type" facet terms.
const TypeTerm = (props) => {
    const { filters, total } = props;
    const term = props.term.key;
    let title;
    try {
        title = types[term];
    } catch (e) {
        title = term;
    }
    return <Term {...props} title={title} filters={filters} total={total} />;
};

TypeTerm.propTypes = {
    term: PropTypes.object.isRequired,
    filters: PropTypes.array.isRequired,
    total: PropTypes.number.isRequired,
};

const allMonths = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];

class DateSelectorFacet extends React.Component {
    constructor() {
        super();

        // Set initial React component state.
        this.state = {
            possibleYears: [], // all years with results
            startYears: [], // possible years for the start year drop-down
            endYears: [], // possible years for the end year drop-down
            startMonths: [], // possible months for the start month drop-down
            endMonths: [], // possible months for the end month drop-down
            startYear: undefined, // chosen start year
            startMonth: undefined, // chosen start month
            endYear: undefined, // chosen end year
            endMonth: undefined, // chosen end month
            activeFacet: 'date_released', // for toggle, either 'date_released' or 'date_submitted'
        };

        this.selectYear = this.selectYear.bind(this);
        this.selectMonth = this.selectMonth.bind(this);
        this.checkForSameYear = this.checkForSameYear.bind(this);
        this.toggleDateFacet = this.toggleDateFacet.bind(this);
        this.setActiveFacetParameters = this.setActiveFacetParameters.bind(this);
        this.handleReset = this.handleReset.bind(this);
        this.resetMonthDropDowns = this.resetMonthDropDowns.bind(this);
    }

    componentDidMount() {
        this.setActiveFacetParameters(true);
    }

    setActiveFacetParameters(initializationFlag) {
        let activeFacet = null;
        let activeFilter = null;
        let startYear = null;
        let endYear = null;
        // If there is a date filter applied, we'll use that filter to set state when the component is mounted
        if (initializationFlag) {
            // if a date range has already been selected, we will use that date range to populate drop-downs
            const existingFilter = this.props.filters.filter(filter => filter.field === 'advancedQuery');
            if (existingFilter[0]) {
                activeFilter = true;
                const filterString = existingFilter[0].term;
                activeFacet = (filterString.indexOf('date_released') !== -1) ? 'date_released' : 'date_submitted';
                startYear = filterString.split('[')[1].split('-')[0];
                const startMonth = filterString.split('[')[1].split('-')[1];
                endYear = filterString.split('TO ')[1].split('-')[0];
                const endMonth = filterString.split('TO ')[1].split('-')[1];
                // Set dropdown lists to match existing query
                this.setState({
                    activeFacet,
                    startYear,
                    endYear,
                    startMonth,
                    endMonth,
                });
            }
        }
        if (activeFacet === null) {
            activeFacet = this.state.activeFacet;
        }

        // Set possible years to be 2009 -> current year for 'date_released'
        // Set possible years to be 2008 -> current year for 'date_submitted'
        const currentYear = moment().format('YYYY');
        let firstYear = 2007;
        if (activeFacet === 'date_released') {
            firstYear = 2008;
        }
        const numberOfYears = +currentYear - firstYear;
        const possibleYears = Array.from({ length: numberOfYears }, (e, i) => (i + firstYear + 1));

        if (!initializationFlag || !activeFilter) {
            // Set dropdown lists to be full lists of possiblities and initialize to boundaries of full range
            this.setState({
                startYear: possibleYears[0],
                endYear: possibleYears[possibleYears.length - 1],
                startMonth: '01',
                endMonth: '12',
                startYears: possibleYears,
                endYears: possibleYears,
            });
        } else {
            const startYears = possibleYears.filter(year => +year <= endYear);
            const endYears = possibleYears.filter(year => +year >= startYear);
            this.setState({
                startYears,
                endYears,
            });
        }

        // Set dropdown options to include all possibilities
        this.setState({
            possibleYears,
            startMonths: allMonths,
            endMonths: allMonths,
        }, () => this.checkForSameYear());
    }

    selectYear(event) {
        // We are changing the start year, which means we need to change the possibilities for the end years and also the possible start months
        if (event.target.id === 'select-start-year') {
            // Set startYear to be user choice
            this.setState({ startYear: event.target.value }, () => {
                // Check if now the years match and month lists need to be limited
                this.checkForSameYear();
            });
            // Possibilities for endYears must now all be greater than the new startYear
            const endYears = this.state.possibleYears.filter(year => +year >= event.target.value);
            this.setState({ endYears });
            // We are changing the end year, which means we need to change the possiblities for the starting year and also the possible end months
        } else {
            // Set endYear to be user choice
            this.setState({ endYear: event.target.value }, () => {
                // Check if now the years match and month lists need to be limited
                this.checkForSameYear();
            });
            // Possiblities for startYears must now all be less than the new endYears
            const startYears = this.state.possibleYears.filter(year => +year <= event.target.value);
            this.setState({ startYears });
        }
    }

    resetMonthDropDowns() {
        this.setState({
            startMonths: allMonths,
            startMonth: '01',
            endMonths: allMonths,
            endMonth: '12',
        });
    }

    // If the start year and the end year match, we have to be careful to not allow the user to pick an end month that is earlier than the start month
    checkForSameYear() {
        if (+this.state.startYear === +this.state.endYear) {
            // If start month is later than the end month and years match, this is not allowed, so we reset
            if (+this.state.endMonth < +this.state.startMonth) {
                this.resetMonthDropDowns();
                // If start and end months are allowed, we still need to filter dropdown possible lists so they can't select an unallowed combination
            } else {
                // endMonths can only display months that are after the chosen startMonth
                const endMonths = allMonths.filter(month => +month >= +this.state.startMonth);
                // startMonths can only display months that are before the chosen endMonth
                const startMonths = allMonths.filter(month => +month <= +this.state.endMonth);
                this.setState({
                    endMonths,
                    startMonths,
                });
            }
            // If the start and end years previously matched (but now they don't), an incomplete list of months may be set and we need to update
        } else {
            if (allMonths.length !== this.state.startMonths.length) {
                this.setState({ startMonths: allMonths });
            }
            if (allMonths.length !== this.state.endMonths.length) {
                this.setState({ endMonths: allMonths });
            }
        }
    }

    selectMonth(event) {
        // When a month changes, we need to check if the years match and filter the month dropdown possibilities if they do
        if (event.target.id === 'select-start-month') {
            this.setState({ startMonth: event.target.value }, () => {
                this.checkForSameYear();
            });
        } else {
            this.setState({ endMonth: event.target.value }, () => {
                this.checkForSameYear();
            });
        }
    }

    // Toggle the 'activeFacet' state and also reset the drop down options by calling 'setActiveFacetParameters'
    toggleDateFacet() {
        this.setState(prevState => ({ activeFacet: prevState.activeFacet === 'date_released' ? 'date_submitted' : 'date_released' }), this.setActiveFacetParameters);
    }

    // Reset the dropdowns and state, and clear query
    handleReset(resetString) {
        this.setState({ activeFacet: 'date_released' }, () => {
            this.setActiveFacetParameters();
            this.context.navigate(resetString);
        });
    }

    // Set dropdowns to match quick link query and nagivate to quick link
    handleQuickLink(searchBaseForDateRange, field) {
        const currentYear = moment().format('YYYY');
        const currentMonth = moment().format('MM');
        const currentDay = moment().format('DD');
        const quickLinkString = `${searchBaseForDateRange}advancedQuery=@type:Experiment ${field}:[${currentYear - 1}-${currentMonth}-${currentDay} TO ${currentYear}-${currentMonth}-${currentDay}]`;
        this.setState({
            startMonth: currentMonth,
            endMonth: currentMonth,
            startYear: (currentYear - 1),
            endYear: currentYear,
            startMonths: allMonths,
            endMonths: allMonths,
            startYears: this.state.possibleYears.filter(year => +year <= currentYear),
            endYears: this.state.possibleYears.filter(year => +year >= (currentYear - 1)),
        }, () => {
            this.context.navigate(quickLinkString);
        });
    }

    render() {
        const { facet, searchBase, facets } = this.props;
        const field = this.state.activeFacet;
        const activeFacet = facets.filter(f => f.field === this.state.activeFacet)[0];

        const daysInEndMonth = moment(`${this.state.endYear}-${this.state.endMonth}`, 'YYYY-MM').daysInMonth();

        // if a date range has already been selected, we want to over-write that date range with a new one
        const existingFilter = this.props.filters.filter(filter => filter.field === 'advancedQuery');
        let resetString = '';
        let searchBaseForDateRange = searchBase;
        if (existingFilter.length > 0) {
            resetString = `${existingFilter[0].remove}&`;
            searchBaseForDateRange = `${existingFilter[0].remove}&`;
        } else {
            resetString = searchBase;
        }

        const searchString = `${searchBaseForDateRange}advancedQuery=@type:Experiment ${this.state.activeFacet}:[${this.state.startYear}-${this.state.startMonth}-01 TO ${this.state.endYear}-${this.state.endMonth}-${daysInEndMonth}]`;

        // Print selected date range next to date selector facet
        let dateRangeString = '';
        if (existingFilter.length > 0) {
            if (existingFilter[0].term.indexOf('date_released') > -1) {
                dateRangeString = `Data released between ${existingFilter[0].term.substring(existingFilter[0].term.indexOf('[') + 1, existingFilter[0].term.indexOf(']')).replace('TO', 'and')}`;
            } else {
                dateRangeString = `Data submitted between ${existingFilter[0].term.substring(existingFilter[0].term.indexOf('[') + 1, existingFilter[0].term.indexOf(']')).replace('TO', 'and')}`;
            }
        }

        if (((activeFacet.terms.length > 0) && activeFacet.terms.some(term => term.doc_count)) || (field.charAt(field.length - 1) === '!')) {
            return (
                <div className={`facet date-selector-facet ${facet.field === 'date_released' ? 'display-date-selector' : ''}`}>
                    <h5>Date range selection</h5>
                    {existingFilter.length > 0 ?
                        <div className="selected-date-range">
                            <div>Selected range: </div>
                            {existingFilter.map(filter =>
                                <div key={filter.term}>{dateRangeString}</div>
                            )}
                        </div>
                        : null}

                    <div className="date-selector-toggle-wrapper">
                        <div className="date-selector-toggle"><input
                            type="radio"
                            name="released"
                            value="released"
                            checked={this.state.activeFacet === 'date_released'}
                            onChange={this.toggleDateFacet}
                        />Released
                        </div>
                        <div className="date-selector-toggle"><input
                            type="radio"
                            name="submitted"
                            value="submitted"
                            checked={this.state.activeFacet === 'date_submitted'}
                            onChange={this.toggleDateFacet}
                        />Submitted
                        </div>
                    </div>
                    <button className="date-selector-btn" onClick={() => this.handleQuickLink(searchBaseForDateRange, field)}>
                        <i className="icon icon-caret-right" />
                        See results for the past year
                    </button>
                    <div className="date-container">
                        <div className="date-selector-module">
                            <h6>Start date:</h6>
                            <div className="date-selector">
                                <select id="select-start-month" value={this.state.startMonth} onChange={this.selectMonth}>
                                    {this.state.startMonths.map(month =>
                                        <option value={month} key={month}>{month}</option>
                                    )}
                                </select>
                                <select id="select-start-year" value={this.state.startYear} onChange={this.selectYear}>
                                    {this.state.startYears.map(year =>
                                        <option value={year} key={year}>{year}</option>
                                    )}
                                </select>
                            </div>
                        </div>
                        <div className="date-arrow">
                            <i className="icon icon-arrow-right" />
                        </div>
                        <div className="date-selector-module">
                            <h6>End date:</h6>
                            <div className="date-selector">
                                <select id="select-end-month" value={this.state.endMonth} onChange={this.selectMonth}>
                                    {this.state.endMonths.map(month =>
                                        <option value={month} key={month}>{month}</option>
                                    )}
                                </select>
                                <select id="select-end-year" value={this.state.endYear} onChange={this.selectYear}>
                                    {this.state.endYears.map(year =>
                                        <option value={year} key={year}>{year}</option>
                                    )}
                                </select>
                            </div>
                        </div>
                    </div>
                    <a href={searchString}>
                        <button className="btn btn-info btn-sm apply-date-selector">
                            Apply changes
                        </button>
                    </a>
                    <button className="btn btn-info btn-sm reset-date-selector" onClick={() => this.handleReset(resetString)}>
                        Reset
                    </button>
                </div>
            );
        }

        // Facet had all zero terms and was not a "not" facet.
        return null;
    }
}

DateSelectorFacet.propTypes = {
    facet: PropTypes.object.isRequired,
    facets: PropTypes.array.isRequired,
    filters: PropTypes.array.isRequired,
    searchBase: PropTypes.string.isRequired, // Base URI for the search
};

DateSelectorFacet.contextTypes = {
    navigate: PropTypes.func,
};

// Sanitize user input and facet terms for comparison: convert to lowercase, remove white space and asterisks (which cause regular expression error)
const sanitizedString = inputString => inputString.toLowerCase()
    .replace(/ /g, '') // remove spaces (to allow multiple word searches)
    .replace(/[*?()+[\]\\/]/g, ''); // remove certain special characters (these cause console errors)

class Facet extends React.Component {
    constructor() {
        super();

        // Set initial React commponent state.
        this.state = {
            initialState: true,
            unsanitizedSearchTerm: '',
            searchTerm: '',
        };

        // Bind `this` to non-React methods.
        this.handleSearch = this.handleSearch.bind(this);
    }

    componentDidMount() {
        this.setState({ initialState: false });
    }

    handleSearch(event) {
        // Unsanitized search term entered by user for display
        this.setState({ unsanitizedSearchTerm: event.target.value });
        // Search term entered by the user
        const filterVal = String(sanitizedString(event.target.value));
        this.setState({ searchTerm: filterVal });
    }

    render() {
        const { facet, filters } = this.props;
        const title = facet.title;
        const field = facet.field;
        const total = facet.total;
        const typeahead = facet.type === 'typeahead';

        // Filter facet terms to create list of those matching the search term entered by the user
        // Note: this applies only to Typeahead facets
        let filteredList = null;
        if (typeahead && this.state.searchTerm !== '') {
            filteredList = facet.terms.filter(
                (term) => {
                    if (term.doc_count > 0) {
                        const termKey = sanitizedString(term.key);
                        if (termKey.match(this.state.searchTerm)) {
                            return term;
                        }
                        return null;
                    }
                    return null;
                }
            );
        }

        // Make a list of terms for this facet that should appear, by filtering out terms that
        // shouldn't. Any terms with a zero doc_count get filtered out, unless the term appears in
        // the search result filter list.
        const unsortedTerms = facet.terms.filter((term) => {
            if (term.key) {
                // See if the facet term also exists in the search result filters (i.e. the term
                // exists in the URL query string).
                const found = filters.some(filter => filter.field.replace('!', '') === facet.field.replace('!', '') && filter.term === term.key);

                // If the term wasn't in the filters list, allow its display only if it has a non-
                // zero doc_count. If the term *does* exist in the filters list, display it
                // regardless of its doc_count.
                return found || term.doc_count > 0;
            }

            // The term exists, but without a key, so don't allow its display.
            return false;
        });

        // Sort numerical terms by value not by frequency
        // This should ultimately be accomplished in the back end, but the front end fix is much simpler so we are starting with that
        // We have to check the full list for now (until schema change) because some lists contain both numerical and string terms ('Encyclopedia version' under Annotations) and we do not want to sort those by value
        const numericalTest = a => !isNaN(a.key);
        // For date facets, sort by date
        let terms = [];
        if (field.match('date')) {
            terms = _.sortBy(unsortedTerms, obj => moment(obj.key, 'YYYY-MM-DD').toISOString()).reverse();
        } else if (field.match('month')) {
            terms = _.sortBy(unsortedTerms, obj => moment(obj.key, 'MMMM, YYYY').toISOString()).reverse();
        } else if (field.match('year')) {
            terms = _.sortBy(unsortedTerms, obj => moment(obj.key, 'YYYY').toISOString()).reverse();
            // For straightforward numerical facets, just sort by value
        } else if (unsortedTerms.every(numericalTest)) {
            terms = _.sortBy(unsortedTerms, obj => obj.key);
        } else if (field.match('range')) {
            terms = _.sortBy(unsortedTerms, obj => parseInt(obj.key.match(/\d+/)));
        } else {
            terms = unsortedTerms;
        }

        const moreTerms = terms.slice(5);
        const TermComponent = field === 'type' ? TypeTerm : Term;
        const selectedTermCount = countSelectedTerms(moreTerms, facet, filters);
        const canDeselect = (!facet.restrictions || selectedTermCount >= 2);
        const statusFacet = field === 'status' || field === 'lot_reviews.status';

        // collecting selected search terms to display at the top of the facet
        const selectedTerms = filters.filter(filter => (filter.field === field || filter.field === `${field}!`));

        // Number of terms to show, the rest will be viewable on scroll
        const displayedTermsCount = 5;

        // Audit facet titles get mapped to a corresponding icon.
        let titleComponent = title;
        if (field.substr(0, 6) === 'audit.') {
            // Get the human-readable part of the audit facet title.
            const titleParts = title.split(': ');

            // Get the non-human-readable part so we can generate a corresponding CSS class name.
            const fieldParts = field.match(/^audit.(.+).category$/i);
            if (fieldParts && fieldParts.length === 2 && titleParts) {
                // We got something that looks like an audit title. Generate a CSS class name for
                // the corresponding audit icon, and generate the title.
                const iconClass = `icon audit-activeicon-${fieldParts[1].toLowerCase()}`;
                titleComponent = <span>{titleParts[0]}: <i className={iconClass} /></span>;
            } else {
                // Something about the audit facet title doesn't match expectations, so just
                // display the given non-human-readable audit title.
                titleComponent = <span>{title}</span>;
            }
        }

        // Return Facet component if there are terms with doc_count > 0 or for negated facet
        if (((terms.length > 0) && terms.some(term => term.doc_count)) || (field.charAt(field.length - 1) === '!') || facet.appended === 'true') {
            return (
                <div className="facet">
                    <h5>{titleComponent}</h5>
                    {/* Display selected filters at the top */}
                    {(selectedTerms.length > 0) ?
                        <div className="filter-container">
                            <div className="filter-hed">Selected filters:</div>
                            {selectedTerms.map(filter =>
                                <a href={filter.remove} key={filter.term} className={(filter.field.indexOf('!') !== -1) ? 'negation-filter' : ''}><div className="filter-link">
                                    <i className="icon icon-times-circle" className={(filter.field.indexOf('!') !== -1) ? 'icon icon-times-circle' : 'icon icon-check-circle'} /> {filter.term}</div></a>
                            )}
                        </div>
                        : null}
                    <ul className={`facet-list nav${statusFacet ? ' facet-status' : ''}`}>
                        {/* Display searchbar for typeahead facets if there are more than 5 terms */}
                        {typeahead ?
                            <div className="typeahead-entry" role="search">
                                <i className="icon icon-search" />
                                <div className="searchform">
                                    <input type="search" aria-label={`search to filter list of terms for facet ${titleComponent}`} placeholder="Search" value={this.state.unsanitizedSearchTerm} onChange={this.handleSearch} name={`search${titleComponent.replace(/\s+/g, '')}`} />
                                </div>
                            </div>
                            : null}
                        {/* If user has searched using the typeahead, we will not display the full set of facet terms, just those matching the search */}
                        {(filteredList !== null) ?
                            <div>
                                {/* Display error message if there is a search but no results found */}
                                {(filteredList.length === 0) ?
                                    <div className="searcherror">
                                        Try a different search term for results.
                                    </div>
                                    :
                                    <div className="terms-block">
                                        {/* List of results does not overflow top on initialization */}
                                        <div className="top-shading hide-shading" />
                                        {/* List of filtered terms */}
                                        <div className={`term-list search${titleComponent.replace(/\s+/g, '')}`} onScroll={shadeOverflowOnScroll}>
                                            {filteredList.map(term =>
                                                <TermComponent {...this.props} key={term.key} term={term} filters={filters} total={total} canDeselect={canDeselect} statusFacet={statusFacet} />
                                            )}
                                        </div>
                                        {/* Only show bottom shading when list of results overflows */}
                                        <div className={`shading ${(filteredList.length < displayedTermsCount) ? 'hide-shading' : ''}`} />
                                    </div>
                                }
                            </div>
                            :
                            <div>
                                {/* If the user has not searched, we will display the full set of facet terms */}
                                {(((terms.length > 0) && terms.some(term => term.doc_count)) || (field.charAt(field.length - 1) === '!') || (facet.appended === 'true')) ?
                                    <div className="terms-block">
                                        {/* List of results does not overflow top on initialization */}
                                        <div className="top-shading hide-shading" />
                                        {/* List of terms */}
                                        <div className={`term-list${typeahead ? ` search${titleComponent.replace(/\s+/g, '')}` : ''}`} onScroll={shadeOverflowOnScroll}>
                                            {/* To prevent long render time, wait for component to mount to display all typeahead terms and display 50 terms in the interim. */}
                                            {(this.state.initialState && typeahead) ?
                                                <div>
                                                    {terms.slice(0, 50).map(term =>
                                                        <TermComponent {...this.props} key={term.key} term={term} filters={filters} total={total} canDeselect={canDeselect} statusFacet={statusFacet} />
                                                    )}
                                                </div>
                                                :
                                                <div>
                                                    {terms.map(term =>
                                                        <TermComponent {...this.props} key={term.key} term={term} filters={filters} total={total} canDeselect={canDeselect} statusFacet={statusFacet} />
                                                    )}
                                                </div>
                                            }
                                        </div>
                                        {/* Only show bottom shading when list of results overflows */}
                                        <div className={`shading ${(terms.length < displayedTermsCount) ? 'hide-shading' : ''}`} />
                                    </div>
                                    : null}
                            </div>
                        }
                    </ul>
                </div>
            );
        }

        // Facet had all zero terms and was not a "not" facet.
        return null;
    }
}

Facet.propTypes = {
    facet: PropTypes.object.isRequired,
    filters: PropTypes.array.isRequired,
};

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
export const SearchControls = ({ context, visualizeDisabledTitle, showResultsToggle, onFilter, hideBrowserSelector, activeFilters, showDownloadButton }, reactContext) => {
    const results = context['total'];
    const searchBase = url.parse(reactContext.location_href).search || '';
    let trimmedSearchBase = ''
    if (searchBase.indexOf("&limit=") !== -1 || searchBase.indexOf("?limit=") !== -1 ) {
        console.log("has limit")
        if (searchBase.indexOf("limit=all") !== -1) {
            trimmedSearchBase =searchBase.replace(/[?|&]limit=all/, '')
        } else {
            trimmedSearchBase =searchBase.replace(/[?|&]limit=\d*/, '')
        }
    }else{
        trimmedSearchBase = searchBase
    }
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
    const buttonStyle = {
        marginRight: '5px',
    };



    resultsToggle = (

            <div className="btn-attached">
                {results > 25 &&
                <a
                className="btn btn-info btn-sm"
                style={buttonStyle}
                href={trimmedSearchBase || '/search/'}
                onClick={onFilter}
                >
                    View 25
                </a>}
                {results > 50 &&
                <a
                className="btn btn-info btn-sm"
                style={buttonStyle}
                href={trimmedSearchBase ? `${trimmedSearchBase}&limit=50` : '/search/?limit=50'}
                onClick={onFilter}
                >
                    View 50
                </a>}
                {results > 100 &&
                <a
                    className="btn btn-info btn-sm"
                    style={buttonStyle}
                    href={trimmedSearchBase ? `${trimmedSearchBase}&limit=100` : '/search/?limit=100'}
                    onClick={onFilter}
                >
                    View 100
                </a>}
                {results > 25 &&
                <a
                rel="nofollow"
                className="btn btn-info btn-sm"
                style={buttonStyle}
                href={trimmedSearchBase ? `${trimmedSearchBase}&limit=all` : '?limit=all'}
                onClick={onFilter}
                >
                    View All
                </a>
                }

            </div>
    );
    return (
        <div className="results-table-control">
            <div className="results-table-control__main">
                <ViewControls results={context} activeFilters={activeFilters} />
                {Boolean(context['title'] == "Search") && resultsToggle}
                {showDownloadButton ? <BatchDownloadControls results={context} modalText={modalText} canDownload={canDownload} /> : ''}
                {!hideBrowserSelector ?
                    <BrowserSelector results={context} disabledTitle={visualizeDisabledTitle} activeFilters={activeFilters} />
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
    activeFilters: PropTypes.array,
    /** Determines whether or not download button is displayed */
    showDownloadButton: PropTypes.bool,
};

SearchControls.defaultProps = {
    visualizeDisabledTitle: '',
    showResultsToggle: false,
    onFilter: null,
    hideBrowserSelector: false,
    activeFilters: [],
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
