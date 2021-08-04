import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
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
    AlternateAccession,
    ItemAccessories,
    InternalTags,
    TopAccessories,
} from './objectutils';
import { softwareVersionList } from './software';
import { SortTablePanel, SortTable } from './sorttable';
import { ProjectBadge } from './image';
import { DocumentsPanelReq } from './doc';
import { FileGallery } from './filegallery';
import sortMouseArray from './matrix_mouse_development';
import Status, { getObjectStatuses, sessionToAccessLevel } from './status';
import { AwardRef, ReplacementAccessions, ControllingExperiments, FileTablePaged, ExperimentTable, DoiRef } from './typeutils';

/**
 * All Series types allowed to have a download button. Keep in sync with the same variable in
 * reports/constants.py.
 */
const METADATA_SERIES_TYPES = [
    'AggregateSeries',
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
    const adminUser = !!(reactContext.session_properties && reactContext.session_properties.admin);
    const experimentsUrl = `/search/?type=Experiment&possible_controls.accession=${context.accession}`;
    const fccexperimentsUrl = `/search/?type=FunctionalCharacterizationExperiment&elements_references=${context['@id']}`;

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
                                    <dd>{context.assay_term_name}</dd>
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

                            {context.organism ?
                                <div data-test="organism">
                                    <dt>Organism</dt>
                                    <dd>{context.organism.name}</dd>
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

                            {context.biochemical_inputs && context.biochemical_inputs.length > 0 ?
                                 <div data-test="biochemicalinputs">
                                     <dt>Biochemical inputs</dt>
                                     <dd>{context.biochemical_inputs.join(', ')}</dd>
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
                        <div className="panel__split-heading panel__split-heading--annotation">
                            <h4>Attribution</h4>
                            <ProjectBadge award={context.award} addClasses="badge-heading" />
                        </div>
                        <dl className="key-value">
                            {context.encyclopedia_version ?
                                <div data-test="encyclopediaversion">
                                    <dt>Encyclopedia version</dt>
                                    <dd>{context.encyclopedia_version}</dd>
                                </div>
                            : null}

                            {context.lab ?
                                <div data-test="lab">
                                    <dt>Lab</dt>
                                    <dd>{context.lab.title}</dd>
                                </div>
                            : null}

                            <AwardRef context={context} adminUser={adminUser} />

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
    const adminUser = !!(reactContext.session_properties && reactContext.session_properties.admin);
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

                            <AwardRef context={context} adminUser={adminUser} />

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
    const adminUser = !!(reactContext.session_properties && reactContext.session_properties.admin);
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

                            <AwardRef context={context} adminUser={adminUser} />

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
    const adminUser = !!(reactContext.session_properties && reactContext.session_properties.admin);
    const experimentsUrl = `/search/?type=Experiment&possible_controls.accession=${context.accession}`;
    const fccexperimentsUrl = `/search/?type=FunctionalCharacterizationExperiment&elements_references=${context['@id']}`;

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

                            <AwardRef context={context} adminUser={adminUser} />

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
    const adminUser = !!(reactContext.session_properties && reactContext.session_properties.admin);
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
                                    <dd>{[...new Set(context.biosample_ontology.map((b) => b.term_name))]}</dd>
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

                            <AwardRef context={context} adminUser={adminUser} />

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
    const adminUser = !!(reactContext.session_properties && reactContext.session_properties.admin);
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

                            <AwardRef context={context} adminUser={adminUser} />

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
                {meta.adminUser || publicDataset(experiment) ?
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
                {meta.adminUser || publicDataset(experiment) ?
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
                {meta.adminUser || publicDataset(experiment) ?
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
                {meta.adminUser || publicDataset(experiment) ?
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
                {meta.adminUser || publicDataset(experiment) ?
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
        const biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample);
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
                {meta.adminUser || publicDataset(experiment) ?
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
        const biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample);
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
                {meta.adminUser || publicDataset(experiment) ?
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
        const biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample);
        phases = _.chain(biosamples.map((biosample) => biosample.phase)).compact().uniq().value();
    }
    return phases.join(', ');
}

const replicationTimingSeriesTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => (
            <span>
                {meta.adminUser || publicDataset(experiment) ?
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
        biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample);
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
                {meta.adminUser || publicDataset(experiment) ?
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
                {meta.adminUser || publicDataset(experiment) ?
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
    const age = ageStage.split(/ (.+)/)[1];
    let ageNumerical = 0;
    if (age.includes('days')) {
        ageNumerical += +age.split('days')[0];
    } else if (age.includes('weeks')) {
        ageNumerical += +age.split('weeks')[0] * 7;
    } else if (age.includes(' years')) {
        ageNumerical += +age.split('years')[0] * 365;
    }
    return ageNumerical;
}

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
    if (a.replicates[0].library.biosample.age_display && b.replicates[0].library.biosample.age_display) {
        return (a.replicates[0].library.biosample.age_display.split(' ')[0] - b.replicates[0].library.biosample.age_display.split(' ')[0]);
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
        biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample);
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
                {meta.adminUser || publicDataset(experiment) ?
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
                    biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample);
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
        biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample);
    }
    if (biosamples && biosamples.length > 0) {
        synchronizationBiosample = biosamples.find((biosample) => biosample.synchronization);
        if (synchronizationBiosample.age_display.indexOf('-') > -1) {
            postSynch = synchronizationBiosample.age_display.split('-')[0];
        } else {
            postSynch = synchronizationBiosample.age_display.split(' ')[0];
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
                {meta.adminUser || publicDataset(experiment) ?
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
        objSorter: (a, b) => sortMouseAge(a.life_stage_age, b.life_stage_age),
    },

    postsynchtime: {
        title: 'Post-synchronization time',
        display: (experiment) => {
            let biosamples;
            let synchronizationBiosample;

            if (experiment.replicates && experiment.replicates.length > 0) {
                biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample);
            }
            if (biosamples && biosamples.length > 0) {
                synchronizationBiosample = biosamples.find((biosample) => biosample.synchronization);
            }
            return (
                <span>{`${synchronizationBiosample.age_display}`}</span>
            );
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
                {meta.adminUser || publicDataset(experiment) ?
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
    const files = context.related_datasets
        ? (
            context.related_datasets.reduce(
                (datasetFiles, dataset) => (
                    datasetFiles.concat(
                        dataset.files.filter(
                            // If the analysis array has zero length, include all default files.
                            // Otherwise, include default files included in the given analyses.
                            (file) => file.preferred_default && (analysesFilePaths.length === 0 || analysesFilePaths.includes(file['@id']))
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
 * Displays a standard table of related experiments on Series pages. It can appear with one or two
 * sections; one containing related datasets and the other containing control experiments from the
 * related datasets.
 */
const SeriesExperimentTable = ({ context, experiments, title, tableColumns, sortColumn, adminUser, accessLevel }) => {
    if (experiments.length > 0) {
        // Get all the control experiments from the given experiments' `possible_controls`. Then
        // filter those out of the given experiments.
        const controls = _.uniq(experiments.reduce((accControls, experiment) => accControls.concat(experiment.possible_controls), []), (control) => control['@id']);
        const experimentsWithoutControls = experiments.filter((experiment) => !controls.find((control) => control['@id'] === experiment['@id']));

        return (
            <SortTablePanel
                header={
                    <div className="experiment-table__header">
                        <h4 className="experiment-table__title">{`Experiments in ${title.toLowerCase()} ${context.accession}`}</h4>
                    </div>
                }
            >
                <>
                    <div className="experiment-table__subheader">
                        Experiments
                        <CartAddAllElements elements={experimentsWithoutControls.map((experiment) => experiment['@id'])} />
                    </div>
                    <div className="table-counts">
                        {experimentsWithoutControls.length} experiment{experimentsWithoutControls.length === 1 ? '' : 's'}
                    </div>
                    <SortTable
                        list={experimentsWithoutControls}
                        columns={tableColumns}
                        meta={{ adminUser, accessLevel }}
                        sortColumn={sortColumn}
                    />
                </>
                {controls.length > 0 ?
                    <>
                        <div className="experiment-table__subheader">
                            Control experiments
                            <CartAddAllElements elements={controls.map((experiment) => experiment['@id'])} />
                        </div>
                        <div className="table-counts">
                            {controls.length} control experiment{controls.length === 1 ? '' : 's'}
                        </div>
                        <SortTable
                            list={controls}
                            columns={controlTableColumns}
                            meta={{ adminUser, accessLevel }}
                        />
                    </>
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
    /** True if the user is an admin user */
    adminUser: PropTypes.bool.isRequired,
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
    const itemClass = globals.itemClass(context, 'view-item');
    const adminUser = !!(reactContext.session_properties && reactContext.session_properties.admin);
    const experimentsUrl = `/search/?type=Experiment&possible_controls.accession=${context.accession}`;
    const seriesType = context['@type'][0];
    const accessLevel = sessionToAccessLevel(reactContext.session, reactContext.session_properties);

    // Collect all the default files from all the related datasets of the given Series object,
    // filtered by the files in the released analyses of the related datasets, if any.
    const { analyses, files } = collectSeriesAnalysesAndFiles(context);

    // Build up array of documents attached to this dataset
    const datasetDocuments = (context.documents && context.documents.length > 0) ? context.documents : [];

    // Set up the breadcrumbs, either specific to a series type or the default ones.
    const displayedBreadCrumbs = breadcrumbs || composeSeriesBreadcrumbs(context, title);

    // Get a list of reference links, if any
    const references = pubReferenceList(context.references);

    // Calculate the species for biosample summary
    let speciesRender = null;
    if (context.organism && context.organism.length > 0) {
        const speciesList = [...new Set(context.organism.map((organism) => organism.scientific_name))];
        speciesRender = (
            <span>
                {speciesList.map((species, i) => (
                    <span key={i}>
                        {i > 0 ? <span> and </span> : null}
                        <i>{species}</i>
                    </span>
                ))}
            </span>
        );
    }

    // Calculate the donor diversity.
    const diversity = options.suppressDonorDiversity ? null : donorDiversity(context);

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
            const diseasesTermNames = currentRelatedDataset.replicates.map((replicate) => {
                if (typeof replicate !== 'string') {
                    return replicate.library.biosample.disease_term_name;
                }
                return null;
            });
            return accumulatedDiseases.concat(...diseasesTermNames);
        }, [])),
    ].filter((disease) => disease);

    return (
        <div className={itemClass}>
            <header>
                <TopAccessories context={context} crumbs={displayedBreadCrumbs} />
                <h1>Summary for {title.toLowerCase()} {context.accession}</h1>
                <DoiRef context={context} />
                <ReplacementAccessions context={context} />
                <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'series-audit' }} hasCartControls={seriesType === 'FunctionalCharacterizationSeries'} />
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

                            {context.biosample_summary || speciesRender ?
                                <div data-test="biosamplesummary">
                                    <dt>Biosample summary</dt>
                                    <dd>
                                        {context.biosample_summary ? <span>{context.biosample_summary} </span> : null}
                                        {speciesRender ? <span>({speciesRender})</span> : null}
                                    </dd>
                                </div>
                            : null}

                            <div data-test="diseasetermname">
                                <dt>Disease{diseases && diseases.length !== 1 ? 's' : ''}</dt>
                                <dd>{diseases && diseases.length > 0 ? diseases.join(', ') : 'Not reported'}</dd>
                            </div>

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

                            <AwardRef context={context} adminUser={adminUser} />

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
                    adminUser={adminUser}
                    accessLevel={accessLevel}
                />
            )}

            {/* Display list of released and unreleased files */}
            {/* Set hideGraph to false to show "Association Graph" for all series */}
            {files.length > 0 ?
                <FileGallery
                    context={context}
                    files={files}
                    analyses={analyses}
                    fileQueryKey="related_datasets.files"
                    supplementalShortLabels={supplementalShortLabels}
                    showReplicateNumber={false}
                    hideControls={!METADATA_SERIES_TYPES.includes(context['@type'][0])}
                    collapseNone
                    hideGraph={seriesType !== 'FunctionalCharacterizationSeries'}
                    showDetailedTracks
                    hideAnalysisSelector
                    defaultOnly
                    relatedDatasets={experimentList}
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
        /** True to suppress the calculation and display of donor diversity */
        suppressDonorDiversity: PropTypes.bool,
        /** Retrieves short label from an experiment */
        getSupplementalShortLabel: PropTypes.func,
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

globals.contentViews.register(StandardSeries, 'AggregateSeries');
globals.contentViews.register(StandardSeries, 'MatchedSet');
globals.contentViews.register(StandardSeries, 'MultiomicsSeries');


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
const DiseaseExperimentTable = ({ datasetsByDisease, title, accession, adminUser }) => {
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
                            <CartAddAllElements elements={diseaseDatasets.map((experiment) => experiment['@id'])} />
                        </div>
                        <SortTable
                            list={diseaseDatasets}
                            columns={diseaseSeriesColumns}
                            meta={{ adminUser }}
                        />
                    </>
                : null}
                {noDiseaseDatasets.length > 0 ?
                    <>
                        <div className="experiment-table__subheader">
                            Non-diseased experiments in series
                            <CartAddAllElements elements={noDiseaseDatasets.map((experiment) => experiment['@id'])} />
                        </div>
                        <SortTable
                            list={noDiseaseDatasets}
                            columns={basicTableColumns}
                            meta={{ adminUser }}
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
    /** True if logged-in user has admin privileges */
    adminUser: PropTypes.bool.isRequired,
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
    const adminUser = !!(reactContext.session_properties && reactContext.session_properties.admin);

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
                        adminUser={adminUser}
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
 * Wrapper component for functional characterization series pages.
 */
const FunctionalCharacterizationSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={functionalCharacterizationSeriesTableColumns}
            sortColumn="examined_loci"
            breadcrumbs={composeSeriesBreadcrumbs(context, seriesTitle)}
            options={{
                getSupplementalShortLabel: (dataset) => computeExaminedLoci(dataset),
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
        const biosamples = relatedDataset.replicates.reduce((accBiosamples, replicate) => {
            const biosample = replicate.library && replicate.library.biosample;
            return biosample ? accBiosamples.concat(biosample) : accBiosamples;
        }, []);

        // Collect durations in the biosample treatments and compose them into displayable strings.
        const collectedDurations = biosamples.reduce((accCollectedDurations, biosample) => {
            const durations = biosample.treatments.reduce((accDurations, treatment) => (
                treatment.duration
                    ? accDurations.concat(`${treatment.duration} ${treatment.duration_units}${treatment.duration > 1 ? 's' : ''}`)
                    : accDurations
            ), []);
            return accCollectedDurations.concat(durations);
        }, []);

        return [...new Set(accTreatmentDurations.concat(collectedDurations))];
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
 * Wrapper component for treatment time series pages.
 */
const PulseChaseTimeSeries = ({ context }, reactContext) => {
    const seriesType = context['@type'][0];
    const seriesTitle = reactContext.profilesTitles[seriesType] || '';

    // Build an array of treatment display strings from the biosample treatments of the
    // related datasets to display in the summary panel.
    const treatmentAmounts = collectTreatmentAmounts(context.related_datasets);
    const options = {};
    if (treatmentAmounts.length > 0) {
        options.Treatments = <>{treatmentAmounts.join(', ')}</>;
    }

    return (
        <Series
            context={context}
            title={seriesTitle}
            tableColumns={timeSeriesTableColumns}
            options={options}
        />
    );
};

PulseChaseTimeSeries.propTypes = {
    /** Treatment time series object */
    context: PropTypes.object.isRequired,
};

PulseChaseTimeSeries.contextTypes = {
    profilesTitles: PropTypes.object,
};

globals.contentViews.register(PulseChaseTimeSeries, 'PulseChaseTimeSeries');
