import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import UserRoles from '../libs/user_roles';
import * as Pager from '../libs/ui/pager';
import { Panel, PanelBody } from '../libs/ui/panel';
import DropdownButton from '../libs/ui/button';
import { CartToggle, CartAddAllElements } from './cart';
import * as globals from './globals';
import { DbxrefList } from './dbxref';
import { FetchedItems } from './fetched';
import { auditDecor } from './audit';
import pubReferenceList from './reference';
import {
    collectDatasetBiosamples,
    computeExaminedLoci,
    donorDiversity,
    publicDataset,
    requestObjects,
    AlternateAccession,
    ItemAccessories,
    InternalTags,
    TopAccessories,
    treatmentDisplay,
} from './objectutils';
import { softwareVersionList } from './software';
import { SortTablePanel, SortTable } from './sorttable';
import { ProjectBadge } from './image';
import { DocumentsPanelReq } from './doc';
import { FileGallery } from './filegallery';
import Status, { getObjectStatuses, sessionToAccessLevel } from './status';
import { AwardRef, ReplacementAccessions, ControllingExperiments, FileTablePaged, ExperimentTable, DoiRef } from './typeutils';
import getNumberWithOrdinal from '../libs/ordinal_suffix';
import { useMount } from './hooks';

/**
 * All Series types allowed to have a download button. Keep in sync with the same variable in
 * reports/constants.py.
 */
const METADATA_SERIES_TYPES = [
    'AggregateSeries',
    'CollectionSeries',
    'DifferentialAccessibilitySeries',
    'DifferentiationSeries',
    'DiseaseSeries',
    'FunctionalCharacterizationSeries',
    'GeneSilencingSeries',
    'MatchedSet',
    'MultiomicsSeries',
    'OrganismDevelopmentSeries',
    'PulseChaseTimeSeries',
    'ReferenceEpigenome',
    'ReplicationTimingSeries',
    'SingleCellRnaSeries',
    'TreatmentConcentrationSeries',
    'TreatmentTimeSeries',
];

/**
 * Series @types that have a visible file association graph. All other @type for series have
 * hidden file association graphs.
 */
const SERIES_WITH_VISIBLE_FILE_GRAPHS = [
    'FunctionalCharacterizationSeries',
    'AggregateSeries',
];


// Return a summary of the given biosamples, ready to be displayed in a React component.
export function annotationBiosampleSummary(annotation) {
    const organismName = (annotation.organism && annotation.organism.scientific_name) ? <i>{annotation.organism.scientific_name}</i> : null;
    const lifeStageString = (annotation.relevant_life_stage && annotation.relevant_life_stage !== 'unknown') ? <span>{annotation.relevant_life_stage}</span> : null;
    const timepointString = annotation.relevant_timepoint ? <span>{annotation.relevant_timepoint + (annotation.relevant_timepoint_units ? ` ${annotation.relevant_timepoint_units}` : '')}</span> : null;

    // Build an array of strings we can join, not including empty strings
    const summaryStrings = _.compact([organismName, lifeStageString, timepointString]);

    if (summaryStrings.length > 0) {
        return (
            <span className="biosample-summary">
                {summaryStrings.map((summaryString, i) => (
                    <span key={i}>
                        {i > 0 ? <span>{', '}{summaryString}</span> : <span>{summaryString}</span>}
                    </span>
                ))}
            </span>
        );
    }
    return null;
}


// Break the given camel-cased name into space-separated words just before the interior capital letters.
function breakSetName(name) {
    return name.replace(/(\S)([A-Z])/g, '$1 $2');
}


// Display Annotation page, a subtype of Dataset.
const AnnotationComponent = (props, reactContext) => {
    const { context, auditIndicators, auditDetail } = props;
    const itemClass = globals.itemClass(context, 'view-item');
    const userRoles = new UserRoles(reactContext.session_properties);
    const experimentsUrl = `/search/?type=Experiment&possible_controls.accession=${context.accession}`;
    const fccexperimentsUrl = `/search/?type=FunctionalCharacterizationExperiment&elements_references.accession=${context.accession}`;

    // Build up array of documents attached to this dataset
    const datasetDocuments = (context.documents && context.documents.length > 0) ? [...new Set(context.documents.map((documents) => documents['@id']))] : [];

    // Make a biosample summary string
    const biosampleSummary = annotationBiosampleSummary(context);

    // Set up the breadcrumbs
    const datasetType = context['@type'][1];
    const filesetType = context['@type'][0];
    const crumbs = [
        { id: 'Datasets' },
        { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
        { id: breakSetName(filesetType), uri: `/search/?type=${filesetType}`, wholeTip: `Search for ${filesetType}` },
    ];

    // Get a list of reference links, if any
    const references = pubReferenceList(context.references);

    return (
        <div className={itemClass}>
            <header>
                <TopAccessories context={context} crumbs={crumbs} />
                <h1>Summary for annotation file set {context.accession}</h1>
                <DoiRef context={context} />
                <ReplacementAccessions context={context} />
                <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'annotation-audit' }} hasCartControls />
            </header>
            {auditDetail(context.audit, 'annotation-audit', { session: reactContext.session, sessionProperties: reactContext.session_properties, except: context['@id'] })}
            <Panel>
                <PanelBody addClasses="panel__split">
                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--annotation">
                            <h4>Summary</h4>
                        </div>
                        <dl className="key-value">
                            <div data-test="status">
                                <dt>Status</dt>
                                <dd><Status item={context} inline /></dd>
                            </div>

                            <div data-test="accession">
                                <dt>Accession</dt>
                                <dd>{context.accession}</dd>
                            </div>

                            {context.description ?
                                <div data-test="description">
                                    <dt>Description</dt>
                                    <dd>{context.description}</dd>
                                </div>
                            : null}

                            {context.assay_term_name ?
                                <div data-test="assaytermname">
                                    <dt>Assay</dt>
                                    <dd>{context.assay_term_name.join(', ')}</dd>
                                </div>
                            : null}

                            {context.targets && context.targets.length > 0 ?
                                <div data-test="targets">
                                    <dt>Target</dt>
                                    <dd>
                                        {context.targets.map((target, i) => (
                                            <>
                                                {i > 0 ? <span>, </span> : null}
                                                <a href={target['@id']}>{target.label}</a>
                                            </>
                                        ))}
                                    </dd>
                                </div>
                            : null}

                            {context.biosample_ontology || biosampleSummary ?
                                <div data-test="biosample">
                                    <dt>Biosample summary</dt>
                                    <dd>
                                        {context.biosample_ontology ? <span>{context.biosample_ontology.term_name}{' '}</span> : null}
                                        {biosampleSummary ? <span>({biosampleSummary})</span> : null}
                                    </dd>
                                </div>
                            : null}

                            {context.biosample_ontology ?
                                <div data-test="biosampletype">
                                    <dt>Biosample type</dt>
                                    <dd>{context.biosample_ontology.classification}</dd>
                                </div>
                            : null}

                            {context.disease_term_name && context.disease_term_name.length > 0 ?
                                <div data-test="healthstatus">
                                    <dt>Health status</dt>
                                    <dd>
                                        <ul>
                                            {context.disease_term_name.map((disease) => (
                                                <li key={disease} className="multi-comma">
                                                    {disease}
                                                </li>
                                            ))}
                                        </ul>
                                    </dd>
                                </div>
                            : null}

                            {context.organism ?
                                <div data-test="organism">
                                    <dt>Organism</dt>
                                    <dd>{context.organism.name}</dd>
                                </div>
                            : null}

                            {context.donor ?
                                <div data-test="donor">
                                    <dt>Donor</dt>
                                    <dd><a href={context.donor}>{globals.atIdToAccession(context.donor)}</a></dd>
                                </div>
                            : null}

                            {context.annotation_type ?
                                <div data-test="type">
                                    <dt>Annotation type</dt>
                                    <dd className="sentence-case">
                                        <span>{context.annotation_type}</span>
                                        {context.annotation_subtype ? <span> ({context.annotation_subtype})</span> : null}
                                    </dd>
                                </div>
                            : null}

                            {context.trait ?
                                <div data-test="trait">
                                    <dt>Trait</dt>
                                    <dd>{context.trait}</dd>
                                </div>
                            : null}

                            {context.experimental_input?.length > 0 ?
                                <div data-test="experimentalinput">
                                    <dt>Experimental input</dt>
                                    <dd>
                                        <ul>
                                            {context.experimental_input.map((input) => (
                                                <li key={input}>
                                                    <a href={input}>
                                                        {globals.atIdToAccession(input)}
                                                    </a>
                                                </li>
                                            ))}
                                        </ul>
                                    </dd>
                                </div>
                            : null}

                            {context.biochemical_inputs && context.biochemical_inputs.length > 0 ?
                                 <div data-test="biochemicalinputs">
                                     <dt>Biochemical activity</dt>
                                     <dd>{context.biochemical_inputs.join(', ')}</dd>
                                 </div>
                             : null}

                            {context.software_used && context.software_used.length > 0 ?
                                <div data-test="softwareused">
                                    <dt>Software used</dt>
                                    <dd>{softwareVersionList(context.software_used)}</dd>
                                </div>
                            : null}

                            {context.treatments && context.treatments.length > 0 ?
                                <PanelBody addClasses="panel__below-split">
                                    <h4>Treatment details</h4>
                                    {context.treatments.map((treatment) => treatmentDisplay(treatment))}
                                </PanelBody>
                            : null}
                        </dl>
                    </div>

                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--annotation">
                            <h4>Attribution</h4>
                            <ProjectBadge award={context.award} addClasses="badge-heading" />
                        </div>
                        <dl className="key-value">
                            {context.encyclopedia_version ?
                                <div data-test="encyclopediaversion">
                                    <dt>Encyclopedia version</dt>
                                    <dd>{context.encyclopedia_version.join(', ')}</dd>
                                </div>
                            : null}

                            {context.lab ?
                                <div data-test="lab">
                                    <dt>Lab</dt>
                                    <dd>{context.lab.title}</dd>
                                </div>
                            : null}

                            <AwardRef context={context} adminUser={userRoles.isAdmin} />

                            {context.aliases.length > 0 ?
                                <div data-test="aliases">
                                    <dt>Aliases</dt>
                                    <dd><DbxrefList context={context} dbxrefs={context.aliases} /></dd>
                                </div>
                            : null}

                            <div data-test="externalresources">
                                <dt>External resources</dt>
                                <dd>
                                    {context.dbxrefs && context.dbxrefs.length > 0 ?
                                        <DbxrefList context={context} dbxrefs={context.dbxrefs} />
                                    : <em>None submitted</em> }
                                </dd>
                            </div>

                            {references ?
                                <div data-test="references">
                                    <dt>Publications</dt>
                                    <dd>{references}</dd>
                                </div>
                            : null}

                            {context.internal_tags && context.internal_tags.length > 0 ?
                                <div className="tag-badges" data-test="tags">
                                    <dt>Tags</dt>
                                    <dd><InternalTags internalTags={context.internal_tags} objectType={context['@type'][0]} /></dd>
                                </div>
                            : null}
                        </dl>
                    </div>
                </PanelBody>
            </Panel>

            {/* Display the file widget with the facet, graph, and tables */}
            <FileGallery context={context} showReplicateNumber={false} />

            <FetchedItems {...props} url={experimentsUrl} Component={ControllingExperiments} />

            <FetchedItems {...props} url={fccexperimentsUrl} Component={ExperimentTable} title={`Functional characterization experiments with ${context.accession} as an elements reference`} />

            <DocumentsPanelReq documents={datasetDocuments} />
        </div>
    );
};

AnnotationComponent.propTypes = {
    context: PropTypes.object.isRequired, // Annotation being displayed
    auditIndicators: PropTypes.func.isRequired, // From audit decorator
    auditDetail: PropTypes.func.isRequired, // From audit decorator
};

AnnotationComponent.contextTypes = {
    session: PropTypes.object, // Login session information
    session_properties: PropTypes.object,
};

const Annotation = auditDecor(AnnotationComponent);

globals.contentViews.register(Annotation, 'Annotation');


// Display PublicationData page, a subtype of Dataset.
const PublicationDataComponent = ({ context, auditIndicators, auditDetail }, reactContext) => {
    const itemClass = globals.itemClass(context, 'view-item');
    const userRoles = new UserRoles(reactContext.session_properties);
    const experimentsUrl = `/search/?type=Experiment&possible_controls.accession=${context.accession}`;

    // Build up array of documents attached to this dataset
    const datasetDocuments = (context.documents && context.documents.length > 0) ? context.documents : [];

    // Set up the breadcrumbs
    const datasetType = context['@type'][1];
    const filesetType = context['@type'][0];
    const crumbs = [
        { id: 'Datasets' },
        { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
        { id: breakSetName(filesetType), uri: `/search/?type=${filesetType}`, wholeTip: `Search for ${filesetType}` },
    ];

    // Render the publication links
    const referenceList = pubReferenceList(context.references);

    return (
        <div className={itemClass}>
            <header>
                <TopAccessories context={context} crumbs={crumbs} />
                <h1>Summary for publication file set {context.accession}</h1>
                <DoiRef context={context} />
                <div className="replacement-accessions">
                    <AlternateAccession altAcc={context.alternate_accessions} />
                </div>
                <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'publicationdata-audit' }} />
            </header>
            {auditDetail(context.audit, 'publicationdata-audit', { session: reactContext.session, sessionProperties: reactContext.session_properties, except: context['@id'] })}
            <Panel>
                <PanelBody addClasses="panel__split">
                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--publication-data">
                            <h4>Summary</h4>
                        </div>
                        <dl className="key-value">
                            <div data-test="status">
                                <dt>Status</dt>
                                <dd><Status item={context} inline /></dd>
                            </div>

                            <div data-test="accession">
                                <dt>Accession</dt>
                                <dd>{context.accession}</dd>
                            </div>

                            {context.description ?
                                <div data-test="description">
                                    <dt>Description</dt>
                                    <dd>{context.description}</dd>
                                </div>
                            : null}

                            {context.dataset_type ?
                                <div data-test="type">
                                    <dt>Dataset type</dt>
                                    <dd className="sentence-case">{context.dataset_type}</dd>
                                </div>
                            : null}
                        </dl>
                    </div>

                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--publication-data">
                            <h4>Attribution</h4>
                            <ProjectBadge award={context.award} addClasses="badge-heading" />
                        </div>
                        <dl className="key-value">
                            {context.lab ?
                                <div data-test="lab">
                                    <dt>Lab</dt>
                                    <dd>{context.lab.title}</dd>
                                </div>
                            : null}

                            <AwardRef context={context} adminUser={userRoles.isAdmin} />

                            <div data-test="externalresources">
                                <dt>External resources</dt>
                                <dd>
                                    {context.dbxrefs && context.dbxrefs.length > 0 ?
                                        <DbxrefList context={context} dbxrefs={context.dbxrefs} />
                                    : <em>None submitted</em> }
                                </dd>
                            </div>

                            {referenceList ?
                                <div data-test="references">
                                    <dt>Publications</dt>
                                    <dd>{referenceList}</dd>
                                </div>
                            : null}

                            {context.internal_tags && context.internal_tags.length > 0 ?
                                <div className="tag-badges" data-test="tags">
                                    <dt>Tags</dt>
                                    <dd><InternalTags internalTags={context.internal_tags} objectType={context['@type'][0]} /></dd>
                                </div>
                            : null}
                        </dl>
                    </div>
                </PanelBody>
            </Panel>

            <FileTablePaged context={context} fileIds={context.files} title="Files" />

            <FetchedItems context={context} url={experimentsUrl} Component={ControllingExperiments} />

            <DocumentsPanelReq documents={datasetDocuments} />
        </div>
    );
};

