import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { Panel, PanelBody } from '../libs/ui/panel';
import QueryString from '../libs/query_string';
import { svgIcon } from '../libs/svg-icons';
import { auditDecor } from './audit';
import { CartToggle, CartSearchControls, cartGetAllowedTypes } from './cart';
import {
    FacetRegistry,
    SpecialFacetRegistry,
    FacetGroup,
    filterTopLevelFacets,
    generateFacetGroupIdentifier,
    generateFacetGroupIdentifierList,
    generateFacetGroupNameList,
    getFacetGroupFieldsInFacets,
    areFacetGroupsEqual,
} from './facets';
import * as globals from './globals';
import { usePrevious } from './hooks';
import {
    DisplayAsJson,
    DocTypeTitle,
    singleTreatment,
} from './objectutils';
import { DbxrefList } from './dbxref';
import Status from './status';
import { BiosampleSummaryDisplay, BiosampleOrganismNames, GeneticModificationOrganismNames } from './typeutils';
import { BatchDownloadControls, ViewControls } from './view_controls';
import { BrowserSelector } from './vis_defines';
import { BodyMapThumbnailAndModal } from './body_map';


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
    gene_silencing_series: { title: 'Gene silencing series' },
    differentiation_series: { title: 'Differentiation series' },
    pulse_chase_time_series: { title: 'Pulse-chase time series' },
    single_cell_unit: { title: 'Single cell units' },
    disease_series: { title: 'Disease series' },
    multiomics_series: { title: 'Multiomics series' },
    collection_series: { title: 'Collection series' },
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
    GeneSilencingSeries: types.gene_silencing_series.title,
    DifferentiationSeries: types.differentiation_series.title,
    PulseChaseTimeSeries: types.pulse_chase_time_series.title,
    SingleCellUnit: types.single_cell_unit.title,
    DiseaseSeries: types.disease_series.title,
    MultiomicsSeries: types.multiomics_series.title,
    CollectionSeries: types.collection_series.title,
};

const getUniqueTreatments = (treatments) => _.uniq(treatments.map((treatment) => singleTreatment(treatment)));

// session storage used to preserve opened/closed facets
const FACET_STORAGE = 'FACET_STORAGE';

// marker for determining user just opened the page
const MARKER_FOR_NEWLY_LOADED_FACET_PREFIX = 'MARKER_FOR_NEWLY_LOADED_FACETS_';

/**
 * Maximum  downloadable result count
 */
const MAX_DOWNLOADABLE_RESULT = 5000000;

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
export const resultItemClass = (item) => `result-item--type-${item['@type'][0]}`;

