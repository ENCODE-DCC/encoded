import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/bootstrap/modal';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import { auditDecor } from './audit';
import { DocumentsPanel } from './doc';
import globals from './globals';
import { Graph, JsonGraph } from './graph';
import { Breadcrumbs } from './navigation';
import search from './search';
import { softwareVersionList } from './software';
import StatusLabel from './statuslabel';


const PanelLookup = function (properties) {
    // XXX not all panels have the same markup
    let context;
    let localProperties = properties;
    if (localProperties['@id']) {
        context = properties;
        localProperties = { context: context };
    }
    const PanelView = globals.panel_views.lookup(localProperties.context);
    return <PanelView {...localProperties} />;
};


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
            stepVersions = step.versions && _(step.versions).sortBy(version => version.version);
            swStepVersions = _.compact(stepVersions.map((version) => {
                if (version.software_versions && version.software_versions.length) {
                    return (
                        <span className="sw-step-versions" key={version.uuid}><strong>Version {version.version}</strong>: {softwareVersionList(version.software_versions)}<br /></span>
                    );
                }
                return { header: null, body: null };
            }));
        }

        header = (
            <div className="details-view-info">
                <h4>
                    {swVersions ?
                        <span>{`${step.title} — Version ${node.metadata.stepVersion.version}`}</span>
                    :
                        <span>{step.title}</span>
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
    return { header: header, body: body };
}


class PipelineComponent extends React.Component {
    static detailNodes(jsonGraph, infoNodeId) {
        let meta;

        // Find data matching selected node, if any
        if (infoNodeId) {
            const node = jsonGraph.getNode(infoNodeId);
            if (node) {
                meta = globals.graph_detail.lookup(node)(node);
            }
        }

        return meta;
    }

    constructor() {
        super();

        // Set initial React component state.
        this.state = {
            infoNodeId: '', // ID of node whose info panel is open
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
                allSteps[step['@id']] = step;
            });

            // Create an empty graph architecture.
            jsonGraph = new JsonGraph(accession);

            // Add steps to the graph.
            analysisSteps.forEach((step) => {
                const stepId = step['@id'];
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
                    cssClass: `pipeline-node-analysis-step${this.state.infoNodeId === stepId ? ' active' : ''}`,
                    type: 'Step',
                    shape: 'rect',
                    cornerRadius: 4,
                    ref: step,
                });

                // If the node has parents, render the edges to those parents
                if (step.parents && step.parents.length) {
                    step.parents.forEach((parent) => {
                        if (allSteps[parent]) {
                            jsonGraph.addEdge(parent, stepId);
                        }
                    });
                }
            });

            // If any analysis step parents haven't been seen yet,
            // add them to the graph too
            analysisSteps.forEach((step) => {
                if (step.parents && step.parents.length) {
                    step.parents.forEach((parent) => {
                        if (parent.uuid in allSteps) {
                            const stepId = parent['@id'];
                            let swVersionList = [];
                            let label;

                            if (!jsonGraph.getNode(stepId)) {
                                // Collect software version titles
                                if (parent.software_versions && parent.software_versions.length) {
                                    swVersionList = parent.software_versions.map(version => version.software.title);
                                }

                                // Build the node label; both step types and sw version titles if available
                                if (swVersionList.length) {
                                    label = [parent.analysis_step_types.join(', '), swVersionList.join(', ')];
                                } else {
                                    label = parent.analysis_step_types.join(', ');
                                }

                                // Assemble a single analysis step node.
                                jsonGraph.addNode(stepId, label, {
                                    cssClass: `pipeline-node-analysis-step${this.state.infoNodeId === stepId ? ' active' : ''}`,
                                    type: 'Step',
                                    shape: 'rect',
                                    cornerRadius: 4,
                                    ref: parent,
                                });
                            }
                        }
                    });
                }
            });
        }
        return jsonGraph;
    }

    handleNodeClick(nodeId) {
        this.setState({
            infoNodeId: nodeId,
            infoModalOpen: true,
        });
    }

    closeModal() {
        // Called when user wants to close modal somehow
        this.setState({ infoModalOpen: false });
    }

    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');

        const assayTerm = context.assay_term_name ? 'assay_term_name' : 'assay_term_id';
        const assayName = context[assayTerm];
        const crumbs = [
            { id: 'Pipelines' },
            { id: assayName, query: `${assayTerm}=${assayName}`, tip: assayName },
        ];

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
        if (this.state.infoNodeId) {
            selectedNode = this.jsonGraph.getNode(this.state.infoNodeId);
            if (selectedNode) {
                selectedStep = selectedNode.metadata.ref;
                meta = AnalysisStep(selectedStep, selectedNode);
            }
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=pipeline" crumbs={crumbs} />
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

                            {context.assay_term_name ?
                                <div data-test="assay">
                                    <dt>Assay</dt>
                                    <dd>{context.assay_term_name}</dd>
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
                        </dl>
                    </PanelBody>
                </Panel>
                {this.jsonGraph ?
                    <div>
                        <h3>Pipeline schematic</h3>
                        <Graph graph={this.jsonGraph} nodeClickHandler={this.handleNodeClick} forceRedraw />
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
                : null}
                {context.documents && context.documents.length ?
                    <DocumentsPanel documentSpecs={[{ documents: context.documents }]} />
                : null}
            </div>
        );
    }
}

PipelineComponent.propTypes = {
    context: PropTypes.object, // Pipeline object being rendered
    auditDetail: PropTypes.func, // Audit decorator function
    auditIndicators: PropTypes.func, // Audit decorator function
};

PipelineComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Pipeline = auditDecor(PipelineComponent);

globals.content_views.register(Pipeline, 'Pipeline');


// Display the metadata of the selected analysis step in the graph
const StepDetailView = function (node) {
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
    };
};

globals.graph_detail.register(StepDetailView, 'Step');


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
                    <search.PickerActions {...this.props} />
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
                        {result.assay_term_name ?
                            <div><strong>Assay: </strong>{result.assay_term_name}</div>
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
    context: PropTypes.object, // Search result object
    auditIndicators: PropTypes.func, // Audit decorator function
    auditDetail: PropTypes.func, // Audit decorator function
};

ListingComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Listing = auditDecor(ListingComponent);

globals.listing_views.register(Listing, 'Pipeline');
