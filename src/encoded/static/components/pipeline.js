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
                allSteps[step.uuid] = step;
            });

            // Create an empty graph architecture
            jsonGraph = new JsonGraph(this.props.context.accession);

            // Add files and their steps as nodes to the graph
            analysis_steps.forEach(function(step) {
                var stepId = step['@id'];

                // Make an array of step types
                var stepTypesList = step.analysis_step_types.map(function(type) {
                    return type;
                });

                // Assemble a single analysis step node.
                jsonGraph.addNode(stepId, step.name,
                    {cssClass: 'pipeline-node-analysis-step' + (this.state.infoNodeId === stepId ? ' active' : ''), type: 'step', shape: 'rect', cornerRadius: 4, ref: step});

                // If the node has parents, render the edges to those parents
                if (step.parents && step.parents.length) {
                    step.parents.forEach(function(parent) {
                        if (parent.uuid in allSteps) {
                            jsonGraph.addEdge(parent['@id'], stepId);
                        }
                    });
                }
            }, this);

            // If any analysis step parents haven't been seen yet,
            // add them to the graph too
            analysis_steps.forEach(function(step) {
                if (step.parents && step.parents.length) {
                    step.parents.forEach(function(parent) {
                        if (parent.uuid in allSteps) {
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

    handleNodeClick: function(nodeId) {
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

        // Find the selected step, if any
        var selectedStep;
        if (this.state.infoNodeId) {
            var selectedNode = this.jsonGraph.getNode(this.state.infoNodeId);
            if (selectedNode) {
                selectedStep = selectedNode.metadata.ref;
            }
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
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
                        {context.accession ?
                            <div data-test="accession">
                                <dt>Accession</dt>
                                <dd>{context.accession}</dd>
                            </div>
                        : null}

                        <div data-test="title">
                            <dt>Title</dt>
                            <dd>{context.source_url ? <a href={context.source_url}>{context.title}</a> : context.title}</dd>
                        </div>

                        {context.version ?
                            <div data-test="version">
                                <dt>Version</dt>
                                <dd>{context.version}</dd>
                            </div>
                        : null}

                        {context.assay_term_name ?
                            <div data-test="assay">
                                <dt>Assay</dt>
                                <dd>{context.assay_term_name}</dd>
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

                        {context.description ?
                            <div data-test="description">
                                <dt>Description</dt>
                                <dd>{context.description}</dd>
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
                                        <AnalysisStep step={selectedStep} />
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
globals.content_views.register(Pipeline, 'pipeline');



var AnalysisStep = module.exports.AnalysisStep = React.createClass({
    render: function() {
        var step = this.props.step;
        var node = this.props.node;
        var typesList = step.analysis_step_types.join(", ");

        return (
            <div>
                <dl className="key-value">
                    <div data-test="stepname">
                        <dt>Name</dt>
                        <dd>{step.title}</dd>
                    </div>

                    <div data-test="steptype">
                        <dt>Step type</dt>
                        <dd>{step.analysis_step_types.join(', ')}</dd>
                    </div>

                    <div data-test="stepname">
                        <dt>Step name</dt>
                        <dd>{step.name}</dd>
                    </div>

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
                                    <span>
                                        {i > 0 ? <span>{','}<br /></span> : null}
                                        {type}
                                    </span>
                                );
                            })}</dd>
                        </div>
                    : null}

                    {node && node.metadata.pipeline ?
                        <div data-test="pipeline">
                            <dt>Pipeline</dt>
                            <dd>{node.metadata.pipeline.title}</dd>
                        </div>
                    : null}

                    {step.qa_stats_generated && step.qa_stats_generated.length ?
                        <div data-test="qastats">
                            <dt>QA statistics</dt>
                            <dd>{step.qa_stats_generated.map(function(stat, i) {
                                return (
                                    <span>
                                        {i > 0 ? <span>{','}<br /></span> : null}
                                        {stat}
                                    </span>
                                );
                            })}</dd>
                        </div>
                    : null}

                    {step.software_versions && step.software_versions.length ?
                        <div data-test="swversions">
                            <dt>Software</dt>
                            <dd>
                                {step.software_versions.map(function(version, i) {
                                    var versionNum = version.version === 'unknown' ? 'version unknown' : version.version;
                                    return (
                                        <a href={version.software['@id'] + '?version=' + version.version} key={i} className="software-version">
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

                    {step.aliases.length ?
                        <div data-test="aliases">
                            <dt>Aliases</dt>
                            <dd>{step.aliases.join(', ')}</dd>
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

globals.graph_detail.register(StepDetailView, 'step');


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

                        {result.version ?
                            <div><strong>Version: </strong>{result.version}</div>
                        : null}

                        {swTitle.length ?
                            <div><strong>Software: </strong>{swTitle.join(', ')}</div>
                        : null}

                        {publishedBy.length ?
                            <div><strong>Created by: </strong>{publishedBy.join(', ')}</div>
                        : null}
                    </div>
                </div>
                <AuditDetail context={result} id={this.props.context['@id']} forcedEditLink />
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