export const PickerActions = ({ context }, reactContext) => {
    if (reactContext.actions && reactContext.actions.length > 0) {
        return (
            <div className="result-item__picker">
                {reactContext.actions.map((action) => React.cloneElement(action, { key: context.name, id: context['@id'] }))}
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


/**
 * Displays the search result data line for target objects when the parent object's targets
 * comprise an array. The parent object's schema must include the target array's @id in its
 * `columns` property.
 */
export const TargetsDataLine = ({ result, targetPropertyName }) => {
    if (result[targetPropertyName] && result[targetPropertyName].length > 0) {
        return (
            <>
                <span className="result-item__property-title">Target{result[targetPropertyName].length > 1 ? 's' : ''}: </span>
                {result[targetPropertyName].map((target, i) => (
                    <React.Fragment key={target['@id']}>
                        {i > 0 ? ', ' : null}
                        <a href={target['@id']} aria-label={`Target ${target.label}`}>{target.label}</a>
                    </React.Fragment>
                ))}
            </>
        );
    }
    return null;
};

TargetsDataLine.propTypes = {
    /** Search result object */
    result: PropTypes.object.isRequired,
    /** Name of the property that contains the array of target objects */
    targetPropertyName: PropTypes.string,
};

TargetsDataLine.defaultProps = {
    targetPropertyName: 'targets',
};


const ItemComponent = ({ context: result, auditIndicators, auditDetail }, reactContext) => {
    const title = globals.listingTitles.lookup(result)({ context: result });
    const itemType = result['@type'][0];
    return (
        <div className={resultItemClass(result)}>
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
        </div>
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
        const treatment = [];
        if (result.treatments && result.treatments.length > 0) {
            result.treatments.forEach((treat) => {
                if (treat.treatment_type_details) {
                    treatment.push(`${treat.treatment_term_name} (${treat.treatment_type_details})`);
                } else {
                    treatment.push(treat.treatment_term_name);
                }
            });
        }
        const organismName = BiosampleOrganismNames([result]);

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
            <div className={resultItemClass(result)}>
                <div className="result-item">
                    <div className="result-item__data">
                        <a href={result['@id']} className="result-item__link">
                            {`${result.biosample_ontology.term_name} (`}
                            <em>{result.organism.scientific_name}</em>
                            {`${separator}${lifeStage}${ageDisplay})`}
                        </a>
                        <div className="result-item__data-row">
                            <div><span className="result-item__property-title">Type: </span>{result.biosample_ontology.classification}</div>
                            {result.summary ? <div><span className="result-item__property-title">Summary: </span><BiosampleSummaryDisplay summary={result.summary} organisms={organismName.concat(GeneticModificationOrganismNames([result]))} /> </div> : null}
                            {rnais.length > 0 ? <div><span className="result-item__property-title">RNAi targets: </span>{rnais.join(', ')}</div> : null}
                            {constructs.length > 0 ? <div><span className="result-item__property-title">Constructs: </span>{constructs.join(', ')}</div> : null}
                            {treatment.length > 0 ? <div><span className="result-item__property-title">Treatment: </span>{treatment.join(', ')}</div> : null}
                            {mutatedGenes.length > 0 ? <div><span className="result-item__property-title">Mutated genes: </span>{mutatedGenes.join(', ')}</div> : null}
                            {result.culture_harvest_date ? <div><span className="result-item__property-title">Culture harvest date: </span>{result.culture_harvest_date}</div> : null}
                            {result.date_obtained ? <div><span className="result-item__property-title">Date obtained: </span>{result.date_obtained}</div> : null}
                            {synchText ? <div><span className="result-item__property-title">Synchronization timepoint: </span>{synchText}</div> : null}
                            <div><span className="result-item__property-title">Source: </span>{result.source.title}</div>
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
            </div>
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
 * Renders both Experiment, FunctionalCharacterizationExperiment, SingleCellUnit, and TransgenicEnhancerExperiment search results.
 */
const ExperimentComponent = (props, reactContext) => {
    const { context: result, cartControls, mode } = props;
    let synchronizations;
    let constructionPlatforms;
    let constructionMethods;
    let cellularComponents;
    let examinedLoci = [];

    // Determine if search result is allowed in carts.
    const isResultAllowedInCart = cartGetAllowedTypes().includes(result['@type'][0]);

    // Determine whether object is Experiment, FunctionalCharacterizationExperiment, or TransgenicEnhancerExperiment.
    const experimentType = result['@type'][0];
    const isFunctionalExperiment = experimentType === 'FunctionalCharacterizationExperiment';
    const isSingleCellUnit = experimentType === 'SingleCellUnit';
    const isEnhancerExperiment = experimentType === 'TransgenicEnhancerExperiment';
    let displayType;
    if (isFunctionalExperiment) {
        displayType = 'Functional Characterization Experiment';
    } else if (isSingleCellUnit) {
        displayType = 'Single Cell Unit';
    } else if (isEnhancerExperiment) {
        displayType = 'Transgenic Enhancer Experiment';
    } else {
        displayType = 'Experiment';
    }

    // Collect all biosamples associated with the experiment. This array can contain duplicate
    // biosamples, but no null entries.
    let biosamples = [];
    const treatments = [];
    let perturbationTreatments = [];

    if (isEnhancerExperiment) {
        if (result.biosamples && result.biosamples.length > 0) {
            ({ biosamples } = result);
        }
    } else {
        if (result.replicates && result.replicates.length > 0) {
            biosamples = (result.replicates.map((replicate) => replicate.library && replicate.library.biosample)).filter((biosample) => !!biosample);
        }
        // flatten treatment array of arrays
        (biosamples.map((biosample) => biosample.treatments)).filter((treatment) => !!treatment).forEach((treatment) => treatment.forEach((t) => {
            treatments.push(t);
        }));
        // filter treatments with the purpose of perturbation
        perturbationTreatments = _.flatten(biosamples.map((biosample) => biosample.treatments)).filter((a) => a?.purpose === 'perturbation');
    }

    // Get all biosample organism names
    const organismNames = biosamples.length > 0 ? BiosampleOrganismNames(biosamples) : [];

    // Collect synchronizations
    if (isEnhancerExperiment) {
        if (biosamples && biosamples.length > 0) {
            synchronizations = _.uniq(biosamples.filter((biosample) => biosample && biosample.synchronization).map((biosample) => (
                `${biosample.synchronization}${biosample.post_synchronization_time ? ` + ${biosample.age_display}` : ''}`
            )));
        }
    } else if (result.replicates && result.replicates.length > 0) {
        synchronizations = _.uniq(result.replicates.filter((replicate) => (
            replicate.library && replicate.library.biosample && replicate.library.biosample.synchronization
        )).map((replicate) => {
            const { biosample } = replicate.library;
            return `${biosample.synchronization}${biosample.post_synchronization_time ? ` + ${biosample.age_display}` : ''}`;
        }));
    }

    // Collect crispr_screen_tiling for FunctionalCharacterizationExperiment
    let tilingModality = [];
    let elementsSelectionMethod = [];
    let referenceLoci = [];
    if (isFunctionalExperiment) {
        if (result.elements_references && result.elements_references.length > 0) {
            result.elements_references.forEach((er) => {
                tilingModality = er.crispr_screen_tiling ? tilingModality.concat(er.crispr_screen_tiling) : tilingModality;
                referenceLoci = er.examined_loci ? referenceLoci.concat(er.examined_loci) : referenceLoci;
                elementsSelectionMethod = er.elements_selection_method ? elementsSelectionMethod.concat(er.elements_selection_method) : elementsSelectionMethod;
            });
        }
        tilingModality = _.uniq(tilingModality);
        referenceLoci = _.uniq(referenceLoci, (locus) => locus['@id']);
        elementsSelectionMethod = _.uniq(elementsSelectionMethod);
    }


    // Collect library construction platforms / methods / cellular components
    if (result.replicates && result.replicates.length > 0) {
        constructionPlatforms = _.uniq(result.replicates.filter((replicate) => (
            replicate.library && replicate.library.construction_platform && replicate.library.construction_platform.term_name
        )).map((replicate) => replicate.library.construction_platform.term_name));

        constructionMethods = _.uniq(result.replicates.filter((replicate) => (
            replicate.library && replicate.library.construction_method
        )).map((replicate) => replicate.library.construction_method));

        cellularComponents = _.uniq(result.replicates.filter((replicate) => (
            replicate.library && replicate.library.biosample && replicate.library.biosample.subcellular_fraction_term_name
        )).map((replicate) => replicate.library.biosample.subcellular_fraction_term_name));
    }

    // Collect examined loci
    if (result.examined_loci && result.examined_loci.length > 0) {
        result.examined_loci.forEach((loci) => {
            examinedLoci.push(loci.gene.symbol);
        });
        examinedLoci = _.uniq(examinedLoci);
    }

    const uniqueTreatments = getUniqueTreatments(treatments);
    const uniquePerturbationTreatments = getUniqueTreatments(perturbationTreatments);

    // Get a map of related datasets, possibly filtering on their status and
    // categorized by their type.
    let seriesMap = {};
    if (result.related_series && result.related_series.length > 0) {
        seriesMap = _.groupBy(
            result.related_series, (series) => series['@type'][0],
        );
    }

    // Get SCREEN link and FactorBook link if they exist
    const screenLink = (result.dbxrefs && result.dbxrefs.some((dbxref) => (dbxref.indexOf('SCREEN') > -1))) ? result.dbxrefs.filter((dbxref) => (dbxref.indexOf('SCREEN') > -1))[0] : null;
    const motifsLink = (result.dbxrefs && result.dbxrefs.some((dbxref) => (dbxref.indexOf('FactorBook') > -1))) ? result.dbxrefs.filter((dbxref) => (dbxref.indexOf('FactorBook') > -1))[0] : null;
    let screenSearch = '';
    let screenAssembly = '';
    if (screenLink) {
        screenSearch = screenLink.split(':')[1];
        screenAssembly = screenLink.split('-')[1].split(':')[0];
    }
    let motifsSearch = '';
    if (motifsLink) {
        motifsSearch = motifsLink.split(':')[1];
    }

    return (
        <div className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">
                        {(isFunctionalExperiment && result.perturbation_type) ?
                            <span>
                                {`${result.perturbation_type} `}
                            </span>
                        : null}
                        {result.assay_title ?
                            <span>{result.assay_title}</span>
                        :
                            <span>{result.assay_term_name}</span>
                        }
                        {(isFunctionalExperiment && referenceLoci.length > 0) ?
                            <span>{referenceLoci.length === 1 ? ` of ${referenceLoci[0].symbol}` : ' of multiple loci'}</span>
                        : null}
                        {result.biosample_ontology && result.biosample_ontology.term_name ? <span>{` in ${result.biosample_ontology.term_name}`}</span> : null}
                        {(isFunctionalExperiment && examinedLoci.length > 0) ?
                            <span>
                                {` with readout of ${examinedLoci.join(', ')}`}
                            </span>
                        : null}
                        {(isFunctionalExperiment && result.crispr_screen_readout) ?
                            <span>
                                {` (${result.crispr_screen_readout})`}
                            </span>
                        : null}
                    </a>
                    {result.biosample_summary ?
                        <div className="result-item__highlight-row">
                            {result.biosample_summary ? <div><BiosampleSummaryDisplay summary={result.biosample_summary} organisms={organismNames.concat(GeneticModificationOrganismNames(biosamples))} /> </div> : null}
                        </div>
                    : null}
                    <div className="result-item__data-row">
                        {result.target && result.target.label ?
                            <div><span className="result-item__property-title">Target: </span>
                                <a href={result.target['@id']} aria-label={`Target ${result.target.label}`}>{result.target.label}</a>
                                {motifsLink ?
                                    <span> (<a href={`https://factorbook.org/experiment/${motifsSearch}`}>Factorbook</a>)</span>
                                : null}
                            </div>
                        : null}

                        {mode !== 'cart-view' ?
                            <>
                                {synchronizations && synchronizations.length > 0 ?
                                    <div><span className="result-item__property-title">Synchronization timepoint: </span>{synchronizations.join(', ')}</div>
                                : null}
                                {elementsSelectionMethod && elementsSelectionMethod.length > 0 ?
                                    <div><span className="result-item__property-title">Elements selection method: </span>{elementsSelectionMethod.join(', ')}</div>
                                : null}
                                {referenceLoci && referenceLoci.length > 0 ?
                                    <div><span className="result-item__property-title">Loci: </span>{referenceLoci.map((locus, i) => (
                                        <span key={locus['@id']}>
                                            {i > 0 ? ', ' : null}
                                            <a href={locus['@id']}>
                                                {locus.symbol}
                                            </a>
                                        </span>
                                    ))}
                                    </div>
                                : null}
                                {tilingModality && tilingModality.length > 0 ?
                                    <div><span className="result-item__property-title">Tiling modality: </span>{tilingModality.join(', ')}</div>
                                : null}
                                <div><span className="result-item__property-title">Lab: </span>{result.lab.title}</div>
                                <div><span className="result-item__property-title">Project: </span>{result.award.project}</div>
                                {!isFunctionalExperiment && treatments.length > 0 ?
                                    <div><span className="result-item__property-title">Treatment{uniqueTreatments.length !== 1 ? 's' : ''}: </span>
                                        <span>
                                            {uniqueTreatments.join(', ')}
                                        </span>
                                    </div>
                                : null}
                                {isFunctionalExperiment && uniquePerturbationTreatments.length > 0 ?
                                    <div><span className="result-item__property-title">Treatment{uniquePerturbationTreatments.length !== 1 ? 's' : ''}: </span>
                                        <span>
                                            {uniquePerturbationTreatments.join(', ')}
                                        </span>
                                    </div>
                                : null}
                                {Object.keys(seriesMap).map((seriesType) => (
                                    <div key={seriesType}>
                                        <span className="result-item__property-title">{seriesType.replace(/([A-Z])/g, ' $1')}: </span>
                                        {seriesMap[seriesType].map(
                                            (series, i) => (
                                                <span key={series.accession}>
                                                    {i > 0 ? ', ' : null}
                                                    <a href={series['@id']}>
                                                        {series.accession}
                                                    </a>
                                                </span>
                                            ),
                                        )}
                                    </div>
                                ))}
                                {screenLink ?
                                    <div><span className="result-item__property-title">candidate Cis-Regulatory Elements (cCREs): </span><a href={`https://screen.encodeproject.org/search?q=${screenSearch}&assembly=${screenAssembly}`}>SCREEN</a></div>
                                : null}
                                {cellularComponents && cellularComponents.length > 0 ?
                                    <div><span className="result-item__property-title">Cellular component{cellularComponents.length > 1 ? 's' : ''}: </span>{cellularComponents.join(', ')}</div>
                                : null}
                                {constructionPlatforms && constructionPlatforms.length > 0 ?
                                    <div><span className="result-item__property-title">Library construction platform{constructionPlatforms.length > 1 ? 's' : ''}: </span>{constructionPlatforms.join(', ')}</div>
                                : null}
                                {constructionMethods && constructionMethods.length > 0 ?
                                    <div><span className="result-item__property-title">Library construction method{constructionMethods.length > 1 ? 's' : ''}: </span>{constructionMethods.join(', ')}</div>
                                : null}
                            </>
                        : null}
                    </div>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">{displayType}</div>
                    <div className="result-item__meta-id">{` ${result.accession}`}</div>
                    {mode !== 'cart-view' ?
                        <>
                            <Status item={result.status} badgeSize="small" css="result-table__status" />
                            {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
                        </>
                    : null}
                </div>
                {cartControls && isResultAllowedInCart && !(reactContext.actions && reactContext.actions.length > 0) ?
                    <div className="result-item__cart-control">
                        <CartToggle element={result} />
                    </div>
                : null}
                <PickerActions context={result} />
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties })}
        </div>
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
globals.listingViews.register(Experiment, 'SingleCellUnit');
globals.listingViews.register(Experiment, 'TransgenicEnhancerExperiment');


const AnnotationComponent = ({ context: result, cartControls, mode, auditIndicators, auditDetail }, reactContext) => (
    <div className={resultItemClass(result)}>
        <div className="result-item">
            <div className="result-item__data">
                <a href={result['@id']} className="result-item__link">
                    {datasetTypes[result['@type'][0]]}
                    {result.description ? <span>{`: ${result.description}`}</span> : null}
                </a>
                <div className="result-item__data-row">
                    <div><strong>Lab: </strong>{result.lab.title}</div>
                    <div><strong>Project: </strong>{result.award.project}</div>
                    <TargetsDataLine result={result} />
                </div>
            </div>
            <div className="result-item__meta">
                <div className="result-item__meta-title">Annotation</div>
                <div className="result-item__meta-id">{` ${result.accession}`}</div>
                {mode !== 'cart-view' ?
                    <>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
                    </>
                : null}
            </div>
            {cartControls && !(reactContext.actions && reactContext.actions.length > 0) ?
                <div className="result-item__cart-control">
                    <CartToggle element={result} />
                </div>
            : null}
            <PickerActions context={result} />
        </div>
        {auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties })}
    </div>
);

AnnotationComponent.propTypes = {
    /** Dataset search results */
    context: PropTypes.object.isRequired,
    /** True if displayed in active cart */
    cartControls: PropTypes.bool,
    /** Special search-result modes, e.g. "picker" */
    mode: PropTypes.string,
    /** Audit decorator function */
    auditIndicators: PropTypes.func.isRequired,
    /** Audit decorator function */
    auditDetail: PropTypes.func.isRequired,
};

AnnotationComponent.defaultProps = {
    cartControls: false,
    mode: '',
};

AnnotationComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Annotation = auditDecor(AnnotationComponent);

globals.listingViews.register(Annotation, 'Annotation');


const DatasetComponent = ({ context: result, auditIndicators, auditDetail }, reactContext) => {
    const haveFileSet = result['@type'].indexOf('FileSet') >= 0;
    const isReference = result['@type'][0] === 'Reference';

    return (
        <div className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">
                        <span>{`${datasetTypes[result['@type'][0]]}`}</span>
                        <span>{result.description ? <span>{`: ${result.description}`}</span> : null}</span>
                    </a>
                    <div className="result-item__data-row">
                        {(isReference && result.crispr_screen_tiling) ?
                            <div><span className="result-item__property-title">CRISPR screen tiling: </span>{result.crispr_screen_tiling}</div>
                         : null}
                        <div><span className="result-item__property-title">Lab: </span>{result.lab.title}</div>
                        <div><span className="result-item__property-title">Project: </span>{result.award.project}</div>
                    </div>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">{haveFileSet ? 'FileSet' : 'Dataset'}</div>
                    <div className="result-item__meta-id">{` ${result.accession}`}</div>
                    <Status item={result.status} badgeSize="small" css="result-table__status" />
                    {auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
                </div>
                <PickerActions context={result} />
            </div>
            {auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties })}
        </div>
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


/**
 * Renders the search results of all Series dataset objects.
 */
const SeriesComponent = ({ context: result, cartControls, removeConfirmation, auditDetail, auditIndicators }, reactContext) => {
    let assays = [];
    let organism;
    let crisprReadout = [];
    let examineLociGene = [];
    let perturbationType = [];
    let fullStages = [];
    let ages = [];
    let ageUnits;
    let postSynchTime = [];
    let synchronization;
    let postSynchronizationTimeUnits;
    let postDiffTime = [];
    let postDiffTimeUnits;
    let lifeStages = [];
    let organisms = [];
    let phases = [];
    let perturbationTreatments = [];
    let treatmentTerm = [];
    let treatments = [];
    let treatmentUnit;
    let diseases = [];
    let constructionMethods = [];
    let constructionPlatforms = [];
    let cellularComponents = [];

    const treatmentTime = result['@type'].indexOf('TreatmentTimeSeries') >= 0;
    const treatmentConcentration = result['@type'].indexOf('TreatmentConcentrationSeries') >= 0;
    const fccSeries = result['@type'].indexOf('FunctionalCharacterizationSeries') >= 0;
    const organismSeries = result['@type'].indexOf('OrganismDevelopmentSeries') >= 0;
    const differentiationSeries = result['@type'].indexOf('DifferentiationSeries') >= 0;

    const biosampleTerm = result.biosample_ontology ? result.biosample_ontology[0].term_name : '';
    const biosampleclassifications = result.biosample_ontology ? result.biosample_ontology[0].classification : '';

    let biosamples;
    if (differentiationSeries && result.biosample_ontology && Object.keys(result.biosample_ontology).length > 1) {
        biosamples = result.biosample_ontology.map((biosample) => biosample.term_name);
    }

    // Collect crispr_screen_tiling, examined_loci, and elements_selection_method for each dataset elements_references in FunctionalCharacterizationSeries
    let tilingModality = [];
    let referenceLoci = [];
    let elementsSelectionMethod = [];
    if (fccSeries) {
        if (result.elements_references && result.elements_references.length > 0) {
            result.elements_references.forEach((er) => {
                tilingModality = er.crispr_screen_tiling ? tilingModality.concat(er.crispr_screen_tiling) : tilingModality;
                referenceLoci = er.examined_loci ? referenceLoci.concat(er.examined_loci) : referenceLoci;
                elementsSelectionMethod = er.elements_selection_method ? elementsSelectionMethod.concat(er.elements_selection_method) : elementsSelectionMethod;
            });
        }
        tilingModality = _.uniq(tilingModality);
        referenceLoci = _.uniq(referenceLoci, (locus) => locus['@id']);
        elementsSelectionMethod = _.uniq(elementsSelectionMethod);
    }

    // Dig through the biosample life stages and ages
    if (result.related_datasets && result.related_datasets.length > 0) {
        result.related_datasets.forEach((dataset) => {
            if (dataset.assay_term_name) {
                assays.push(dataset.assay_term_name);
            }
            if (dataset.crispr_screen_readout) {
                crisprReadout.push(dataset.crispr_screen_readout);
            }
            if (dataset.examined_loci && dataset.examined_loci.length > 0) {
                dataset.examined_loci.forEach((loci) => {
                    examineLociGene.push(loci.gene.symbol);
                });
            }
            if (dataset.perturbation_type) {
                perturbationType.push(dataset.perturbation_type);
            }
            if (dataset.replicates && dataset.replicates.length > 0) {
                dataset.replicates.forEach((replicate) => {
                    if (replicate.library && replicate.library.biosample) {
                        const { biosample } = replicate.library;
                        const lifeStage = (biosample.life_stage && biosample.life_stage !== 'unknown') ? biosample.life_stage : '';
                        if (biosample.life_stage !== 'unknown' && biosample.life_stage && biosample.age_display) {
                            const fullStage = `${biosample.life_stage[0].toUpperCase()}${biosample.age_display.split(' ')[0]}`;
                            fullStages.push(fullStage);
                            ages.push(biosample.age_display.split(' ')[0]);
                            ageUnits = biosample.age_display.split(' ')[1];
                        }

                        if (biosample.disease_term_name && biosample.disease_term_name.length > 0) {
                            diseases.push(...biosample.disease_term_name);
                        }
                        if (biosample.post_synchronization_time) {
                            postSynchTime.push(biosample.post_synchronization_time);
                        }
                        if (biosample.synchronization) {
                            ({ synchronization } = biosample);
                        }
                        if (biosample.post_synchronization_time_units) {
                            postSynchronizationTimeUnits = biosample.post_synchronization_time_units;
                        }
                        if (biosample.post_differentiation_time) {
                            postDiffTime.push(biosample.post_differentiation_time);
                        }
                        if (biosample.post_differentiation_time_units) {
                            postDiffTimeUnits = biosample.post_differentiation_time_units;
                        }
                        if (lifeStage) {
                            lifeStages.push(lifeStage);
                        }
                        if (biosample.treatments?.length > 0 && differentiationSeries) {
                            treatmentTerm = [...treatmentTerm, ...biosample.treatments.filter((t) => t.treatment_term_name).map((t) => t.treatment_term_name)];
                        }
                        if (biosample.treatments?.length > 0 && fccSeries) {
                            perturbationTreatments = biosample.treatments.filter((a) => a.purpose === 'perturbation').map((t) => t.treatment_term_name);
                        }
                        if (biosample.treatments?.length > 0 && treatmentConcentration) {
                            treatmentTerm = [...treatmentTerm, ...biosample.treatments.filter((t) => t.treatment_term_name).map((t) => t.treatment_term_name)];
                            treatments = [...treatments, ...biosample.treatments.reduce((output, t) => {
                                if (t.amount) {
                                    output.push(t.amount);
                                }
                                return output;
                            }, [])];
                            treatmentUnit = biosample.treatments[0].amount_units;
                        }
                        if (biosample.treatments?.length > 0 && treatmentTime) {
                            treatmentTerm = [...treatmentTerm, ...biosample.treatments.filter((t) => t.treatment_term_name).map((t) => t.treatment_term_name)];
                            treatments = [...treatments, ...biosample.treatments.reduce((output, t) => {
                                if (t.duration) {
                                    output.push(t.duration);
                                }
                                return output;
                            }, [])];
                            treatmentUnit = `${biosample.treatments[0].duration_units}s`;
                        }
                        if (biosample.organism && biosample.organism.scientific_name) {
                            organisms.push(biosample.organism.scientific_name);
                        }
                        if (biosample.phase) {
                            phases.push(biosample.phase);
                        }
                    }
                    if (replicate.library) {
                        if (replicate.library.construction_platform) {
                            constructionPlatforms.push(replicate.library.construction_platform.term_name);
                        }
                        if (replicate.library.construction_method) {
                            constructionMethods.push(replicate.library.construction_method);
                        }
                        if (replicate.library.subcellular_fraction_term_name) {
                            cellularComponents.push(replicate.library.subcellular_fraction_term_name);
                        }
                    }
                });
            }
        });
        lifeStages = _.uniq(lifeStages);
        fullStages = _.uniq(fullStages);
        ages = _.uniq(ages).sort();
        postSynchTime = _.uniq(postSynchTime).sort();
        postDiffTime = _.uniq(postDiffTime).sort();
        organisms = _.uniq(organisms);
        phases = _.uniq(phases);
        examineLociGene = _.uniq(examineLociGene);
        crisprReadout = _.uniq(crisprReadout);
        perturbationType = _.uniq(perturbationType);
        perturbationTreatments = _.uniq(perturbationTreatments);
        diseases = _.uniq(diseases);
        constructionPlatforms = _.uniq(constructionPlatforms);
        constructionMethods = _.uniq(constructionMethods);
        cellularComponents = _.uniq(cellularComponents);
    }
    const lifeSpec = _.compact([lifeStages.length === 1 ? lifeStages[0] : null, ages.length === 1 ? ages[0] : null]);

    // Get list of assay labels
    if (result.assay_term_name) {
        assays = _.uniq(result.assay_term_name);
    }
    if (assays.length > 0) {
        assays = _.uniq(assays);
    }

    const sortedTreatments = _.uniq(treatments).sort((a, b) => (a - b));
    treatmentTerm = _.uniq(treatmentTerm);
    let uniqueTreatments;
    if (sortedTreatments.length > 0) {
        uniqueTreatments = `${treatmentTerm.join(', ')} at ${sortedTreatments.join(', ')} ${treatmentUnit}`;
    } else {
        uniqueTreatments = treatmentTerm.join(', ');
    }

    return (
        <div className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">
                        {fccSeries
                            ? (
                                <>
                                    {perturbationType.length > 0 ?
                                        <span>
                                            {`${perturbationType.join(', ')}`}
                                        </span>
                                    : null}
                                    {assays.length > 0 ?
                                        <span>
                                            {` ${assays.join(', ')} series`}
                                        </span>
                                    : null}
                                    {referenceLoci.length > 0 ?
                                        <span>{referenceLoci.length === 1 ? ` of ${referenceLoci[0].symbol}` : ' of multiple loci'}</span>
                                    : null}
                                </>
                            )
                            : <span>{`${datasetTypes[result['@type'][0]]}`}</span>
                        }
                        {biosampleTerm ? <span>{` in ${biosampleTerm}`}</span> : null}
                        {fccSeries
                            ? (
                                <>
                                    {examineLociGene.length > 0 ?
                                        <span>
                                            {` with readout of ${examineLociGene.join(', ')}`}
                                        </span>
                                    : null}
                                    {crisprReadout.length > 0 ?
                                        <span>
                                            {` (${crisprReadout.join(', ')})`}
                                        </span>
                                    : null}
                                </>
                            )
                        : null}
                        {(!fccSeries && (organism || lifeSpec.length > 0)) || (fccSeries && biosampleclassifications !== 'cell line' && (organism || lifeSpec.length > 0)) ?
                            <span>
                                {' ('}
                                {organism ? <i>{organism}</i> : null}
                                {lifeSpec.length > 0 ? <span>{organism ? ', ' : ''}{lifeSpec.join(', ')}</span> : null}
                                )
                            </span>
                        : null}
                    </a>
                    <div className="result-item__data-row">
                        {result.dataset_type ?
                            <div><span className="result-item__property-title">Dataset type: </span>{result.dataset_type}</div>
                        : null}
                        {assays && assays.length > 0 ?
                            <div><span className="result-item__property-title">Assays: </span>{assays.join(', ')}</div>
                        : null}
                        {biosamples && biosamples.length > 0 && differentiationSeries ?
                            <div><span className="result-item__property-title">Biosamples: </span>{biosamples.join(', ')}</div>
                        : null}
                        {phases && phases.length > 0 ?
                            <div><span className="result-item__property-title">Cell cycle phases: </span>{phases.join(', ')}</div>
                        : null}
                        {(organisms.length > 0 && organismSeries) ?
                            <div><span className="result-item__property-title">Organism: </span>{organisms.join(', ')}</div>
                        : null}
                        {(ages.length > 0 && organismSeries && (organisms.indexOf('Homo sapiens') > -1)) ?
                            <div><span className="result-item__property-title">Ages: </span>{ages.join(', ')} {ageUnits}</div>
                        : null}
                        {(fullStages.length > 0 && organismSeries && (organisms.indexOf('Mus musculus') > -1)) ?
                            <div><span className="result-item__property-title">Stages: </span>{fullStages.join(', ')}</div>
                        : null}
                        {synchronization ?
                            <div><span className="result-item__property-title">Synchronization: </span>{synchronization}</div>
                        : null}
                        {postSynchTime.length > 0 ?
                            <div><span className="result-item__property-title">Post-synchronization time: </span>{postSynchTime.join(', ')} {postSynchronizationTimeUnits}s</div>
                        : null}
                        {postDiffTime.length > 0 ?
                            <div><span className="result-item__property-title">Post-differentiation time: </span>{postDiffTime.join(', ')} {postDiffTimeUnits}s</div>
                        : null}
                        { (uniqueTreatments && (treatmentTime || treatmentConcentration || differentiationSeries)) ?
                            <div><span className="result-item__property-title">Treatment{treatments.length !== 1 ? 's' : ''}: </span>
                                <span>
                                    {uniqueTreatments}
                                </span>
                            </div>
                        : null}
                        <TargetsDataLine result={result} targetPropertyName="target" />
                        {diseases.length > 0 ? <div><span className="result-item__property-title">Diseases: </span>{diseases.join(', ')}</div> : null}
                        <div><span className="result-item__property-title">Lab: </span>{result.lab.title}</div>
                        <div><span className="result-item__property-title">Project: </span>{result.award.project}</div>
                        {cellularComponents.length > 0 ?
                            <div><span className="result-item__property-title">Cellular component{cellularComponents.length > 1 ? 's' : ''}: </span>{cellularComponents.join(', ')}</div>
                        : null}
                        {constructionPlatforms.length > 0 ?
                            <div><span className="result-item__property-title">Construction platform{constructionPlatforms.length > 1 ? 's' : ''}: </span>{constructionPlatforms.join(', ')}</div>
                        : null}
                        {constructionMethods.length > 0 ?
                            <div><span className="result-item__property-title">Construction method{constructionMethods.length > 1 ? 's' : ''}: </span>{constructionMethods.join(', ')}</div>
                        : null}
                        {elementsSelectionMethod && elementsSelectionMethod.length > 0 ?
                            <div><span className="result-item__property-title">Elements selection method: </span>{elementsSelectionMethod.join(', ')}</div>
                        : null}
                        {referenceLoci && referenceLoci.length > 0 ?
                            <div><span className="result-item__property-title">Loci: </span>{referenceLoci.map((locus, i) => (
                                <span key={locus['@id']}>
                                    {i > 0 ? ', ' : null}
                                    <a href={locus['@id']}>
                                        {locus.symbol}
                                    </a>
                                </span>
                            ))}
                            </div>
                        : null}
                        {tilingModality.length > 0 ?
                            <div><span className="result-item__property-title">Tiling modality: </span>{tilingModality.join(', ')}</div>
                        : null}
                        {fccSeries && perturbationTreatments.length > 0 ?
                            <div><span className="result-item__property-title">Treatment{perturbationTreatments.length !== 1 ? 's' : ''}: </span>{perturbationTreatments.join(', ')}</div>
                        : null}
                    </div>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">Series</div>
                    <div className="result-item__meta-id">{` ${result.accession}`}</div>
                    <Status item={result.status} badgeSize="small" css="result-table__status" />
                    {auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
                </div>
                {cartControls && !(reactContext.actions && reactContext.actions.length > 0) ?
                    <div className="result-item__cart-control">
                        <CartToggle
                            element={result}
                            removeConfirmation={Object.keys(removeConfirmation).length > 0 ? removeConfirmation : { immediate: true }}
                        />
                    </div>
                : null}
                <PickerActions context={result} />
            </div>
            {auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties })}
        </div>
    );
};

SeriesComponent.propTypes = {
    context: PropTypes.object.isRequired, // Dataset search results
    /** True to display cart toggle button */
    cartControls: PropTypes.bool,
    /** Needed for series removals that require user confirmation */
    removeConfirmation: PropTypes.shape({
        /** Called by cart toggle when the user requests removing a series object from the cart */
        requestRemove: PropTypes.func,
        /** Called when the user confirms removing a series object from the cart */
        requestRemoveConfirmation: PropTypes.func,
        /** True if the user has confirmed they want to remove the series object from the cart */
        isRemoveConfirmed: PropTypes.bool,
        /** True to remove series and its related datasets without a confirmation modal */
        immediate: PropTypes.bool,
    }),
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

SeriesComponent.defaultProps = {
    cartControls: false,
    removeConfirmation: {},
};

SeriesComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Series = auditDecor(SeriesComponent);

globals.listingViews.register(Series, 'Series');


const TargetComponent = ({ context: result, auditIndicators, auditDetail }, reactContext) => (
    <div className={resultItemClass(result)}>
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
    </div>
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
        <div className={resultItemClass(result)}>
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
        </div>
    );
};

Image.propTypes = {
    context: PropTypes.object.isRequired, // Image search results
};

globals.listingViews.register(Image, 'Image');


/**
 * Context to pass options from facets to any downstream facet code that needs it.
 */
export const FacetContext = React.createContext({});


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
        const filter = this.props.filters.filter((f) => f.field === 'searchTerm');
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
        const { value } = e.target;
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
            <input
                type="search"
                className="search-query"
                placeholder="Enter search term(s)"
                defaultValue={this.getValue(this.props)}
                onKeyDown={this.onKeyDown}
                data-test="filter-search-box"
            />
        );
    }
}

