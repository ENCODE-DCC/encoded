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
    this['@type'] = [];
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
    newNode['@type'] = [];
    newNode['@type'][0] = options.type;
    newNode.label = [];
    if (typeof label === 'string' || typeof label === 'number') {
        // label is a string; assign to first array element
        newNode.label[0] = label;
    } else {
        // Otherwise, assume label is an array; clone it
        newNode.label = label.slice(0);
    }
    newNode.metadata = _.clone(options);
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
