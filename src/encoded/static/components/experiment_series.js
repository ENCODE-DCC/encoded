import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import { CartAddAllElements, CartToggle } from './cart';
import { auditDecor } from './audit';
import { FilePanelHeader } from './dataset';
import { FetchedItems } from './fetched';
import { DatasetFiles } from './filegallery';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { DisplayAsJson, InternalTags, publicDataset } from './objectutils';
import { PickerActions } from './search';
import { SortTablePanel, SortTable } from './sorttable';
import Status from './status';


const experimentTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) =>
            <span>
                {meta.adminUser || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>,
    },

    assay_term_name: {
        title: 'Assay',
    },

    target: {
        title: 'Target',
        getValue: experiment => (experiment.target ? experiment.target.label : null),
    },

    description: {
        title: 'Description',
    },

    lab: {
        title: 'Lab',
        getValue: experiment => (experiment.lab ? experiment.lab.title : null),

    },

    date_released: {
        title: 'Date released',
    },

    status: {
        title: 'Status',
        display: experiment => <Status item={experiment} badgeSize="small" />,
    },

    cart: {
        title: 'Cart',
        display: experiment => <CartToggle element={experiment} />,
        sorter: false,
    },
};


/**
 * Component to display experiment series pages.
 */
const ExperimentSeriesComponent = (props, reactContext) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'view-item');
    const adminUser = !!(reactContext.session_properties && reactContext.session_properties.admin);

    // Set up the breadcrumbs.
    const datasetType = context['@type'][1];
    const crumbs = [
        { id: 'Datasets' },
        { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
        { id: 'Experiment Series', uri: '/search/?type=ExperimentSeries&status=released', wholeTip: 'Search for released experiment series' },
    ];
    const crumbsReleased = (context.status === 'released');

    // Calculate the biosample summary from the organism and the biosample onotology.
    let speciesRender = null;
    const biosampleOntologies = context.biosample_ontology || [];
    if (context.organism && context.organism.length > 0) {
        const speciesList = _.uniq(context.organism.map(organism => organism.scientific_name));
        speciesRender = (
            <span>
                {speciesList.map((species, i) =>
                    <span key={i}>
                        {i > 0 ? <span> and </span> : null}
                        <i>{species}</i>
                    </span>
                )}
            </span>
        );
    }
    const terms = biosampleOntologies.length > 0 ? _.uniq(biosampleOntologies.map(biosampleOntology => biosampleOntology.term_name)) : [];

    // Filter out any files we shouldn't see.
    const experimentList = context.related_datasets.filter(dataset => dataset.status !== 'revoked' && dataset.status !== 'replaced' && dataset.status !== 'deleted');

    // Add the "Add all to cart" button and internal tags from all related datasets.
    let addAllToCartControl;
    let internalTags = [];
    if (experimentList.length > 0) {
        addAllToCartControl = (
            <div className="experiment-table__header">
                <h4 className="experiment-table__title">{`Experiments in experiment series ${context.accession}`}</h4>
                <CartAddAllElements elements={experimentList} />
            </div>
        );

        // Collect unique internal_tags from all relevant experiments.
        internalTags = _.uniq(experimentList.reduce((allInternalTags, experiment) => (
            experiment.internal_tags && experiment.internal_tags.length > 0 ? allInternalTags.concat(experiment.internal_tags) : allInternalTags
        ), []));
    }

    return (
        <div className={itemClass}>
            <header className="row">
                <div className="col-sm-12">
                    <Breadcrumbs crumbs={crumbs} crumbsReleased={crumbsReleased} />
                    <h2>Summary for experiment series {context.accession}</h2>
                    {props.auditIndicators(context.audit, 'series-audit', { session: reactContext.session })}
                    <DisplayAsJson />
                </div>
            </header>
            {props.auditDetail(context.audit, 'series-audit', { session: reactContext.session, except: context['@id'] })}
            <Panel addClasses="data-display">
                <PanelBody addClasses="panel-body-with-header">
                    <div className="flexrow">
                        <div className="flexcol-sm-6">
                            <div className="flexcol-heading experiment-heading"><h4>Summary</h4></div>
                            <dl className="key-value">
                                <div data-test="status">
                                    <dt>Status</dt>
                                    <dd><Status item={context} inline /></dd>
                                </div>

                                {context.description ?
                                    <div data-test="description">
                                        <dt>Description</dt>
                                        <dd>{context.description}</dd>
                                    </div>
                                : null}

                                {context.assay_term_name && context.assay_term_name.length > 0 ?
                                    <div data-test="description">
                                        <dt>Assay</dt>
                                        <dd>{context.assay_term_name.join(', ')}</dd>
                                    </div>
                                : null}

                                {terms.length > 0 || speciesRender ?
                                    <div data-test="biosamplesummary">
                                        <dt>Biosample summary</dt>
                                        <dd>
                                            {terms.length > 0 ? <span>{terms.join(' and ')} </span> : null}
                                            {speciesRender ? <span>({speciesRender})</span> : null}
                                        </dd>
                                    </div>
                                : null}
                            </dl>
                        </div>

                        <div className="flexcol-sm-6">
                            <div className="flexcol-heading experiment-heading">
                                <h4>Attribution</h4>
                            </div>
                            <dl className="key-value">
                                {context.contributors.length > 0 ?
                                    <div data-test="contributors">
                                        <dt>Contributors</dt>
                                        <dd>
                                            {context.contributors.map(contributor => (
                                                <span key={contributor['@id']} className="line-item">
                                                    {contributor.title}
                                                </span>
                                            ))}
                                        </dd>
                                    </div>
                                : null}

                                {context.aliases.length > 0 ?
                                    <div data-test="aliases">
                                        <dt>Aliases</dt>
                                        <dd>{context.aliases.join(', ')}</dd>
                                    </div>
                                : null}

                                {context.submitter_comment ?
                                    <div data-test="submittercomment">
                                        <dt>Submitter comment</dt>
                                        <dd>{context.submitter_comment}</dd>
                                    </div>
                                : null}

                                {internalTags.length > 0 ?
                                    <div className="tag-badges" data-test="tags">
                                        <dt>Tags</dt>
                                        <dd><InternalTags internalTags={internalTags} objectType="Experiment" /></dd>
                                    </div>
                                : null}
                            </dl>
                        </div>
                    </div>
                </PanelBody>
            </Panel>

            {addAllToCartControl ?
                <div>
                    <SortTablePanel header={addAllToCartControl}>
                        <SortTable
                            list={experimentList}
                            columns={experimentTableColumns}
                            css="table-experiment-series"
                            meta={{ adminUser }}
                            footer="Use cart to download files"
                        />
                    </SortTablePanel>
                </div>
            : null}

            <FetchedItems
                {...props}
                url={`/search/?limit=all&type=File&dataset=${context['@id']}`}
                Component={DatasetFiles}
                filePanelHeader={<FilePanelHeader context={context} />}
                encodevers={globals.encodeVersion(context)}
                session={reactContext.session}
            />
        </div>
    );
};

