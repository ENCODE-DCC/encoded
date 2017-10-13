import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/bootstrap/modal';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import { auditDecor } from './audit';
import { DocumentsPanel } from './doc';
import * as globals from './globals';
import { Graph, JsonGraph } from './graph';
import { Breadcrumbs } from './navigation';
import { PanelLookup } from './objectutils';
import { PickerActions } from './search';
import { softwareVersionList } from './software';
import StatusLabel from './statuslabel';


const stepNodePrefix = 'step'; // Prefix for step node IDs
const fileNodePrefix = 'file'; // Prefix for file node IDs


function AnalysisStep(step, node) {
    let header = null;
    let body = null;

    if (step) {
        let stepVersions;
        let swVersions;
        let swStepVersions;

        // node.metadata.stepVersion is set by the experiment file graph. It's undefined for pipeline graphs.
        if (node.metadata && node.metadata.stepVersion) {
            // Get the analysis_step_version that this step came from.
            swVersions = node.metadata.stepVersion.software_versions;
        } else {
            // Get the analysis_step_version array from the step for pipeline graph display.
            stepVersions = step.versions && _(step.versions).sortBy(version => version.minor_version);
            swStepVersions = _.compact(stepVersions.map((version) => {
                if (version.software_versions && version.software_versions.length) {
                    return (
                        <span className="sw-step-versions" key={version.uuid}><strong>Version {step.major_version}.{version.minor_version}</strong>: {softwareVersionList(version.software_versions)}<br /></span>
                    );
                }
                return { header: null, body: null };
            }));
        }

        header = (
            <div className="details-view-info">
                <h4>
                    {swVersions ?
                        <span>{`${step.title} — Version ${node.metadata.ref.major_version}.${node.metadata.stepVersion.minor_version}`}</span>
                    :
                        <span>{step.title} — Version {node.metadata.ref.major_version}</span>
                    }
                </h4>
            </div>
        );
        body = (
            <div>
                <dl className="key-value">
                    <div data-test="steptype">
                        <dt>Step type</dt>
                        <dd>{step.analysis_step_types.join(', ')}</dd>
                    </div>

                    {step.aliases && step.aliases.length ?
                        <div data-test="stepname">
                            <dt>Step aliases</dt>
                            <dd>{step.aliases.join(', ')}</dd>
                        </div>
                    : null}

                    {step.input_file_types && step.input_file_types.length ?
                        <div data-test="inputtypes">
                            <dt>Input</dt>
                            <dd>{step.input_file_types.join(', ')}</dd>
                        </div>
                    : null}

                    {step.output_file_types && step.output_file_types.length ?
                        <div data-test="outputtypes">
                            <dt>Output</dt>
                            <dd>{step.output_file_types.map((type, i) =>
                                <span key={i}>
                                    {i > 0 ? <span>{','}<br /></span> : null}
                                    {type}
                                </span>
                            )}</dd>
                        </div>
                    : null}

                    {node && node.metadata.pipelines && node.metadata.pipelines.length ?
                        <div data-test="pipeline">
                            <dt>Pipeline</dt>
                            <dd>
                                {node.metadata.pipelines.map((pipeline, i) =>
                                    <span key={i}>
                                        {i > 0 ? <span>{','}<br /></span> : null}
                                        <a href={pipeline['@id']}>{pipeline.title}</a>
                                    </span>
                                )}
                            </dd>
                        </div>
                    : null}

                    {step.qa_stats_generated && step.qa_stats_generated.length ?
                        <div data-test="qastats">
                            <dt>QA statistics</dt>
                            <dd>{step.qa_stats_generated.map((stat, i) =>
                                <span key={i}>
                                    {i > 0 ? <span>{','}<br /></span> : null}
                                    {stat}
                                </span>
                            )}</dd>
                        </div>
                    : null}

                    {swVersions ?
                        <div data-test="swversions">
                            <dt>Software</dt>
                            <dd>{softwareVersionList(swVersions)}</dd>
                        </div>
                    : stepVersions && stepVersions.length ?
                        <div data-test="swstepversions">
                            <dt>Software</dt>
                            <dd>{swStepVersions}</dd>
                        </div>
                    : null}

                    {step.documents && step.documents.length ?
                        <div data-test="documents">
                            <dt>Documents</dt>
                            <dd>
                                {step.documents.map((document, i) => {
                                    const docName = document.attachment ? document.attachment.download : document['@id'];
                                    return (<span>{i > 0 ? ', ' : null}<a href={document['@id']}>{docName}</a></span>);
                                })}
                            </dd>
                        </div>
                    : null}
                </dl>
            </div>
        );
    }
    return { header, body, type: 'Step' };
}


