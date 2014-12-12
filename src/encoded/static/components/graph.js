/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
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

// Return the JSON graph node matching the given ID
JsonGraph.prototype.getNode = function(id) {
    var node;

    return _(this.children).find(function(child) {
        return child.id === id;
    });
};

module.exports.JsonGraph = JsonGraph;


var Graph = module.exports.Graph = React.createClass({
    getInitialState: function() {
        return {
            leftScrollDisabled: true,
            rightScrollDisabled: true
        };
    },

    // Take a JsonGraph object and convert it to an SVG graph with the Dagre-D3 library.
    // jsonGraph: JsonGraph object containing nodes and edges.
    // graph: Initialized empty Dagre-D3 graph.
    convertGraph: function(jsonGraph, graph) {
        // Convert the nodes
        jsonGraph.children.forEach(function(node) {
            graph.setNode(node.id, {label: node.labels[0].text, rx: 4, ry: 4, class: node.cssClass});
        });

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
        var g = new dagreD3.graphlib.Graph()
            .setGraph({rankdir: "TB"})
            .setDefaultEdgeLabel(function() { return {}; });

        // Convert from given node architecture to the dagre nodes and edges
        this.convertGraph(this.props.graph, g);

        // Run the renderer. This is what draws the final graph.
        var render = new dagreD3.render();
        render(d3.select("svg g"), g);

        // Dagre-D3 has a width and height for the graph.
        // Set the viewbox's and viewport's width and height to that plus a little extra
        var width = g.graph().width;
        var height = g.graph().height;
        svg.attr("width", width + 40).attr("height", height + 40)
            .attr("viewBox", "-20 -20 " + (width + 40) + " " + (height + 40));
    },

    componentDidMount: function () {
        globals.bindEvent(window, 'resize', this.handleResize);

        // Delay loading dagre for Jest testing compatibility;
        // Both D3 and Jest have their own conflicting JSDOM instances
        $script('dagre', function() {
            var d3 = require('d3');
            var dagreD3 = require('dagre-d3');
            var el = this.refs.graphdisplay.getDOMNode();
            this.dagreLoaded = true;

            // Add SVG element to the graph component, and assign it classes, sizes, and a group
            var svg = d3.select(el).insert('svg', '#scroll-buttons')
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

            // Make sure the left and right scroll buttons are enabled/disabled appropriately
            this.scrollHandler();
        }.bind(this));
    },

    // State change; redraw the graph
    componentDidUpdate: function() {
        if (this.dagreLoaded) {
            var el = this.refs.graphdisplay.getDOMNode();
            this.drawGraph(el);
        }
    },

    // Handle window resizing for doing the right thing with scrolling the graph
    handleResize: function() {
        this.scrollHandler();
    },

    componentWillUnmount: function() {
        globals.unbindEvent(window, 'resize', this.handleResize);
    },

    // Handle a click in the left scroll button
    scrollLeftStart: function() {
        this.scrollTimer = null;
        var displayNode = this.refs.graphdisplay.getDOMNode();
        var newScrollLeft = displayNode.scrollLeft - 30;
        if (newScrollLeft > 0) {
            // The graph isn't scrolled all the way left yet; allow more scrolling
            // after a delay
            displayNode.scrollLeft = newScrollLeft;
            this.scrollTimer = setTimeout(this.scrollLeftStart, 100);
        } else {
            // The graph is scrolled all the way to the left; that's it for scrolling
            displayNode.scrollLeft = 0;
        }
    },

    // Handle a click in the right scroll button
    scrollRightStart: function() {
        this.scrollTimer = null;
        var displayNode = this.refs.graphdisplay.getDOMNode();
        var newScrollLeft = displayNode.scrollLeft + 30;
        var svg = document.getElementById('graphsvg');
        var widthDiff = svg.scrollWidth - displayNode.clientWidth;
        if (newScrollLeft < widthDiff) {
            // The graph isn't scrolled all the way right yet; allow more scrolling
            // after a delay
            displayNode.scrollLeft = newScrollLeft;
            this.scrollTimer = setTimeout(this.scrollRightStart, 100);
        } else {
            // The graph is scrolled all the way to the right; that's it for scrolling
            displayNode.scrollLeft = widthDiff;
        }
        console.log('scrollRightStart');
    },

    // Called when the visitor releases the mouse button from either scroll button
    // Cancel the timer if any, and update the scroll button enable/disable state
    scrollStop: function() {
        if (this.scrollTimer) {
            clearTimeout(this.scrollTimer);
            this.scrollTimer = null;
            this.scrollHandler();
        }
    },

    // Handle scrolling either through the scroll buttons or the mouse
    // Only handle if the scroll timer isn't running so that we don't update the
    // display a bunch of times while the visitor's holding down a scroll button
    scrollHandler: function() {
        if (!this.scrollTimer) {
            var leftScrollDisabled = true;
            var rightScrollDisabled = true;
            var container = this.refs.graphdisplay.getDOMNode();
            var svg = document.getElementById('graphsvg');
            var containerWidth = container.clientWidth;
            var svgWidth = svg.scrollWidth;
            if (containerWidth < svgWidth) {
                // The graph is wide enough within the panel to scroll
                // Enable or disable the left or right scroll buttons depending on
                // whether we've scrolled all the way in that direction or not
                leftScrollDisabled = container.scrollLeft === 0;
                rightScrollDisabled = container.scrollLeft >= svgWidth - containerWidth;
            }
            if (this.state.rightScrollDisabled !== rightScrollDisabled) {
                this.setState({rightScrollDisabled: rightScrollDisabled});
            }
            if (this.state.leftScrollDisabled !== leftScrollDisabled) {
                this.setState({leftScrollDisabled: leftScrollDisabled});
            }
        }
    },

    render: function() {
        return (
            <div className="panel-full">
                <div ref="graphdisplay" className="graph-display" onScroll={this.scrollHandler}>
                </div>
                <div id="scroll-buttons">
                    <button className="scroll-graph icon icon-arrow-left" onMouseDown={this.scrollLeftStart}
                        onMouseUp={this.scrollStop} disabled={this.state.leftScrollDisabled}><span className="sr-only">Left</span></button>
                    <button className="scroll-graph icon icon-arrow-right" onMouseDown={this.scrollRightStart}
                        onMouseUp={this.scrollStop} disabled={this.state.rightScrollDisabled}><span className="sr-only">Right</span></button>
                </div>
                {this.props.children}
            </div>
        );
    }
});
