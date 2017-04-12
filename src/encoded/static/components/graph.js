import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Panel } from '../libs/bootstrap/panel';
import { BrowserFeat } from './browserfeat';
import { svgIcon } from '../libs/svg-icons';


// Zoom slider constants
const minZoom = 0; // Minimum zoom slider level
const maxZoom = 100; // Maximum zoom slider level
const graphWidthMargin = 40; // Margin on horizontal edges of graph SVG
const graphHeightMargin = 40; // Margin on vertical edges of graph SVG


// The JsonGraph object helps build JSON graph objects. Create a new object
// with the constructor, then add edges and nodes with the methods.
// This merges the hierarchical structure from the JSON Graph structure described in:
// http://rtsys.informatik.uni-kiel.de/confluence/display/KIELER/JSON+Graph+Format
// and the overall structure of https://github.com/jsongraph/json-graph-specification.
// In this implementation, all edges are in the root object, not in the nodes array.
// This allows edges to cross between children and parents.

export class JsonGraph {

    constructor(id) {
        this.id = id;
        this.root = true;
        this['@type'] = [];
        this.label = [];
        this.shape = '';
        this.metadata = {};
        this.nodes = [];
        this.edges = [];
        this.subnodes = [];
    }

    // Add node to the graph architecture. The caller must keep track that all node IDs
    // are unique -- this code doesn't verify this.
    // id: uniquely identify the node
    // label: text to display in the node; it can be an array to display a list of labels
    // options: Object containing options to save in the node that can be used later when displayed
    // subnodes: Array of nodes to use as subnodes of a regular node.
    addNode(id, label, options, subnodes) {
        const newNode = {};
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
        newNode.subnodes = subnodes;
        const target = (options.parentNode && options.parentNode.nodes) || this.nodes;
        target.push(newNode);
    }

    // Add edge to the graph architecture
    // source: ID of node for the edge to originate; corresponds to 'id' parm of addNode
    // target: ID of node for the edge to terminate
    addEdge(source, target) {
        const newEdge = {};
        newEdge.id = '';
        newEdge.source = source;
        newEdge.target = target;
        this.edges.push(newEdge);
    }

    // Return the JSON graph node matching the given ID. This function finds the node
    // regardless of where it is in the hierarchy of nodes.
    // id: ID of the node to search for
    // parent: Optional parent node to begin the search; graph root by default
    getNode(id, parent) {
        const nodes = (parent && parent.nodes) || this.nodes;

        for (let i = 0; i < nodes.length; i += 1) {
            if (nodes[i].id === id) {
                return nodes[i];
            }
            if (nodes[i].nodes.length) {
                const matching = this.getNode(id, nodes[i]);
                if (matching) {
                    return matching;
                }
            }
            if (nodes[i].subnodes && nodes[i].subnodes.length) {
                const matching = nodes[i].subnodes.find(subnode => id === subnode.id);
                if (matching) {
                    return matching;
                }
            }
        }
        return undefined;
    }

    getSubnode(id, parent) {
        const nodes = (parent && parent.nodes) || this.nodes;

        for (let i = 0; i < nodes.length; i += 1) {
            const node = nodes[i];
            if (node.subnodes && node.subnodes.length) {
                for (let j = 0; j < node.subnodes.length; j += 1) {
                    if (node.subnodes[j].id === id) {
                        return node.subnodes[j];
                    }
                }
            } else if (nodes[i].nodes.length) {
                const matching = this.getSubnode(id, nodes[i]);
                if (matching) {
                    return matching;
                }
            }
        }
        return undefined;
    }

    getEdge(source, target) {
        if (this.edges && this.edges.length) {
            const matching = _(this.edges).find(edge =>
                (source === edge.source) && (target === edge.target)
            );
            return matching;
        }
        return undefined;
    }

    // Return array of function results for each node in the graph. The supplied function, fn, gets called with each node
    // in the graph. An array of these function results is returned.
    map(fn, context, nodes) {
        const thisNodes = nodes || this.nodes;
        let returnArray = [];

        for (let i = 0; i < thisNodes.length; i += 1) {
            const node = thisNodes[i];

            // Call the given function and add its return value to the array we're collecting
            returnArray.push(fn.call(context, node));

            // If the node has its own nodes, recurse
            if (node.nodes && node.nodes.length) {
                returnArray = returnArray.concat(this.map(fn, context, node.nodes));
            }
        }
        return returnArray;
    }

}


