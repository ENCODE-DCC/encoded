'use strict';
var React = require('react');
var url = require('url');
var _ = require('underscore');
var graph = require('./graph');
var navbar = require('./navbar');
var globals = require('./globals');
var dbxref = require('./dbxref');
var search = require('./search');
var software = require('./software');
var StatusLabel = require('./statuslabel').StatusLabel;
var Citation = require('./publication').Citation;
var audit = require('./audit');

var Breadcrumbs = navbar.Breadcrumbs;
var Graph = graph.Graph;
var JsonGraph = graph.JsonGraph;
var SoftwareVersionList = software.SoftwareVersionList;
var AuditIndicators = audit.AuditIndicators;
var AuditDetail = audit.AuditDetail;
var AuditMixin = audit.AuditMixin;


var DbxrefList = dbxref.DbxrefList;

var Panel = function (props) {
    // XXX not all panels have the same markup
    var context;
    if (props['@id']) {
        context = props;
        props = {context: context};
    }
    var PanelView = globals.panel_views.lookup(props.context);
    return <PanelView {...props} />;
};



var Pipeline = module.exports.Pipeline = React.createClass({
    mixins: [AuditMixin],

    getInitialState: function() {
        return {
            infoNodeId: '' // ID of node whose info panel is open
        };
    },

    assembleGraph: function() {
        var jsonGraph;
        var analysis_steps = this.props.context.analysis_steps;

        // Only produce a graph if there's at least one analysis step
        if (analysis_steps && analysis_steps.length) {
            // Make an object with all step UUIDs in the pipeline
            var allSteps = {};
            analysis_steps.forEach(function(step) {
                allSteps[step['@id']] = step;
            });

            // Create an empty graph architecture
            jsonGraph = new JsonGraph(this.props.context.accession);

            // Add files and their steps as nodes to the graph
            analysis_steps.forEach(step => {
                var stepId = step['@id'];
                var swVersionList = [];
                var label;

                // Make an array of step types
                var stepTypesList = step.analysis_step_types.map(function(type) {
                    return type;
                });

                // Collect software version titles
                if (step.current_version) {
                    var software_versions = step.current_version.software_versions;
                    swVersionList = software_versions.map(function(version) {
                        return version.software.title;
                    });
                }

                // Build the node label; both step types and sw version titles if available
                if (swVersionList.length) {
                    label = [step.analysis_step_types.join(', '), swVersionList.join(', ')];
                } else {
                    label = step.analysis_step_types.join(', ');
                }

                // Assemble a single analysis step node.
                jsonGraph.addNode(stepId, label,
                    {cssClass: 'pipeline-node-analysis-step' + (this.state.infoNodeId === stepId ? ' active' : ''), type: 'Step', shape: 'rect', cornerRadius: 4, ref: step});

                // If the node has parents, render the edges to those parents
                if (step.parents && step.parents.length) {
                    step.parents.forEach(function(parent) {
                        if (allSteps[parent]) {
                            jsonGraph.addEdge(parent, stepId);
                        }
                    });
                }
            });

            // If any analysis step parents haven't been seen yet,
            // add them to the graph too
            analysis_steps.forEach(step => {
                if (step.parents && step.parents.length) {
                    step.parents.forEach(parent => {
                        if (parent.uuid in allSteps) {
                            var stepId = parent['@id'];
                            var swVersionList = [];
                            var label;

                            if (!jsonGraph.getNode(stepId)) {
                                // Collect software version titles
                                if (parent.software_versions && parent.software_versions.length) {
                                    swVersionList = parent.software_versions.map(function(version) {
                                        return version.software.title;
                                    });
                                }

                                // Build the node label; both step types and sw version titles if available
                                if (swVersionList.length) {
                                    label = [parent.analysis_step_types.join(', '), swVersionList.join(', ')];
                                } else {
                                    label = parent.analysis_step_types.join(', ');
                                }

                                // Assemble a single analysis step node.
                                jsonGraph.addNode(stepId, label,
                                    {cssClass: 'pipeline-node-analysis-step' + (this.state.infoNodeId === stepId ? ' active' : ''), type: 'Step', shape: 'rect', cornerRadius: 4, ref: parent});
                            }
                        }
                    });
                }
            });

        }
        return jsonGraph;
    },

    detailNodes: function(jsonGraph, infoNodeId) {
        var meta;

        // Find data matching selected node, if any
        if (infoNodeId) {
            var node = jsonGraph.getNode(infoNodeId);
            if (node) {
                meta = globals.graph_detail.lookup(node)(node);
            }
        }

        return meta;
    },

    handleNodeClick: function(nodeId) {
        this.setState({infoNodeId: this.state.infoNodeId !== nodeId ? nodeId : ''});
    },

    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');

        var assayTerm = context.assay_term_name ? 'assay_term_name' : 'assay_term_id';
        var assayName = context[assayTerm];
        var crumbs = [
            {id: 'Pipelines'},
            {id: assayName, query:  assayTerm + '=' + assayName, tip: assayName}
        ];

        var documents = {};
        if (context.documents) {
            context.documents.forEach(function(doc, i) {
                documents[doc['@id']] = Panel({context: doc, key: i + 1});
            });
        }

        // Build node graph of the files and analysis steps with this experiment
        this.jsonGraph = this.assembleGraph();

        // Find the selected step, if any
        var selectedStep, selectedNode;
        if (this.state.infoNodeId) {
            selectedNode = this.jsonGraph.getNode(this.state.infoNodeId);
            if (selectedNode) {
                selectedStep = selectedNode.metadata.ref;
            }
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root='/search/?type=pipeline' crumbs={crumbs} />
                        <h2>{context.title}</h2>
                        <div className="characterization-status-labels">
                            <div className="characterization-status-labels">
                                <StatusLabel title="Status" status={context.status} />
                            </div>
                            <AuditIndicators audits={context.audit} id="biosample-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail context={context} id="biosample-audit" />
                <div className="panel data-display">
                    <dl className="key-value">
                        <div data-test="title">
                            <dt>Title</dt>
                            <dd>{context.source_url ? <a href={context.source_url}>{context.title}</a> : context.title}</dd>
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
                    </dl>
                </div>
                {this.jsonGraph ?
                    <div>
                        <h3>Pipeline schematic</h3>
                        <Graph graph={this.jsonGraph} nodeClickHandler={this.handleNodeClick}>
                            <div className="graph-node-info">
                                {selectedStep ?
                                    <div className="step-info">
                                        <AnalysisStep step={selectedStep} node={selectedNode} />
                                    </div>
                                : null}
                            </div>
                        </Graph>
                    </div>
                : null}
                {context.documents && context.documents.length ?
                    <div data-test="documents">
                        <h3>Documents</h3>
                        <div className="row multi-columns-row">
                            {context.documents.map(function(doc) {
                                return <Panel context={doc} />;
                            })}
                        </div>
                    </div>
                : null}
            </div>

        );
    }
});
globals.content_views.register(Pipeline, 'Pipeline');