PublicationDataComponent.propTypes = {
    context: PropTypes.object.isRequired, // PublicationData object to display
    auditIndicators: PropTypes.func.isRequired, // From audit decorator
    auditDetail: PropTypes.func.isRequired, // From audit decorator
};

PublicationDataComponent.contextTypes = {
    session: PropTypes.object, // Login session information
    session_properties: PropTypes.object,
};

const PublicationData = auditDecor(PublicationDataComponent);

globals.contentViews.register(PublicationData, 'PublicationData');


// Columns to display in Deriving/Derived From file tables.
const fileCols = {
    accession: {
        title: 'Accession',
        display: (file) => <a href={file['@id']} title={`View page for file ${file.title}`}>{file.title}</a>,
    },
    dataset: {
        title: 'Dataset',
        display: (file) => {
            const datasetAccession = globals.atIdToAccession(file.dataset);
            return <a href={file.dataset} title={`View page for dataset ${datasetAccession}`}>{datasetAccession}</a>;
        },
        sorter: (aId, bId) => {
            const aAccession = globals.atIdToAccession(aId);
            const bAccession = globals.atIdToAccession(bId);
            return aAccession < bAccession ? -1 : (aAccession > bAccession ? 1 : 0);
        },
    },
    file_format: { title: 'File format' },
    output_type: { title: 'Output type' },
    title: {
        title: 'Lab',
        getValue: (file) => (file.lab && file.lab.title ? file.lab.title : ''),
    },
    assembly: { title: 'Mapping assembly' },
    status: {
        title: 'File status',
        display: (item) => <Status item={item} badgeSize="small" inline />,
        sorter: (aStatus, bStatus) => (aStatus < bStatus ? -1 : (aStatus > bStatus ? 1 : 0)),
    },
};


// Display Computational Model page, a subtype of Dataset.
const ComputationalModelComponent = (props, reactContext) => {
    const { context, auditIndicators, auditDetail } = props;
    const itemClass = globals.itemClass(context, 'view-item');
    const userRoles = new UserRoles(reactContext.session_properties);
    const experimentsUrl = `/search/?type=Experiment&possible_controls.accession=${context.accession}`;
    const fileCountDisplay = <div className="table-paged__count">{`${context.files.length} file${context.files.length === 1 ? '' : 's'}`}</div>;

    // Build up array of documents attached to this dataset
    const datasetDocuments = (context.documents && context.documents.length > 0) ? context.documents : [];

    // Set up the breadcrumbs
    const datasetType = context['@type'][1];
    const filesetType = context['@type'][0];
    const crumbs = [
        { id: 'Datasets' },
        { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
        { id: breakSetName(filesetType), uri: `/search/?type=${filesetType}`, wholeTip: `Search for ${filesetType}` },
    ];

    // Render the publication links
    const referenceList = pubReferenceList(context.references);

    return (
        <div className={itemClass}>
            <header>
                <TopAccessories context={context} crumbs={crumbs} />
                <h1>Summary for computational model file set {context.accession}</h1>
                <DoiRef context={context} />
                <div className="replacement-accessions">
                    <AlternateAccession altAcc={context.alternate_accessions} />
                </div>
                <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'computationalmodel-audit' }} />
            </header>
            {auditDetail(context.audit, 'computationalmodel-audit', { session: reactContext.session, sessionProperties: reactContext.session_properties, except: context['@id'] })}
            <Panel>
                <PanelBody addClasses="panel__split">
                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--computational-model">
                            <h4>Summary</h4>
                        </div>
                        <dl className="key-value">
                            <div data-test="status">
                                <dt>Status</dt>
                                <dd><Status item={context} inline /></dd>
                            </div>

                            <div data-test="accession">
                                <dt>Accession</dt>
                                <dd>{context.accession}</dd>
                            </div>

                            {context.description ?
                                <div data-test="description">
                                    <dt>Description</dt>
                                    <dd>{context.description}</dd>
                                </div>
                            : null}

                            {context.computational_model_type ?
                                <div data-test="type">
                                    <dt>Computational model type</dt>
                                    <dd className="sentence-case">{context.computational_model_type}</dd>
                                </div>
                            : null}

                            {context.dataset_type ?
                                <div data-test="type">
                                    <dt>Dataset type</dt>
                                    <dd className="sentence-case">{context.dataset_type}</dd>
                                </div>
                            : null}

                            {context.software_used && context.software_used.length > 0 ?
                                <div data-test="softwareused">
                                    <dt>Software used</dt>
                                    <dd>{softwareVersionList(context.software_used)}</dd>
                                </div>
                            : null}
                        </dl>
                    </div>

                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--computational-model-data">
                            <h4>Attribution</h4>
                            <ProjectBadge award={context.award} addClasses="badge-heading" />
                        </div>
                        <dl className="key-value">
                            {context.lab ?
                                <div data-test="lab">
                                    <dt>Lab</dt>
                                    <dd>{context.lab.title}</dd>
                                </div>
                            : null}

                            <AwardRef context={context} adminUser={userRoles.isAdmin} />

                            <div data-test="externalresources">
                                <dt>External resources</dt>
                                <dd>
                                    {context.dbxrefs && context.dbxrefs.length > 0 ?
                                        <DbxrefList context={context} dbxrefs={context.dbxrefs} />
                                    : <em>None submitted</em> }
                                </dd>
                            </div>

                            {referenceList ?
                                <div data-test="references">
                                    <dt>Publications</dt>
                                    <dd>{referenceList}</dd>
                                </div>
                            : null}

                            {context.internal_tags && context.internal_tags.length > 0 ?
                                <div className="tag-badges" data-test="tags">
                                    <dt>Tags</dt>
                                    <dd><InternalTags internalTags={context.internal_tags} objectType={context['@type'][0]} /></dd>
                                </div>
                            : null}
                        </dl>
                    </div>
                </PanelBody>
            </Panel>

            {context.files.length > 0 ?
                <SortTablePanel title="Files" subheader={fileCountDisplay}>
                    <SortTable list={context.files} columns={fileCols} sortColumn="accession" />
                </SortTablePanel>
            : null}

            <FileTablePaged fileIds={context.contributing_files} title="Contributing files" />

            <FetchedItems {...props} url={experimentsUrl} Component={ControllingExperiments} />

            <DocumentsPanelReq documents={datasetDocuments} />
        </div>
    );
};

ComputationalModelComponent.propTypes = {
    context: PropTypes.object.isRequired, // Computational Model object to display
    auditIndicators: PropTypes.func.isRequired, // From audit decorator
    auditDetail: PropTypes.func.isRequired, // From audit decorator
};

ComputationalModelComponent.contextTypes = {
    session: PropTypes.object, // Login session information
    session_properties: PropTypes.object,
};

const ComputationalModel = auditDecor(ComputationalModelComponent);

globals.contentViews.register(ComputationalModel, 'ComputationalModel');


// Display Reference page, a subtype of Dataset.
const ReferenceComponent = (props, reactContext) => {
    const { context, auditIndicators, auditDetail } = props;
    const itemClass = globals.itemClass(context, 'view-item');
    const userRoles = new UserRoles(reactContext.session_properties);
    const experimentsUrl = `/search/?type=Experiment&possible_controls.accession=${context.accession}`;
    const fccexperimentsUrl = `/search/?type=FunctionalCharacterizationExperiment&elements_references.accession=${context.accession}`;

    // Build up array of documents attached to this dataset
    const datasetDocuments = (context.documents && context.documents.length > 0) ? context.documents : [];

    // Set up the breadcrumbs
    const datasetType = context['@type'][1];
    const filesetType = context['@type'][0];
    const crumbs = [
        { id: 'Datasets' },
        { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
        { id: breakSetName(filesetType), uri: `/search/?type=${filesetType}`, wholeTip: `Search for ${filesetType}` },
    ];

    // Get a list of reference links, if any
    const references = pubReferenceList(context.references);

    return (
        <div className={itemClass}>
            <header>
                <TopAccessories context={context} crumbs={crumbs} />
                <h1>Summary for reference file set {context.accession}</h1>
                <DoiRef context={context} />
                <div className="replacement-accessions">
                    <AlternateAccession altAcc={context.alternate_accessions} />
                </div>
                <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'reference-audit' }} />
            </header>
            {auditDetail(context.audit, 'reference-audit', { session: reactContext.session, sessionProperties: reactContext.session_properties, except: context['@id'] })}
            <Panel>
                <PanelBody addClasses="panel__split">
                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--reference">
                            <h4>Summary</h4>
                        </div>
                        <dl className="key-value">
                            <div data-test="status">
                                <dt>Status</dt>
                                <dd><Status item={context} inline /></dd>
                            </div>

                            <div data-test="accession">
                                <dt>Accession</dt>
                                <dd>{context.accession}</dd>
                            </div>

                            {context.description ?
                                <div data-test="description">
                                    <dt>Description</dt>
                                    <dd>{context.description}</dd>
                                </div>
                            : null}

                            {context.donor ?
                                <div data-test="donor">
                                    <dt>Donor</dt>
                                    <dd><a href={context.donor['@id']} title="Donor">{context.donor.accession}</a></dd>
                                </div>
                            : null}

                            {context.reference_type ?
                                <div data-test="type">
                                    <dt>Reference type</dt>
                                    <dd>{context.reference_type}</dd>
                                </div>
                            : null}

                            {context.organism ?
                                <div data-test="organism">
                                    <dt>Organism</dt>
                                    <dd>{context.organism.name}</dd>
                                </div>
                            : null}

                            {context.crispr_screen_tiling ?
                                 <div data-test="crisprscreentiling">
                                     <dt>CRISPR screen tiling</dt>
                                     <dd>{context.crispr_screen_tiling}</dd>
                                 </div>
                             : null}

                            {context.examined_loci && context.examined_loci.length > 0 ?
                                <div data-test="examinedloci">
                                    <dt>Examined loci</dt>
                                    <dd>
                                        <ul>
                                            {context.examined_loci.map((examinedLocus) => (
                                                <li key={examinedLocus['@id']} className="multi-comma">
                                                    <a href={examinedLocus['@id']}>
                                                        {examinedLocus.symbol}
                                                    </a>
                                                </li>
                                            ))}
                                        </ul>
                                    </dd>
                                </div>
                            : null}

                            {context.examined_regions && context.examined_regions.length > 0 ?
                                <div data-test="examinedregions">
                                    <dt>Examined regions</dt>
                                    <dd>
                                        <ul>
                                            {context.examined_regions.map((region, l) => (
                                                <li key={l} className="multi-comma">{`${region.assembly} ${region.chromosome}:${region.start}-${region.end}`}</li>
                                            ))}
                                        </ul>
                                    </dd>
                                </div>
                            : null}

                            {context.elements_selection_method && context.elements_selection_method.length > 0 ?
                            <div data-test="elementsselectionmethod">
                                <dt>Elements selection method</dt>
                                <dd>{context.elements_selection_method.join(', ')}</dd>
                            </div>
                            : null}

                            {context.experimental_input?.length > 0 ?
                                <div data-test="experimentalinput">
                                    <dt>Experimental input</dt>
                                    <dd>
                                        <ul>
                                            {context.experimental_input.map((input) => (
                                                <li key={input}>
                                                    <a href={input}>
                                                        {globals.atIdToAccession(input)}
                                                    </a>
                                                </li>
                                            ))}
                                        </ul>
                                    </dd>
                                </div>
                            : null}

                            {context.related_pipelines && context.related_pipelines.length > 0 ?
                                <div data-test="relatedpipelines">
                                    <dt>Related Pipelines</dt>
                                    <dd>
                                        {context.related_pipelines.map((pipeline, i) => (
                                            <React.Fragment key={pipeline['@id']}>
                                                {i > 0 ? <span>, </span> : null}
                                                <a href={pipeline['@id']}>{pipeline.accession}</a>
                                            </React.Fragment>
                                        ))}
                                    </dd>
                                </div>
                            : null}

                            {context.software_used && context.software_used.length > 0 ?
                                <div data-test="softwareused">
                                    <dt>Software used</dt>
                                    <dd>{softwareVersionList(context.software_used)}</dd>
                                </div>
                            : null}
                        </dl>
                    </div>

                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--reference">
                            <h4>Attribution</h4>
                            <ProjectBadge award={context.award} addClasses="badge-heading" />
                        </div>
                        <dl className="key-value">
                            {context.lab ?
                                <div data-test="lab">
                                    <dt>Lab</dt>
                                    <dd>{context.lab.title}</dd>
                                </div>
                            : null}

                            <AwardRef context={context} adminUser={userRoles.isAdmin} />

                            {context.aliases.length > 0 ?
                                <div data-test="aliases">
                                    <dt>Aliases</dt>
                                    <dd><DbxrefList context={context} dbxrefs={context.aliases} /></dd>
                                </div>
                            : null}

                            <div data-test="externalresources">
                                <dt>External resources</dt>
                                <dd>
                                    {context.dbxrefs && context.dbxrefs.length > 0 ?
                                        <DbxrefList context={context} dbxrefs={context.dbxrefs} />
                                    : <em>None submitted</em> }
                                </dd>
                            </div>

                            {references ?
                                <div data-test="references">
                                    <dt>Publications</dt>
                                    <dd>{references}</dd>
                                </div>
                            : null}

                            {context.internal_tags && context.internal_tags.length > 0 ?
                                <div className="tag-badges" data-test="tags">
                                    <dt>Tags</dt>
                                    <dd><InternalTags internalTags={context.internal_tags} objectType={context['@type'][0]} /></dd>
                                </div>
                            : null}
                        </dl>
                    </div>
                </PanelBody>
            </Panel>

            {/* Display the file widget with the facet, graph, and tables */}
            <FileGallery context={context} hideGraph collapseNone />

            <FetchedItems {...props} url={experimentsUrl} Component={ControllingExperiments} />

            <FetchedItems {...props} url={fccexperimentsUrl} Component={ExperimentTable} title={`Functional characterization experiments with ${context.accession} as an elements reference`} />

            <DocumentsPanelReq documents={datasetDocuments} />
        </div>
    );
};

