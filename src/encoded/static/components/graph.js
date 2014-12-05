/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('./globals');
var $script = require('scriptjs');


// The JsonGraph object helps build JSON graph objects. Create a new object
// with the constructor, then add edges and nodes with the methods.
// Uses a variation of the JSON Graph structure described in:
// http://rtsys.informatik.uni-kiel.de/confluence/display/KIELER/JSON+Graph+Format
// The variation is that this one doesn't use 'width' and 'height' in the node, and it
// adds 'cssClass' and 'type' to the node.

// Constructor for a graph architecture
function JsonGraph(id) {
    this.id = id;
    this.type = '';
    this.children = [];
    this.edges = [];
    this.cssClass = '';
}

// Add node to the graph architecture
// id: uniquely identify the node
// label: text to display in the node
// cssClass: optional CSS class to assign to the SVG object for this node
// type: Optional text type to track the type of node this is
JsonGraph.prototype.addNode = function(id, label, cssClass, type) {
    var newNode = {};
    newNode.id = id;
    newNode.type = type;
    newNode.labels = [];
    newNode.labels[0] = {};
    newNode.labels[0].text = label;
    newNode.cssClass = cssClass;
    this.children.push(newNode);
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

// Return the node matching the given ID
JsonGraph.prototype.getNode = function(id) {
    var node;

    this.children.some(function(child) {
        if (child.id === id) {
            nodeType = child;
            return true;
        } else {
            return false;
        }
    });
    return node;
};

module.exports.JsonGraph = JsonGraph;


var Graph = module.exports.Graph = React.createClass({
    // Take a JsonGraph object and convert it to an SVG graph with the Dagre-D3 library.
    // graphArch: JsonGraph object containing nodes and edges.
    // graph: Initialized empty Dagre-D3 graph.
    convertGraph: function(graphArch, graph) {
        // Convert the nodes
        graphArch.children.forEach(function(node) {
            graph.setNode(node.id, {label: node.labels[0].text, rx: 4, ry: 4, class: node.cssClass});
        });

        // Convert the edges
        graphArch.edges.forEach(function(edge) {
            graph.setEdge(edge.source, edge.target);
        });
    },

    // Draw the graph on initial draw as well as on state changes
    drawGraph: function(el) {
        var d3 = require('d3');
        var dagreD3 = require('dagre-d3');
        var svg = d3.select(el).select('svg');

        // Create a new empty graph
        var g = new dagreD3.graphlib.Graph()
            .setGraph({rankdir: "TB"})
            .setDefaultEdgeLabel(function() { return {}; });

        // Convert from given node architecture to the dagre nodes and edges
        this.convertGraph(this.props.graph, g);

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

    componentDidMount: function () {
        // Delay loading dagre
        $script('dagre', function() {
            var d3 = require('d3');
            var dagreD3 = require('dagre-d3');
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

            // Add click event listeners to each node rendering. Node's ID is its ENCODE object ID
            var reactThis = this;
            svg.selectAll("g.node").each(function(nodeId) {
                globals.bindEvent(this, 'click', function(e) {
                    reactThis.props.nodeClickHandler(e, nodeId);
                });
            });
            this.dagreLoaded = true;
        }.bind(this));
    },

    // State change; redraw the graph
    componentDidUpdate: function() {
        if (this.dagreLoaded) {
            var el = this.getDOMNode();
            this.drawGraph(el);
        }
    },

    render: function() {
        return (
            <div className="panel graph-display">
            </div>
        );
    }
});
