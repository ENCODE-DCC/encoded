import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Panel, PanelBody } from '../libs/ui/panel';
import { CartAddAllElements, CartToggle } from './cart';
import { auditDecor, AuditCounts } from './audit';
import { FilePanelHeader } from './dataset';
import { FetchedItems } from './fetched';
import { DatasetFiles } from './filegallery';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { ItemAccessories, InternalTags } from './objectutils';
import { PickerActions, resultItemClass } from './search';
import { SortTablePanel, SortTable } from './sorttable';
import Status, { getObjectStatuses, sessionToAccessLevel } from './status';


const experimentTableColumns = {
    accession: {
        title: 'Accession',
        display: experiment => <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>,
    },

    lab: {
        title: 'Lab',
        getValue: experiment => (experiment.lab ? experiment.lab.title : null),
    },

    date_released: {
        title: 'Date released',
    },

    award: {
        title: 'RFA',
        getValue: experiment => (experiment.award ? experiment.award.rfa : null),
    },

    status: {
        title: 'Status',
        display: experiment => <Status item={experiment} badgeSize="small" />,
    },

    audit: {
        title: 'Audit status',
        display: (item, meta) => <AuditCounts audits={meta.auditsByDataset[item['@id']]} isAuthorized={meta.isAuthorized} />,
        sorter: false,
    },

    cart: {
        title: 'Cart',
        display: experiment => <CartToggle element={experiment} />,
        sorter: false,
    },
};


/**
 * Experiment statuses we can display at the different access levels. Defined separately from how
 * they're defined in status.js because they're slightly differently from datasetStatuses.
 */
const viewableDatasetStatuses = {
    Dataset: {
        external: [
            'released',
            'archived',
        ],
        consortium: [
            'in progress',
            'submitted',
            'revoked',
        ],
        administrator: [
            'deleted',
            'replaced',
        ],
    },
};


/**
 * Component to display experiment series pages.
 */
class ExperimentSeriesComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            /** Audit objects keyed by dataset @id. Datasets w/o audits included with empty object */
            auditsByDataset: {},
        };
        this.getDatasetAudits = this.getDatasetAudits.bind(this);
        this.getViewableDatasets = this.getViewableDatasets.bind(this);
    }

    componentDidMount() {
        this.getDatasetAudits();
    }

    componentDidUpdate() {
        const relatedDatasets = this.props.context.related_datasets;
        if (relatedDatasets.length > 0) {
            // If any @id in related_datasets isn't in this.state.auditsByDataset, retrieve all
            // dataset audits. This can happen if the user edits the viewed ExperimentSeries
            // object.
            const datasetsInAudits = relatedDatasets.some(dataset => !!this.state.auditsByDataset[dataset['@id']]);
            if (!datasetsInAudits) {
                this.getDatasetAudits();
            }
        }
    }

    /**
     * Retrieve the audits of all related datasets in the current ExperimentSeries object. Once
     * all dataset audits have been retrieved, they're put into this.state.datasetAudit.
     */
    getDatasetAudits() {
        const relatedDatasets = this.props.context.related_datasets;
        if (relatedDatasets.length > 0) {
            // Retrieve the audits of all related datasets.
            const datasetAtIds = relatedDatasets.map(dataset => dataset['@id']);
            Promise.all(datasetAtIds.map(datasetAtId => (
                fetch(`${datasetAtId}?frame=audit`, {
                    method: 'GET',
                    headers: {
                        Accept: 'application/json',
                    },
                }).then((response) => {
                    // Convert each response response to JSON
                    if (response.ok) {
                        return response.json();
                    }
                    return Promise.resolve(null);
                })
            ))).then((datasetAudits) => {
                // All dataset audits have been retrieved, or we got an error when trying to
                // retrieve one or more of them.
                const auditsByDataset = {};
                if (datasetAudits && datasetAudits.length > 0) {
                    datasetAudits.forEach((datasetAudit) => {
                        auditsByDataset[datasetAudit['@id']] = datasetAudit.audit || {};
                    });
                }
                this.setState({ auditsByDataset });
            });
        }
    }

    /**
     * Calculate a list of related_datasets that we can view given our access level and each
     * dataset's status and place this list into this.viewableDatasets.
     *
     * @return {array} All datasets from ExperimentSeries object we can display. Empty array if
     *                 none.
     */
    getViewableDatasets() {
        if (this.props.context.related_datasets.length > 0) {
            const accessLevel = sessionToAccessLevel(this.context.session, this.context.session_properties);
            const viewableStatuses = getObjectStatuses('Dataset', accessLevel, viewableDatasetStatuses);
            return this.props.context.related_datasets.filter(dataset => viewableStatuses.includes(dataset.status));
        }
        return [];
    }

    render() {
        const { context, auditDetail, auditIndicators } = this.props;
        const itemClass = globals.itemClass(context, 'view-item');
        const viewableDatasets = this.getViewableDatasets();
        const roles = globals.getRoles(this.context.session_properties);
        const isAuthorized = ['admin', 'submitter'].some(role => roles.includes(role));

        // Set up the breadcrumbs.
        const datasetType = context['@type'][1];
        const crumbs = [
            { id: 'Datasets' },
            { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
            { id: 'Experiment Series', uri: '/search/?type=ExperimentSeries&status=released', wholeTip: 'Search for released experiment series' },
        ];
        const crumbsReleased = (context.status === 'released');

        // Calculate the biosample summary from the organism and the biosample ontology.
        let speciesRender = null;
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

        // Add the "Add all to cart" button and internal tags from all related datasets.
        let addAllToCartControl;
        let internalTags = [];
        if (viewableDatasets.length > 0) {
            addAllToCartControl = (
                <div className="experiment-table__header">
                    <h4 className="experiment-table__title">{`Experiments in experiment series ${context.accession}`}</h4>
                    <CartAddAllElements elements={viewableDatasets} />
                </div>
            );

            // Collect unique internal_tags from all relevant experiments.
            internalTags = _.uniq(viewableDatasets.reduce((allInternalTags, experiment) => (
                experiment.internal_tags && experiment.internal_tags.length > 0 ? allInternalTags.concat(experiment.internal_tags) : allInternalTags
            ), []));
        }

        return (
            <div className={itemClass}>
                <header>
                    <Breadcrumbs crumbs={crumbs} crumbsReleased={crumbsReleased} />
                    <h2>Summary for experiment series {context.accession}</h2>
                    <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'series-audit' }} />
                </header>
                {auditDetail(context.audit, 'series-audit', { session: this.context.session, sessionProperties: this.context.session_properties })}
                <Panel>
                    <PanelBody addClasses="panel__split">
                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--experiment-series">
                                <h4>Summary</h4>
                            </div>
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

                                {(context.biosample_summary && context.biosample_summary.length > 0) || speciesRender ?
                                    <div data-test="biosamplesummary">
                                        <dt>Biosample summary</dt>
                                        <dd>
                                            {speciesRender ? <span>{speciesRender}&nbsp;</span> : null}
                                            {context.biosample_summary && context.biosample_summary.length > 0 ? <span>{context.biosample_summary.join(' and ')} </span> : null}
                                        </dd>
                                    </div>
                                : null}
                            </dl>
                        </div>

                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--experiment-series">
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
                    </PanelBody>
                </Panel>

                {addAllToCartControl ?
                    <SortTablePanel header={addAllToCartControl}>
                        <SortTable
                            list={viewableDatasets}
                            columns={experimentTableColumns}
                            css="table-experiment-series"
                            footer="Use cart to download files"
                            meta={{ auditsByDataset: this.state.auditsByDataset, isAuthorized }}
                        />
                    </SortTablePanel>
                : null}

                <FetchedItems
                    {...this.props}
                    url={`/search/?limit=all&type=File&dataset=${context['@id']}`}
                    Component={DatasetFiles}
                    filePanelHeader={<FilePanelHeader context={context} />}
                    encodevers={globals.encodeVersion(context)}
                    session={this.context.session}
                />
            </div>
        );
    }
}

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


/**
 * Related dataset statuses that get counted in totals, and specified in searches.
 */