TextFilter.propTypes = {
    filters: PropTypes.array.isRequired,
    searchBase: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
};


/**
 * Renders a single facet of any type.
 */
const Facet = ({
    facet,
    expandedFacets,
    results,
    mode,
    onFilter,
    expanderClickHandler,
    keyDownHandler,
    isExpandable,
    forceDisplay,
}) => {
    const parsedUrl = results && results['@id'] && url.parse(results['@id']);

    // Filter the filters to just the ones relevant to the current facet,
    // matching negation filters too.
    const relevantFilters = results && results.filters.filter((filter) => (
        filter.field === facet.field || filter.field === `${facet.field}!`
    ));

    // Look up the renderer registered for this facet and use it to render this
    // facet if a renderer exists. A non-existing renderer suppresses the
    // display of a facet.
    let FacetRenderer;
    if (facet.specialFieldName) {
        FacetRenderer = SpecialFacetRegistry.Facet.lookup(facet.field);
    } else {
        FacetRenderer = FacetRegistry.Facet.lookup(facet.field);
    }
    const isExpanded = expandedFacets.has(facet.field);
    return FacetRenderer && <FacetRenderer
        key={facet.specialFieldName || facet.field}
        facet={facet}
        results={results}
        mode={mode}
        relevantFilters={relevantFilters}
        pathname={parsedUrl.pathname}
        queryString={parsedUrl.query}
        onFilter={onFilter}
        isExpanded={isExpanded}
        handleExpanderClick={expanderClickHandler}
        handleKeyDown={keyDownHandler}
        isExpandable={isExpandable}
        forceDisplay={forceDisplay}
    />;
};