class PipelineComponent extends React.Component {
    // For the given step, calculate its unique ID for the graph nodes. You can pass an
    // analysis_step object in `step`, or just its @id string to get the same result.
    static genStepId(step) {
        if (typeof step === 'string') {
            // `step` is an @id.
            return `${stepNodePrefix}:${step}`;
        }

        // `step` is an analysis_step object.
        return `step:${step['@id']}`;
    }

    // For the given step and input_file_type/output_file_type, calculate its unique ID for the
    // graph nodes. Pass the analysis_step object this file type is associated with, and the single
    // input our output file type in `file`.
    static genFileId(step, file) {
        // `step` is an analysis_step object.
        return `${fileNodePrefix}:${step['@id']}${file}`;
    }

    // Given a graph node ID, return the prefix portion that identifies what kind of node this is.
    static getNodeIdPrefix(node) {
        return node.id.split(':')[0];
    }

    constructor() {
        super();

        // Set initial React component state.
        this.state = {
            infoNode: null, // ID of node whose info panel is open
            infoModalOpen: false, // Graph information modal open
        };

        // Bind `this` to non-React methods.
        this.assembleGraph = this.assembleGraph.bind(this);
        this.handleNodeClick = this.handleNodeClick.bind(this);
        this.closeModal = this.closeModal.bind(this);
    }

    assembleGraph() {
        const { context } = this.props;
        const accession = context.accession;
        const analysisSteps = context.analysis_steps;
        let jsonGraph;

        // Only produce a graph if there's at least one analysis step.
        if (analysisSteps && analysisSteps.length) {
            // Make an object with all step UUIDs in the pipeline.
            const allSteps = {};
            analysisSteps.forEach((step) => {
                const stepId = PipelineComponent.genStepId(step);
                allSteps[stepId] = step;
            });

            // Create an empty graph architecture.
            jsonGraph = new JsonGraph(accession);

            // Add steps to the graph.
            analysisSteps.forEach((step) => {
                const stepId = PipelineComponent.genStepId(step);
                let swVersionList = [];
                let label;

                // Collect software version titles.
                if (step.current_version) {
                    const softwareVersions = step.current_version.software_versions;
                    swVersionList = softwareVersions.map(version => version.software.title);
                }

                // Build the node label; both step types and sw version titles if available.
                if (swVersionList.length) {
                    label = [step.analysis_step_types.join(', '), swVersionList.join(', ')];
                } else {
                    label = step.analysis_step_types.join(', ');
                }

                // Assemble a single analysis step node.
                jsonGraph.addNode(stepId, label, {
                    cssClass: `pipeline-node-analysis-step${this.state.infoNode && this.state.infoNode.id === stepId ? ' active' : ''}`,
                    type: 'Step',
                    shape: 'rect',
                    cornerRadius: 4,
                    ref: step,
                });

                // Add this step's `output_file_types` nodes to the graph, and connect edges from
                // them to the current step.
                if (step.output_file_types && step.output_file_types.length) {
                    step.output_file_types.forEach((outputFile) => {
                        // Get the unique ID for the file type node. We can have repeats of the
                        // same output_file_type all over the graph, so we have to include the step
                        // identifier along with it, and each step's identifier is unique in the
                        // graph.
                        const fileId = PipelineComponent.genFileId(step, outputFile);
                        jsonGraph.addNode(fileId, outputFile, {
                            cssClass: 'pipeline-node-file-type',
                            type: 'File',
                            shape: 'rect',
                            cornerRadius: 16,
                            ref: outputFile,
                        });

                        // Connect this file node to the current step with an edge.
                        jsonGraph.addEdge(stepId, fileId);
                    });
                }

                // If the node has parents, render the edges to those parents or to those parents'
                // output_file_types nodes. `parentlessInputs` tracks input file types that *don't*
                // overlap with the parents' output file types.
                let parentlessInputs = step.input_file_types || [];
                if (step.parents && step.parents.length) {
                    step.parents.forEach((parent) => {
                        // Get this step's parent object so we can look at its output_file_types array.
                        const parentId = PipelineComponent.genStepId(parent);
                        const parentStep = allSteps[parentId];
                        if (parentStep) {
                            if (parentStep.output_file_types && parentStep.output_file_types.length) {
                                // We have the parent analysis_step object and it has output_file_types.
                                // Compare that array with this step's input_file_types elements.
                                // Draw an edge to any that overlap.
                                const overlaps = _.intersection(parentStep.output_file_types, step.input_file_types);
                                if (overlaps.length) {
                                    overlaps.forEach((overlappingFile) => {
                                        const overlappingFileId = PipelineComponent.genFileId(parentStep, overlappingFile);
                                        jsonGraph.addEdge(overlappingFileId, stepId);
                                    });
                                } else {
                                    // The input and output file types of the step and its parent
                                    // don't overlap. Just connect it directly to the parent.
                                    jsonGraph.addEdge(parentId, stepId);
                                }

                                // Remove the parent’s output file types from the array of this
                                // step's input file types so that we know what parentless input
                                // file types we have to draw later.
                                parentlessInputs = _.difference(parentlessInputs, parentStep.output_file_types);
                            } else {
                                // The parent step doesn't have any output file types, so just
                                // connect this step to the parent step directly.
                                jsonGraph.addEdge(parentId, stepId);
                            }
                        }
                        // No parent step object when this step has parents means a data error.
                        // At least don't crash.
                    });
                }

                // Render input file types not shared by a parent step. `parentlessInputs` is an
                // array holding all the input file types for the current step that aren't shared
                // with a parent's output file types.
                if (parentlessInputs.length) {
                    // The step doesn't have parents but it has input_file_types. Draw nodes for
                    // all its input_file_types.
                    parentlessInputs.forEach((fileType) => {
                        // Most file-type nodes have IDs containing their parent step @id. These
                        // file-type nodes don't have a parent, so we take the child's and add "IO"
                        // to it to distinguish it from the odd case of a step having the same
                        // input and output file types. "IO" stands for "Input Only."
                        const fileId = PipelineComponent.genFileId(step, `IO${fileType}`);
                        jsonGraph.addNode(fileId, fileType, {
                            cssClass: 'pipeline-node-file-type',
                            type: 'File',
                            shape: 'rect',
                            cornerRadius: 16,
                            ref: fileType,
                        });

                        // Connect this file node to the current step with an edge.
                        jsonGraph.addEdge(fileId, stepId);
                    });
                }
            });
        }
        return jsonGraph;
    }