const searchableDatasetStatuses = ['released', 'archived'];
const searchableDatasetStatusQuery = searchableDatasetStatuses.reduce((query, status) => `${query}&status=${status}`, '');


const ListingComponent = (props, reactContext) => {
    const result = props.context;
    let targets = [];
    let lifeStages = [];
    let ages = [];

    // Get the biosample info and organism for Series types. Only use if we have precisely one of each.
    const biosampleTerm = (result.biosample_ontology && result.biosample_ontology.length === 1 && result.biosample_ontology[0].term_name) || '';
    const organism = (result.organism && result.organism.length === 1 && result.organism[0].scientific_name) || '';

    // Collect replicates and generate life stage and age display for the search result link. Do
    // not include any where zero or more than one exist.
    const replicates = result.related_datasets.reduce((collectedReplicates, dataset) => (
        dataset.replicates && dataset.replicates.length > 0 ? collectedReplicates.concat(dataset.replicates) : collectedReplicates
    ), []);
    replicates.forEach((replicate) => {
        if (replicate.library && replicate.library.biosample) {
            const biosample = replicate.library.biosample;
            const lifeStage = (biosample.life_stage && biosample.life_stage !== 'unknown') ? biosample.life_stage : '';
            if (lifeStage) {
                lifeStages.push(lifeStage);
            }
            if (biosample.age_display) {
                ages.push(biosample.age_display);
            }
        }
    });
    lifeStages = _.uniq(lifeStages);
    ages = _.uniq(ages);
    const lifeSpec = [lifeStages.length === 1 ? lifeStages[0] : null, ages.length === 1 ? ages[0] : null].filter(Boolean);

    // Get list of target labels.
    if (result.target) {
        targets = _.uniq(result.target.map(target => target.label));
    }

    const contributors = _.uniq(result.contributors.map(lab => lab.title));
    const contributingAwards = _.uniq(result.contributing_awards.map(award => award.project));

    // Work out the count of related datasets
    const totalDatasetCount = result.related_datasets.reduce((datasetCount, dataset) => (searchableDatasetStatuses.includes(dataset.status) ? datasetCount + 1 : datasetCount), 0);

    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">
                        {result.assay_title && result.assay_title.length > 0 ? <span>{result.assay_title.join(', ')} </span> : null}
                        Experiment Series
                        <span>
                            {biosampleTerm ? <span>{` in ${biosampleTerm}`}</span> : null}
                            {lifeSpec.length > 0 ?
                                <span>
                                    {' ('}
                                    {organism ? <i>{organism}</i> : null}
                                    {lifeSpec.length > 0 ? <span>{organism ? ', ' : ''}{lifeSpec.join(', ')}</span> : null}
                                    {')'}
                                </span>
                            : null}
                        </span>
                    </a>
                    <div className="result-item__data-row">
                        {result.dataset_type ? <div><strong>Dataset type: </strong>{result.dataset_type}</div> : null}
                        {targets.length > 0 ? <div><strong>Target: </strong>{targets.join(', ')}</div> : null}
                        <div><strong>Lab: </strong>{contributors.join(', ')}</div>
                        <div><strong>Project: </strong>{contributingAwards.join(', ')}</div>
                    </div>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">Experiment Series</div>
                    <div className="result-item__meta-id">{` ${result.accession}`}</div>
                    <div className="result-experiment-series-search">
                        <a href={`/search/?type=Experiment&related_series.@id=${result['@id']}${searchableDatasetStatusQuery}`}>View {totalDatasetCount} datasets</a>
                    </div>
                    <Status item={result.status} badgeSize="small" css="result-table__status" />
                    {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
                </div>
                <PickerActions context={result} />
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties })}
        </li>
    );
};

ListingComponent.propTypes = {
    /** ExperimentSeries search results */
    context: PropTypes.object.isRequired,
    /** Audit decorator function */
    auditIndicators: PropTypes.func.isRequired,
    /** Audit decorator function */
    auditDetail: PropTypes.func.isRequired,
};

ListingComponent.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'ExperimentSeries');