Facet.propTypes = {
    /** Facet to render from search results */
    facet: PropTypes.object.isRequired,
    /** List of facets that are expanded */
    expandedFacets: PropTypes.object.isRequired,
    /** Entire search results object */
    results: PropTypes.object.isRequired,
    /** Special facet-term click handler for edit forms */
    onFilter: PropTypes.func,
    /** Called when the user clicks a facet title to expand/collapse it */
    expanderClickHandler: PropTypes.func.isRequired,
    /** Called when the user presses a key while the facet title has focus */
    keyDownHandler: PropTypes.func.isRequired,
    /** True if the collapsible, false otherwise  */
    isExpandable: PropTypes.bool,
    /** True to force facet to display in cases it would normally be hidden */
    forceDisplay: PropTypes.bool,
    /** Special search-result modes, e.g. "picker" */
    mode: PropTypes.string,
};

Facet.defaultProps = {
    onFilter: null,
    isExpandable: false,
    forceDisplay: false,
    mode: '',
};


// Displays the entire list of facets. It contains a number of <Facet> components.
export const FacetList = (props) => {
    const {
        context,
        facets,
        filters,
        mode,
        orientation,
        hideTextFilter,
        addClasses,
        docTypeTitleSuffix,
        supressTitle,
        onFilter,
        isExpandable,
        hideDocType,
        options,
    } = props;

    const [expandedFacets, setExpandFacets] = React.useState(new Set());
    const [expandedGroups, setExpandedGroups] = React.useState(() => new Set());

    // Get facets from storage that need to be expanded
    React.useEffect(() => {
        const facetsStorage = sessionStorage.getItem(FACET_STORAGE);
        const facetList = new Set(facetsStorage ? facetsStorage.split(',') : []);

        sessionStorage.setItem(FACET_STORAGE, facetList.size !== 0 ? [...facetList].join(',') : []);
        setExpandFacets(facetList); // initialize facet collapse-state
    }, []);

    // Only on initialize load, get facets from facet-section and schema that need to be expanded
    React.useEffect(() => {
        const facetsStorage = sessionStorage.getItem(FACET_STORAGE);
        const facetList = new Set(facetsStorage ? facetsStorage.split(',') : []);

        facets.forEach((facet) => {
            const { field } = facet;
            const newlyLoadedFacetStorage = `${MARKER_FOR_NEWLY_LOADED_FACET_PREFIX}${field}`;
            const isFacetNewlyLoaded = sessionStorage.getItem(newlyLoadedFacetStorage);

            const relevantFilters = context && context.filters.filter((filter) => (
                filter.field === facet.field || filter.field === `${facet.field}!`
            ));

            // auto-open facets based on selected terms (see url) or it set in the schema (open_on_load)
            if (!isFacetNewlyLoaded && ((relevantFilters && relevantFilters.length > 0) || facet.open_on_load === true)) {
                sessionStorage.setItem(newlyLoadedFacetStorage, field); // ensure this is not called again on this active session storage
                facetList.add(facet.field);
            }
        });

        sessionStorage.setItem(FACET_STORAGE, facetList.size !== 0 ? [...facetList].join(',') : []);
        setExpandFacets(facetList); // initialize facet collapse-state
    }, [context, facets]);

    // Initialize expanded facet groups if `facet_groups` has changed.
    const prevFacetGroups = usePrevious(context.facet_groups);
    React.useEffect(() => {
        if (!areFacetGroupsEqual(prevFacetGroups, context.facet_groups)) {
            // Initialize the expanded groups to all be closed except for the first facet group.
            const firstFacetGroupIdentifier = context.facet_groups && generateFacetGroupIdentifier(context.facet_groups[0]);
            setExpandedGroups(new Set(firstFacetGroupIdentifier && [firstFacetGroupIdentifier]));
        }
    }, [context.facet_groups, prevFacetGroups]);

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
            facetList = new Set(status ? [] : facets.map((f) => f.field));
        } else {
            facetList = new Set(expandedFacets);
            facetList[status ? 'delete' : 'add'](field);
        }

        sessionStorage.setItem(FACET_STORAGE, [...facetList].join(',')); // replace rather than update memory
        setExpandFacets(facetList); // controls open/closed facets
    };

    /**
     * Called when the user clicks a facet group title to expand or collapse it.
     * @param {string} groupIdentifier Title of the facet group
     * @param {boolean} altKey True if the user has held down the alt-key
     */
    const handleGroupExpanderClick = (groupIdentifier, altKey) => {
        const isGroupExpanded = expandedGroups.has(groupIdentifier);
        if (altKey) {
            if (isGroupExpanded) {
                // Empty the list of expanded groups to close all facet groups.
                const newExpandedGroups = new Set();
                setExpandedGroups(newExpandedGroups);
            } else {
                // Add every facet group identifier to the expanded groups to open all facet groups.
                const allFacetGroupIdentifiers = generateFacetGroupIdentifierList(context.facet_groups);
                const newExpandedGroups = new Set(allFacetGroupIdentifiers);
                setExpandedGroups(newExpandedGroups);
            }
        } else {
            const newExpandedGroups = new Set(expandedGroups);
            if (isGroupExpanded) {
                newExpandedGroups.delete(groupIdentifier);
            } else {
                newExpandedGroups.add(groupIdentifier);
            }
            setExpandedGroups(newExpandedGroups);
        }
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

    // Combine facets from search results with special facets, and treat them mostly the same.
    const allFacets = SpecialFacetRegistry.Facet.getFacets().concat(facets);
    const topLevelFacets = filterTopLevelFacets(allFacets, context.facet_groups);
    const isNameDisplayed = generateFacetGroupNameList(context.facet_groups).length > 1;

    // If we have facet groups, add an "Other filters" group to hold facets not included in a group.
    let facetGroups = context.facet_groups || [];
    if (facetGroups.length > 0 && topLevelFacets.length > 0) {
        const otherFacetGroup = {
            name: 'OtherFilters',
            title: 'Other filters',
            facet_fields: topLevelFacets.map((facet) => facet.field),
        };
        facetGroups = facetGroups.concat(otherFacetGroup);
    }

    return (
        <div className="search-results__facets">
            <div className={`box facets${addClasses ? ` ${addClasses}` : ''}`}>
                <div className={`orientation${orientation === 'horizontal' ? ' horizontal' : ''}`} data-test="facetcontainer">
                    <FacetContext.Provider value={options}>
                        {(!supressTitle || clearButton) ?
                            <div className="search-header-control">
                                {!(hideDocType) ?
                                    <DocTypeTitle searchResults={context} wrapper={(children) => <h1>{children} {docTypeTitleSuffix}</h1>} />
                                : null}
                                {context.clear_filters ?
                                    <ClearFilters clearUri={context.clear_filters} searchUri={context['@id']} enableDisplay={clearButton} />
                                : null}
                            </div>
                        : null}
                        {mode === 'picker' && !hideTextFilter ? <TextFilter {...props} filters={filters} /> : ''}
                        {facetGroups.length > 0
                            ? (
                                <div className="facet-list-wrapper facet-list-wrapper--facet-group">
                                    {props.bodyMap ?
                                        <BodyMapThumbnailAndModal
                                            context={context}
                                            location={context['@id']}
                                            organism="Homo sapiens"
                                        />
                                    : null}
                                    {props.additionalFacet ?
                                        <>
                                            {props.additionalFacet}
                                        </>
                                    : null}
                                    {facetGroups.map((group) => {
                                        // Only render facet group if it actually contains facets.
                                        const facetGroupFieldsInFacets = getFacetGroupFieldsInFacets(group, allFacets);
                                        if (facetGroupFieldsInFacets.length > 0) {
                                            const groupIdentifier = generateFacetGroupIdentifier(group);
                                            const isGroupExpanded = expandedGroups.has(groupIdentifier);
                                            return (
                                                <FacetGroup
                                                    key={groupIdentifier}
                                                    group={group}
                                                    filters={context.filters}
                                                    isExpanded={isGroupExpanded}
                                                    isNameDisplayed={isNameDisplayed}
                                                    expanderHandler={handleGroupExpanderClick}
                                                >
                                                    {isGroupExpanded && group.facet_fields.map((facetField) => {
                                                        const facet = allFacets.find((singleFacet) => singleFacet.field === facetField);
                                                        if (facet) {
                                                            return (
                                                                <Facet
                                                                    key={facet.specialFieldName || facet.field}
                                                                    facet={facet}
                                                                    expandedFacets={expandedFacets}
                                                                    results={context}
                                                                    mode={mode}
                                                                    onFilter={onFilter}
                                                                    expanderClickHandler={handleExpanderClick}
                                                                    keyDownHandler={handleKeyDown}
                                                                    isExpandable={isExpandable}
                                                                    forceDisplay
                                                                />
                                                            );
                                                        }
                                                        return null;
                                                    })}
                                                </FacetGroup>
                                            );
                                        }
                                        return null;
                                    })}
                                </div>
                            )
                            : (
                                <>
                                    {topLevelFacets.length > 0 &&
                                        <div className="facet-list-wrapper">
                                            {props.additionalFacet ?
                                                <>
                                                    {props.additionalFacet}
                                                </>
                                            : null}
                                            {topLevelFacets.map((facet) => (
                                                <Facet
                                                    key={facet.specialFieldName || facet.field}
                                                    facet={facet}
                                                    expandedFacets={expandedFacets}
                                                    results={context}
                                                    mode={mode}
                                                    onFilter={onFilter}
                                                    expanderClickHandler={handleExpanderClick}
                                                    keyDownHandler={handleKeyDown}
                                                    isExpandable={isExpandable}
                                                />
                                            ))}
                                        </div>
                                    }
                                </>
                            )
                        }
                    </FacetContext.Provider>
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
    hideDocType: PropTypes.bool,
    hideTextFilter: PropTypes.bool,
    docTypeTitleSuffix: PropTypes.string,
    addClasses: PropTypes.string, // CSS classes to use if the default isn't needed.
    /** True to suppress the display of facet-list title */
    supressTitle: PropTypes.bool,
    /** Special facet-term click handler for edit forms */
    onFilter: PropTypes.func,
    /** True if the collapsible, false otherwise  */
    isExpandable: PropTypes.bool,
    bodyMap: PropTypes.bool,
    additionalFacet: PropTypes.object,
    /** Options to pass to facet components in FacetContext */
    options: PropTypes.object,
};

FacetList.defaultProps = {
    mode: '',
    orientation: 'vertical',
    hideDocType: false,
    hideTextFilter: false,
    addClasses: '',
    docTypeTitleSuffix: 'search',
    supressTitle: false,
    onFilter: null,
    isExpandable: true,
    bodyMap: false,
    additionalFacet: null,
    options: {},
};

FacetList.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
    location_href: PropTypes.string,
};


