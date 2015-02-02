/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
var globals = require('./globals');
var $script = require('scriptjs');
var BrowserFeat = require('./mixins').BrowserFeat;


// The JsonGraph object helps build JSON graph objects. Create a new object
// with the constructor, then add edges and nodes with the methods.
// This merges the hierarchical structure from the JSON Graph structure described in:
// http://rtsys.informatik.uni-kiel.de/confluence/display/KIELER/JSON+Graph+Format
// and the overall structure of https://github.com/jsongraph/json-graph-specification.
// In this implementation, all edges are in the root object, not in the nodes array.
// This allows edges to cross between children and parents.

// Constructor for a graph architecture
function JsonGraph(id) {
    this.id = id;
    this.type = '';
    this.label = [];
    this.shape = '';
    this.metadata = {};
    this.nodes = [];
    this.edges = [];
}

// Add node to the graph architecture. The caller must keep track that all node IDs
// are unique -- this code doesn't verify this.
// id: uniquely identify the node
// label: text to display in the node
// cssClass: optional CSS class to assign to the SVG object for this node
// type: Optional text type to track the type of node this is
// parentNode: Optional reference to parent node; defaults to graph root
JsonGraph.prototype.addNode = function(id, label, cssClass, type, shape, cornerRadius, parentNode) {
    var newNode = {};
    newNode.id = id;
    newNode.type = type;
    newNode.label = [];
    if (typeof label === 'string' || typeof label === 'number') {
        // label is a string; assign to first array element
        newNode.label[0] = label;
    } else {
        // Otherwise, assume label is an array; clone it
        newNode.label = label.slice(0);
    }
    newNode.metadata = {cssClass: cssClass, shape: shape, cornerRadius: cornerRadius};
    newNode.nodes = [];
    var target = (parentNode && parentNode.nodes) || this.nodes;
    target.push(newNode);
};

// Add edge to the graph architecture
// source: ID of node for the edge to originate; corresponds to 'id' parm of addNode
// target: ID of node for the edge to terminate
JsonGraph.prototype.addEdge = function(source, target) {
    var newEdge = {};
    newEdge.id = '';
    newEdge.source = source;
    newEdge.target = target;
    this.edges.push(newEdge);
};

// Return the JSON graph node matching the given ID. This function finds the node
// regardless of where it is in the hierarchy of nodes.
// id: ID of the node to search for
// parent: Optional parent node to begin the search; graph root by default
JsonGraph.prototype.getNode = function(id, parent) {
    var nodes = (parent && parent.nodes) || this.nodes;

    for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].id === id) {
            return nodes[i];
        } else if (nodes[i].nodes.length) {
            var matching = this.getNode(id, nodes[i]);
            if (matching) {
                return matching;
            }
        }
    }
    return undefined;
};

module.exports.JsonGraph = JsonGraph;