    // Called when a node in the graph is clicked.
    handleNodeClick(nodeId) {
        // We do different things depending on whether this is a step node or file node, which we
        // can tell from the given node ID's prefix. For step nodes, set the state so that we
        // rerender this component with a modal.
        const nodePrefix = PipelineComponent.getNodeIdPrefix(nodeId);
        if (nodePrefix === stepNodePrefix) {
            // Click was in a step node. Set a new state so that a modal for the step node appears.
            this.setState({
                infoNode: nodeId,
                infoModalOpen: true,
            });
        }
    }

    closeModal() {
        // Called when user wants to close modal somehow
        this.setState({ infoModalOpen: false });
    }

    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');

        let crumbs;
        const assayName = (context.assay_term_names && context.assay_term_names.length) ? context.assay_term_names.join(' + ') : null;
        if (assayName) {
            const query = context.assay_term_names.map(name => `assay_term_names=${name}`).join('&');
            crumbs = [
                { id: 'Pipelines' },
                { id: assayName, query, tip: assayName },
            ];
        }

        const documents = {};
        if (context.documents) {
            context.documents.forEach((doc, i) => {
                documents[doc['@id']] = PanelLookup({ context: doc, key: i + 1 });
            });
        }

        // Build node graph of the files and analysis steps with this experiment
        this.jsonGraph = this.assembleGraph();