export const Graph = React.createClass({
    propTypes: {
        graph: PropTypes.object, // JSON graph object to render
        nodeClickHandler: PropTypes.func, // Function to call to handle clicks in a node
        noDefaultClasses: PropTypes.bool, // True to supress default CSS classes on <Panel> components
        children: PropTypes.node,
    },

    getInitialState: () => ({
        dlDisabled: false, // Download button disabled because of IE
        verticalGraph: false, // True for vertically oriented graph, false for horizontal
        zoomLevel: null, // Graph zoom level; null to indicate not set
    }),

    componentDidMount: function () {
        if (BrowserFeat.getBrowserCaps('svg')) {
            // Delay loading dagre for Jest testing compatibility;
            // Both D3 and Jest have their own conflicting JSDOM instances
            require.ensure(['dagre-d3', 'd3'], (require) => {
                if (this.refs.graphdisplay) {
                    this.d3 = require('d3');
                    this.dagreD3 = require('dagre-d3');

                    const el = this.refs.graphdisplay;

                    // Add SVG element to the graph component, and assign it classes, sizes, and a group
                    const svg = this.d3.select(el).insert('svg', '#graph-node-info')
                        .attr('id', 'pipeline-graph')
                        .attr('preserveAspectRatio', 'none')
                        .attr('version', '1.1');
                    this.cv.savedSvg = svg;

                    // Draw the graph into the panel; get the graph's view box and save it for
                    // comparisons later
                    const { viewBoxWidth, viewBoxHeight } = this.drawGraph(el);
                    this.cv.viewBoxWidth = viewBoxWidth;
                    this.cv.viewBoxHeight = viewBoxHeight;

                    // Based on the size of the graph and view box, set the initial zoom level to
                    // something that fits well.
                    const initialZoomLevel = this.setInitialZoomLevel(el, svg);
                    this.setState({ zoomLevel: initialZoomLevel });

                    // Bind node/subnode click handlers to parent component handlers
                    this.bindClickHandlers(this.d3, el);
                }
            });
        } else {
            // Output text indicating that graphs aren't supported.
            let el = this.refs.graphdisplay;
            const para = document.createElement('p');
            para.className = 'browser-error';
            para.innerHTML = 'Graphs not supported in your browser. You need a more modern browser to view it.';
            el.appendChild(para);

            // Disable the download button
            el = this.refs.dlButton;
            el.setAttribute('disabled', 'disabled');
        }

        // Disable download button if running on Trident (IE non-Spartan) browsers
        if (BrowserFeat.getBrowserCaps('uaTrident') || BrowserFeat.getBrowserCaps('uaEdge')) {
            this.setState({ dlDisabled: true });
        }
    },

    // State change; redraw the graph
    componentDidUpdate: function () {
        if (this.dagreD3 && !this.cv.zoomMouseDown) {
            const el = this.refs.graphdisplay; // Change in React 0.14
            const { viewBoxWidth, viewBoxHeight } = this.drawGraph(el);

            // Bind node/subnode click handlers to parent component handlers
            this.bindClickHandlers(this.d3, el);

            // If the viewbox has changed since the last time, need to recalculate the zooming
            // parameters.
            if (Math.abs(viewBoxWidth - this.cv.viewBoxWidth) > 10 || Math.abs(viewBoxHeight - this.cv.viewBoxHeight) > 10) {
                // Based on the size of the graph and view box, set the initial zoom level to
                // something that fits well.
                const initialZoomLevel = this.setInitialZoomLevel(el, this.cv.savedSvg);
                this.setState({ zoomLevel: initialZoomLevel });
            }

            this.cv.viewBoxWidth = viewBoxWidth;
            this.cv.viewBoxHeight = viewBoxHeight;
        }
    },

    // For the given container element and its svg, calculate an initial zoom level that fits the
    // graph into the container element. Returns the zoom level appropriate for the initial zoom.
    // Also sets component variables for later zoom calculations, and sets the "width" and "height"
    // of the SVG to scale it to fit the container element.
    setInitialZoomLevel: function (el, svg) {
        let svgWidth;
        let svgHeight;
        const viewBox = svg.attr('viewBox').split(' ');
        const viewBoxWidth = viewBox[2];
        const viewBoxHeight = viewBox[3];

        // Calculate minimum and maximum pixel width, and zoom factor which is the amount each
        // slider value gets multiplied by to get a new graph width. Save all these in component
        // variables.
        const minZoomWidth = viewBoxWidth / 4;
        const maxZoomWidth = viewBoxWidth * 2;
        this.cv.zoomFactor = (maxZoomWidth - minZoomWidth) / 100;
        this.cv.minZoomWidth = minZoomWidth;
        this.cv.aspectRatio = viewBoxWidth / viewBoxHeight;

        // Get the width of the graph panel
        if (el.clientWidth >= viewBoxWidth) {
            svgWidth = viewBoxWidth;
            svgHeight = viewBoxHeight;
        } else {
            svgWidth = el.clientWidth;
            svgHeight = svgWidth / this.cv.aspectRatio;
        }
        const zoomLevel = (svgWidth - this.cv.minZoomWidth) / this.cv.zoomFactor;
        svg.attr('width', svgWidth).attr('height', svgHeight);
        return zoomLevel;
    },

    // Take a JsonGraph object and convert it to an SVG graph with the Dagre-D3 library.
    // jsonGraph: JsonGraph object containing nodes and edges.
    // graph: Initialized empty Dagre-D3 graph.
    convertGraph: function (jsonGraph, graph) {
        // graph: dagre graph object
        // parent: JsonGraph node to insert nodes into
        function convertGraphInner(subgraph, parent) {
            // For each node in parent node (or top-level graph)
            parent.nodes.forEach((node) => {
                subgraph.setNode(node.id, {
                    label: node.label.length > 1 ? node.label : node.label[0],
                    rx: node.metadata.cornerRadius,
                    ry: node.metadata.cornerRadius,
                    class: node.metadata.cssClass,
                    shape: node.metadata.shape,
                    paddingLeft: '20',
                    paddingRight: '20',
                    paddingTop: '10',
                    paddingBottom: '10',
                    subnodes: node.subnodes,
                });
                if (!parent.root) {
                    subgraph.setParent(node.id, parent.id);
                }
                if (node.nodes.length) {
                    convertGraphInner(subgraph, node);
                }
            });
        }

        // Convert the nodes
        convertGraphInner(graph, jsonGraph);

        // Convert the edges
        jsonGraph.edges.forEach((edge) => {
            graph.setEdge(edge.source, edge.target, { lineInterpolate: 'basis' });
        });
    },

    // Draw the graph on initial draw as well as on state changes. An <svg> element to draw into
    // must already exist in the HTML element in the el parm. This also sets the viewBox of the
    // SVG to its natural height. eslint exception for dagreD3.render call.
    /* eslint new-cap: ["error", { "newIsCap": false }] */
    drawGraph: function (el) {
        const d3 = this.d3;
        const dagreD3 = this.dagreD3;
        d3.selectAll('svg#pipeline-graph > *').remove(); // http://stackoverflow.com/questions/22452112/nvd3-clear-svg-before-loading-new-chart#answer-22453174
        const svg = d3.select(el).select('svg');

        // Clear `width` and `height` attributes if they exist
        svg.attr('width', null).attr('height', null).attr('viewBox', null);

        // Create a new empty graph
        const g = new dagreD3.graphlib.Graph({ multigraph: true, compound: true })
            .setGraph({ rankdir: this.state.verticalGraph ? 'TB' : 'LR' })
            .setDefaultEdgeLabel(() => ({}));
        const render = new dagreD3.render();

        // Convert from given node architecture to the dagre nodes and edges
        this.convertGraph(this.props.graph, g);

        // Run the renderer. This is what draws the final graph.
        render(svg, g);

        // Get the natural (unscaled) width and height of the graph
        const graphWidth = Math.ceil(g.graph().width);
        const graphHeight = Math.ceil(g.graph().height);

        // Get the unscaled width and height of the graph including margins, and make a viewBox
        // for the graph so it'll render with the margins. The SVG's viewBox is always the
        // unscaled coordinates and immutable
        const viewBoxWidth = graphWidth + (graphWidthMargin * 2);
        const viewBoxHeight = graphHeight + (graphHeightMargin * 2);
        const viewBox = [-graphWidthMargin, -graphHeightMargin, viewBoxWidth, viewBoxHeight];

        // Set the viewBox of the SVG based on its unscaled extents
        this.cv.savedSvg.attr('viewBox', viewBox.join(' '));

        // Now set the `width` and `height` attributes based on the current zoom level
        if (this.state.zoomLevel && this.cv.zoomFactor) {
            const width = (this.state.zoomLevel * this.cv.zoomFactor) + this.cv.minZoomWidth;
            const height = width / this.cv.aspectRatio;
            svg.attr('width', width).attr('height', height);
        }

        // Return the SVG so callers can do more with this after drawing the unscaled graph
        return { viewBoxWidth: viewBoxWidth, viewBoxHeight: viewBoxHeight };
    },

    bindClickHandlers: function (d3, el) {
        // Add click event listeners to each node rendering. Node's ID is its ENCODE object ID
        const svg = d3.select(el);
        const nodes = svg.selectAll('g.node');
        const subnodes = svg.selectAll('g.subnode circle');

        nodes.on('click', (nodeId) => {
            this.props.nodeClickHandler(nodeId);
        });
        subnodes.on('click', (subnode) => {
            d3.event.stopPropagation();
            this.props.nodeClickHandler(subnode.id);
        });
    },

    handleOrientationClick: function () {
        this.setState({ verticalGraph: !this.state.verticalGraph });
    },

    handleDlClick: function () {
        // Collect CSS styles that apply to the graph and insert them into the given SVG element
        function attachStyles(el) {
            let stylesText = '';
            const sheets = document.styleSheets;

            // Search every style in the style sheet(s) for those applying to graphs.
            // Note: Not using ES5 looping constructs because these aren’t real arrays.
            if (sheets) {
                for (let i = 0; i < sheets.length; i += 1) {
                    const rules = sheets[i].cssRules;
                    if (rules) {
                        for (let j = 0; j < rules.length; j += 1) {
                            const rule = rules[j];

                            // If a style rule starts with 'g.' (svg group), we know it applies to the graph.
                            // Note: In some browsers, indexOf is a bit faster; on others substring is a bit faster.
                            // FF(31)'s substring is much faster than indexOf.
                            if (typeof (rule.style) !== 'undefined' && rule.selectorText && rule.selectorText.substring(0, 2) === 'g.') {
                                // If any elements use this style, add the style's CSS text to our style text accumulator.
                                const elems = el.querySelectorAll(rule.selectorText);
                                if (elems.length) {
                                    stylesText += `${rule.selectorText} { ${rule.style.cssText} }\n`;
                                }
                            }
                        }
                    }
                }
            }

            // Insert the collected SVG styles into a new style element
            const styleEl = document.createElement('style');
            styleEl.setAttribute('type', 'text/css');
            styleEl.innerHTML = `/* <![CDATA[ */\n${stylesText}\n/* ]]> */`;

            // Insert the new style element into the beginning of the given SVG element
            el.insertBefore(styleEl, el.firstChild);
        }

        // Going to be manipulating the SVG node, so make a clone to make GC’s job harder
        const svgNode = this.cv.savedSvg.node().cloneNode(true);

        // Reset the SVG's size to its natural size
        const viewBox = this.cv.savedSvg.attr('viewBox').split(' ');
        svgNode.setAttribute('width', viewBox[2]);
        svgNode.setAttribute('height', viewBox[3]);

        // Attach graph CSS to SVG node clone
        attachStyles(svgNode);

        // Turn SVG node clone into a data url and attach to a new Image object. This begins "loading" the image.
        const serializer = new XMLSerializer();
        const svgXml = `<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">${serializer.serializeToString(svgNode)}`;
        const img = new Image();
        img.src = `data:image/svg+xml;base64,${window.btoa(svgXml)}`;

        // Once the svg is loaded into the image (purely in memory, not in DOM), draw it into a <canvas>
        img.onload = function () {
            // Make a new memory-based canvas and draw the image into it.
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            const context = canvas.getContext('2d');
            context.drawImage(img, 0, 0, img.width, img.height);

            // Make the image download by making a fake <a> and pretending to click it.
            const a = document.createElement('a');
            a.download = this.props.graph.id ? `${this.props.graph.id}.png` : 'graph.png';
            a.href = canvas.toDataURL('image/png');
            a.setAttribute('data-bypass', 'true');
            document.body.appendChild(a);
            a.click();
        }.bind(this);
    },

    rangeChange: function (e) {
        // Called when the user clicks/drags the zoom slider; value comes from the slider 0-100
        const value = e.target.value;

        // Calculate the new graph width and height for the new zoom value
        const width = (value * this.cv.zoomFactor) + this.cv.minZoomWidth;
        const height = width / this.cv.aspectRatio;

        // Get the SVG in the DOM and update its width and height
        const svgEl = document.getElementById('pipeline-graph');
        svgEl.setAttribute('width', width);
        svgEl.setAttribute('height', height);

        // Remember zoom level as a state -- causes rerender remember!
        this.setState({ zoomLevel: value });
    },

    rangeMouseDown: function () {
        // Mouse clicked in zoom slider
        this.cv.zoomMouseDown = true;
    },

    rangeMouseUp: function (e) {
        // Mouse released from zoom slider
        this.cv.zoomMouseDown = false;
        this.rangeChange(e); // Fix for IE11 as onChange doesn't get called; at least call this after dragging
        // For IE11 fix, see https://github.com/facebook/react/issues/554#issuecomment-188288228
    },

    rangeDoubleClick: function () {
        // Handle a double click in the zoom slider
        const el = this.refs.graphdisplay;
        const zoomLevel = this.setInitialZoomLevel(el, this.cv.savedSvg);
        this.setState({ zoomLevel: zoomLevel });
    },

    // Component state variables we don't want to cause a rerender
    cv: {
        viewBoxWidth: 0, // Width of the SVG's viewBox
        viewBoxHeight: 0, // Height of the SVG's viewBox
        aspectRatio: 0, // Aspect ratio of graph -- width:height
        zoomMouseDown: false, // Mouse currently controlling zoom slider
        dagreLoaded: false, // Dagre JS library has been loaded
        zoomFactor: 0, // Amount zoom slider value changes should change width of graph
    },

    render: function () {
        const orientBtnAlt = `Orient graph ${this.state.verticalGraph ? 'horizontally' : 'vertically'}`;
        const currOrientKey = this.state.verticalGraph ? 'orientH' : 'orientV';
        const noDefaultClasses = this.props.noDefaultClasses;

        return (
            <Panel noDefaultClasses={noDefaultClasses}>
                <div className="zoom-control-area">
                    <table className="zoom-control">
                        <tbody>
                            <tr>
                                <td className="zoom-indicator"><i className="icon icon-minus" /></td>
                                <td className="zomm-controller"><input type="range" className="zoom-slider" min={minZoom} max={maxZoom} value={this.state.zoomLevel === null ? 0 : this.state.zoomLevel} onChange={this.rangeChange} onDoubleClick={this.rangeDoubleClick} onMouseUp={this.rangeMouseUp} onMouseDown={this.rangeMouseDown} /></td>
                                <td className="zoom-indicator"><i className="icon icon-plus" /></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div ref="graphdisplay" className="graph-display" onScroll={this.scrollHandler} />
                <div className="graph-dl clearfix">
                    <button className="btn btn-info btn-sm btn-orient" title={orientBtnAlt} onClick={this.handleOrientationClick}>{svgIcon(currOrientKey)}<span className="sr-only">{orientBtnAlt}</span></button>
                    <button ref="dlButton" className="btn btn-info btn-sm" value="Test" onClick={this.handleDlClick} disabled={this.state.dlDisabled}>Download Graph</button>
                </div>
                {this.props.children}
            </Panel>
        );
    },
});
