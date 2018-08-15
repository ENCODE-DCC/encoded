import React from 'react';
import PropTypes from 'prop-types';
import queryString from 'query-string';
import _ from 'underscore';
import url from 'url';
import { svgIcon } from '../libs/svg-icons';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/bootstrap/modal';
import { TabPanel, TabPanelPane } from '../libs/bootstrap/panel';
import { auditDecor } from './audit';
import { CartToggle, CartSearchControls } from './cart';
import { FetchedData, Param } from './fetched';
import GenomeBrowser from './genome_browser';
import * as globals from './globals';
import { Attachment } from './image';
import { BrowserSelector, requestSearch } from './objectutils';
import { DbxrefList } from './dbxref';
import Status from './status';
import { BiosampleSummaryString, BiosampleOrganismNames } from './typeutils';


// Should really be singular...
const types = {
    annotation: { title: 'Annotation file set' },
    antibody_lot: { title: 'Antibodies' },
    biosample: { title: 'Biosamples' },
    experiment: { title: 'Experiments' },
    gene: { title: 'Genes' },
    target: { title: 'Targets' },
    dataset: { title: 'Datasets' },
    image: { title: 'Images' },
    matched_set: { title: 'Matched set series' },
    aggregate_series: { title: 'Aggregate series' },
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
    AggregateSeries: types.aggregate_series.title,
    UcscBrowserComposite: types.ucsc_browser_composite.title,
};


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


/* eslint-disable react/prefer-stateless-function */
export class PickerActions extends React.Component {
    render() {
        if (this.context.actions && this.context.actions.length) {
            return (
                <div className="pull-right">
                    {this.context.actions.map(action => React.cloneElement(action, { key: this.props.context.name, id: this.props.context['@id'] }))}
                </div>
            );
        }

        // No actions; don't render anything.
        return <span />;
    }
}
/* eslint-enable react/prefer-stateless-function */

PickerActions.propTypes = {
    context: PropTypes.object.isRequired,
};

PickerActions.contextTypes = {
    actions: PropTypes.array,
};