var Graph = module.exports.Graph = React.createClass({
    // Take a JsonGraph object and convert it to an SVG graph with the Dagre-D3 library.
    // jsonGraph: JsonGraph object containing nodes and edges.
    // graph: Initialized empty Dagre-D3 graph.
    convertGraph: function(jsonGraph, graph) {
        // graph: dagre graph object
        // parent: JsonGraph node to insert nodes into
        function convertGraphInner(graph, parent) {
            // For each node in parent node (or top-level graph)
            parent.nodes.forEach(function(node) {
                graph.setNode(node.id + '', {label: node.label.length > 1 ? node.label : node.label[0],
                    rx: node.metadata.cornerRadius, ry: node.metadata.cornerRadius, class: node.metadata.cssClass, shape: node.metadata.shape,
                    paddingLeft: "20", paddingRight: "20", paddingTop: "10", paddingBottom: "10"});
                if (parent.id) {
                    graph.setParent(node.id + '', parent.id + '');
                }
                if (node.nodes.length) {
                    convertGraphInner(graph, node);
                }
            });
        }

        // Convert the nodes
        convertGraphInner(graph, jsonGraph);

        // Convert the edges
        jsonGraph.edges.forEach(function(edge) {
            graph.setEdge(edge.source, edge.target, {lineInterpolate: 'basis'});
        });
    },

    // Draw the graph on initial draw as well as on state changes.
    // An <svg> element to draw into must already exist in the HTML element in the el parm.
    drawGraph: function(el) {
        var d3 = require('d3');
        var dagreD3 = require('dagre-d3');
        var svg = d3.select(el).select('svg');

        // Create a new empty graph
        var g = new dagreD3.graphlib.Graph({multigraph: true, compound: true})
            .setGraph({rankdir: "TB"})
            .setDefaultEdgeLabel(function() { return {}; });

        // Convert from given node architecture to the dagre nodes and edges
        this.convertGraph(this.props.graph, g);

        // Run the renderer. This is what draws the final graph.
        var render = new dagreD3.render();
        render(d3.select("svg g"), g);

        // Dagre-D3 has a width and height for the graph.
        // Set the viewbox's and viewport's width and height to that plus a little extra.
        // Round the graph dimensions up to avoid problems detecting the end of scrolling.
        var width = Math.ceil(g.graph().width);
        var height = Math.ceil(g.graph().height);
        svg.attr("width", width + 40).attr("height", height + 60)
            .attr("viewBox", "-20 -40 " + (width + 40) + " " + (height + 60));
    },

    componentDidMount: function () {
        if (BrowserFeat.getBrowserCaps('svg')) {
            // Delay loading dagre for Jest testing compatibility;
            // Both D3 and Jest have their own conflicting JSDOM instances
            $script('dagre', function() {
                var d3 = require('d3');
                var dagreD3 = require('dagre-d3');
                var el = this.refs.graphdisplay.getDOMNode();
                this.dagreLoaded = true;

                // Add SVG element to the graph component, and assign it classes, sizes, and a group
                var svg = d3.select(el).insert('svg', '#graph-node-info')
                    .attr('id', 'graphsvg')
                    .attr('preserveAspectRatio', 'xMidYMid');
                var svgGroup = svg.append("g");

                // Draw the graph into the panel
                this.drawGraph(el);

                // Add click event listeners to each node rendering. Node's ID is its ENCODE object ID
                var reactThis = this;
                svg.selectAll("g.node").each(function(nodeId) {
                    globals.bindEvent(this, 'click', function(e) {
                        reactThis.props.nodeClickHandler(e, nodeId);
                    });
                });
            }.bind(this));
        } else {
            // Output text indicating that graphs aren't supported.
            var el = this.refs.graphdisplay.getDOMNode();
            var para = document.createElement('p');
            para.className = 'browser-error';
            para.innerHTML = 'Graphs not supported in your browser. You need a more modern browser to view it.';
            el.appendChild(para);
        }
    },

    // State change; redraw the graph
    componentDidUpdate: function() {
        if (this.dagreLoaded) {
            var el = this.refs.graphdisplay.getDOMNode();
            this.drawGraph(el);
        }
    },

    render: function() {
        return (
            <div className="panel-full">
                <div ref="graphdisplay" className="graph-display" onScroll={this.scrollHandler}>
                </div>
                {this.props.children}
            </div>
        );
    }
});


// This component should really be in experiments.js, but it's here temporarily
// so that both experiment.js and dataset.js can use it without a cyclical dependency.

