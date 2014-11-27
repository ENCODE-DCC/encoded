var React = require('react');
var d3 = require('d3');
var dagreD3 = require('dagre-d3');
var globals = require('./globals');


var Graph = module.exports.Graph = React.createClass({
    getInitialState: function() {
        return {
            infoNode: '' // ID of node whose info panel is open
        };
    },

    // Draw the graph on initial draw as well as on state changes
    drawGraph: function(el) {
        var svg = d3.select(el).select('svg');

        // Create a new empty graph
        var g = new dagreD3.graphlib.Graph()
            .setGraph({rankdir: "LR"})
            .setDefaultEdgeLabel(function() { return {}; });

        // Loop over each analysis step to insert it into the graph
        this.props.files.forEach(function(file) {
            // Render each node. Set node ID to analysis step object ID so we can find it later
            g.setNode(file['@id'], {label: file.accession + ' (' + file.output_type + ')', rx: 4, ry: 4,
                class: 'pipeline-node-file' + (this.state.infoNode === file['@id'] ? ' active' : '')});

            // If the node has parents, render the edges to the analysis step
            if (file.derived_from && file.derived_from.length && file.step) {
                var step = file.step.analysis_step;
                g.setNode(step['@id'] + file['@id'], {label: step.analysis_step_types.join(', '), rx: 4, ry: 4,
                    class: 'pipeline-node-analysis-step' + (this.state.infoNode === (step['@id'] + file['@id']) ? ' active' : '')});
                g.setEdge(file['@id'], step['@id'] + file['@id']);
                file.derived_from.forEach(function(derived) {
                    g.setEdge(step['@id'] + file['@id'], derived);
                });
            }
        }, this);

        // Run the renderer. This is what draws the final graph.
        var render = new dagreD3.render();
        render(svg, g);

        // Dagre-D3 has a width and height for the graph.
        // Set the viewbox's and viewport's width and height to that plus a little extra
        var width = g.graph().width;
        var height = g.graph().height;
        svg.attr("width", width + 20);
        svg.attr("height", height + 20);
        svg.attr("viewBox", "-10 -10 " + (width + 20) + " " + (height + 20));
    },

    // After the graph panel is mounted in the DOM, use D3/Dagre/Dagre-D3 to draw into it
    componentDidMount: function() {
        var el = this.getDOMNode();

        // Add SVG element to the graph component, and assign it classes, sizes, and a group
        var svg = d3.select(el).insert('svg', '.graph-node-info')
            .attr('class', 'd3')
            .attr('width', '960px') // Just choose an initial viewport size; we'll resize it later
            .attr('height', '300px')
            .attr('viewBox', '0 0 960 300') // Choose an inital viewbox size; we'll resize it later
            .attr('preserveAspectRatio', 'xMidYMid');
        svg.append('g').attr('class', 'd3-points');

        // Draw the graph into the panel
        this.drawGraph(el);

        // Add hover event listeners to each node rendering. Node's ID is its ENCODE object ID
        var reactThis = this;
        svg.selectAll("g.node").each(function(nodeId) {
            globals.bindEvent(this, 'click', function(e) {
                reactThis.handleMouseClick(e, nodeId);
            });
        });
    },

    // State change; redraw the graph
    componentDidUpdate: function() {
        var el = this.getDOMNode();
        this.drawGraph(el);
    },

    // Handle mouse clicks in any of the nodes
    handleMouseClick: function(e, nodeId) {
        this.setState({infoNode: this.state.infoNode !== nodeId ? nodeId : ''});
    },

    render: function() {
        // Find analysis step matching selected node, if any
        var displayMeta;
        if (this.state.infoNode) {
            this.props.item.some(function(file) {
                if (file['@id'] === this.state.infoNode) {
                    displayMeta = file;
                    return true; // Found it; save the matching analysis step and exit loop
                } else {
                    return false; // Keep searching...
                }
            }, this);
        }

        return (
            <div className="panel graph-display">
                <div className="graph-node-info">
                    <hr />
                    <dl className="key-value">
                        <div>
                            <dt>Format</dt>
                            <dd>
                                {displayMeta ?
                                    <span>
                                        {displayMeta.file_format ?
                                            <span>{displayMeta.file_format}</span>
                                        :
                                            <span className="select-note">Unspecified</span>
                                        }
                                    </span>
                                :
                                    <span className="select-note">Select a node above</span>
                                }
                            </dd>
                        </div>

                        <div>
                            <dt>Output</dt>
                            <dd>
                                {displayMeta ?
                                    <span>
                                        {displayMeta.output_type ?
                                            <span>{displayMeta.output_type}</span>
                                        :
                                            <span className="select-note">Unspecified</span>
                                        }
                                    </span>
                                :
                                    <span className="select-note">Select a node above</span>
                                }
                            </dd>
                        </div>
                    </dl>
                </div>
            </div>
        );
    }
});