/**
 * Display the "Clear filters" link.
 */
export const ClearFilters = ({ clearUri, searchUri, enableDisplay }) => {
    // Preserve any 'config=' query parameters in the current URI in `clearUri`.
    let composedClearUri = clearUri;
    const parsedSearchUri = url.parse(searchUri);
    const searchQuery = new QueryString(parsedSearchUri.query);
    const searchQueryKeyValues = searchQuery.getKeyValues('config');
    if (searchQueryKeyValues.length > 0) {
        // Add the 'config=' query parameters from the current URI to the clear URI.
        const parsedClearUri = url.parse(clearUri);
        const clearQuery = new QueryString(parsedClearUri.query);
        searchQueryKeyValues.forEach((value) => {
            clearQuery.addKeyValue('config', value);
        });
        composedClearUri = `?${clearQuery.format()}`;
    }

    return (
        <div className="clear-filters-control">
            {enableDisplay && (
                <div className="filter-container">
                    <a href={composedClearUri} className="filter-link">
                        <div className="filter-link__title">
                            Clear all selections
                        </div>
                        <div className="filter-link__icon">
                            {svgIcon('multiplication')}
                        </div>
                    </a>
                </div>
            )}
        </div>
    );
};

ClearFilters.propTypes = {
    /** URI for the Clear Filters link */
    clearUri: PropTypes.string.isRequired,
    /** Current search page's URI */
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
    const modalText = canDownload
        ? null
        : (
            <>
                <p>
                    This search is too large (&gt;{MAX_DOWNLOADABLE_RESULT} datasets) to automatically generate a manifest or metadata file.
                </p>
                <p>
                    You can directly access the files in AWS: <a href="https://registry.opendata.aws/encode-project/" target="_blank" rel="noopener noreferrer">https://registry.opendata.aws/encode-project/</a>
                </p>
            </>
        );

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
                {showDownloadButton
                    ? <BatchDownloadControls results={context} additionalFilters={additionalFilters} modalText={modalText} canDownload={canDownload} />
                    : null}
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
    /** Text to display with disabled Visualize button */
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

        // Bind `this` to non-React methods.
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
        const { context, searchBase, actions, hideDocType, bodyMap } = this.props;
        const { facets, total, columns, filters } = context;
        const results = context['@graph'];
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
                    hideDocType={hideDocType}
                    bodyMap={bodyMap}
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
    hideDocType: PropTypes.bool,
    bodyMap: PropTypes.bool,
};

ResultTable.defaultProps = {
    actions: [],
    searchBase: '',
    currentRegion: null,
    hideDocType: false,
    bodyMap: false,
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
            results.map((result) => (
                <li key={result['@id']} className="result-item__wrapper">
                    {Listing({ context: result, columns, cartControls, mode })}
                </li>
            ))
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
        const { context } = this.props;
        const { notification } = context;
        const searchBase = url.parse(this.context.location_href).search || '';
        const facetdisplay = context.facets && context.facets.some((facet) => facet.total > 0);

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