var ExperimentGraph = module.exports.ExperimentGraph = React.createClass({
    // Create nodes based on all files in this experiment
    assembleGraph: function() {
        var context = this.props.context;
        var files = this.props.files || context.files;
        var jsonGraph;

        // Save list of files and analysis steps so we can click-test them later
        this.fileList = files ? files.concat(context.contributing_files) : null; // Copy so we can modify
        this.stepLists = [];

        // Only produce a graph if there's at least one file with an analysis step
        // and the file has derived from other files.
        if (files && files.some(function(file) {
            return file.derived_from && file.derived_from.length && file.step_run;
        })) {
            // Create an empty graph architecture
            jsonGraph = new JsonGraph('');

            // Create nodes for the replicates
            context.replicates.forEach(function(replicate) {
                jsonGraph.addNode(replicate.biological_replicate_number, 'Replicate ' + replicate.biological_replicate_number, 'pipeline-replicate', 'rp', 'rect', 0);
            });

            // Add files and their steps as nodes to the graph
            files.forEach(function(file) {
                var fileId = file['@id'];
                var replicateNode = file.replicate ? jsonGraph.getNode(file.replicate.biological_replicate_number) : null;

                // Assemble a single file node; can have file and step nodes in this graph, so use 'fi' type
                // to show that this is a file node.
                if (!jsonGraph.getNode(fileId)) {
                    jsonGraph.addNode(fileId, file.accession + ' (' + file.output_type + ')',
                        'pipeline-node-file' + (this.state.infoNodeId === fileId ? ' active' : ''), 'fi', 'rect', 16, replicateNode);
                }

                // If the node has parents, build the edges to the analysis step between this node and its parents
                if (file.derived_from && file.derived_from.length && file.step_run) {
                    // Remember this step for later hit testing
                    this.stepLists.push(file.step_run);

                    // Make the ID of the node using the first step in the array, and it connects to
                    var stepId = file.step_run.analysis_step['@id'] + '&' + file['@id'];

                    // Make a label for the step node
                    var label = file.step_run.analysis_step.analysis_step_types;

                    // Insert a node for the analysis step, with an ID combining the IDs of this step and the file that
                    // points to it; there may be more than one copy of this step on the graph if more than one
                    // file points to it, so we have to uniquely ID each analysis step copy with the file's ID.
                    // 'as' type identifies these as analysis step nodes. Also add an edge from the file to the
                    // analysis step.
                    jsonGraph.addNode(stepId, label,
                        'pipeline-node-analysis-step' + (this.state.infoNodeId === stepId ? ' active' : ''), 'as', 'rect', 4, replicateNode);
                    jsonGraph.addEdge(stepId, fileId);

                    // Draw an edge from the analysis step to each of the derived_from files
                    file.derived_from.forEach(function(derived) {
                        jsonGraph.addEdge(derived['@id'], stepId);
                    });
                }
            }, this);

            // Add contributing files to the graph
            context.contributing_files.forEach(function(file) {
                var fileId = file['@id'];

                // Assemble a single file node; can have file and step nodes in this graph, so use 'fi' type
                // to show that this is a file node.
                if (!jsonGraph.getNode(fileId)) {
                    jsonGraph.addNode(fileId, file.accession + ' (' + file.output_type + ')',
                        'pipeline-node-file' + (this.state.infoNodeId === fileId ? ' active' : ''), 'fi', 'rect', 16);
                }
            }, this);
        }
        return jsonGraph;
    },

    getInitialState: function() {
        return {
            infoNodeId: '' // @id of node whose info panel is open
        };
    },

    detailNodes: function(jsonGraph, infoNodeId) {
        var meta;
        var selectedFile;

        // Find data matching selected node, if any
        if (infoNodeId) {
            var node = jsonGraph.getNode(infoNodeId);
            if (node) {
                switch(node.type) {
                    case 'fi':
                        // The node is for a file
                        selectedFile = _(this.fileList).find(function(file) {
                            return file['@id'] === infoNodeId;
                        });

                        if (selectedFile) {
                            meta = (
                                <dl className="key-value">
                                    {selectedFile.file_format ?
                                        <div data-test="format">
                                            <dt>Format</dt>
                                            <dd>{selectedFile.file_format}</dd>
                                        </div>
                                    : null}

                                    {selectedFile.output_type ?
                                        <div data-test="output">
                                            <dt>Output</dt>
                                            <dd>{selectedFile.output_type}</dd>
                                        </div>
                                    : null}

                                    {selectedFile.paired_end ?
                                        <div data-test="pairedend">
                                            <dt>Paired end</dt>
                                            <dd>{selectedFile.paired_end}</dd>
                                        </div>
                                    : null}

                                    {selectedFile.replicate ?
                                        <div data-test="replicate">
                                            <dt>Associated replicates</dt>
                                            <dd>{'(' + selectedFile.replicate.biological_replicate_number + ', ' + selectedFile.replicate.technical_replicate_number + ')'}</dd>
                                        </div>
                                    : null}

                                    {selectedFile.submitted_by && selectedFile.submitted_by.title ?
                                        <div data-test="submitted">
                                            <dt>Added by</dt>
                                            <dd>{selectedFile.submitted_by.title}</dd>
                                        </div>
                                    : null}

                                    {selectedFile.date_created ?
                                        <div data-test="datecreated">
                                            <dt>Date added</dt>
                                            <dd>{selectedFile.date_created}</dd>
                                        </div>
                                    : null}

                                    {selectedFile.step_run ?
                                        <div>
                                            <dt>Software</dt>
                                            <dd>
                                                {selectedFile.step_run.analysis_step.software_versions.map(function(version, i) {
                                                    return (
                                                        <a href={version.software['@id']} className="software-version">
                                                            <span className="software">{version.software.name}</span>
                                                            {version.version ?
                                                                <span className="version">{version.version}</span>
                                                            : null}
                                                        </a>
                                                    );
                                                })}
                                            </dd>
                                        </div>
                                    : null}
                                </dl>
                            );
                        }

                        break;

                    case 'as':
                        // The node is for an analysis step
                        var analysisStepId = node.id.slice(0, node.id.indexOf('&'));
                        var selectedStep = _(this.stepLists).find(function(step) {
                            return step.analysis_step['@id'] === analysisStepId;
                        });

                        var step = selectedStep.analysis_step;
                        meta = (
                            <div>
                                <dl className="key-value">
                                    <div data-test="steptype">
                                        <dt>Step type</dt>
                                        <dd>{step.analysis_step_types.join(', ')}</dd>
                                    </div>

                                    {step.input_file_types && step.input_file_types.length ?
                                        <div data-test="inputtypes">
                                            <dt>Input file types</dt>
                                            <dd>{step.input_file_types.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {step.output_file_types && step.output_file_types.length ?
                                        <div data-test="outputtypes">
                                            <dt>Output file types</dt>
                                            <dd>{step.output_file_types.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {step.qa_stats_generated && step.qa_stats_generated.length ?
                                        <div data-test="steptypes">
                                            <dt>QA statistics</dt>
                                            <dd>{step.qa_stats_generated.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {step.software_versions && step.software_versions.length ?
                                        <div>
                                            <dt>Software</dt>
                                            <dd>
                                                {step.software_versions.map(function(version) {
                                                    return (
                                                        <a href={version.software['@id']} className="software-version">
                                                            <span className="software">{version.software.name}</span>
                                                            {version.version ?
                                                                <span className="version">{version.version}</span>
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

                        break;

                    default:
                        break;
                }
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

        // Build node graph of the files and analysis steps with this experiment
        var jsonGraph = this.assembleGraph();
        if (jsonGraph) {
            var meta = this.detailNodes(jsonGraph, this.state.infoNodeId);
            return (
                <div>
                    <h3>Files generated by pipeline</h3>
                    <Graph graph={jsonGraph} nodeClickHandler={this.handleNodeClick}>
                        <div id="graph-node-info">
                            {meta ? <div className="panel-insert">{meta}</div> : null}
                        </div>
                    </Graph>
                </div>
            );
        } else {
            return null;
        }
    }
});
