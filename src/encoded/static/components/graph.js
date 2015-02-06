
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
    this.root = true;
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
JsonGraph.prototype.addNode = function(id, label, options) { //cssClass, type, shape, cornerRadius, parentNode
    var newNode = {};
    newNode.id = id;
    newNode.type = options.type;
    newNode.label = [];
    if (typeof label === 'string' || typeof label === 'number') {
        // label is a string; assign to first array element
        newNode.label[0] = label;
    } else {
        // Otherwise, assume label is an array; clone it
        newNode.label = label.slice(0);
    }
    newNode.metadata = {
        cssClass: options.cssClass, // CSS class
        shape: options.shape, // Shape to use for node; see dagre-d3 for options
        cornerRadius: options.cornerRadius, // # pixels to round corners of nodes
        ref: options.ref, // Reference to object this node represents
        contributing: options.contributing, // True if this is a contributing file
        error: options.error, // True if this is an error node
        accession: options.accession // Accession number for misc reference if needed (errors mostly)
    };
    newNode.nodes = [];
    var target = (options.parentNode && options.parentNode.nodes) || this.nodes;
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
                if (!parent.root) {
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
        var svg = this.savedSvg = d3.select(el).select('svg');

        // Create a new empty graph
        var g = new dagreD3.graphlib.Graph({multigraph: true, compound: true})
            .setGraph({rankdir: 'TB'})
            .setDefaultEdgeLabel(function() { return {}; });

        // Convert from given node architecture to the dagre nodes and edges
        this.convertGraph(this.props.graph, g);

        // Run the renderer. This is what draws the final graph.
        var render = new dagreD3.render();
        render(svg.select('g'), g);

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
                    .attr('preserveAspectRatio', 'xMidYMid')
                    .attr('version', '1.1');
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

            // Disable the download button
            el = this.refs.dlButton.getDOMNode();
            el.setAttribute('disabled', 'disabled');
        }
    },

    // State change; redraw the graph
    componentDidUpdate: function() {
        if (this.dagreLoaded) {
            var el = this.refs.graphdisplay.getDOMNode();
            this.drawGraph(el);
        }
    },

    handleClick: function() {

        // Collect CSS styles that apply to the graph and insert them into the given SVG element
        function attachStyles(el) {
            var stylesText = '';
            var sheets = document.styleSheets;

            // Search every style in the style sheet(s) for those applying to graphs.
            // Note: Not using ES5 looping constructs because these aren’t real arrays
            for (var i = 0; i < sheets.length; i++) {
                var rules = sheets[i].cssRules;
                for (var j = 0; j < rules.length; j++) {
                    var rule = rules[j];

                    // If a style rule starts with 'g.' (svg group), we know it applies to the graph.
                    // Note: In some browsers, indexOf is a bit faster; on others substring is a bit faster.
                    // FF(31)'s substring is much faster than indexOf.
                    if (typeof(rule.style) != 'undefined' && rule.selectorText && rule.selectorText.substring(0, 2) === 'g.') {
                        // If any elements use this style, add the style's CSS text to our style text accumulator.
                        var elems = el.querySelectorAll(rule.selectorText);
                        if (elems.length) {
                            stylesText += rule.selectorText + " { " + rule.style.cssText + " }\n";
                        }
                    }
                }
            }

            // Insert the collected SVG styles into a new style element
            var styleEl = document.createElement('style');
            styleEl.setAttribute('type', 'text/css');
            styleEl.innerHTML = "/* <![CDATA[ */\n" + stylesText + "\n/* ]]> */";

            // Insert the new style element into the beginning of the given SVG element
            el.insertBefore(styleEl, el.firstChild);
        }

        // Going to be manipulating the SVG node, so make a clone to make GC’s job harder
        var svgNode = this.savedSvg.node().cloneNode(true);

        // Attach graph CSS to SVG node clone
        attachStyles(svgNode);

        // Turn SVG node clone into a data url and attach to a new Image object. This begins "loading" the image.
        var serializer = new XMLSerializer();
        var svgXml = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">' +
            serializer.serializeToString(svgNode);
        var img = new Image();
        img.src = 'data:image/svg+xml;base64,' + window.btoa(svgXml);

        // Once the svg is loaded into the image (purely in memory, not in DOM), draw it into a <canvas>
        img.onload = function() {
            // Make a new memory-based canvas and draw the image into it.
            var canvas = document.createElement('canvas');
            canvas.width = img.width * 2;
            canvas.height = img.height * 2;
            var context = canvas.getContext('2d');
            context.drawImage(img, 0, 0, img.width * 2, img.height * 2);

            // Make the image download by making a fake <a> and pretending to click it.
            var a = document.createElement('a');
            a.download = this.props.graph.id ? this.props.graph.id + '.png' : 'graph.png';
            a.href = canvas.toDataURL('image/png');
            a.setAttribute('data-bypass', 'true');
            document.body.appendChild(a);
            a.click();
        }.bind(this);
    },

    render: function() {
        return (
            <div className="panel-full">
                <div ref="graphdisplay" className="graph-display" onScroll={this.scrollHandler}></div>
                <div className="graph-dl clearfix">
                    <button ref="dlButton" className="btn btn-info btn-sm pull-right" value="Test" onClick={this.handleClick}>Download Graph</button>
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
    assembleGraph: function(context, infoNodeId, files) {
        var jsonGraph;

        // Track orphans -- files with no derived_from and no one derives_from them.
        var usedFiles = {}; // Object with file ID keys of all files that belong in graph
        files.forEach(function(file) {
            usedFiles[file['@id']] = usedFiles[file['@id']] ||
                (!!(file.derived_from && file.derived_from.length)); // File included if it's derived from others
            if (file.derived_from && file.derived_from.length) {
                file.derived_from.forEach(function(derived) {
                    usedFiles[derived['@id']] = true; // File included if others derive from it.
                });
            }
        });

        // Only produce a graph if there's at least one file with an analysis step
        // and the file has derived from other files.
        if (usedFiles && Object.keys(usedFiles).some(function(fileKey) {
            return usedFiles[fileKey];
        })) {
            // Create an empty graph architecture
            jsonGraph = new JsonGraph(context.accession);

            // Create nodes for the replicates
            context.replicates.forEach(function(replicate) {
                jsonGraph.addNode(replicate.biological_replicate_number, 'Replicate ' + replicate.biological_replicate_number,
                    {cssClass: 'pipeline-replicate', type: 'rp', shape: 'rect', cornerRadius: 0, ref: replicate});
            });

            // Add files and their steps as nodes to the graph
            files.forEach(function(file) {
                var fileId = file['@id'];
                if (usedFiles[fileId]) {
                    var replicateNode = file.replicate ? jsonGraph.getNode(file.replicate.biological_replicate_number) : null;

                    // Assemble a single file node; can have file and step nodes in this graph, so use 'fi' type
                    // to show that this is a file node.
                    jsonGraph.addNode(fileId, file.accession + ' (' + file.output_type + ')',
                        {cssClass: 'pipeline-node-file' + (this.state.infoNodeId === fileId ? ' active' : ''),
                         type: 'fi', shape: 'rect', cornerRadius: 16, parentNode: replicateNode, ref: file});

                    // If the node has parents, build the edges to the analysis step between this node and its parents
                    if (file.derived_from && file.derived_from.length) {
                        var stepRun = file.step_run;
                        var stepId;

                        // If has derived_from but no step_run, make a dummy step to show error.
                        if (!stepRun) {
                            stepRun = {
                                error: true,
                                analysis_step: {'@id': 'ERROR:' + file.accession, analysis_step_types: 'Error in ' + file.accession}
                            };
                        }

                        // Make a label for the step node
                        var label = stepRun.analysis_step.analysis_step_types;

                        // Virtual step runs need to be duplicated on the graph
                        if (stepRun.status === 'virtual') {
                            // Make the ID of the node using the analysis step ID, and the ID of the file it connects to.
                            // Need to combine these so that duplicated steps have unique IDs.
                            stepId = stepRun.analysis_step['@id'] + '&' + file['@id'];

                            // Insert a node for the analysis step, with an ID combining the IDs of this step and the file that
                            // points to it; there may be more than one copy of this step on the graph if more than one
                            // file points to it, so we have to uniquely ID each analysis step copy with the file's ID.
                            // 'as' type identifies these as analysis step nodes. Also add an edge from the file to the
                            // analysis step.
                            jsonGraph.addNode(stepId, label,
                                {cssClass: 'pipeline-node-analysis-step' + (infoNodeId === stepId ? ' active' : ''),
                                 type: 'as', shape: 'rect', cornerRadius: 4, parentNode: replicateNode, ref: stepRun});
                            jsonGraph.addEdge(stepId, fileId);
                        } else {
                            stepId = stepRun.analysis_step['@id'];

                            // Add the step only if we haven't added it yet.
                            if (!jsonGraph.getNode(stepId)) {
                                jsonGraph.addNode(stepId, label,
                                    {cssClass: 'pipeline-node-analysis-step' + (infoNodeId === stepId ? ' active' : '') + (stepRun.error ? ' error' : ''),
                                     type: 'as', shape: 'rect', cornerRadius: 4, parentNode: replicateNode, accession: file.accession, error: stepRun.error, ref: stepRun});
                            }

                            // Now hook the file to the step
                            jsonGraph.addEdge(stepId, fileId);
                        }

                        // Draw an edge from the analysis step to each of the derived_from files
                        file.derived_from.forEach(function(derived) {
                            jsonGraph.addEdge(derived['@id'], stepId);
                        });
                    }
                }
            }, this);

            // Add contributing files to the graph
            context.contributing_files.forEach(function(file) {
                var fileId = file['@id'];

                // Assemble a single file node; can have file and step nodes in this graph, so use 'fi' type
                // to show that this is a file node.
                if (!jsonGraph.getNode(fileId)) {
                    jsonGraph.addNode(fileId, file.accession + ' (' + file.output_type + ')',
                        {cssClass: 'pipeline-node-file contributing' + (infoNodeId === fileId ? ' active' : ''),
                         type: 'fi', shape: 'rect', cornerRadius: 16, ref: file, contributing: true});
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
                        selectedFile = node.metadata.ref;

                        if (selectedFile) {
                            var contributingAccession;

                            if (node.metadata.contributing) {
                                var accessionStart = selectedFile.dataset.indexOf('/', 1) + 1;
                                var accessionEnd = selectedFile.dataset.indexOf('/', accessionStart) - accessionStart;
                                contributingAccession = selectedFile.dataset.substr(accessionStart, accessionEnd);
                            }
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

                                    {selectedFile.assembly ?
                                        <div data-test="assembly">
                                            <dt>Mapping assembly</dt>
                                            <dd>{selectedFile.assembly}</dd>
                                        </div>
                                    : null}

                                    {selectedFile.genome_annotation ?
                                        <div data-test="annotation">
                                            <dt>Genome annotation</dt>
                                            <dd>{selectedFile.genome_annotation}</dd>
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
                                                    var versionNum = version.version === 'unknown' ? 'version unknown' : version.version;
                                                    return (
                                                        <a href={version.software['@id']} className="software-version">
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
                                   
                                   {selectedFile.pipeline ?
                                        <div data-test="pipeline">
                                            <dt>Pipeline</dt>
                                            <dd>{selectedFile.pipeline.title}</dd>
                                        </div>
                                   : null}

                                    {node.metadata.contributing && selectedFile.dataset ?
                                        <div>
                                            <dt>Contributed from</dt>
                                            <dd>
                                                <a href={selectedFile.dataset}>{contributingAccession}</a>
                                            </dd>
                                        </div>
                                    : null}
                                </dl>
                            );
                        }

                        break;

                    case 'as':
                        // The node is for an analysis step
                        if (node.metadata.error) {
                            meta = (<p className="browser-error">Missing step_run derivation information for {node.metadata.accession}</p>);
                        } else {
                            var step = node.metadata.ref.analysis_step;
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
                                                        var versionNum = version.version === 'unknown' ? 'version unknown' : version.version;
                                                        return (
                                                            <a href={version.software['@id']} className="software-version">
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
                        }


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
        this.jsonGraph = this.assembleGraph(context, this.state.infoNodeId, this.props.files || context.files);
        if (this.jsonGraph && Object.keys(this.jsonGraph).length) {
            var meta = this.detailNodes(this.jsonGraph, this.state.infoNodeId);
            return (
                <div>
                    <h3>{this.props.files ? 'Unreleased files' : 'Files'} generated by pipeline</h3>
                    <Graph graph={this.jsonGraph} nodeClickHandler={this.handleNodeClick}>
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