ReferenceComponent.propTypes = {
    context: PropTypes.object.isRequired, // Reference object to display
    auditIndicators: PropTypes.func.isRequired, // From audit decorator
    auditDetail: PropTypes.func.isRequired, // From audit decorator
};

ReferenceComponent.contextTypes = {
    session: PropTypes.object, // Login session information
    session_properties: PropTypes.object,
};

const Reference = auditDecor(ReferenceComponent);

globals.contentViews.register(Reference, 'Reference');


// Display Annotation page, a subtype of Dataset.
const ProjectComponent = (props, reactContext) => {
    const { context, auditIndicators, auditDetail } = props;
    const itemClass = globals.itemClass(context, 'view-item');
    const userRoles = new UserRoles(reactContext.session_properties);
    const experimentsUrl = `/search/?type=Experiment&possible_controls.accession=${context.accession}`;

    // Build up array of documents attached to this dataset
    const datasetDocuments = (context.documents && context.documents.length > 0) ? context.documents : [];

    // Collect organisms
    const organisms = (context.organism && context.organism.length > 0) ? [...new Set(context.organism.map((organism) => organism.name))] : [];

    // Set up the breadcrumbs
    const datasetType = context['@type'][1];
    const filesetType = context['@type'][0];
    const crumbs = [
        { id: 'Datasets' },
        { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
        { id: breakSetName(filesetType), uri: `/search/?type=${filesetType}`, wholeTip: `Search for ${filesetType}` },
    ];

    // Get a list of reference links
    const references = pubReferenceList(context.references);

    return (
        <div className={itemClass}>
            <header>
                <TopAccessories context={context} crumbs={crumbs} />
                <h1>Summary for project file set {context.accession}</h1>
                <DoiRef context={context} />
                <div className="replacement-accessions">
                    <AlternateAccession altAcc={context.alternate_accessions} />
                </div>
                <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'project-audit' }} />
            </header>
            {auditDetail(context.audit, 'project-audit', { session: reactContext.session, except: context['@id'] })}
            <Panel>
                <PanelBody addClasses="panel__split">
                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--project">
                            <h4>Summary</h4>
                        </div>
                        <dl className="key-value">
                            <div data-test="status">
                                <dt>Status</dt>
                                <dd><Status item={context} inline /></dd>
                            </div>

                            {context.assay_term_name && context.assay_term_name.length > 0 ?
                                <div data-test="assaytermname">
                                    <dt>Assay(s)</dt>
                                    <dd>{context.assay_term_name.join(', ')}</dd>
                                </div>
                            : null}

                            <div data-test="accession">
                                <dt>Accession</dt>
                                <dd>{context.accession}</dd>
                            </div>

                            {context.description ?
                                <div data-test="description">
                                    <dt>Description</dt>
                                    <dd>{context.description}</dd>
                                </div>
                            : null}

                            {context.project_type ?
                                <div data-test="type">
                                    <dt>Project type</dt>
                                    <dd className="sentence-case">{context.project_type}</dd>
                                </div>
                            : null}

                            {context.biosample_ontology && context.biosample_ontology.length > 0 ?
                                <div data-test="biosampletermname">
                                    <dt>Biosample term name</dt>
                                    <dd>{[...new Set(context.biosample_ontology.map((b) => b.term_name))].join(', ')}</dd>
                                </div>
                            : null}

                            {context.biosample_ontology && context.biosample_ontology.length > 0 ?
                                <div data-test="biosampletype">
                                    <dt>Biosample type</dt>
                                    <dd>{[...new Set(context.biosample_ontology.map((b) => (b.classification ? b.classification : '')))].join(', ')}</dd>
                                </div>
                            : null}

                            {organisms.length > 0 ?
                                <div data-test="organism">
                                    <dt>Organism</dt>
                                    <dd>{organisms.join(', ')}</dd>
                                </div>
                            : null}

                            {context.software_used && context.software_used.length > 0 ?
                                <div data-test="softwareused">
                                    <dt>Software used</dt>
                                    <dd>{softwareVersionList(context.software_used)}</dd>
                                </div>
                            : null}
                        </dl>
                    </div>

                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--project">
                            <h4>Attribution</h4>
                            <ProjectBadge award={context.award} addClasses="badge-heading" />
                        </div>
                        <dl className="key-value">
                            {context.lab ?
                                <div data-test="lab">
                                    <dt>Lab</dt>
                                    <dd>{context.lab.title}</dd>
                                </div>
                            : null}

                            <AwardRef context={context} adminUser={userRoles.isAdmin} />

                            {context.aliases.length > 0 ?
                                <div data-test="aliases">
                                    <dt>Aliases</dt>
                                    <dd><DbxrefList context={context} dbxrefs={context.aliases} /></dd>
                                </div>
                            : null}

                            <div data-test="externalresources">
                                <dt>External resources</dt>
                                <dd>
                                    {context.dbxrefs && context.dbxrefs.length > 0 ?
                                        <DbxrefList context={context} dbxrefs={context.dbxrefs} />
                                    : <em>None submitted</em> }
                                </dd>
                            </div>

                            {references ?
                                <div data-test="references">
                                    <dt>Publications</dt>
                                    <dd>{references}</dd>
                                </div>
                            : null}

                            {context.internal_tags && context.internal_tags.length > 0 ?
                                <div className="tag-badges" data-test="tags">
                                    <dt>Tags</dt>
                                    <dd><InternalTags internalTags={context.internal_tags} objectType={context['@type'][0]} /></dd>
                                </div>
                            : null}
                        </dl>
                    </div>
                </PanelBody>
            </Panel>

            {/* Display the file widget with the facet, graph, and tables */}
            <FileGallery context={context} hideGraph collapseNone />

            <FetchedItems {...props} url={experimentsUrl} Component={ControllingExperiments} />

            <DocumentsPanelReq documents={datasetDocuments} />
        </div>
    );
};

ProjectComponent.propTypes = {
    context: PropTypes.object.isRequired, // Project object to display
    auditIndicators: PropTypes.func.isRequired, // From audit decorator
    auditDetail: PropTypes.func.isRequired, // From audit decorator
};

ProjectComponent.contextTypes = {
    session: PropTypes.object, // Login session information
    session_properties: PropTypes.object,
};

const Project = auditDecor(ProjectComponent);

globals.contentViews.register(Project, 'Project');


// Display Annotation page, a subtype of Dataset.
const UcscBrowserCompositeComponent = (props, reactContext) => {
    const { context, auditIndicators, auditDetail } = props;
    const itemClass = globals.itemClass(context, 'view-item');
    const userRoles = new UserRoles(reactContext.session_properties);
    const experimentsUrl = `/search/?type=Experiment&possible_controls.accession=${context.accession}`;

    // Build up array of documents attached to this dataset
    const datasetDocuments = (context.documents && context.documents.length > 0) ? context.documents : [];

    // Collect organisms
    const organisms = (context.organism && context.organism.length > 0) ? [...new Set(context.organism.map((organism) => organism.name))] : [];

    // Set up the breadcrumbs
    const datasetType = context['@type'][1];
    const filesetType = context['@type'][0];
    const crumbs = [
        { id: 'Datasets' },
        { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
        { id: breakSetName(filesetType), uri: `/search/?type=${filesetType}`, wholeTip: `Search for ${filesetType}` },
    ];

    // Get a list of reference links, if any
    const references = pubReferenceList(context.references);

    return (
        <div className={itemClass}>
            <header>
                <TopAccessories context={context} crumbs={crumbs} />
                <h1>Summary for UCSC browser composite file set {context.accession}</h1>
                <DoiRef context={context} />
                <div className="replacement-accessions">
                    <AlternateAccession altAcc={context.alternate_accessions} />
                </div>
                <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'ucscbrowsercomposite-audit' }} />
            </header>
            {auditDetail(context.audit, 'ucscbrowsercomposite-audit', { session: reactContext.session, sessionProperties: reactContext.session_properties, except: context['@id'] })}
            <Panel>
                <PanelBody addClasses="panel__split">
                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--ucsc-browser">
                            <h4>Summary</h4>
                        </div>
                        <dl className="key-value">
                            <div data-test="status">
                                <dt>Status</dt>
                                <dd><Status item={context} inline /></dd>
                            </div>

                            {context.assay_term_name && context.assay_term_name.length > 0 ?
                                <div data-test="assays">
                                    <dt>Assay(s)</dt>
                                    <dd>{context.assay_term_name.join(', ')}</dd>
                                </div>
                            : null}

                            <div data-test="accession">
                                <dt>Accession</dt>
                                <dd>{context.accession}</dd>
                            </div>

                            {context.description ?
                                <div data-test="description">
                                    <dt>Description</dt>
                                    <dd>{context.description}</dd>
                                </div>
                            : null}

                            {context.dataset_type ?
                                <div data-test="type">
                                    <dt>Dataset type</dt>
                                    <dd className="sentence-case">{context.dataset_type}</dd>
                                </div>
                            : null}

                            {organisms.length > 0 ?
                                <div data-test="organism">
                                    <dt>Organism</dt>
                                    <dd>{organisms.join(', ')}</dd>
                                </div>
                            : null}

                            {context.software_used && context.software_used.length > 0 ?
                                <div data-test="software-used">
                                    <dt>Software used</dt>
                                    <dd>{softwareVersionList(context.software_used)}</dd>
                                </div>
                            : null}
                        </dl>
                    </div>

                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--ucsc-browser">
                            <h4>Attribution</h4>
                            <ProjectBadge award={context.award} addClasses="badge-heading" />
                        </div>
                        <dl className="key-value">
                            {context.lab ?
                                <div data-test="lab">
                                    <dt>Lab</dt>
                                    <dd>{context.lab.title}</dd>
                                </div>
                            : null}

                            <AwardRef context={context} adminUser={userRoles.isAdmin} />

                            {context.aliases.length > 0 ?
                                <div data-test="aliases">
                                    <dt>Aliases</dt>
                                    <dd><DbxrefList context={context} dbxrefs={context.aliases} /></dd>
                                </div>
                            : null}

                            <div data-test="externalresources">
                                <dt>External resources</dt>
                                <dd>
                                    {context.dbxrefs && context.dbxrefs.length > 0 ?
                                        <DbxrefList context={context} dbxrefs={context.dbxrefs} />
                                    : <em>None submitted</em> }
                                </dd>
                            </div>

                            {references ?
                                <div data-test="references">
                                    <dt>Publications</dt>
                                    <dd>{references}</dd>
                                </div>
                            : null}

                            {context.internal_tags && context.internal_tags.length > 0 ?
                                <div className="tag-badges" data-test="tags">
                                    <dt>Tags</dt>
                                    <dd><InternalTags internalTags={context.internal_tags} objectType={context['@type'][0]} /></dd>
                                </div>
                            : null}
                        </dl>
                    </div>
                </PanelBody>
            </Panel>

            {/* Display the file widget with the facet, graph, and tables */}
            <FileGallery context={context} hideGraph collapseNone />

            <FetchedItems {...props} url={experimentsUrl} Component={ControllingExperiments} />

            <DocumentsPanelReq documents={datasetDocuments} />
        </div>
    );
};

UcscBrowserCompositeComponent.propTypes = {
    context: PropTypes.object.isRequired, // UCSC browser composite object to display
    auditIndicators: PropTypes.func.isRequired, // From audit decorator
    auditDetail: PropTypes.func.isRequired, // From audit decorator
};

UcscBrowserCompositeComponent.contextTypes = {
    session: PropTypes.object, // Login session information
    session_properties: PropTypes.object,
};

const UcscBrowserComposite = auditDecor(UcscBrowserCompositeComponent);

globals.contentViews.register(UcscBrowserComposite, 'UcscBrowserComposite');


export const FilePanelHeader = (props) => {
    const { context } = props;

    return (
        <div>
            {context.visualize && context.status === 'released' ?
                <span className="pull-right">
                    <DropdownButton.Immediate label="Visualize Data">
                        {Object.keys(context.visualize).sort().map((assembly) => (
                            Object.keys(context.visualize[assembly]).sort().map((browser) => (
                                <a key={[assembly, '_', browser].join()} data-bypass="true" target="_blank" rel="noopener noreferrer" href={context.visualize[assembly][browser]}>
                                    {assembly} {browser}
                                </a>
                            ))
                        ))}
                    </DropdownButton.Immediate>
                </span>
            : null}
            <h4>File summary</h4>
        </div>
    );
};

FilePanelHeader.propTypes = {
    context: PropTypes.object.isRequired, // Object being displayed
};