var AnalysisStep = module.exports.AnalysisStep = React.createClass({
    render: function() {
        var stepVersions, swVersions, swStepVersions;
        var step = this.props.step;
        var node = this.props.node;
        var typesList = step.analysis_step_types.join(", ");

        // node.metadata.stepVersion is set by the experiment file graph. It's undefined for pipeline graphs.
        if (node.metadata && node.metadata.stepVersion) {
            // Get the analysis_step_version that this step came from.
            swVersions = node.metadata.stepVersion.software_versions;
        } else {
            // Get the analysis_step_version array from the step for pipeline graph display.
            stepVersions = step.versions && _(step.versions).sortBy(function(version) { return version.version; });
            swStepVersions = _.compact(stepVersions.map(function(version) {
                if (version.software_versions && version.software_versions.length) {
                    return (
                        <span className="sw-step-versions" key={version.uuid}><strong>Version {version.version}</strong>: {SoftwareVersionList(version.software_versions)}<br /></span>
                    );
                }
                return null;
            }));
        }

        return (
            <div>
                <dl className="key-value">
                    {swVersions ?
                        <div data-test="stepversionname">
                            <dt>Name</dt>
                            <dd>{step.title + '— Version ' + node.metadata.stepVersion.version}</dd>
                        </div>
                    :
                        <div data-test="stepversionname">
                            <dt>Name</dt>
                            <dd>{step.title}</dd>
                        </div>
                    }

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
                            <dd>{step.output_file_types.map(function(type, i) {
                                return (
                                    <span key={i}>
                                        {i > 0 ? <span>{','}<br /></span> : null}
                                        {type}
                                    </span>
                                );
                            })}</dd>
                        </div>
                    : null}

                    {node && node.metadata.pipelines && node.metadata.pipelines.length ?
                        <div data-test="pipeline">
                            <dt>Pipeline</dt>
                            <dd>
                                {node.metadata.pipelines.map(function(pipeline, i) {
                                    return (
                                        <span key={i}>
                                            {i > 0 ? <span>{','}<br /></span> : null}
                                            <a href={pipeline['@id']}>{pipeline.title}</a>
                                        </span>
                                    );
                                })}
                            </dd>
                        </div>
                    : null}

                    {step.qa_stats_generated && step.qa_stats_generated.length ?
                        <div data-test="qastats">
                            <dt>QA statistics</dt>
                            <dd>{step.qa_stats_generated.map(function(stat, i) {
                                return (
                                    <span key={i}>
                                        {i > 0 ? <span>{','}<br /></span> : null}
                                        {stat}
                                    </span>
                                );
                            })}</dd>
                        </div>
                    : null}

                    {swVersions ?
                        <div data-test="swversions">
                            <dt>Software</dt>
                            <dd>{SoftwareVersionList(swVersions)}</dd>
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
                                {step.documents.map(function(document, i) {
                                    var docName = document.attachment ? document.attachment.download : document['@id'];
                                    return (<span>{i > 0 ? ', ' : null}<a href={document['@id']}>{docName}</a></span>);
                                })}
                            </dd>
                        </div>
                    : null}
                </dl>
            </div>
        );
    }
});