/* eslint-disable react/prefer-stateless-function */
class ItemComponent extends React.Component {
    render() {
        const result = this.props.context;
        const title = globals.listingTitles.lookup(result)({ context: result });
        const itemType = result['@type'][0];
        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    {result.accession ?
                        <div className="pull-right type sentence-case search-meta">
                            <p>{itemType}: {` ${result.accession}`}</p>
                            {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
                        </div>
                    : null}
                    <div className="accession">
                        <a href={result['@id']}>{title}</a>
                    </div>
                    <div className="data-row">
                        {result.description}
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

ItemComponent.propTypes = {
    context: PropTypes.object.isRequired, // Component to render in a listing view
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ItemComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Item = auditDecor(ItemComponent);

globals.listingViews.register(Item, 'Item');


/* eslint-disable react/prefer-stateless-function */
class BiosampleComponent extends React.Component {
    render() {
        const result = this.props.context;
        const lifeStage = (result.life_stage && result.life_stage !== 'unknown') ? ` ${result.life_stage}` : '';
        const age = (result.age && result.age !== 'unknown') ? ` ${result.age}` : '';
        const ageUnits = (result.age_units && result.age_units !== 'unknown' && age) ? ` ${result.age_units}` : '';
        const separator = (lifeStage || age) ? ',' : '';
        const treatment = (result.treatments && result.treatments.length) ? result.treatments[0].treatment_term_name : '';

        // Calculate genetic modification properties for display.
        const rnais = [];
        const constructs = [];
        const mutatedGenes = [];
        if (result.applied_modifications && result.applied_modifications.length) {
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
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
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
                        {rnais.length ? <div><strong>RNAi targets: </strong>{rnais.join(', ')}</div> : null}
                        {constructs.length ? <div><strong>Constructs: </strong>{constructs.join(', ')}</div> : null}
                        {treatment ? <div><strong>Treatment: </strong>{treatment}</div> : null}
                        {mutatedGenes.length ? <div><strong>Mutated genes: </strong>{mutatedGenes.join(', ')}</div> : null}
                        {result.culture_harvest_date ? <div><strong>Culture harvest date: </strong>{result.culture_harvest_date}</div> : null}
                        {result.date_obtained ? <div><strong>Date obtained: </strong>{result.date_obtained}</div> : null}
                        {synchText ? <div><strong>Synchronization timepoint: </strong>{synchText}</div> : null}
                        <div><strong>Source: </strong>{result.source.title}</div>
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
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
};

const Biosample = auditDecor(BiosampleComponent);

globals.listingViews.register(Biosample, 'Biosample');


const ExperimentComponent = (props, reactContext) => {
    const { activeCart } = props;
    const result = props.context;
    let synchronizations;

    // Collect all biosamples associated with the experiment. This array can contain duplicate
    // biosamples, but no null entries.
    let biosamples = [];
    if (result.replicates && result.replicates.length) {
        biosamples = _.compact(result.replicates.map(replicate => replicate.library && replicate.library.biosample));
    }

    // Get all biosample organism names
    const organismNames = biosamples.length ? BiosampleOrganismNames(biosamples) : [];

    // Bek: Forrest should review the change for correctness
    // Collect synchronizations
    if (result.replicates && result.replicates.length) {
        synchronizations = _.uniq(result.replicates.filter(replicate =>
            replicate.library && replicate.library.biosample && replicate.library.biosample.synchronization
        ).map((replicate) => {
            const biosample = replicate.library.biosample;
            return (biosample.synchronization +
                (biosample.post_synchronization_time ?
                    ` + ${biosample.post_synchronization_time}${biosample.post_synchronization_time_units ? ` ${biosample.post_synchronization_time_units}` : ''}`
                : ''));
        }));
    }

    return (
        <li>
            <div className="result-item">
                <div className="result-item__data">
                    <PickerActions {...props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Experiment</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <p className="type meta-status">{` ${result.status}`}</p>
                        {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, search: true })}
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
                {activeCart ?
                    <div className="result-item__cart-control">
                        <CartToggle current={result} />
                    </div>
                : null}
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, except: result['@id'], forcedEditLink: true })}
        </li>
    );
};

ExperimentComponent.propTypes = {
    context: PropTypes.object.isRequired, // Experiment search results
    activeCart: PropTypes.bool, // True if displayed in active cart
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired,
};

ExperimentComponent.defaultProps = {
    activeCart: false,
};

ExperimentComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Experiment = auditDecor(ExperimentComponent);

globals.listingViews.register(Experiment, 'Experiment');


const DatasetComponent = (props, reactContext) => {
    const { activeCart } = props;
    const result = props.context;
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
        const organisms = (result.organism && result.organism.length) ? _.uniq(result.organism.map(resultOrganism => resultOrganism.scientific_name)) : [];
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
            <div className="result-item">
                <div className="result-item__data">
                    <PickerActions {...props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">{haveSeries ? 'Series' : (haveFileSet ? 'FileSet' : 'Dataset')}</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, search: true })}
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
                {activeCart ?
                    <div className="result-item__cart-control">
                        <CartToggle current={result} />
                    </div>
                : null}
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, except: result['@id'], forcedEditLink: true })}
        </li>
    );
};

