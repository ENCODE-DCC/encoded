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
import Status from './status';
import pubReferenceList from './reference';
import { donorDiversity, publicDataset, AlternateAccession, ItemAccessories, InternalTags, TopAccessories } from './objectutils';
import { softwareVersionList } from './software';
import { SortTablePanel, SortTable } from './sorttable';
import { ProjectBadge } from './image';
import { DocumentsPanelReq } from './doc';
import { FileGallery, DatasetFiles } from './filegallery';
import sortMouseArray from './matrix_mouse_development';
import { AwardRef, ReplacementAccessions, ControllingExperiments, FileTablePaged, ExperimentTable } from './typeutils';

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
    const datasetDocuments = (context.documents && context.documents.length > 0) ? context.documents : [];

    // Make a biosample summary string
    const biosampleSummary = annotationBiosampleSummary(context);

    // Determine this experiment's ENCODE version
    const encodevers = globals.encodeVersion(context);

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
                                    <dd className="sentence-case">{context.annotation_type}</dd>
                                </div>
                            : null}

                            {context.biochemical_inputs && context.biochemical_inputs.length > 0 ?
                                 <div data-test="biochemicalinputs">
                                     <dt>Biochemical inputs</dt>
                                     <dd>{context.biochemical_inputs}</dd>
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
            <FileGallery context={context} encodevers={encodevers} showReplicateNumber={false} />

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
            <FileGallery context={context} encodevers={globals.encodeVersion(context)} hideGraph altFilterDefault />

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
            <FileGallery context={context} encodevers={globals.encodeVersion(context)} hideGraph />

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
            <FileGallery context={context} encodevers={globals.encodeVersion(context)} hideGraph />

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


function displayPossibleControls(item, adminUser) {
    if (item.possible_controls && item.possible_controls.length > 0) {
        return (
            <span>
                {item.possible_controls.map((control, i) => (
                    <span key={control.uuid}>
                        {i > 0 ? <span>, </span> : null}
                        {adminUser || publicDataset(control) ?
                            <a href={control['@id']}>{control.accession}</a>
                        :
                            <span>{control.accession}</span>
                        }
                    </span>
                ))}
            </span>
        );
    }
    return null;
}


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

    target: {
        title: 'Target',
        getValue: (experiment) => (experiment.target ? experiment.target.label : null),
    },

    description: {
        title: 'Description',
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

    target: {
        title: 'Target',
        getValue: (experiment) => (experiment.target ? experiment.target.label : '(control)'),
    },

    description: {
        title: 'Description',
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

const treatmentTimeSeriesTableColumns = {
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

    possible_controls: {
        title: 'Possible controls',
        display: (experiment, meta) => displayPossibleControls(experiment, meta.adminUser),
        sorter: false,
    },

    duration: {
        title: 'Duration',
        getValue: (experiment) => {
            let durations = [];
            if (experiment.replicates && experiment.replicates.length > 0) {
                const biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample);
                durations.push(biosamples.map((biosample) => {
                    if (biosample.treatments && biosample.treatments.length > 0) {
                        durations = `${biosample.treatments[0].duration} ${biosample.treatments[0].duration_units}${biosample.treatments[0].duration > 1 ? 's' : ''}`;
                    }
                    return null;
                }));
            }
            return durations;
        },
    },

    description: {
        title: 'Description',
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

    possible_controls: {
        title: 'Possible controls',
        display: (experiment, meta) => displayPossibleControls(experiment, meta.adminUser),
        sorter: false,
    },

    concentration: {
        title: 'Concentration',
        getValue: (experiment) => computeConcentration(experiment),
    },

    description: {
        title: 'Description',
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

    description: {
        title: 'Description',
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

    possible_controls: {
        title: 'Possible controls',
        display: (experiment, meta) => displayPossibleControls(experiment, meta.adminUser),
        sorter: false,
    },

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
            let biosamples;
            let lifeStageAge = [];

            if (experiment.replicates && experiment.replicates.length > 0) {
                biosamples = experiment.replicates.map((replicate) => replicate.library && replicate.library.biosample);
            }
            if (biosamples && biosamples.length > 0) {
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
            return (
                <span>{lifeStageAge && lifeStageAge.length > 0 ? <span>{lifeStageAge.join(', ')}</span> : 'unknown'}</span>
            );
        },
        objSorter: (a, b) => sortStage(a, b),
    },

    description: {
        title: 'Description',
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

    possible_controls: {
        title: 'Possible controls',
        display: (experiment, meta) => displayPossibleControls(experiment, meta.adminUser),
        sorter: false,
    },

    synch: {
        title: 'Synchronization',
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
                <span>{`${synchronizationBiosample.synchronization}`}</span>
            );
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

    description: {
        title: 'Description',
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


// Map series @id to title and table columns
const seriesComponents = {
    MatchedSet: { title: 'matched set series', table: basicTableColumns },
    OrganismDevelopmentSeries: { title: 'organism development series', table: organismDevelopmentSeriesTableColumns },
    OrganismDevelopmentSeriesWormFly: { title: 'organism development series', table: organismDevelopmentSeriesWormFlyTableColumns },
    ReferenceEpigenome: { title: 'reference epigenome series', table: basicTableColumns },
    ReplicationTimingSeries: { title: 'replication timing series', table: replicationTimingSeriesTableColumns },
    TreatmentConcentrationSeries: { title: 'treatment concentration series', table: treatmentSeriesTableColumns },
    TreatmentTimeSeries: { title: 'treatment time series', table: treatmentTimeSeriesTableColumns },
    AggregateSeries: { title: 'aggregate series', table: basicTableColumns },
    SingleCellRnaSeries: { title: 'single cell rna series', table: basicTableColumns },
    FunctionalCharacterizationSeries: { title: 'functional characterization series', table: basicTableColumns },
    GeneSilencingSeries: { title: 'gene silencing series', table: geneSilencingSeriesTableColumns },
    DifferentiationSeries: { title: 'differentiation series', table: basicTableColumns },
};

export const SeriesComponent = (props, reactContext) => {
    const { context, auditIndicators, auditDetail } = props;
    const itemClass = globals.itemClass(context, 'view-item');
    const adminUser = !!(reactContext.session_properties && reactContext.session_properties.admin);
    const experimentsUrl = `/search/?type=Experiment&possible_controls.accession=${context.accession}`;
    let experiments = {};
    context.files.forEach((file) => {
        const experiment = file.replicate && file.replicate.experiment;
        if (experiment) {
            experiments[experiment['@id']] = experiment;
        }
    });
    experiments = _.values(experiments);

    // Build up array of documents attached to this dataset
    const datasetDocuments = (context.documents && context.documents.length > 0) ? context.documents : [];

    // Set up the breadcrumbs
    const datasetType = context['@type'][1];
    let seriesType = context['@type'][0];
    let crumbs;
    const functionalGenomicsSeries = ['OrganismDevelopmentSeries', 'TreatmentTimeSeries', 'TreatmentConcentrationSeries', 'ReplicationTimingSeries', 'GeneSilencingSeries'];
    if (functionalGenomicsSeries.indexOf(seriesType) > -1) {
        crumbs = [
            { id: 'Datasets' },
            { id: breakSetName(seriesType), uri: `/series-search/?type=${seriesType}`, wholeTip: `Search for ${seriesType}` },
        ];
    } else {
        crumbs = [
            { id: 'Datasets' },
            { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
            { id: breakSetName(seriesType), uri: `/search/?type=${seriesType}`, wholeTip: `Search for ${seriesType}` },
        ];
    }

    if (seriesType === 'OrganismDevelopmentSeries' && context.organism && context.organism.length > 0 && ((context.organism[0].scientific_name === 'Caenorhabditis elegans') || (context.organism[0].scientific_name === 'Drosophila melanogaster'))) {
        seriesType = 'OrganismDevelopmentSeriesWormFly';
    }

    let treatmentDuration = [];
    let combinedTreatmentDuration;
    let treatmentAmounts = [];
    let combinedTreatmentAmounts;
    context.related_datasets.forEach((d) => {
        let biosamples;
        if (d.replicates && d.replicates.length > 0) {
            biosamples = d.replicates.map((replicate) => replicate.library && replicate.library.biosample);
        }
        if (biosamples && biosamples.length > 0) {
            biosamples.forEach((biosample) => biosample.treatments.forEach((treatment) => {
                if (treatment.duration) {
                    treatmentDuration.push(`${treatment.duration} ${treatment.duration_units}${treatment.duration > 1 ? 's' : ''}`);
                }
                if (treatment.amount) {
                    treatmentAmounts.push(`${treatment.amount} ${treatment.amount_units} ${treatment.treatment_term_name}`);
                } else if (treatment.treatment_term_name) {
                    treatmentAmounts.push(treatment.treatment_term_name);
                }
            }));
        }
    });

    // Get a list of reference links, if any
    const references = pubReferenceList(context.references);

    // Make the series title
    const seriesComponent = seriesComponents[seriesType];
    const seriesTitle = seriesComponent ? seriesComponent.title : 'series';

    // Calculate the biosample summary
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
    const terms = (context.biosample_ontology && context.biosample_ontology.length > 0) ? [...new Set(context.biosample_ontology.map((b) => b.term_name))] : [];

    // Calculate the donor diversity.
    const diversity = donorDiversity(context);

    // Filter out any files we shouldn't see.
    const experimentList = context.related_datasets.filter((dataset) => dataset.status !== 'revoked' && dataset.status !== 'replaced' && dataset.status !== 'deleted');

    // If we display a table of related experiments, have to render the control to add all of
    // them to the current cart.
    let addAllToCartControl;
    if (experimentList.length > 0) {
        const experimentIds = experimentList.map((experiment) => experiment['@id']);
        addAllToCartControl = (
            <div className="experiment-table__header">
                <h4 className="experiment-table__title">{`Experiments in ${seriesTitle} ${context.accession}`}</h4>
                <CartAddAllElements elements={experimentIds} />
            </div>
        );
    }

    let targets;
    // Get list of target labels
    if (context.target) {
        targets = [...new Set(context.target.map((target) => target.label))];
    }
    if (treatmentDuration.length > 0) {
        treatmentDuration = [...new Set(treatmentDuration)];
        combinedTreatmentDuration = treatmentDuration.join(', ');
    }
    if (treatmentAmounts.length > 0) {
        treatmentAmounts = [...new Set(treatmentAmounts)];
        combinedTreatmentAmounts = treatmentAmounts.join(', ');
    }

    return (
        <div className={itemClass}>
            <header>
                <TopAccessories context={context} crumbs={crumbs} />
                <h1>Summary for {seriesTitle} {context.accession}</h1>
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

                            <div data-test="donordiversity">
                                <dt>Donor diversity</dt>
                                <dd>{diversity}</dd>
                            </div>

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

                            {terms.length > 0 || speciesRender ?
                                <div data-test="biosamplesummary">
                                    <dt>Biosample summary</dt>
                                    <dd>
                                        {terms.length > 0 ? <span>{terms.join(' and ')} </span> : null}
                                        {speciesRender ? <span>({speciesRender})</span> : null}
                                    </dd>
                                </div>
                            : null}

                            {context.treatment_term_name && context.treatment_term_name.length > 0 ?
                                <div data-test="treatmenttermname">
                                    <dt>Treatment{context.treatment_term_name.length > 0 ? 's' : ''}</dt>
                                    <dd>
                                        {seriesType === 'TreatmentConcentrationSeries' && treatmentDuration ?
                                            <>{context.treatment_term_name} for {combinedTreatmentDuration}</>
                                        : null}
                                        {seriesType === 'TreatmentTimeSeries' && treatmentAmounts ?
                                            <>{combinedTreatmentAmounts}</>
                                        : null}
                                        {(treatmentDuration.length === 0 || seriesType !== 'TreatmentConcentrationSeries') && (treatmentAmounts.length === 0 || seriesType !== 'TreatmentTimeSeries') ?
                                            <>{context.treatment_term_name.join(', ')}</>
                                        : null}
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

            {addAllToCartControl ?
                <SortTablePanel header={addAllToCartControl}>
                    <SortTable
                        list={experimentList}
                        columns={seriesComponent.table}
                        meta={{ adminUser }}
                    />
                </SortTablePanel>
            : null}

            {/* Display list of released and unreleased files */}
            <FetchedItems
                {...props}
                url={`/search/?limit=all&type=File&dataset=${context['@id']}`}
                Component={DatasetFiles}
                filePanelHeader={<FilePanelHeader context={context} />}
                encodevers={globals.encodeVersion(context)}
                session={reactContext.session}
            />

            <FetchedItems {...props} url={experimentsUrl} Component={ControllingExperiments} />

            <DocumentsPanelReq documents={datasetDocuments} />
        </div>
    );
};

SeriesComponent.propTypes = {
    context: PropTypes.object.isRequired, // Series object to display
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

SeriesComponent.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};

const Series = auditDecor(SeriesComponent);

globals.contentViews.register(Series, 'Series');
