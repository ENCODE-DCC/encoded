/** @jsx React.DOM */
'use strict';
var React = require('react');
var url = require('url');
var _ = require('underscore');
var graph = require('./graph');
var globals = require('./globals');
var dbxref = require('./dbxref');
var search = require('./search');
var StatusLabel = require('./statuslabel').StatusLabel;
var Citation = require('./publication').Citation;
var audit = require('./audit');

var Graph = graph.Graph;
var JsonGraph = graph.JsonGraph;
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
    return globals.panel_views.lookup(props.context)(props);
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

        // Only produce a graph if there's at least one analysis step
        if (this.props.context.analysis_steps) {
            // Create an empty graph architecture
            jsonGraph = new JsonGraph(this.props.context.accession);

            // Add files and their steps as nodes to the graph
            this.props.context.analysis_steps.forEach(function(step) {
                var stepId = step['@id'];

                // Make an array of step types
                var stepTypesList = step.analysis_step_types.map(function(type) {
                    return type;
                });

                // Assemble a single analysis step node.
                jsonGraph.addNode(stepId, stepTypesList.join(', '),
                    {cssClass: 'pipeline-node-analysis-step' + (this.state.infoNodeId === stepId ? ' active' : ''), type: 'step', shape: 'rect', cornerRadius: 4, ref: step});

                // If the node has parents, render the edges to those parents
                if (step.parents && step.parents.length) {
                    step.parents.forEach(function(parent) {
                        jsonGraph.addEdge(parent['@id'], stepId);
                    });
                }
            }, this);

            // If any analysis step parents haven't been seen yet,
            // add them to the graph too
            this.props.context.analysis_steps.forEach(function(step) {
                if (step.parents) {
                    step.parents.forEach(function(parent) {
                        var stepId = parent['@id'];
                        if (!jsonGraph.getNode(stepId)) {
                            // Make an array of step types
                            var stepTypesList = parent.analysis_step_types.map(function(type) {
                                return type;
                            });

                            // Assemble a single analysis step node.
                            jsonGraph.addNode(stepId, stepTypesList.join(', '),
                                {cssClass: 'pipeline-node-analysis-step' + (this.state.infoNodeId === stepId ? ' active' : ''), type: 'step', shape: 'rect', cornerRadius: 4, ref: parent});
                        }
                    }, this);
                }
            }, this);

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

    handleNodeClick: function(e, nodeId) {
        e.stopPropagation(); e.preventDefault();
        this.setState({infoNodeId: this.state.infoNodeId !== nodeId ? nodeId : ''});
    },

    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');

        var documents = {};
        if (context.documents) {
            context.documents.forEach(function(doc, i) {
                documents[doc['@id']] = Panel({context: doc, key: i + 1});
            });
        }

        // Build node graph of the files and analysis steps with this experiment
        this.jsonGraph = this.assembleGraph();
        var meta = this.detailNodes(this.jsonGraph, this.state.infoNodeId);

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{context.title}</h2>
                        <div className="characterization-status-labels">
                            <div className="characterization-status-labels">
                                <StatusLabel title="Status" status={context.status} />
                            </div>
                            <AuditIndicators audits={context.audit} key="biosample-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail audits={context.audit} key="biosample-audit" />
                <div className="panel data-display">
                    <dl className="key-value">
                        <div data-test="title">
                            <dt>Title</dt>
                            {context.source_url ?
                                <dd><a href={context.source_url}>{context.title}</a></dd> :
                                <dd>{context.title}</dd>
                            }
                        </div>

                        <div data-test="assay">
                            <dt>Assay</dt>
                            <dd>{context.assay_term_name}</dd>
                        </div>
                    </dl>
                </div>
                {context.analysis_steps && context.analysis_steps.length ?
                    <div>
                        <h3>Steps</h3>
                        <div className="panel view-detail" data-test="supplementarydata">
                            {context.analysis_steps.map(function(props, i) {
                                return (
                                    <div>
                                        {i > 0 ? <hr /> : null}
                                        {AnalysisStep(props, i)}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                : null}
                {Object.keys(documents).length ?
                    <div data-test="protocols">
                        <h3>Documents</h3>
                        <div className="row multi-columns-row">
                            {documents}
                        </div>
                    </div>
                : null}
                {this.jsonGraph ?
                    <div>
                        <h3>Pipeline</h3>
                        <Graph graph={this.jsonGraph} nodeClickHandler={this.handleNodeClick}>
                            <div className="graph-node-info">
                                {meta ? <div className="panel-insert">{meta}</div> : null}
                            </div>
                        </Graph>
                    </div>
                : null}
            </div>

        );
    }
});
globals.content_views.register(Pipeline, 'pipeline');


var AnalysisStep = module.exports.AnalysisStep = function (props, i) {
    var typesList = props.analysis_step_types.join(", ");

    return (
        <dl className="key-value">
            {props.analysis_step_types.length ?
                <dl data-test="analysis_step_types">
                    <dt>Category</dt>
                    <dd>{typesList}</dd>
                </dl>
            : null}
            {props.software_versions.length ?
                <dl>
                    <dt> Software</dt>
                    <dd>
                        {props.software_versions.map(function(software_version, i) {
                            return ( <span> {
                                i > 0 ? ", ": ""
                            }
                            <a href ={software_version.software['@id']}>{software_version.software.title}</a>
                            </span>);
                        })}
                    </dd>
                </dl>
            : null}
        </dl>
    );
};


// Display the metadata of the selected analysis step in the graph
var StepDetailView = module.exports.StepDetailView = function(node) {
    // The node is for a step. It can be called with analysis_step_run (for file graphs) or analysis_step (for pipeline graphs) nodes.
    // This code detects which is the case, and adjusts accordingly.
    var selectedStep = node.metadata.ref;
    var meta;

    if (selectedStep) {
        // The node is for an analysis step
        return (
            <div>
                <dl className="key-value">
                    <div data-test="steptype">
                        <dt>Step type</dt>
                        <dd>{selectedStep.analysis_step_types.join(', ')}</dd>
                    </div>

                    {selectedStep.input_file_types && selectedStep.input_file_types.length ?
                        <div data-test="inputtypes">
                            <dt>Input file types</dt>
                            <dd>{selectedStep.input_file_types.join(', ')}</dd>
                        </div>
                    : null}

                    {selectedStep.output_file_types && selectedStep.output_file_types.length ?
                        <div data-test="outputtypes">
                            <dt>Output file types</dt>
                            <dd>{selectedStep.output_file_types.join(', ')}</dd>
                        </div>
                    : null}

                    {node.metadata.pipeline ?
                        <div data-test="pipeline">
                            <dt>Pipeline</dt>
                            <dd>{node.metadata.pipeline.title}</dd>
                        </div>
                    : null}

                    {selectedStep.qa_stats_generated && selectedStep.qa_stats_generated.length ?
                        <div data-test="qastats">
                            <dt>QA statistics</dt>
                            <dd>{selectedStep.qa_stats_generated.join(', ')}</dd>
                        </div>
                    : null}

                    {selectedStep.software_versions && selectedStep.software_versions.length ?
                        <div data-test="swversions">
                            <dt>Software</dt>
                            <dd>
                                {selectedStep.software_versions.map(function(version, i) {
                                    var versionNum = version.version === 'unknown' ? 'version unknown' : version.version;
                                    return (
                                        <a href={version.software['@id']} key={i} className="software-version">
                                            <span className="software">{version.software.name}</span>
                                            {version.version ?
                                                <span className="version">{versionNum}</span>
                                            : null}
                                        </a>
                                    );
                                })}
                            </dd>
                        </div>
                    : null}
                </dl>
            </div>
        );
    } else {
        return (<p className="browser-error">Missing step_run derivation information for {node.metadata.fileAccession}</p>);
    }
};

globals.graph_detail.register(StepDetailView, 'step');


var Listing = React.createClass({
    mixins: [search.PickerActionsMixin, AuditMixin],
    render: function() {
        var result = this.props.context;
        return (
            <li>
                <div className="clearfix">
                    {this.renderActions()}
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Pipeline</p>
                        {result.status ? <p className="type meta-status">{' ' + result.status}</p> : ''}
                        <AuditIndicators audits={result.audit} key={result['@id']} search />
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {result['title']}
                        </a>
                    </div>
                </div>
                <AuditDetail audits={result.audit} key={this.props.context['@id']} />
            </li>
        );
    }
});
globals.listing_views.register(Listing, 'pipeline');


var PipelineTable = module.exports.PipelineTable = React.createClass({
    render: function() {
        var pipelines;

        // If there's a limit on entries to display and the array is greater than that
        // limit, then clone the array with just that specified number of elements
        if (this.props.limit && (this.props.limit < this.props.items.length)) {
            // Limit the pipelines list by cloning first {limit} elements
            pipelines = this.props.items.slice(0, this.props.limit);
        } else {
            // No limiting; just reference the original array
            pipelines = this.props.items;
        }

        // Get the software version numbers for all matching software
        var softwareId = url.parse(this.props.href).pathname;
        var swVers = [];
        pipelines.forEach(function(pipeline, i) {
            return pipeline.analysis_steps.some(function(analysis_step) {
                // Get the software_version object for any with a software @id matching softwareId, and save to array
                var matchedSwVers = _(analysis_step.software_versions).find(function(software_version) {
                    return software_version.software['@id'] === softwareId;
                });
                if (matchedSwVers) {
                    swVers[i] = matchedSwVers;
                }
                return matchedSwVers;
            });
        });

        return (
            <div className="table-responsive">
                <table className="table table-panel table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Pipeline</th>
                            <th>Assay</th>
                            <th>Version</th>
                            <th>Download checksum</th>
                        </tr>
                    </thead>
                    <tbody>
                    {pipelines.map(function (pipeline, i) {
                        // Ensure this can work with search result columns too
                        return (
                            <tr key={pipeline['@id']}>
                                <td><a href={pipeline['@id']}>{pipeline.accession}</a></td>
                                <td>{pipeline.assay_term_name}</td>
                                <td><a href={swVers[i].downloaded_url}>{swVers[i].version}</a></td>
                                <td>{swVers[i].download_checksum}</td>
                            </tr>
                        );
                    })}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colSpan="6">
                                {this.props.limit && (this.props.limit < this.props.total) ?
                                    <div>
                                        {'Displaying '}{this.props.limit}{' pipelines out of '}{this.props.total}{' total related pipelines'}
                                    </div>
                                : ''}
                            </td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        );
    }
});