DatasetComponent.propTypes = {
    context: PropTypes.object.isRequired, // Dataset search results
    activeCart: PropTypes.bool, // True if displayed in active cart
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

DatasetComponent.defaultProps = {
    activeCart: false,
};

DatasetComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Dataset = auditDecor(DatasetComponent);

globals.listingViews.register(Dataset, 'Dataset');


/* eslint-disable react/prefer-stateless-function */
class TargetComponent extends React.Component {
    render() {
        const result = this.props.context;
        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Target</p>
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
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
                            <DbxrefList context={result} dbxrefs={result.dbxref} />
                        : <em>None submitted</em> }
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

TargetComponent.propTypes = {
    context: PropTypes.object.isRequired, // Target search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

TargetComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Target = auditDecor(TargetComponent);

globals.listingViews.register(Target, 'Target');


const Image = (props) => {
    const result = props.context;

    return (
        <li>
            <div className="clearfix">
                <PickerActions {...props} />
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
};

Image.propTypes = {
    context: PropTypes.object.isRequired, // Image search results
};

globals.listingViews.register(Image, 'Image');


/**
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
        } else if (filterFieldName === facet.field && filter.term === term) {
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


class Facet extends React.Component {
    constructor() {
        super();

        // Set initial React commponent state.
        this.state = {
            facetOpen: false,
        };

        // Bind `this` to non-React methods.
        this.handleClick = this.handleClick.bind(this);
    }

    handleClick() {
        this.setState(prevState => ({ facetOpen: !prevState.facetOpen }));
    }

    render() {
        const { facet, filters } = this.props;
        const title = facet.title;
        const field = facet.field;
        const total = facet.total;
        const termID = title.replace(/\s+/g, '');

        // Make a list of terms for this facet that should appear, by filtering out terms that
        // shouldn't. Any terms with a zero doc_count get filtered out, unless the term appears in
        // the search result filter list.
        const terms = facet.terms.filter((term) => {
            if (term.key) {
                // See if the facet term also exists in the search result filters (i.e. the term
                // exists in the URL query string).
                const found = filters.some(filter => filter.field === facet.field && filter.term === term.key);

                // If the term wasn't in the filters list, allow its display only if it has a non-
                // zero doc_count. If the term *does* exist in the filters list, display it
                // regardless of its doc_count.
                return found || term.doc_count > 0;
            }

            // The term exists, but without a key, so don't allow its display.'
            return false;
        });
        const moreTerms = terms.slice(5);
        const TermComponent = field === 'type' ? TypeTerm : Term;
        const selectedTermCount = countSelectedTerms(moreTerms, facet, filters);
        const moreTermSelected = selectedTermCount > 0;
        const canDeselect = (!facet.restrictions || selectedTermCount >= 2);
        const moreSecClass = `collapse${(moreTermSelected || this.state.facetOpen) ? ' in' : ''}`;
        const seeMoreClass = `btn btn-link facet-list__expander${(moreTermSelected || this.state.facetOpen) ? '' : ' collapsed'}`;
        const statusFacet = field === 'status' || field === 'lot_reviews.status';

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

        if ((terms.length && terms.some(term => term.doc_count)) || (field.charAt(field.length - 1) === '!')) {
            return (
                <div className="facet">
                    <h5>{titleComponent}</h5>
                    <ul className={`facet-list nav${statusFacet ? ' facet-status' : ''}`}>
                        <div>
                            {/* Display the first five terms of the facet */}
                            {terms.slice(0, 5).map(term =>
                                <TermComponent {...this.props} key={term.key} term={term} filters={filters} total={total} canDeselect={canDeselect} statusFacet={statusFacet} />
                            )}
                        </div>
                        {terms.length > 5 ?
                            <div id={termID} className={moreSecClass}>
                                {/* If the user has expanded the "+ See more" button, then display
                                     the rest of the terms beyond 5 */}
                                {moreTerms.map(term =>
                                    <TermComponent {...this.props} key={term.key} term={term} filters={filters} total={total} canDeselect={canDeselect} statusFacet={statusFacet} />
                                )}
                            </div>
                        : null}
                        {(terms.length > 5 && !moreTermSelected) ?
                            <div className="pull-right">
                                {/* Display the "+ See more" button if more than five terms exist for this facet */}
                                <small>
                                    <button type="button" className={seeMoreClass} data-toggle="collapse" data-target={`#${termID}`} onClick={this.handleClick} />
                                </small>
                            </div>
                        : null}
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

Facet.defaultProps = {
    width: 'inherit',
};


// Entry field for filtering the results list when search results appear in edit forms.
export class TextFilter extends React.Component {
    static onChange(e) {
        e.stopPropagation();
        e.preventDefault();
    }

    constructor() {
        super();

        // Bind `this` to non-React component methods.
        this.onBlur = this.onBlur.bind(this);
        this.onKeyDown = this.onKeyDown.bind(this);
    }

    onBlur(e) {
        let searchStr = this.props.searchBase.replace(/&?searchTerm=[^&]*/, '');
        const value = e.target.value;
        if (value) {
            searchStr += `searchTerm=${e.target.value}`;
        } else {
            searchStr = searchStr.substring(0, searchStr.length - 1);
        }
        this.props.onChange(searchStr);
    }

    onKeyDown(e) {
        if (e.keyCode === 13) {
            this.onBlur(e);
            e.preventDefault();
        }
    }

    getValue() {
        const filter = this.props.filters.filter(f => f.field === 'searchTerm');
        return filter.length ? filter[0].term : '';
    }

    shouldUpdateComponent(nextProps) {
        return (this.getValue(this.props) !== this.getValue(nextProps));
    }

    render() {
        return (
            <div className="facet">
                <input
                    type="search"
                    className="form-control search-query"
                    placeholder="Enter search term(s)"
                    defaultValue={this.getValue(this.props)}
                    onChange={TextFilter.onChange}
                    onBlur={this.onBlur}
                    onKeyDown={this.onKeyDown}
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


// Displays the entire list of facets. It contains a number of <Facet> cmoponents.
/* eslint-disable react/prefer-stateless-function */
export class FacetList extends React.Component {
    render() {
        const { context, facets, filters, mode, orientation, hideTextFilter, addClasses } = this.props;

        // Get "normal" facets, meaning non-audit facets.
        const normalFacets = facets.filter(facet => facet.field.substring(0, 6) !== 'audit.');

        let width = 'inherit';
        if (!facets.length && mode !== 'picker') return <div />;
        let hideTypes;
        if (mode === 'picker') {
            // The edit forms item picker (search results in an edit item) shows the Types facet.
            hideTypes = false;
        } else {
            // Hide the types facet if one "type=" term exists in the URL. and it's not the only
            // facet.
            hideTypes = filters.filter(filter => filter.field === 'type').length === 1 && normalFacets.length > 1;
        }
        if (orientation === 'horizontal') {
            width = `${100 / facets.length}%`;
        }

        // See if we need the Clear Filters link or not. context.clear_filters.
        let clearButton;
        const searchQuery = context && context['@id'] && url.parse(context['@id']).search;
        if (searchQuery) {
            // Convert search query string to a query object for easy parsing.
            const terms = queryString.parse(searchQuery);

            // See if there are terms in the query string aside from `searchTerm`. We have a Clear
            // Filters button if we do.
            let nonPersistentTerms = _(Object.keys(terms)).any(term => term !== 'searchTerm');
            clearButton = nonPersistentTerms && terms.searchTerm;

            // If no Clear Filters button yet, do the same check with `type` in the query string.
            if (!clearButton) {
                nonPersistentTerms = _(Object.keys(terms)).any(term => term !== 'type');
                clearButton = nonPersistentTerms && terms.type;
            }
        }

        // Collect negation filters ie filters with fields ending in an exclamation point. These
        // are the negation facet terms that need to get merged into the regular facets that their
        // non-negated versions inhabit.
        const negationFilters = filters.filter(filter => filter.field.charAt(filter.field.length - 1) === '!');

        return (
            <div className={`box facets${addClasses ? ` ${addClasses}` : ''}`}>
                <div className={`orientation${this.props.orientation === 'horizontal' ? ' horizontal' : ''}`}>
                    {clearButton ?
                        <div className="clear-filters-control">
                            <a href={context.clear_filters}>Clear Filters <i className="icon icon-times-circle" /></a>
                        </div>
                    : null}
                    {mode === 'picker' && !hideTextFilter ? <TextFilter {...this.props} filters={filters} /> : ''}
                    {facets.map((facet) => {
                        if (hideTypes && facet.field === 'type') {
                            return <span key={facet.field} />;
                        }
                        return (
                            <Facet
                                {...this.props}
                                key={facet.field}
                                facet={facet}
                                filters={filters}
                                width={width}
                                negationFilters={negationFilters}
                            />
                        );
                    })}
                </div>
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

FacetList.propTypes = {
    context: PropTypes.object,
    facets: PropTypes.oneOfType([
        PropTypes.array,
        PropTypes.object,
    ]).isRequired,
    filters: PropTypes.array.isRequired,
    mode: PropTypes.string,
    orientation: PropTypes.string,
    hideTextFilter: PropTypes.bool,
    addClasses: PropTypes.string, // CSS classes to use if the default isn't needed.
};

FacetList.defaultProps = {
    context: null,
    mode: '',
    orientation: 'vertical',
    hideTextFilter: false,
    addClasses: '',
};

FacetList.contextTypes = {
    session: PropTypes.object,
};


/**
 * Display the modal for batch download, and pass back clicks in the Download button
 */
export const BatchDownloadModal = ({ handleDownloadClick }) => (
    <Modal actuator={<button className="btn btn-info btn-sm">Download</button>}>
        <ModalHeader title="Using batch download" closeModal />
        <ModalBody>
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
            <code>xargs -n 1 curl -O -L &lt; files.txt</code><br />
        </ModalBody>
        <ModalFooter
            closeModal={<button className="btn btn-info btn-sm">Close</button>}
            submitBtn={<button className="btn btn-info btn-sm" onClick={handleDownloadClick}>Download</button>}
            dontClose
        />
    </Modal>
);

BatchDownloadModal.propTypes = {
    handleDownloadClick: PropTypes.func.isRequired, // Function to call when Download button gets clicked
};


export class BatchDownload extends React.Component {
    constructor() {
        super();
        this.handleDownloadClick = this.handleDownloadClick.bind(this);
    }

    handleDownloadClick() {
        if (!this.props.context) {
            requestSearch(this.props.query).then((results) => {
                this.context.navigate(results.batch_download);
            });
        } else {
            this.context.navigate(this.props.context.batch_download);
        }
    }

    render() {
        return <BatchDownloadModal handleDownloadClick={this.handleDownloadClick} />;
    }
}

BatchDownload.propTypes = {
    context: PropTypes.object, // Search result object whose batch_download we're using
    query: PropTypes.string, // Without `context`, perform a search using this query string
};

BatchDownload.defaultProps = {
    context: null,
    query: '',
    downloadClickHandler: null,
};

BatchDownload.contextTypes = {
    navigate: PropTypes.func,
};


export class ResultTable extends React.Component {
    constructor(props) {
        super(props);

        // Make an array of all assemblies found in all files in the search results.
        let assemblies = [];
        const results = this.props.context['@graph'];
        const files = results.length ? results.filter(result => result['@type'][0] === 'File') : [];
        if (files.length) {
            // Reduce all found file assemblies so we don't have duplicates in the 'assemblies' array.
            assemblies = files.reduce((assembliesAcc, file) => ((!file.assembly || assembliesAcc.indexOf(file.assembly) > -1) ? assembliesAcc : assembliesAcc.concat(file.assembly)), []);
        }

        // Set React component state.
        this.state = {
            assemblies,
            browserAssembly: assemblies.length && assemblies[0], // Currently selected assembly for the browser
            selectedTab: '',
        };

        // Bind `this` to non-React moethods.
        this.onFilter = this.onFilter.bind(this);
        this.assemblyChange = this.assemblyChange.bind(this);
        this.handleTabClick = this.handleTabClick.bind(this);
    }

    getChildContext() {
        return {
            actions: this.props.actions,
        };
    }

    componentDidMount() {
        if (window !== undefined) {
            // Determining this in componentDidMount to avoid server/client reactJS conflict.
            if (window.location.hash === '#browser') {
                this.setState({ selectedTab: 'browserpane' });
            }
        }
    }

    onFilter(e) {
        const searchStr = e.currentTarget.getAttribute('href');
        this.props.onChange(searchStr);
        e.stopPropagation();
        e.preventDefault();
        this.setState({ selectedTab: 'listpane' }); // Always return to listpane so that browser can rerender
    }

    // Called when new value chosen from assembly dropdown.
    assemblyChange(e) {
        this.setState({ browserAssembly: e.target.value });
    }

    handleTabClick(tab) {
        // Since we force TabPanel tab selection, we need to keep track of selectedTab.
        if (this.state.selectedTab !== tab) {
            this.setState({ selectedTab: tab });
        }
    }

    render() {
        const visualizeLimit = 100;
        const { context, searchBase, restrictions } = this.props;
        const { assemblies } = this.state;
        const results = context['@graph'];
        const total = context.total;
        const visualizeDisabled = total > visualizeLimit;
        const columns = context.columns;
        const filters = context.filters;
        const label = 'results';
        const trimmedSearchBase = searchBase.replace(/[?|&]limit=all/, '');
        let browseAllFiles = true; // True to pass all files to browser
        let browserAssembly = ''; // Assembly to pass to ResultsBrowser component
        let browserDatasets = []; // Datasets will be used to get vis_json blobs
        let browserFiles = []; // Files to pass to ResultsBrowser component
        let assemblyChooser;

        const facets = context.facets.map((facet) => {
            if (restrictions[facet.field] !== undefined) {
                const workFacet = _.clone(facet);
                workFacet.restrictions = restrictions[workFacet.field];
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
            summary: 'summary',
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
        let browserAvail = counter === 1 && typeFilter && typeFilter.term === 'File' && assemblies.length === 1;
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
                browserAvail = false; // NEW: Limit browser option to type=File&dataset=... only!
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
                    {facets.length ?
                        <div className="col-sm-5 col-md-4 col-lg-3">
                            <FacetList
                                {...this.props}
                                facets={facets}
                                filters={filters}
                                searchBase={searchBase ? `${searchBase}&` : `${searchBase}?`}
                                onFilter={this.onFilter}
                            />
                        </div>
                    : ''}
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
                                            rel="nofollow"
                                            className="btn btn-info btn-sm"
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
                                <CartSearchControls searchResults={context} />
                                {browserAvail ?
                                    <TabPanel tabs={{ listpane: 'List', browserpane: <BrowserTabQuickView /> }} selectedTab={this.state.selectedTab} handleTabClick={this.handleTabClick} addClasses="browser-tab-bg" tabFlange>
                                        <TabPanelPane key="listpane">
                                            <ResultTableList results={results} columns={columns} tabbed />
                                        </TabPanelPane>
                                        <TabPanelPane key="browserpane">
                                            {assemblyChooser}
                                            <ResultBrowser files={results} assembly={browserAssembly} datasets={browserDatasets} limitFiles={!browseAllFiles} currentRegion={this.props.currentRegion} />
                                        </TabPanelPane>
                                    </TabPanel>
                                :
                                    <ResultTableList results={results} columns={columns} activeCart />
                                }
                            </div>
                        :
                            <h4>{context.notification}</h4>
                        }
                    </div>
                </div>
            </div>
        );
    }
}

ResultTable.propTypes = {
    context: PropTypes.object.isRequired,
    actions: PropTypes.array,
    restrictions: PropTypes.object,
    searchBase: PropTypes.string,
    onChange: PropTypes.func.isRequired,
    currentRegion: PropTypes.func,
};

ResultTable.defaultProps = {
    actions: [],
    restrictions: {},
    searchBase: '',
    currentRegion: null,
};

ResultTable.childContextTypes = {
    actions: PropTypes.array,
};

ResultTable.contextTypes = {
    session: PropTypes.object,
};


const BrowserTabQuickView = function BrowserTabQuickView() {
    return <div>Quick View <span className="beta-badge">BETA</span></div>;
};


// Display the list of search results.
export const ResultTableList = ({ results, columns, tabbed, activeCart }) => (
    <ul className={`nav result-table${tabbed ? ' result-table-tabbed' : ''}`} id="result-table">
        {results.length ?
            results.map(result => Listing({ context: result, columns, key: result['@id'], activeCart }))
        : null}
    </ul>
);

ResultTableList.propTypes = {
    results: PropTypes.array.isRequired, // Array of search results to display
    columns: PropTypes.object, // Columns from search results
    tabbed: PropTypes.bool, // True if table is in a tab
    activeCart: PropTypes.bool, // True if items displayed in active cart
};

ResultTableList.defaultProps = {
    columns: null,
    tabbed: false,
    activeCart: false,
};


// Display a local genome browser in the ResultTable where search results would normally go. This
// only gets displayed if the query string contains only one type and it's "File."
const ResultBrowser = (props) => {
    let visUrl = '';
    const datasetCount = props.datasets.length;
    let region; // optionally make a persistent region
    const lastRegion = props.currentRegion();
    if (lastRegion && lastRegion.assembly === props.assembly) {
        region = lastRegion.region;
        console.log('found region %s', region);
    }
    if (datasetCount === 1) {
        // /datasets/{ENCSR000AEI}/@@hub/{hg19}/trackDb.json
        visUrl = `${props.datasets[0]}/@@hub/${props.assembly}/trackDb.json`;
    } else if (datasetCount > 1) {
        // /batch_hub/type%3DExperiment%2C%2Caccession%3D{ENCSR000AAA}%2C%2Caccession%3D{ENCSR000AEI}/{hg19}/vis_blob.json
        for (let ix = 0; ix < datasetCount; ix += 1) {
            const accession = props.datasets[ix].split('/')[2];
            if (visUrl !== '') {
                visUrl += '%2C%2C';
            }
            visUrl += `accession=${accession}`;
        }
        visUrl = `batch_hub/type=Experiment/${visUrl}/${props.assembly}/vis_blob.json`;
    }
    if (datasetCount > 0) {
        return (
            <FetchedData ignoreErrors>
                <Param name="visBlobs" url={visUrl} />
                <GenomeBrowser files={props.files} assembly={props.assembly} limitFiles={props.limitFiles} region={region} currentRegion={props.currentRegion} />
            </FetchedData>
        );
    }
    return (
        <div>
            <GenomeBrowser files={props.files} assembly={props.assembly} limitFiles={props.limitFiles} region={region} currentRegion={props.currentRegion} />
        </div>
    );
};

ResultBrowser.propTypes = {
    files: PropTypes.array.isRequired, // Array of files whose browser we're rendering
    assembly: PropTypes.string.isRequired, // Filter `files` by this assembly
    datasets: PropTypes.array.isRequired, // One or more '/dataset/ENCSRnnnXXX/' that files belong to
    limitFiles: PropTypes.bool, // True to limit browsing to 20 files
    currentRegion: PropTypes.func,
};

ResultBrowser.defaultProps = {
    limitFiles: true,
    currentRegion: null,
};


// Display a dropdown menu of the given assemblies.
const AssemblyChooser = (props) => {
    const { assemblies, currentAssembly, assemblyChange } = props;

    return (
        <select className="form-control" value={currentAssembly} onChange={assemblyChange}>
            {assemblies.map((assembly, i) =>
                <option key={i} value={assembly}>{assembly}</option>
            )}
        </select>
    );
};

AssemblyChooser.propTypes = {
    assemblies: PropTypes.array.isRequired, // Array of assemblies to include in the dropdown
    currentAssembly: PropTypes.string, // Currently selected assembly
    assemblyChange: PropTypes.func.isRequired, // Function to call when the user chooses a new assembly
};

AssemblyChooser.defaultProps = {
    currentAssembly: 'default',
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

        return (
            <div>
                {facetdisplay ?
                    <div className="panel data-display main-panel">
                        <ResultTable {...this.props} searchBase={searchBase} onChange={this.context.navigate} currentRegion={this.currentRegion} />
                    </div>
                : <h4>{notification}</h4>}
            </div>
        );
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
    assembly: React.PropTypes.string,
    region: React.PropTypes.string,
};

globals.contentViews.register(Search, 'Search');