/**
 * Series experiment table target column definition.
 */
const seriesTableTargetColumn = {
    title: 'Target',
    getValue: (experiment) => {
        if (experiment.target) {
            return (
                <a href={experiment.target['@id']} aria-label={`Target ${experiment.target.label}`}>
                    {experiment.target.label}
                </a>
            );
        }
        if (experiment.control_type === 'control') {
            return '(control)';
        }
        return null;
    },
    hide: (experiments) => {
        const uniqueTargets = experiments.reduce((accTargets, experiment) => (
            experiment.target ? accTargets.add(experiment.target['@id']) : accTargets.add('none')
        ), new Set());
        return uniqueTargets.size <= 1;
    },
};


const basicTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    assay_term_name: {
        title: 'Assay',
    },

    target: seriesTableTargetColumn,

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (experiment) => (experiment.lab ? experiment.lab.title : null),

    },
    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },
    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};


const controlTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    control_type: {
        title: 'Control type',
        display: (experiment) => <>{experiment.control_type}</>,
    },

    target: seriesTableTargetColumn,

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (experiment) => (experiment.lab ? experiment.lab.title : null),

    },
    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },
    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};


/**
 * Generate each of the unique diseases from the biosamples within the given experiment.
 * @param {object} experiment The experiment to generate the disease list from.
 * @returns {string} A comma-separated list of diseases.
 */
const computeDiseases = (experiment) => {
    const biosamples = collectDatasetBiosamples(experiment);
    const diseases = biosamples.reduce((accDiseases, biosample) => {
        if (biosample.disease_term_name) {
            return new Set([...accDiseases, ...biosample.disease_term_name]);
        }
        return accDiseases;
    }, new Set());
    return [...diseases].sort().join(', ');
};


const diseaseSeriesColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    assay_term_name: {
        title: 'Assay',
    },

    target: seriesTableTargetColumn,

    diseaseName: {
        title: 'Disease',
        getValue: (experiment) => computeDiseases(experiment),
        hide: (experiments) => {
            // Collect all diseases from all experiment biosamples, de-duplicated.
            const experimentDiseases = experiments.reduce((accExperimentDiseases, experiment) => {
                // Collect all diseases from all the collected biosamples within an experiment,
                // de-duplicated.
                const biosamples = collectDatasetBiosamples(experiment);
                const biosampleDiseases = biosamples.reduce((accBiosampleDiseases, biosample) => {
                    if (biosample.disease_term_name) {
                        return new Set([...accBiosampleDiseases, ...biosample.disease_term_name]);
                    }
                    return accBiosampleDiseases;
                }, new Set());
                return new Set([...accExperimentDiseases, ...biosampleDiseases]);
            }, new Set());

            // Hide the diseases column if only one disease exists across all experiments in the
            // table.
            return experimentDiseases.size <= 1;
        },
    },

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (experiment) => (experiment.lab ? experiment.lab.title : null),

    },
    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },
    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};


/**
 * Collect all donor objects from all the given biosamples. Any duplicate donors get removed.
 * @param {array} biosamples List of biosamples from which to extract donors.
 * @returns {array} List of all distinct donors.
 */
const collectDonorsFromBiosamples = (biosamples) => (
    _(biosamples.reduce((donors, biosample) => (
        biosample.donor ? donors.concat(biosample.donor) : donors
    ), [])).uniq((donor) => donor.accession)
);


const referenceEpigenomeColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    assay_term_name: {
        title: 'Assay',
    },

    target: seriesTableTargetColumn,

    donors: {
        title: 'Donors',
        display: (experiment, meta) => {
            const biosamples = collectDatasetBiosamples(experiment);
            if (biosamples.length > 0) {
                // Collect all biosample donors and dedupe them by accession.
                const allDonors = collectDonorsFromBiosamples(biosamples);
                if (allDonors.length > 0) {
                    return (
                        <>
                            {allDonors.map((donor, i) => {
                                const viewableStatuses = getObjectStatuses(donor, meta.accessLevel);
                                const isViewable = viewableStatuses.includes(donor.status);
                                return (
                                    <React.Fragment key={donor['@id']}>
                                        {i > 0 ? <>, </> : null}
                                        {isViewable
                                            ? <a href={donor['@id']} aria-label={`${donor.organism.name} donor ${donor.accession}`}>{donor.accession}</a>
                                            : <>{donor.accession}</>
                                        }
                                    </React.Fragment>
                                );
                            })}
                        </>
                    );
                }
            }
            return null;
        },

        hide: (experiments) => {
            // Make an array of comma-separated donor accessions, each array entry representing the
            // donors within the experiment's biosamples and de-duped, so frequently the donor array
            // has fewer entries than the number of experiments they came from.
            const donorLists = experiments.reduce((accDonorLists, experiment) => {
                const biosamples = collectDatasetBiosamples(experiment);
                if (biosamples.length > 0) {
                    // Collect all biosample donor accessions into a set.
                    const donors = biosamples.reduce((accDonor, biosample) => (
                        biosample.donor ? accDonor.add(biosample.donor.accession) : accDonor
                    ), new Set());

                    // Sort the donor accessions in the set and put them all into one comma-
                    // separated string.
                    if (donors.size > 0) {
                        return accDonorLists.add([...donors].sort().join());
                    }
                }

                // No biosamples.
                return accDonorLists;
            }, new Set());

            // If more than one donor list exists after sorting and de-duping them, then we know we
            // have different donors for different experiments in the table, and we should
            // therefore display the donor column.
            return donorLists.size <= 1;
        },

        objSorter: (experimentA, experimentB) => {
            const biosamplesA = collectDatasetBiosamples(experimentA);
            const biosamplesB = collectDatasetBiosamples(experimentB);

            // Sort using the donor accessions combined into sorted comma-separated strings.
            const donorsA = collectDonorsFromBiosamples(biosamplesA).map((donor) => donor.accession).sort().join();
            const donorsB = collectDonorsFromBiosamples(biosamplesB).map((donor) => donor.accession).sort().join();
            if (donorsA < donorsB) {
                return -1;
            }
            if (donorsA > donorsB) {
                return 1;
            }
            return 0;
        },
    },

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (experiment) => (experiment.lab ? experiment.lab.title : null),

    },
    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },
    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};

const geneSilencingSeriesTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    target: seriesTableTargetColumn,

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (experiment) => (experiment.lab ? experiment.lab.title : null),

    },
    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },
    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};


/**
 * Generate a comma-separated string of treatment durations from the given experiment's biosamples.
 * @param {object} experiment - The experiment to generate the treatment durations from.
 * @returns {string} - A comma-separated string of treatment durations.
 */
const computeDurations = (experiment) => {
    let durations = [];
    if (experiment.replicates && experiment.replicates.length > 0) {
        const biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample).filter((biosample) => !!biosample);
        durations = biosamples.reduce((accDurations, biosample) => {
            if (biosample.treatments && biosample.treatments.length > 0) {
                return accDurations.add(`${biosample.treatments[0].duration} ${biosample.treatments[0].duration_units}${biosample.treatments[0].duration > 1 ? 's' : ''}`);
            }
            return accDurations;
        }, new Set());
    }
    return [...durations].join(', ');
};


const timeSeriesTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    target: seriesTableTargetColumn,

    duration: {
        title: 'Duration',
        getValue: (experiment) => computeDurations(experiment),
    },

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (experiment) => (experiment.lab ? experiment.lab.title : null),
    },

    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },

    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};

function computeConcentration(experiment) {
    let concentration = [];
    if (experiment.replicates && experiment.replicates.length > 0) {
        const biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample).filter((biosample) => !!biosample);
        if (biosamples && biosamples.length > 0 && biosamples[0].treatments && biosamples[0].treatments.length > 0 && biosamples[0].treatments[0].amount) {
            concentration = `${biosamples[0].treatments[0].amount} ${biosamples[0].treatments[0].amount_units}`;
        }
    }
    return concentration;
}

const treatmentSeriesTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    target: seriesTableTargetColumn,

    concentration: {
        title: 'Concentration',
        getValue: (experiment) => computeConcentration(experiment),
    },

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (experiment) => (experiment.lab ? experiment.lab.title : null),
    },

    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },

    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};

function computePhase(experiment) {
    let phases = [];
    if (experiment.replicates && experiment.replicates.length > 0) {
        const biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample).filter((biosample) => !!biosample);
        phases = _.chain(biosamples.map((biosample) => biosample.phase)).compact().uniq().value();
    }
    return phases.join(', ');
}

const replicationTimingSeriesTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    target: seriesTableTargetColumn,

    phase: {
        title: 'Cell cycle phase',
        display: (experiment) => computePhase(experiment),
        objSorter: (a, b) => {
            const sortOrder = ['G1', 'G1b', 'S', 'early S', 'S1', 'S2', 'S3', 'S4', 'late S', 'G2'];
            const aIdx = sortOrder.indexOf(computePhase(a));
            const bIdx = sortOrder.indexOf(computePhase(b));
            if (aIdx < bIdx) { return -1; }
            if (aIdx > bIdx) { return 1; }
            return 0;
        },
    },

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (experiment) => (experiment.lab ? experiment.lab.title : null),
    },

    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },

    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};


function computeDifferentiation(experiment) {
    let biosamples;
    let postDifferentiationTime;

    if (experiment.replicates && experiment.replicates.length > 0) {
        biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample).filter((biosample) => !!biosample);
    }
    if (biosamples && biosamples.length > 0) {
        biosamples.forEach((biosample) => {
            if (biosample.post_differentiation_time) {
                postDifferentiationTime = `${biosample.post_differentiation_time} ${biosample.post_differentiation_time_units}${biosample.post_differentiation_time > 1 ? 's' : ''}`;
            }
        });
    }
    return postDifferentiationTime;
}


const differentiationTableColumnsWithTime = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    target: seriesTableTargetColumn,

    post_differentiation_time: {
        title: 'Post-differentiation time',
        display: (experiment) => {
            const postDifferentiationTime = computeDifferentiation(experiment);
            return (
                <span>
                    {postDifferentiationTime ?
                        <span>{postDifferentiationTime}</span>
                    : ''}
                </span>
            );
        },
        objSorter: (a, b) => {
            const aTime = computeDifferentiation(a)?.split(' ')[0] || 0;
            const bTime = computeDifferentiation(b)?.split(' ')[0] || 0;
            if (aTime < bTime) { return -1; }
            if (aTime > bTime) { return 1; }
            return 0;
        },
    },

    biosample: {
        title: 'Biosample',
        getValue: (experiment) => experiment.biosample_ontology.term_name,
    },

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (experiment) => (experiment.lab ? experiment.lab.title : null),

    },

    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },

    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};


const differentiationTableColumnsWithoutTime = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    target: seriesTableTargetColumn,

    biosample: {
        title: 'Biosample',
        getValue: (experiment) => experiment.biosample_ontology.term_name,
    },

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (experiment) => (experiment.lab ? experiment.lab.title : null),

    },

    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },

    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};


// Compute approximate number of days of mouse age to compare ages of different units ("weeks" or "years")
// In the future there are likely to be additions to the data which will require updates to this function
// For instance, ages measured by months will likely be added
function computeAgeComparator(ageStage) {
    const matchRegex = /(.+) ([0-9.]+(?:-\d|.+)?) (.+)/;
    const splitAge = ageStage.match(matchRegex);
    const age = `${splitAge[splitAge.length - 2]} ${splitAge[splitAge.length - 1]}`;
    let ageNumerical = 0;
    if (age.includes('hours') && age.includes('-')) {
        ageNumerical += +age.split('hours')[0].split('-')[1] / 24;
    } else if (age.includes('hours')) {
        ageNumerical += +age.split('hours')[0] / 24;
    } else if (age.includes('days')) {
        ageNumerical += +age.split('days')[0];
    } else if (age.includes('weeks')) {
        ageNumerical += +age.split('weeks')[0] * 7;
    } else if (age.includes(' years')) {
        ageNumerical += +age.split('years')[0] * 365;
    }
    return ageNumerical;
}

// Sort the rows of the matrix by stage (embryo -> postnatal -> adult) and then by age
// Age can be denoted in days or weeks
// In the future there are likely to be additions to the data which will require updates to this function
// For instance, ages measured by months will likely be added
const sortMouseArray = (a, b) => {
    const aStage = a.split(/ (.+)/)[0];
    const bStage = b.split(/ (.+)/)[0];
    const aAge = a.split(/ (.+)/)[1];
    const bAge = b.split(/ (.+)/)[1];
    let aNumerical = 0;
    let bNumerical = 0;
    if (aStage === 'embryonic') {
        aNumerical = 100;
    } else if (aStage === 'postnatal') {
        aNumerical = 1000;
    } else if (aStage === 'adult') {
        aNumerical = 10000;
    }
    if (aAge.includes('hours') && aAge.includes('-')) {
        aNumerical += +aAge.split('hours')[0].split('-')[1] / 24;
    } else if (aAge.includes('hours')) {
        aNumerical += +aAge.split('hours')[0] / 24;
    } else if (aAge.includes('days')) {
        aNumerical += +aAge.split('days')[0];
    } else if (aAge.includes('weeks')) {
        aNumerical += +aAge.split('weeks')[0] * 7;
    } else if (aAge.includes(' months')) {
        aNumerical += +bAge.split('months')[0] * 30;
    } else if (aAge.includes(' years')) {
        aNumerical += +aAge.split('years')[0] * 365;
    }
    if (bStage === 'embryonic') {
        bNumerical = 100;
    } else if (bStage === 'postnatal') {
        bNumerical = 1000;
    } else if (bStage === 'adult') {
        bNumerical = 10000;
    }
    if (bAge.includes('hours') && bAge.includes('-')) {
        bNumerical += +bAge.split('hours')[0].split('-')[1] / 24;
    } else if (bAge.includes('hours')) {
        bNumerical += +bAge.split('hours')[0] / 24;
    } else if (bAge.includes('days')) {
        bNumerical += +bAge.split('days')[0];
    } else if (bAge.includes(' weeks')) {
        bNumerical += +bAge.split('weeks')[0] * 7;
    } else if (bAge.includes(' months')) {
        bNumerical += +bAge.split('months')[0] * 30;
    } else if (bAge.includes(' years')) {
        bNumerical += +bAge.split('years')[0] * 365;
    }
    return aNumerical - bNumerical;
};