// Display the metadata of the selected analysis step in the graph
var StepDetailView = module.exports.StepDetailView = function(node) {
    // The node is for a step. It can be called with analysis_step_run (for file graphs) or analysis_step (for pipeline graphs) nodes.
    // This code detects which is the case, and adjusts accordingly.
    var selectedStep = node.metadata.ref;
    var meta;

    if (selectedStep) {
        return <AnalysisStep step={selectedStep} node={node} />;
    } else {
        return (<p className="browser-error">Missing step_run derivation information for {node.metadata.fileAccession}</p>);
    }
};

globals.graph_detail.register(StepDetailView, 'Step');


var Listing = React.createClass({
    mixins: [search.PickerActionsMixin, AuditMixin],
    render: function() {
        var result = this.props.context;
        var publishedBy = [];
        var swTitle = [];

        // Collect up an array of published-by and software titles for all steps in this pipeline
        if (result.analysis_steps && result.analysis_steps.length) {
            result.analysis_steps.forEach(function(step) {
                step.software_versions.forEach(function(version) {
                    swTitle.push(version.software.title);
                    if (version.software.references && version.software.references.length) {
                        version.software.references.forEach(function(reference) {
                            publishedBy.push.apply(publishedBy, reference.published_by); // add published_by array to publishedBy array
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
                    {this.renderActions()}
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Pipeline</p>
                        <p className="type">{' ' + result['accession']}</p>
                        {result.status ? <p className="type meta-status">{' ' + result.status}</p> : ''}
                        <AuditIndicators audits={result.audit} id={result['@id']} search />
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>{result['title']}</a>
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
                <AuditDetail context={result} id={this.props.context['@id']} forcedEditLink />
            </li>
        );
    }
});
globals.listing_views.register(Listing, 'Pipeline');