ExperimentSeriesComponent.propTypes = {
    /** ExperimentSeries object to display */
    context: PropTypes.object.isRequired,
    /** Audit decorator function */
    auditIndicators: PropTypes.func.isRequired,
    /** Audit decorator function */
    auditDetail: PropTypes.func.isRequired,
};

ExperimentSeriesComponent.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};

const ExperimentSeries = auditDecor(ExperimentSeriesComponent);

globals.contentViews.register(ExperimentSeries, 'ExperimentSeries');


const ListingComponent = (props, reactContext) => {
    const result = props.context;
    let organism;
    let targets;
    let lifeStages = [];
    let ages = [];

    // Get the biosample info for Series types if any. Can be string or array. If array, only use iff 1 term name exists
    const biosampleTerm = (result.biosample_ontology && Array.isArray(result.biosample_ontology) && result.biosample_ontology.length === 1 && result.biosample_ontology[0].term_name) ? result.biosample_ontology[0].term_name : ((result.biosample_ontology && result.biosample_ontology.term_name) ? result.biosample_ontology.term_name : '');
    const organisms = (result.organism && result.organism.length) ? [...new Set(result.organism.map(resultOrganism => resultOrganism.scientific_name))] : [];
    if (organisms.length === 1) {
        organism = organisms[0];
    }

    // related_datasets is required and have minItems = 1
    result.related_datasets.forEach((dataset) => {
        if (dataset.replicates && dataset.replicates.length > 0) {
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
    lifeStages = [...new Set(lifeStages)];
    ages = [...new Set(ages)];
    const lifeSpec = [lifeStages.length === 1 ? lifeStages[0] : null, ages.length === 1 ? ages[0] : null].filter(Boolean);

    // Get list of target labels
    if (result.target) {
        targets = [...new Set(result.target.map(target => target.label))];
    }

    const contributors = result.contributors.map(lab => lab.title);
    const contributingAwards = _.uniq(result.contributing_awards.map(award => award.project));

    return (
        <li>
            <div className="result-item">
                <div className="result-item__data">
                    <PickerActions {...props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Experiment Series</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <div className="result-experiment-series-search">
                            <a href={`/search/?type=Experiment&related_series.@id=${result['@id']}`}>View {result.related_datasets.length} datasets</a>
                        </div>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            Experiment Series
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
                        </a>
                    </div>
                    <div className="data-row">
                        {result.dataset_type ? <div><strong>Dataset type: </strong>{result.dataset_type}</div> : null}
                        {targets && targets.length ? <div><strong>Targets: </strong>{targets.join(', ')}</div> : null}
                        <div><strong>Lab: </strong>{contributors.join(', ')}</div>
                        <div><strong>Project: </strong>{contributingAwards.join(', ')}</div>
                    </div>
                </div>
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, except: result['@id'], forcedEditLink: true })}
        </li>
    );
};

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired, // ExperimentSeries search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ListingComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'ExperimentSeries');