// Sort the rows of the matrix by stage (embryo -> postnatal -> adult) and then by age
function sortMouseAge(a, b) {
    const aNumerical = computeAgeComparator(a);
    const bNumerical = computeAgeComparator(b);
    return aNumerical - bNumerical;
}

function sortStage(a, b) {
    if (a.life_stage_age && b.life_stage_age) {
        return sortMouseArray(a.life_stage_age, b.life_stage_age);
    }
    // special case with multiple replicates (old data)
    if (a.replicates && b.replicates && a.replicates[0].library.biosample.age_display && b.replicates[0].library.biosample.age_display) {
        return (a.replicates[0].library.biosample.age_display.split(' ')[0] - b.replicates[0].library.biosample.age_display.split(' ')[0]);
    }
    if (a.replicates && a.replicates[0].library.biosample.age_display) {
        return -a.replicates[0].library.biosample.age_display.split(' ')[0];
    }
    if (b.replicates && b.replicates[0].library.biosample.age_display) {
        return b.replicates[0].library.biosample.age_display.split(' ')[0];
    }
    return 0;
}

const ElementsReferences = ({ reference }) => {
    // Render all examined_loci as links, and all examined_regions as text, and combine them
    // together for final rendering.
    const examinedLoci = (reference.examined_loci && reference.examined_loci.length > 0)
        ? reference.examined_loci.map((locus) => <a key={locus['@id']} href={locus['@id']}>{locus.symbol}</a>)
        : [];
    const examinedRegions = (reference.examined_regions && reference.examined_regions.length > 0)
        ? reference.examined_regions.map((region, i) => <span key={i}>{region.assembly} {region.chromosome}:{region.start}-{region.end}</span>)
        : [];
    const examinedAreas = examinedLoci.concat(examinedRegions);

    // Use the combined components to render to the page.
    if (examinedAreas.length > 0) {
        return (
            <>
                &nbsp;(
                {examinedAreas.map((examinedArea, i) => (
                    <React.Fragment key={i}>
                        {i > 0 ? ', ' : null}
                        {examinedArea}
                    </React.Fragment>
                ))}
                )
            </>
        );
    }
    return null;
};

ElementsReferences.propTypes = {
    reference: PropTypes.object.isRequired,
};


/**
 * Calculate a displayable life stage/age string from the biosamples in the given experiment.
 * @param {object} experiment The experiment to get the life stage/age from.
 * @returns {string} The life stage/age string.
 */
const computeLifeStageAge = (experiment) => {
    let biosamples = [];
    let lifeStageAge = [];

    // Collect all biosamples in all experiment replicates.
    if (experiment.replicates && experiment.replicates.length > 0) {
        biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample).filter((biosample) => !!biosample);
    }
    if (biosamples.length > 0) {
        biosamples.forEach((biosample) => {
            if (biosample.age_units === 'year') {
                lifeStageAge.push(biosample.age_display);
            } else if (biosample.life_stage && biosample.age_display) {
                lifeStageAge.push(`${biosample.life_stage} ${biosample.age_display}`);
            } else if (biosample.life_stage) {
                lifeStageAge.push(biosample.life_stage);
            } else if (biosample.age_display) {
                lifeStageAge.push(biosample.age_display);
            }
        });
    }
    lifeStageAge = [...new Set(lifeStageAge)];
    return lifeStageAge.length > 0 ? lifeStageAge.join(', ') : 'unknown';
};


const organismDevelopmentSeriesTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    target: seriesTableTargetColumn,

    life_stage_age: {
        title: (experiments) => {
            let ageUnits = [];
            experiments.forEach((experiment) => {
                let biosamples;
                if (experiment.replicates && experiment.replicates.length > 0) {
                    biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample).filter((biosample) => !!biosample);
                }
                if (biosamples && biosamples.length > 0) {
                    ageUnits = [...ageUnits, ...biosamples.map((b) => b.age_units)];
                }
            });
            const uniqueAgeUnits = [...new Set(ageUnits)];
            const biosampleOneStage = (uniqueAgeUnits.length === 1) && (uniqueAgeUnits[0] === 'year');
            if (biosampleOneStage) {
                return 'Age';
            }
            return 'Stage';
        },
        display: (experiment) => {
            const lifeStageAge = computeLifeStageAge(experiment);
            return lifeStageAge ? <span>{lifeStageAge}</span> : 'unknown';
        },

        objSorter: (a, b) => sortStage(a, b),
    },

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (item) => (item.lab ? item.lab.title : null),
    },

    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },

    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};

function computeSynchBiosample(experiment) {
    let postSynch;
    let biosamples;
    let synchronizationBiosample;

    if (experiment.replicates && experiment.replicates.length > 0) {
        biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample).filter((biosample) => !!biosample);
    }
    if (biosamples && biosamples.length > 0) {
        synchronizationBiosample = biosamples.find((biosample) => biosample.synchronization);
        if (synchronizationBiosample && synchronizationBiosample.age_display && synchronizationBiosample.age_display.indexOf('-') > -1) {
            postSynch = synchronizationBiosample.age_display.split('-')[0];
        } else if (synchronizationBiosample && synchronizationBiosample.age_display) {
            postSynch = synchronizationBiosample.age_display.split(' ')[0];
        } else {
            return null;
        }
    }
    return postSynch;
}

function sortPostSynch(a, b) {
    const aPostSynch = computeSynchBiosample(a);
    const bPostSynch = computeSynchBiosample(b);
    if (aPostSynch && bPostSynch) {
        return (aPostSynch - bPostSynch);
    }
    return 0;
}

/**
 * Extract the first synchronization value from all the biosamples in the given dataset.
 * @param {object} dataset Dataset from which to extract a synchronization.
 * @returns {string} First synchronization value found in the dataset, or '' if none.
 */
const computeSynch = (dataset) => {
    const biosamples = collectDatasetBiosamples(dataset);
    const synchronizationBiosample = biosamples.find((biosample) => biosample.synchronization);
    return synchronizationBiosample ? synchronizationBiosample.synchronization : '';
};


const organismDevelopmentSeriesWormFlyTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    target: seriesTableTargetColumn,

    synch: {
        title: 'Synchronization',
        display: (experiment) => {
            const synch = computeSynch(experiment);
            return <span>{synch}</span>;
        },
        objSorter: (a, b) => {
            if (a.life_stage_age && b.life_stage_age) {
                return sortMouseAge(a.life_stage_age, b.life_stage_age);
            }
            return null;
        },
    },

    postsynchtime: {
        title: 'Post-synchronization time',
        display: (experiment) => {
            let biosamples;
            let synchronizationBiosample;

            if (experiment.replicates && experiment.replicates.length > 0) {
                biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample).filter((biosample) => !!biosample);
            }
            if (biosamples && biosamples.length > 0) {
                synchronizationBiosample = biosamples.find((biosample) => biosample.synchronization);
            }
            if (synchronizationBiosample) {
                return (
                    <span>{`${synchronizationBiosample.age_display}`}</span>
                );
            }
            return null;
        },
        objSorter: (a, b) => sortPostSynch(a, b),
    },

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (item) => (item.lab ? item.lab.title : null),
    },

    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },

    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};

const functionalCharacterizationSeriesTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    target: seriesTableTargetColumn,

    assay_term_name: {
        title: 'Assay',
    },

    examined_loci: {
        title: 'Examined loci',
        getValue: (experiment) => computeExaminedLoci(experiment),
    },

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (experiment) => (experiment.lab ? experiment.lab.title : null),

    },
    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },
    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};


/**
 * Generate a comma-separated string of expressed_genes from the given experiment's biosamples.
 */
const computeExpressedGenes = (dataset) => {
    // Render all expressed_genes as links.
    const biosamples = collectDatasetBiosamples(dataset);
    let geneList = [];
    biosamples.forEach((biosample) => {
        if (biosample.expressed_genes) {
            geneList = [...geneList, ...biosample.expressed_genes];
        }
    });
    geneList = _.uniq(geneList, (gene) => `${gene.gene.geneid}-${gene.expression_percentile}-${gene.expression_range_maximum}-${gene.expression_range_minimum}`);

    return (
        geneList.map((gene, geneIdx) => (
            <span key={`${gene.uuid}`}>
                {gene.gene.symbol}
                {gene.expression_percentile || gene.expression_percentile === 0 ?
                    <span> ({getNumberWithOrdinal(gene.expression_percentile)} percentile){((geneIdx + 1) < geneList.length && geneList.length > 1) ? ', ' : ''}</span>
                : null}
                {(gene.expression_range_maximum && gene.expression_range_minimum) || (gene.expression_range_maximum === 0 || gene.expression_range_minimum === 0) ?
                    <span> ({gene.expression_range_minimum}-{gene.expression_range_maximum}%){((geneIdx + 1) < geneList.length && geneList.length > 1) ? ', ' : ''}</span>
                : null}
            </span>
        ))
    );
};


const differentialAccessibilitySeriesTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    expressed_genes: {
        title: 'Sorted gene expression',
        getValue: (experiment) => computeExpressedGenes(experiment),
    },

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (experiment) => (experiment.lab ? experiment.lab.title : null),
    },

    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },

    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};


/**
 * Generate a comma-separated string of pulse-chase time durations from the given experiment's biosamples.
 * @param {object} experiment - The experiment to generate the pulse-chase durations from.
 * @returns {string} - A comma-separated string of pulse-chase durations.
 */
const computePulseDurations = (dataset) => {
    const biosamples = collectDatasetBiosamples(dataset);
    let pulseDurations = [];
    if (biosamples.length > 0) {
        biosamples.forEach((biosample) => {
            if (biosample.pulse_chase_time) {
                pulseDurations.push(`${biosample.pulse_chase_time} ${biosample.pulse_chase_time_units}${biosample.pulse_chase_time > 1 ? 's' : ''}`);
            }
        });
    }
    pulseDurations = _.uniq(pulseDurations);
    return pulseDurations.join(', ');
};

const pulseChaseTimeSeriesTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.isPrivileged || publicDataset(experiment) ?
                    <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>
                :
                    <span>{experiment.accession}</span>
                }
            </span>
        ),
    },

    pulseDuration: {
        title: 'Pulse-chase duration',
        getValue: (experiment) => computePulseDurations(experiment),
    },

    biosample_summary: {
        title: 'Biosample summary',
    },

    lab: {
        title: 'Lab',
        getValue: (experiment) => experiment?.lab.title,
    },

    status: {
        title: 'Status',
        display: (experiment) => <Status item={experiment} badgeSize="small" />,
    },

    cart: {
        title: 'Cart',
        display: (experiment) => <CartToggle element={experiment} />,
        sorter: false,
    },
};


/**
 * Collect released analyses from all the related datasets in the given Series object.
 * @param {object} context Series object
 * @return {array} All released analyses from all related datasets; empty if none
 */
const collectSeriesAnalyses = (context) => (
    context.related_datasets
        ? (
            context.related_datasets.reduce(
                (datasetAnalyses, dataset) => (
                    dataset.analyses
                        ? datasetAnalyses.concat(
                            dataset.analyses.filter(
                                (analysis) => analysis.status === 'released'
                            )
                        ) : datasetAnalyses
                ), []
            )
        ) : []
);


/**
 * Collect default files from all related datasets to the given Series object. This only includes
 * files also in the given array of analyses. If no analyses given, then just return all default
 * files.
 * @param {object} context Series object
 * @param {array} analyses Analyses from the related datasets of the Series object
 */
const collectSeriesFiles = (context, analyses) => {
    const analysesFilePaths = analyses.reduce((paths, analysis) => paths.concat(analysis.files), []);
    const isFunctionalCharacterizationSeries = globals.hasType(context, 'FunctionalCharacterizationSeries');
    const files = context.related_datasets
        ? (
            context.related_datasets.reduce(
                (datasetFiles, dataset) => (
                    datasetFiles.concat(
                        dataset.files.filter(
                            // If the analysis array has zero length, include all default files.
                            // Otherwise, include default files included in the given analyses.
                            (file) => (isFunctionalCharacterizationSeries || file.preferred_default) && (analysesFilePaths.length === 0 || analysesFilePaths.includes(file['@id']))
                        )
                    )
                ), []
            )
        ) : null;
    return files;
};


/**
 * Collect all the analyses and files from the related datasets of the given series object.
 * @param {object} context Series object
 * @return {object} arrays of qualified analyses and files
 */
const collectSeriesAnalysesAndFiles = (context) => {
    const analyses = collectSeriesAnalyses(context);
    const files = collectSeriesFiles(context, analyses);
    return { analyses, files };
};


/**
 * Build an object for the standard series breadcrumbs.
 * @param {object} context Series object that displays breadcrumbs
 * @param {string} seriesTitle Title of the series object
 * @returns Object suitable for <Breadcrumbs> component
 */