        // Find the selected step, if any
        let selectedStep;
        let selectedNode;
        let meta;
        if (this.state.infoNode) {
            selectedNode = this.jsonGraph.getNode(this.state.infoNode && this.state.infoNode.id);
            if (selectedNode) {
                selectedStep = selectedNode.metadata.ref;
                meta = AnalysisStep(selectedStep, selectedNode);
            }
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        {crumbs ? <Breadcrumbs root="/search/?type=Pipeline" crumbs={crumbs} /> : null}
                        <h2>{context.title}</h2>
                        <div className="characterization-status-labels">
                            <div className="characterization-status-labels">
                                <StatusLabel title="Status" status={context.status} />
                            </div>
                            {this.props.auditIndicators(context.audit, 'pipeline-audit', { session: this.context.session })}
                        </div>
                    </div>
                </header>
                {this.props.auditDetail(context.audit, 'pipeline-audit', { session: this.context.session, except: context['@id'] })}
                <Panel addClasses="data-display">
                    <PanelBody>
                        <dl className="key-value">
                            <div data-test="title">
                                <dt>Title</dt>
                                <dd>{context.title}</dd>
                            </div>

                            {context.assay_term_names && context.assay_term_names.length ?
                                <div data-test="assay">
                                    <dt>Assays</dt>
                                    <dd>{context.assay_term_names.join(', ')}</dd>
                                </div>
                            : null}

                            {context.description ?
                                <div data-test="description">
                                    <dt>Description</dt>
                                    <dd>{context.description}</dd>
                                </div>
                            : null}

                            <div data-test="lab">
                                <dt>Lab</dt>
                                <dd>{context.lab.title}</dd>
                            </div>

                            {context.award.pi && context.award.pi.lab ?
                                <div data-test="awardpi">
                                    <dt>Award PI</dt>
                                    <dd>{context.award.pi.lab.title}</dd>
                                </div>
                            : null}

                            {context.source_url ?
                                <div data-test="sourceurl">
                                    <dt>Source</dt>
                                    <dd><a href={context.source_url}>{context.source_url}</a></dd>
                                </div>
                            : null}

                            {context.standards_page ?
                                <div data-test="standardspage">
                                    <dt>Pipeline standards</dt>
                                    <dd><a href={context.standards_page['@id']}>{context.standards_page.title}</a></dd>
                                </div>
                            : null}
                        </dl>
                    </PanelBody>
                </Panel>

                {this.jsonGraph ?
                    <Panel>
                        <PanelHeading>
                            <h3>Pipeline schematic</h3>
                        </PanelHeading>
                        <Graph graph={this.jsonGraph} nodeClickHandler={this.handleNodeClick} />
                    </Panel>
                : null}

                {context.documents && context.documents.length ?
                    <DocumentsPanel documentSpecs={[{ documents: context.documents }]} />
                : null}

                {meta && this.state.infoModalOpen ?
                    <Modal closeModal={this.closeModal}>
                        <ModalHeader closeModal={this.closeModal}>
                            {meta ? meta.header : null}
                        </ModalHeader>
                        <ModalBody>
                            {meta ? meta.body : null}
                        </ModalBody>
                        <ModalFooter closeModal={<button className="btn btn-info" onClick={this.closeModal}>Close</button>} />
                    </Modal>
                : null}
            </div>
        );
    }
}

PipelineComponent.propTypes = {
    context: PropTypes.object.isRequired, // Pipeline object being rendered
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
};

PipelineComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Pipeline = auditDecor(PipelineComponent);

globals.contentViews.register(Pipeline, 'Pipeline');


// Display the metadata of the selected analysis step in the graph
const StepDetailView = function StepDetailView(node) {
    // The node is for a step. It can be called with analysis_step_run (for file graphs) or
    // analysis_step (for pipeline graphs) nodes. This code detects which is the case, and adjusts
    // accordingly.
    const selectedStep = node.metadata.ref;

    if (selectedStep) {
        return AnalysisStep(selectedStep, node);
    }
    return {
        header: <h4>Software unknown</h4>,
        body: <p className="browser-error">Missing step_run derivation information for {node.metadata.fileAccession}</p>,
        type: 'Step',
    };
};

globals.graphDetail.register(StepDetailView, 'Step');


class ListingComponent extends React.Component {
    render() {
        const result = this.props.context;
        let publishedBy = [];
        let swTitle = [];

        // Collect up an array of published-by and software titles for all steps in this pipeline
        if (result.analysis_steps && result.analysis_steps.length) {
            result.analysis_steps.forEach((step) => {
                step.software_versions.forEach((version) => {
                    swTitle.push(version.software.title);
                    if (version.software.references && version.software.references.length) {
                        version.software.references.forEach((reference) => {
                            // add published_by array to publishedBy array.
                            publishedBy.push(...reference.published_by);
                        });
                    }
                });
            });
        }
        publishedBy = _.uniq(publishedBy);
        swTitle = _.uniq(swTitle);

        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Pipeline</p>
                        <p className="type">{` ${result.accession}`}</p>
                        {result.status ? <p className="type meta-status">{` ${result.status}`}</p> : ''}
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>{result.title}</a>
                    </div>
                    <div className="data-row">
                        {result.assay_term_names && result.assay_term_names.length ?
                            <div><strong>Assays: </strong>{result.assay_term_names.join(', ')}</div>
                        : null}

                        {swTitle.length ?
                            <div><strong>Software: </strong>{swTitle.join(', ')}</div>
                        : null}
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, forcedEditLink: true })}
            </li>
        );
    }
}

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired, // Search result object
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ListingComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'Pipeline');