const composeSeriesBreadcrumbs = (context, seriesTitle) => {
    const datasetType = context['@type'][1];
    const seriesType = context['@type'][0];
    return [
        { id: 'Datasets' },
        { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
        { id: seriesTitle, uri: `/search/?type=${seriesType}`, wholeTip: `Search for ${seriesType}` },
    ];
};


/**
 * Build the mapping for supplementary short labels.
 * @param {array} experimentList Experiments from which to extract relevant label.
 * @param {function} getSupplementalShortLabel Function to extract the label from an experiment.
 */
const generateSupplementalShortLabels = (experimentList, getSupplementalShortLabel) => (
    experimentList.reduce((accLabels, experiment) => {
        const supplementalShortLabel = getSupplementalShortLabel(experiment);
        return { ...accLabels, [experiment['@id']]: supplementalShortLabel };
    }, {})
);


/**
 * Defines the number of experiments/control experiments that appear at once in the series dataset
 * table.
 */
const PAGE_DATASET_COUNT = 25;


/**
 * Display one of the two sections (experiments or control experiments) of the dataset table on the
 * Series pages.
 */
const SeriesDatasetTableSection = ({ title, datasets, tableColumns, sortColumn, isPrivileged, accessLevel }) => {
    /** The current page of datasets if more than the max number of displayable datasets exist */
    const [currentDatasetPage, setCurrentDatasetPage] = React.useState(0);

    /**
     * Called when the user clicks the pager to go to a new page of datasets.
     * @param {number} New current page number of datasets to display
     */
    const updateCurrentExperimentPage = (newPage) => {
        setCurrentDatasetPage(newPage);
    };

    const totalDatasetPageCount = Math.floor(datasets.length / PAGE_DATASET_COUNT) + (datasets.length % PAGE_DATASET_COUNT !== 0 ? 1 : 0);
    const pageStartIndex = currentDatasetPage * PAGE_DATASET_COUNT;
    const visibleDatasets = datasets.slice(pageStartIndex, pageStartIndex + PAGE_DATASET_COUNT);

    return (
        <>
            <div className="experiment-table__subheader">
                <>{title}s</>
                <div className="experiment-table__subheader-controls">
                    <CartAddAllElements elements={datasets} />
                    {totalDatasetPageCount > 1
                        ? (
                            <Pager.Simple
                                total={totalDatasetPageCount}
                                current={currentDatasetPage}
                                updateCurrentPage={updateCurrentExperimentPage}
                            />
                        )
                        : null
                    }
                </div>
            </div>
            <div className="table-counts">
                {datasets.length} {title.toLowerCase()}{datasets.length === 1 ? '' : 's'}
            </div>
            <SortTable
                list={visibleDatasets}
                columns={tableColumns}
                meta={{ isPrivileged, accessLevel }}
                sortColumn={sortColumn}
            />
        </>
    );
};

SeriesDatasetTableSection.propTypes = {
    /** Title to display in the section table header; non-plural */
    title: PropTypes.string.isRequired,
    /** Datasets to display in the table */
    datasets: PropTypes.array.isRequired,
    /** Table columns to display in the table */
    tableColumns: PropTypes.object.isRequired,
    /** ID of column to sort by; undefined/null for default */
    sortColumn: PropTypes.string,
    /** True if the user is a submitter or admin user */
    isPrivileged: PropTypes.bool.isRequired,
    /** User's access level */
    accessLevel: PropTypes.string.isRequired,
};

SeriesDatasetTableSection.defaultProps = {
    sortColumn: null,
};


/**
 * Displays a standard table of related experiments on Series pages. It can appear with one or two
 * sections; one containing related datasets and the other containing control experiments from the
 * related datasets.
 */
const SeriesExperimentTable = ({ context, experiments, title, tableColumns, sortColumn, isPrivileged, accessLevel }) => {
    if (experiments.length > 0) {
        // Get all the control experiments from the given experiments' `possible_controls`, `elements_mappings` and `elements_cloning`. Then
        // filter those out of the given experiments.
        const controls = _.uniq(experiments.reduce((accControls, experiment) => (experiment.possible_controls ? accControls.concat(experiment.possible_controls) : accControls), []), (control) => control['@id']);
        const elementsMappings = _.uniq(experiments.reduce((accMappings, experiment) => (experiment.elements_mappings ? accMappings.concat(experiment.elements_mappings) : accMappings), []), (mappings) => mappings['@id']);
        const elementsCloning = _.uniq(experiments.reduce((accCloning, experiment) => (experiment.elements_cloning ? accCloning.concat(experiment.elements_cloning) : accCloning), []), (cloning) => cloning['@id']);
        const combinedControls = [...controls, ...elementsMappings, ...elementsCloning];
        const experimentsWithoutControls = experiments.filter((experiment) => !combinedControls.find((control) => control['@id'] === experiment['@id']));

        return (
            <SortTablePanel
                header={
                    <div className="experiment-table__header">
                        <h4 className="experiment-table__title">{`Experiments in ${title.toLowerCase()} ${context.accession}`}</h4>
                    </div>
                }
            >
                <SeriesDatasetTableSection
                    title="Experiment"
                    datasets={experimentsWithoutControls}
                    tableColumns={tableColumns}
                    sortColumn={sortColumn}
                    isPrivileged={isPrivileged}
                    accessLevel={accessLevel}
                />
                {combinedControls.length > 0 ?
                    <SeriesDatasetTableSection
                        title="Control experiment"
                        datasets={combinedControls}
                        tableColumns={controlTableColumns}
                        isPrivileged={isPrivileged}
                        accessLevel={accessLevel}
                    />
                : null}
            </SortTablePanel>
        );
    }
    return null;
};

SeriesExperimentTable.propTypes = {
    /** Series context object */
    context: PropTypes.object.isRequired,
    /** Experiments to display */
    experiments: PropTypes.array.isRequired,
    /** Title of series */
    title: PropTypes.string.isRequired,
    /** Columns for experiment portion of table */
    tableColumns: PropTypes.object.isRequired,
    /** ID of column to sort by; undefined/null for default */
    sortColumn: PropTypes.string,
    /** True if the user is a submitter or admin user */
    isPrivileged: PropTypes.bool.isRequired,
    /** User's access level */
    accessLevel: PropTypes.string.isRequired,
};

SeriesExperimentTable.defaultProps = {
    sortColumn: null,
};


/**
 * Displays the common elements of all Series-derived pages. This must get called from wrappers
 * specific to each type of Series-derived object.
 */
export const SeriesComponent = ({
    context,
    title,
    tableColumns,
    sortColumn,
    breadcrumbs,
    options,
    auditIndicators,
    auditDetail,
}, reactContext) => {
    // File objects from all related series
    const [relatedSeriesFiles, setRelatedSeriesFiles] = React.useState([]);

    const itemClass = globals.itemClass(context, 'view-item');
    const experimentsUrl = `/search/?type=Experiment&possible_controls.accession=${context.accession}`;
    const seriesType = context['@type'][0];
    const userRoles = new UserRoles(reactContext.session_properties);
    const accessLevel = sessionToAccessLevel(reactContext.session, reactContext.session_properties);
    const { isLoggedIn } = userRoles;

    // Collect all the default files from all the related datasets of the given Series object,
    // filtered by the files in the released analyses of the related datasets, if any.
    const { analyses, files } = collectSeriesAnalysesAndFiles(context);

    // Build up array of documents attached to this dataset
    const datasetDocuments = (context.documents && context.documents.length > 0) ? context.documents : [];

    // Set up the breadcrumbs, either specific to a series type or the default ones.
    const displayedBreadCrumbs = breadcrumbs || composeSeriesBreadcrumbs(context, title);

    // Get a list of reference links, if any
    const references = pubReferenceList(context.references);

    // Calculate the donor diversity.
    const diversity = options.suppressDonorDiversity ? null : donorDiversity(context);

    // Fetch all the `related_series` objects in this Series object, and then collect all their
    // file objects into the `relatedSeriesFiles` state. Add these to the files from the series.
    React.useEffect(() => {
        if (context.related_series?.length > 0) {
            requestObjects(context.related_series, '/search/?type=AggregateSeries&limit=all&status!=deleted&status!=revoked&status!=replaced&field=files&field=analyses').then((results) => {
                if (results.length > 0) {
                    const relatedFiles = results.reduce((allFiles, relatedSeries) => (
                        (relatedSeries.files.length > 0) ? allFiles.concat(relatedSeries.files) : allFiles
                    ), []);
                    setRelatedSeriesFiles(relatedFiles);
                }
            });
        }
    }, [isLoggedIn]);
    files.push(...relatedSeriesFiles);

    // Calculate expressed genes
    let genes = [];
    context.related_datasets.forEach((dataset) => {
        if (dataset.replicates) {
            dataset.replicates.forEach((replicate) => {
                if (replicate && replicate.library && replicate.library.biosample && replicate.library.biosample.expressed_genes) {
                    genes.push(...replicate.library.biosample.expressed_genes);
                }
            });
        }
    });
    genes = _.uniq(genes, (gene) => gene.gene.geneid);

    // Collect CRISPR screen tiling modality for FunctionalCharacterizationExperiment only.
    let tilingModality = [];
    if (seriesType === 'FunctionalCharacterizationSeries') {
        if (context.elements_references && context.elements_references.length > 0) {
            context.elements_references.forEach((er) => {
                if (er.crispr_screen_tiling) {
                    tilingModality.push(er.crispr_screen_tiling);
                }
            });
            tilingModality = _.uniq(tilingModality);
        }
    }

    // Filter out any datasets we shouldn't see.
    const experimentList = context.related_datasets.filter((dataset) => dataset.status !== 'revoked' && dataset.status !== 'replaced' && dataset.status !== 'deleted');

    // Get list of target labels
    let targets;
    if (context.target) {
        targets = [...new Set(context.target.map((target) => target.label))];
    }

    const supplementalShortLabels = options.getSupplementalShortLabel
        ? generateSupplementalShortLabels(experimentList, options.getSupplementalShortLabel)
        : null;

    // As of code-time, there is a chance disease term names across biosamples could be different. So
    // the code takes this into account
    const diseases = [
        ...new Set(context.related_datasets.reduce((accumulatedDiseases, currentRelatedDataset) => {
            const diseasesTermNames = currentRelatedDataset.replicates
                ? currentRelatedDataset.replicates.map((replicate) => {
                    if (typeof replicate !== 'string') {
                        return replicate.library?.biosample?.disease_term_name;
                    }
                    return null;
                })
                : [];
            return accumulatedDiseases.concat(...diseasesTermNames);
        }, [])),
    ].filter((disease) => disease);

    return (
        <div className={itemClass}>
            <header>
                <TopAccessories context={context} crumbs={displayedBreadCrumbs} removeConfirmation={{ immediate: true }} />
                <h1>Summary for {title.toLowerCase()} {context.accession}</h1>
                <DoiRef context={context} />
                <ReplacementAccessions context={context} />
                <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'series-audit' }} hasCartControls />
            </header>
            {auditDetail(context.audit, 'series-audit', { session: reactContext.session, sessionProperties: reactContext.session_properties, except: context['@id'] })}
            <Panel>
                <PanelBody addClasses="panel__split">
                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--series">
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

                            {diversity ?
                                <div data-test="donordiversity">
                                    <dt>Donor diversity</dt>
                                    <dd>{diversity}</dd>
                                </div>
                            : null}

                            {context.assay_term_name && context.assay_term_name.length > 0 ?
                                <div data-test="description">
                                    <dt>Assay</dt>
                                    <dd>{context.assay_term_name.join(', ')}</dd>
                                </div>
                            : null}

                            {targets && targets.length > 0 ?
                                <div data-test="description">
                                    <dt>Target</dt>
                                    <dd>{targets.join(', ')}</dd>
                                </div>
                            : null}

                            {context.biosample_summary ?
                                <div data-test="biosamplesummary">
                                    <dt>Biosample summary</dt>
                                    <dd>
                                        {context.biosample_summary ? <span>{context.biosample_summary} </span> : null}
                                    </dd>
                                </div>
                            : null}

                            <div data-test="diseasetermname">
                                <dt>Disease{diseases && diseases.length !== 1 ? 's' : ''}</dt>
                                <dd>{diseases && diseases.length > 0 ? diseases.join(', ') : 'Not reported'}</dd>
                            </div>

                            {genes && genes.length > 0 ?
                                <div data-test="geneexpression">
                                    <dt>Sorted gene expression</dt>
                                    <dd>
                                        {genes.map((gene, geneIdx) => (
                                            <span>
                                                <a href={gene.gene['@id']}>{gene.gene.symbol}</a>
                                                {genes.length > 1 && (geneIdx + 1) < genes.length ? ', ' : ''}
                                            </span>
                                        ))}
                                    </dd>
                                </div>
                            : null}

                            {context.treatment_term_name && context.treatment_term_name.length > 0 ?
                                <div data-test="treatmenttermname">
                                    <dt>Treatment{context.treatment_term_name.length > 0 ? 's' : ''}</dt>
                                    <dd>
                                        {options.Treatments
                                            ? <>{options.Treatments}</>
                                            : <>{context.treatment_term_name.join(', ')}</>
                                        }
                                    </dd>
                                </div>
                            : null}

                            {context.elements_references && context.elements_references.length > 0 ?
                                <div data-test="elements-references">
                                    <dt>Elements references</dt>
                                    <dd>
                                        <ul>
                                            {context.elements_references.map((reference) => (
                                                <li key={reference.uuid}>
                                                    <a className="stacked-link" href={reference['@id']}>{reference.accession}</a>
                                                    <ElementsReferences reference={reference} />
                                                </li>
                                            ))}
                                        </ul>
                                    </dd>
                                </div>
                            : null}

                            {tilingModality.length > 0 ?
                                <div data-test="crisprscreentiling">
                                    <dt>Tiling modality</dt>
                                    <dd>{tilingModality.join(', ')}</dd>
                                </div>
                            : null}

                        </dl>
                    </div>

                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--series">
                            <h4>Attribution</h4>
                            <ProjectBadge award={context.award} addClasses="badge-heading" />
                        </div>
                        <dl className="key-value">
                            <div data-test="lab">
                                <dt>Lab</dt>
                                <dd>{context.lab.title}</dd>
                            </div>

                            <AwardRef context={context} adminUser={userRoles.isAdmin} />

                            <div data-test="project">
                                <dt>Project</dt>
                                <dd>{context.award.project}</dd>
                            </div>

                            {context.aliases.length > 0 ?
                                <div data-test="aliases">
                                    <dt>Aliases</dt>
                                    <dd>{context.aliases.join(', ')}</dd>
                                </div>
                            : null}

                            <div data-test="externalresources">
                                <dt>External resources</dt>
                                <dd>
                                    {context.dbxrefs && context.dbxrefs.length > 0 ?
                                        <DbxrefList context={context} dbxrefs={context.dbxrefs} />
                                    : <em>None submitted</em> }
                                </dd>
                            </div>

                            {references ?
                                <div data-test="references">
                                    <dt>References</dt>
                                    <dd>{references}</dd>
                                </div>
                            : null}

                            {context.submitter_comment ?
                                <div data-test="submittercomment">
                                    <dt>Submitter comment</dt>
                                    <dd>{context.submitter_comment}</dd>
                                </div>
                            : null}

                            {context.internal_tags && context.internal_tags.length > 0 ?
                                <div className="tag-badges" data-test="tags">
                                    <dt>Tags</dt>
                                    <dd><InternalTags internalTags={context.internal_tags} objectType={context['@type'][0]} /></dd>
                                </div>
                            : null}

                            {options.inputDataHeader
                                && (context.related_datasets || context.related_series) ?
                                <div className="panel__split-heading panel__split-heading--experiment">
                                    <h4>Input Datasets</h4>
                                </div>
                            : null}

                            {options.relatedDatasetsInAttribution
                                && context.related_datasets
                                && context.related_datasets.length > 0 ?
                                <div data-test="related_datasets">
                                    <dt>Related datasets</dt>
                                    <dd>
                                        <ul>
                                            {context.related_datasets.map((dataset) => (
                                                <li key={dataset['@id']} className="multi-comma">
                                                    <a href={dataset['@id']}>
                                                        {dataset.accession}
                                                    </a>
                                                </li>
                                            ))}
                                        </ul>
                                    </dd>
                                </div>
                            : null}

                            {options.relatedSeriesInAttribution
                                && context.related_series
                                && context.related_series.length > 0 ?
                                <div data-test="related_series">
                                    <dt>Related series</dt>
                                    <dd>
                                        <ul>
                                            {context.related_series.map((series) => (
                                                <li key={series} className="multi-comma">
                                                    <a href={series}>
                                                        {globals.atIdToAccession(series)}
                                                    </a>
                                                </li>
                                            ))}
                                        </ul>
                                    </dd>
                                </div>
                            : null}
                        </dl>
                    </div>
                </PanelBody>
            </Panel>
            {options.ExperimentTable || (
                <SeriesExperimentTable
                    context={context}
                    experiments={experimentList}
                    title={title}
                    tableColumns={tableColumns}
                    sortColumn={sortColumn}
                    isPrivileged={userRoles.isPrivileged}
                    accessLevel={accessLevel}
                />
            )}

            {/* Display list of released and unreleased files */}
            {/* Set hideGraph to false to show "Association Graph" for all series */}
            {files.length > 0 || context.elements_references?.length > 0 ?
                <FileGallery
                    context={context}
                    files={files}
                    analyses={analyses}
                    fileQueryKey="series_files"
                    supplementalShortLabels={supplementalShortLabels}
                    showReplicateNumber={false}
                    hideControls={!METADATA_SERIES_TYPES.includes(context['@type'][0])}
                    hideGraph={!SERIES_WITH_VISIBLE_FILE_GRAPHS.includes(seriesType)}
                    showDetailedTracks
                    hideAnalysisSelector
                    defaultOnly
                    relatedDatasets={experimentList}
                    cloningMappingsFiles={{
                        cloning: options.seriesCloningDatasetsAndFiles,
                        mappings: options.seriesMappingsDatasetsAndFiles,
                    }}
                />
            : null}

            <FetchedItems context={context} url={experimentsUrl} Component={ControllingExperiments} />

            <DocumentsPanelReq documents={datasetDocuments} />
        </div>
    );
};

SeriesComponent.propTypes = {
    /** Series object to display */
    context: PropTypes.object.isRequired,
    /** Series-dependent title */
    title: PropTypes.string.isRequired,
    /** Series-dependent experiment table columns */
    tableColumns: PropTypes.object,
    /** ID of column to sort by; undefined/null for default */
    sortColumn: PropTypes.string,
    /** Breadcrumbs to display if not default */
    breadcrumbs: PropTypes.array,
    /** Series-dependent options */
    options: PropTypes.exact({
        /** React component to display specialized treatments */
        Treatments: PropTypes.node,
        /** React component to display the experiment table, overriding the default */
        ExperimentTable: PropTypes.node,
        /** elements_cloning files and assemblies organized by dataset */
        seriesCloningDatasetsAndFiles: PropTypes.arrayOf(PropTypes.object),
        /** elements_mappings files organized by dataset */
        seriesMappingsDatasetsAndFiles: PropTypes.arrayOf(PropTypes.object),
        /** True to suppress the calculation and display of donor diversity */
        suppressDonorDiversity: PropTypes.bool,
        /** Retrieves short label from an experiment */
        getSupplementalShortLabel: PropTypes.func,
        /** True to suppress the calculation and display of related_datasets */
        relatedDatasetsInAttribution: PropTypes.bool,
        /** True to suppress the calculation and display of related_series */
        relatedSeriesInAttribution: PropTypes.bool,
        /** True to supress the display of input data header */
        inputDataHeader: PropTypes.bool,
    }),
    /** Audit decorator function */
    auditIndicators: PropTypes.func.isRequired,
    /** Audit decorator function */
    auditDetail: PropTypes.func.isRequired,
};

SeriesComponent.defaultProps = {
    tableColumns: null,
    sortColumn: null,
    breadcrumbs: null,
    options: {},
};

SeriesComponent.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
    profilesTitles: PropTypes.object,
};

const Series = auditDecor(SeriesComponent);


/**
 * Wrapper component for those Series objects that have the standard Series display.
 */
const StandardSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={basicTableColumns}
        />
    );
};

StandardSeries.propTypes = {
    /** Series-derived object */
    context: PropTypes.object.isRequired,
};

StandardSeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(StandardSeries, 'CollectionSeries');
globals.contentViews.register(StandardSeries, 'MatchedSet');
globals.contentViews.register(StandardSeries, 'MultiomicsSeries');


/**
 * Wrapper component for AggregateSeries objects.
 */
const AggregateSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    return (
        <Series
            context={context}
            title={seriesTitle}
            options={{ relatedDatasetsInAttribution: true, relatedSeriesInAttribution: true, inputDataHeader: true }}
            tableColumns={basicTableColumns}
        />
    );
};

AggregateSeries.propTypes = {
    /** Series-derived object */
    context: PropTypes.object.isRequired,
};

AggregateSeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(AggregateSeries, 'AggregateSeries');


/**
 * Composes the breadcrumbs for the various function genomics series objects.
 * @param {object} context Series-derived object
 * @param {*} seriesTitle Title of this series-derived object
 * @returns {object} For the <Breadcrumbs> component
 */
const composeFunctionalGenomicsSeriesBreadcrumbs = (context, seriesTitle) => {
    const seriesType = context['@type'][0];
    return [
        { id: 'Datasets' },
        { id: seriesTitle, uri: `/series-search/?type=${seriesType}`, wholeTip: `Search for ${seriesType}` },
    ];
};


/**
 * Wrapper component for the different functional genomics series objects.
 */
const FunctionalGenomicsSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={geneSilencingSeriesTableColumns}
            breadcrumbs={composeFunctionalGenomicsSeriesBreadcrumbs(context, seriesTitle)}
        />
    );
};

FunctionalGenomicsSeries.propTypes = {
    /** Functional genomics series-derived object */
    context: PropTypes.object.isRequired,
};

FunctionalGenomicsSeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(FunctionalGenomicsSeries, 'GeneSilencingSeries');
globals.contentViews.register(FunctionalGenomicsSeries, 'ReplicationTimingSeries');


/**
 * Displays a table of related experiments on DiseaseSeries pages. It can appear with one or two
 * sections; one containing experiments without disease and the other containing experiments with
 * one or more diseases.
 */
const DiseaseExperimentTable = ({ datasetsByDisease, title, accession, isPrivileged }) => {
    // Combine all datasets with biosamples that have disease terms into one array.
    const diseaseTerms = Object.keys(datasetsByDisease).filter((term) => term !== 'None');
    const diseaseDatasets = diseaseTerms.reduce((allDiseaseDatasets, term) => (
        allDiseaseDatasets.concat(datasetsByDisease[term])
    ), []);

    // Get the datasets without disease biosamples, if any.
    const noDiseaseDatasets = datasetsByDisease.None || [];

    // For the disease dataset table, determine the disease name to use, or "Disease" if more than
    // one.
    const diseaseTerm = diseaseTerms.length === 1 ? diseaseTerms[0] : 'Disease';

    const totalDatasetsLength = diseaseDatasets.length + noDiseaseDatasets.length;
    if (totalDatasetsLength > 0) {
        return (
            <SortTablePanel
                header={
                    <div className="experiment-table__header">
                        <h4 className="experiment-table__title">{`Experiments in ${title.toLowerCase()} ${accession}`}</h4>
                    </div>
                }
                subheader={
                    <div className="table-counts">
                        {totalDatasetsLength} experiment{totalDatasetsLength === 1 ? '' : 's'}
                    </div>
                }
            >
                {diseaseDatasets.length > 0 ?
                    <>
                        <div className="experiment-table__subheader">
                            {`${diseaseTerm.uppercaseFirstChar()} samples in series`}
                            <CartAddAllElements elements={diseaseDatasets} />
                        </div>
                        <SortTable
                            list={diseaseDatasets}
                            columns={diseaseSeriesColumns}
                            meta={{ isPrivileged }}
                        />
                    </>
                : null}
                {noDiseaseDatasets.length > 0 ?
                    <>
                        <div className="experiment-table__subheader">
                            Non-diseased experiments in series
                            <CartAddAllElements elements={noDiseaseDatasets} />
                        </div>
                        <SortTable
                            list={noDiseaseDatasets}
                            columns={basicTableColumns}
                            meta={{ isPrivileged }}
                        />
                    </>
                : null}
            </SortTablePanel>
        );
    }
    return null;
};

DiseaseExperimentTable.propTypes = {
    /** Arrays of datasets with corresponding diseases as keys */
    datasetsByDisease: PropTypes.object.isRequired,
    /** Title of series */
    title: PropTypes.string.isRequired,
    /** Accession of series object */
    accession: PropTypes.string.isRequired,
    /** True if logged-in user is a submitter or admin */
    isPrivileged: PropTypes.bool.isRequired,
};


/**
 * Groups the given datasets by the `disease_term_name` in their biosamples. Any datasets with no
 * such biosamples get listed under the key "None." Any datasets with biosamples with a mix of
 * different `disease_term_name` values -- including those biosamples with more than one value --
 * get listed under the key "Disease." An example:
 * {
 *     'Alzheimer's disease': [datasets where all biosamples specify Alzheimer's]
 *     'Disease': [datasets with a mix of biosample diseases]
 *     'None': [datasets with no disease biosamples]
 * }
 * @param {array} datasets Datasets to group by biosample `disease_term_name`.
 * @returns {object} Arrays of datasets keyed by common disease terms.
 */
const groupDatasetsByDisease = (datasets) => (
    _(datasets).groupBy((dataset) => {
        const relatedDatasetBiosamples = collectDatasetBiosamples(dataset);
        if (relatedDatasetBiosamples.length > 0) {
            // Look for the first biosample in the dataset that contains a filled
            // `disease_term_name` property.
            const firstDiseaseBiosample = relatedDatasetBiosamples.find((biosample) => biosample.disease_term_name && biosample.disease_term_name.length > 0);
            if (firstDiseaseBiosample) {
                // See if all biosamples in the dataset have a single `disease_term_name` value
                // matching the first one we found, guaranteeing all biosamples in the dataset
                // specify the same disease.
                const firstDiseaseTerm = firstDiseaseBiosample.disease_term_name[0] || 'None';
                const isHomogeneous = relatedDatasetBiosamples.every((biosample) => (
                    biosample.disease_term_name.length === 1 && biosample.disease_term_name[0] === firstDiseaseTerm
                ));
                return isHomogeneous ? firstDiseaseTerm : 'Disease';
            }
        }

        // No biosamples in the related dataset, so use disease "None."
        return 'None';
    })
);


/**
 * Wrapper component for DiseaseSeries pages.
 */
const DiseaseSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';
    const userRoles = new UserRoles(reactContext.session_properties);

    // Group the datasets that include at least one biosample with `disease_term_name` by disease.
    const datasetsByDisease = groupDatasetsByDisease(context.related_datasets);

    return (
        <Series
            context={context}
            title={seriesTitle}
            breadcrumbs={composeSeriesBreadcrumbs(context, seriesTitle)}
            options={{
                ExperimentTable: (
                    <DiseaseExperimentTable
                        datasetsByDisease={datasetsByDisease}
                        title={seriesTitle}
                        accession={context.accession}
                        isPrivileged={userRoles.isPrivileged}
                    />
                ),
                getSupplementalShortLabel: (dataset) => computeDiseases(dataset),
            }}
        />
    );
};

DiseaseSeries.propTypes = {
    /** Disease series object */
    context: PropTypes.object.isRequired,
};

DiseaseSeries.contextTypes = {
    session_properties: PropTypes.object,
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(DiseaseSeries, 'DiseaseSeries');


/**
 * The given array of cloning or mappings datasets get mapped to an array of each of these datasets
 * along with their assemblies and default files. Datasets with analyses restrict the files to
 * those they contain.
 * @param {array} datasets Cloning or mappings datasets to map to their files and assemblies
 * @param {array} allFiles File objects from all cloning and mappings datasets
 * @returns {array} Objects with given datasets and corresponding assemblies and files
 */
const collectCloningAndMappings = (datasets, allFiles) => (
    datasets.map((dataset) => {
        let assemblies = dataset.assembly || [];
        let files = [];
        if (dataset.analyses?.length > 0) {
            // Get the file objects for the dataset's analyses' files.
            const analysisFilesPaths = dataset.analyses.reduce((accFiles, analysis) => accFiles.concat(analysis.files), []);
            const cloningAndAnalysisFilePaths = _.intersection(dataset.files, analysisFilesPaths);
            files = cloningAndAnalysisFilePaths
                .map((filePath) => allFiles.find((file) => file['@id'] === filePath))
                .filter((file) => file);

            // Get the cloning dataset's analyses' assemblies.
            assemblies = dataset.analyses.reduce((accAssemblies, analysis) => (analysis.assembly ? accAssemblies.concat(analysis.assembly) : accAssemblies), []);
        } else {
            // No analyses, so get all the dataset's file objects.
            files = dataset.files
                .map((filePath) => allFiles.find((file) => file['@id'] === filePath))
                .filter((file) => file);
        }

        // Add to an array of these objects with the cloning or mappings dataset, its assemblies,
        // and its file objects.
        return {
            dataset,
            assemblies,
            files,
        };
    })
);


/**
 * Retrieve all `elements_cloning` and `elements_mappings` files from all `related_datasets` in the
 * given `context`.
 * @param {object} series Series object for the current page
 * @returns {object} cloning and mappings dataset @ids and their respective file objects
 */
const retrieveCloningAndMappingsFiles = async (series) => {
    // Collect all the `elements_cloning` datasets from the series' `related_datasets`.
    let cloningDatasets = series.related_datasets.reduce((accRelatedDatasets, relatedDataset) => (
        relatedDataset.elements_cloning
            ? accRelatedDatasets.concat(relatedDataset.elements_cloning)
            : accRelatedDatasets
    ), []);
    cloningDatasets = _(cloningDatasets).uniq((dataset) => dataset['@id']);

    // Collect all the `elements_mappings` datasets from the series' `related_datasets`.
    let mappingsDatasets = series.related_datasets.reduce((accRelatedDatasets, relatedDataset) => (
        relatedDataset.elements_mappings
            ? accRelatedDatasets.concat(relatedDataset.elements_mappings)
            : accRelatedDatasets
    ), []);
    mappingsDatasets = _(mappingsDatasets).uniq((dataset) => dataset['@id']);

    // Get the paths of all `elements_cloning` files.
    let allFilePaths = cloningDatasets.reduce((filePaths, cloningDataset) => (
        new Set([...filePaths, ...cloningDataset.files])
    ), new Set());

    // Add to these all the `elements_mappings` files.
    allFilePaths = mappingsDatasets.reduce((filePaths, mappingsDataset) => (
        new Set([...filePaths, ...mappingsDataset.files])
    ), allFilePaths);

    // Retrieve all default file objects collected above from the server.
    let allFiles = [];
    if (allFilePaths) {
        allFiles = await requestObjects(
            [...allFilePaths], '/search/?type=File&limit=all&status!=deleted&status!=revoked&status!=replaced'
        );
    }

    // Make an array of objects containing each `elements_cloning` dataset, its assemblies, and its
    // default files included in the dataset's analyses, or all its default files if the dataset
    // has no analyses. We don't have to de-duplicate the file paths because we just use them to
    // check for inclusion.
    const cloningDatasetsAndFiles = collectCloningAndMappings(cloningDatasets, allFiles);
    const mappingsDatasetsAndFiles = collectCloningAndMappings(mappingsDatasets, allFiles);

    return { cloningDatasetsAndFiles, mappingsDatasetsAndFiles };
};


/**
 * Wrapper component for functional characterization series pages.
 */
const FunctionalCharacterizationSeries = ({ context }, reactContext) => {
    /** elements_cloning files organized by their dataset */
    const [seriesCloningDatasetsAndFiles, setSeriesCloningDatasetsAndFiles] = React.useState(null);
    /** elements_mappings files organized by their dataset */
    const [seriesMappingsDatasetsAndFiles, setSeriesMappingsDatasetsAndFiles] = React.useState(null);

    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    useMount(() => {
        // Retrieve all `elements_cloning` and `elements_mappings` files from all related datasets
        // and set their respective states once they arrive from the server.
        retrieveCloningAndMappingsFiles(context).then(({ cloningDatasetsAndFiles, mappingsDatasetsAndFiles }) => {
            setSeriesCloningDatasetsAndFiles(cloningDatasetsAndFiles);
            setSeriesMappingsDatasetsAndFiles(mappingsDatasetsAndFiles);
        });
    });

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={functionalCharacterizationSeriesTableColumns}
            sortColumn="examined_loci"
            breadcrumbs={composeSeriesBreadcrumbs(context, seriesTitle)}
            options={{
                getSupplementalShortLabel: (dataset) => computeExaminedLoci(dataset),
                seriesCloningDatasetsAndFiles,
                seriesMappingsDatasetsAndFiles,
            }}
        />
    );
};

FunctionalCharacterizationSeries.propTypes = {
    /** Functional characterization series object */
    context: PropTypes.object.isRequired,
};

FunctionalCharacterizationSeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(FunctionalCharacterizationSeries, 'FunctionalCharacterizationSeries');


/**
 * Wrapper component for organism development series pages.
 */
const OrganismDevelopmentSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    // Determine which table columns to display based on the organism type associated with this
    // series object.
    let isFlyOrWorm = false;
    const hasOrganism = context.organism && context.organism.length > 0;
    if (hasOrganism) {
        const organism = context.organism[0].scientific_name;
        isFlyOrWorm = organism === 'Caenorhabditis elegans' || organism === 'Drosophila melanogaster';
    }

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={isFlyOrWorm ? organismDevelopmentSeriesWormFlyTableColumns : organismDevelopmentSeriesTableColumns}
            sortColumn={isFlyOrWorm ? 'synch' : 'life_stage_age'}
            options={{
                getSupplementalShortLabel: (dataset) => (isFlyOrWorm ? computeSynch(dataset) : computeLifeStageAge(dataset)),
            }}
            breadcrumbs={composeFunctionalGenomicsSeriesBreadcrumbs(context, seriesTitle)}
        />
    );
};

OrganismDevelopmentSeries.propTypes = {
    /** Organism development series object */
    context: PropTypes.object.isRequired,
};

OrganismDevelopmentSeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(OrganismDevelopmentSeries, 'OrganismDevelopmentSeries');


/**
 * Extracts all donors from all biosamples in the given dataset, and produce a comma-separated
 * string of donor accessions.
 * @param {object} dataset Dataset object from which to extract donors
 * @returns {string} Comma-separated string of donor accessions
 */
const computeDonorsAccessions = (dataset) => {
    const biosamples = collectDatasetBiosamples(dataset);
    if (biosamples.length > 0) {
        const allDonors = collectDonorsFromBiosamples(biosamples);
        if (allDonors.length > 0) {
            return allDonors.map((donor) => donor.accession).join(', ');
        }
    }
    return '';
};


/**
 * Wrapper component for reference epigenome pages.
 */
const ReferenceEpigenomeSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={referenceEpigenomeColumns}
            sortColumn="donors"
            options={{
                getSupplementalShortLabel: (dataset) => computeDonorsAccessions(dataset),
            }}
        />
    );
};

ReferenceEpigenomeSeries.propTypes = {
    /** Series-derived object */
    context: PropTypes.object.isRequired,
};

ReferenceEpigenomeSeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(ReferenceEpigenomeSeries, 'ReferenceEpigenome');


/**
 * Wrapper component for replication timing series pages.
 */
const ReplicationTimingSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={replicationTimingSeriesTableColumns}
            sortColumn="phase"
            options={{
                getSupplementalShortLabel: (dataset) => computePhase(dataset),
            }}
            breadcrumbs={composeFunctionalGenomicsSeriesBreadcrumbs(context, seriesTitle)}
        />
    );
};

ReplicationTimingSeries.propTypes = {
    /** Replication timing series object */
    context: PropTypes.object.isRequired,
};

ReplicationTimingSeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(ReplicationTimingSeries, 'ReplicationTimingSeries');


/**
 * Wrapper component for differentiation series pages.
 */
const DifferentiationSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';
    const findDifferentiations = context.related_datasets.map((dataset) => (computeDifferentiation(dataset) ? 1 : 0)).reduce((a, b) => a + b, 0);
    const differentiationTableColumns = findDifferentiations > 0 ? differentiationTableColumnsWithTime : differentiationTableColumnsWithoutTime;

    const options = {
        getSupplementalShortLabel: (dataset) => dataset.biosample_ontology.term_name,
    };
    if (context.treatment_term_name) {
        options.Treatments = <>{context.treatment_term_name.join(', ')}</>;
    }

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={differentiationTableColumns}
            options={options}
            breadcrumbs={composeFunctionalGenomicsSeriesBreadcrumbs(context, seriesTitle)}
        />
    );
};

DifferentiationSeries.propTypes = {
    /** Replication timing series object */
    context: PropTypes.object.isRequired,
};

DifferentiationSeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(DifferentiationSeries, 'DifferentiationSeries');


/**
 * Wrapper component for single-cell RNA series pages.
 */
const SingleCellRnaSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={basicTableColumns}
            breadcrumbs={composeSeriesBreadcrumbs(context, seriesTitle)}
            options={{
                suppressDonorDiversity: true,
            }}
        />
    );
};

SingleCellRnaSeries.propTypes = {
    /** Single-cell RNA series object */
    context: PropTypes.object.isRequired,
};

SingleCellRnaSeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(SingleCellRnaSeries, 'SingleCellRnaSeries');


/**
 * Wrapper component for treatment concentration series pages.
 */
const TreatmentConcentrationSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    // Build an array of treatment duration display strings from the biosample treatments of the
    // related datasets.
    const treatmentDurations = context.related_datasets.reduce((accTreatmentDurations, relatedDataset) => {
        // Collect any biosamples found in all related datasets.
        const biosamples = relatedDataset.replicates?.reduce((accBiosamples, replicate) => {
            const biosample = replicate.library && replicate.library.biosample;
            return biosample ? accBiosamples.concat(biosample) : accBiosamples;
        }, []);

        // Collect durations in the biosample treatments and compose them into displayable strings.
        const collectedDurations = biosamples?.reduce((accCollectedDurations, biosample) => {
            const durations = biosample.treatments.reduce((accDurations, treatment) => (
                treatment.duration
                    ? accDurations.concat(`${treatment.duration} ${treatment.duration_units}${treatment.duration > 1 ? 's' : ''}`)
                    : accDurations
            ), []);
            return accCollectedDurations.concat(durations);
        }, []);

        return [...new Set(collectedDurations ? accTreatmentDurations.concat(collectedDurations) : accTreatmentDurations)];
    }, []);

    const options = {
        getSupplementalShortLabel: (dataset) => computeConcentration(dataset),
    };
    if (treatmentDurations.length > 0) {
        options.Treatments = <>{context.treatment_term_name} for {treatmentDurations.join(', ')}</>;
    }

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={treatmentSeriesTableColumns}
            sortColumn="concentration"
            breadcrumbs={composeFunctionalGenomicsSeriesBreadcrumbs(context, seriesTitle)}
            options={options}
        />
    );
};

TreatmentConcentrationSeries.propTypes = {
    /** Treatment concentration series object */
    context: PropTypes.object.isRequired,
};

TreatmentConcentrationSeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(TreatmentConcentrationSeries, 'TreatmentConcentrationSeries');


/**
 * Collect all the treatments from all the biosamples in the given datasets.
 * @param {array} datasets The datasets to collect treatments from.
 * @returns {array} The collected treatments, de-duplicated.
 */
const collectTreatmentAmounts = (datasets) => {
    const treatmentAmounts = datasets.reduce((accTreatmentAmounts, relatedDataset) => {
        // Collect any biosamples found in all related datasets.
        const biosamples = collectDatasetBiosamples(relatedDataset);

        // Collect durations in the biosample treatments and compose them into displayable strings.
        const collectedAmounts = biosamples.reduce((accCollectedDurations, biosample) => {
            const amounts = biosample.treatments.reduce((accAmounts, treatment) => (
                treatment.amount
                    ? accAmounts.add(`${treatment.amount} ${treatment.amount_units} ${treatment.treatment_term_name}`)
                    : accAmounts
            ), new Set());
            return new Set([...accCollectedDurations, ...amounts]);
        }, new Set());
        return new Set([...accTreatmentAmounts, ...collectedAmounts]);
    }, new Set());
    return [...treatmentAmounts].sort();
};


/**
 * Wrapper component for treatment time series pages.
 */
const TreatmentTimeSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    // Build an array of treatment display strings from the biosample treatments of the
    // related datasets to display in the summary panel.
    const treatmentAmounts = collectTreatmentAmounts(context.related_datasets);
    const options = {
        getSupplementalShortLabel: (dataset) => computeDurations(dataset),
    };
    if (treatmentAmounts.length > 0) {
        options.Treatments = <>{treatmentAmounts.join(', ')}</>;
    }

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={timeSeriesTableColumns}
            sortColumn="duration"
            breadcrumbs={composeFunctionalGenomicsSeriesBreadcrumbs(context, seriesTitle)}
            options={options}
        />
    );
};

TreatmentTimeSeries.propTypes = {
    /** Treatment time series object */
    context: PropTypes.object.isRequired,
};

TreatmentTimeSeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(TreatmentTimeSeries, 'TreatmentTimeSeries');


/**
 * Wrapper component for pulse-chase time series pages.
 */
const PulseChaseTimeSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    // Build an array of pulse-chase display strings from the biosample pulse-chase durations of the
    // related datasets to display in the summary panel.
    const durations = computePulseDurations(context.related_datasets);
    const options = {
        getSupplementalShortLabel: (dataset) => computePulseDurations(dataset),
        suppressDonorDiversity: true,
    };
    if (durations.length > 0) {
        options.Durations = <>{durations.join(', ')}</>;
    }

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={pulseChaseTimeSeriesTableColumns}
            sortColumn="pulseDuration"
            breadcrumbs={composeSeriesBreadcrumbs(context, seriesTitle)}
            options={options}
        />
    );
};

PulseChaseTimeSeries.propTypes = {
    /** Pulse-chase time series object */
    context: PropTypes.object.isRequired,
};

PulseChaseTimeSeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(PulseChaseTimeSeries, 'PulseChaseTimeSeries');


/**
 * Wrapper component for differential accessibility series pages.
 */
const DifferentialAccessibilitySeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={differentialAccessibilitySeriesTableColumns}
            breadcrumbs={composeSeriesBreadcrumbs(context, seriesTitle)}
            options={{
                suppressDonorDiversity: true,
            }}
        />
    );
};

DifferentialAccessibilitySeries.propTypes = {
    /** Differential accessibility series object */
    context: PropTypes.object.isRequired,
};

DifferentialAccessibilitySeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(DifferentialAccessibilitySeries, 'DifferentialAccessibilitySeries');
