import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { svgIcon } from '../libs/svg-icons';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/ui/modal';
import { requestFiles } from './objectutils';
import Status, { sessionToAccessLevel, getObjectStatuses } from './status';


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
    // options: Object containing options to save in the edge that can be used later when displayed
    addEdge(source, target, options) {
        const newEdge = {};
        newEdge.id = '';
        newEdge.source = source;
        newEdge.target = target;
        newEdge.class = options ? options.class : '';
        newEdge.metadata = _.clone(options);
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
            if (nodes[i].nodes.length > 0) {
                const matching = this.getNode(id, nodes[i]);
                if (matching) {
                    return matching;
                }
            }
            if (nodes[i].subnodes && nodes[i].subnodes.length > 0) {
                const matching = nodes[i].subnodes.find((subnode) => id === subnode.id);
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
            if (node.subnodes && node.subnodes.length > 0) {
                for (let j = 0; j < node.subnodes.length; j += 1) {
                    if (node.subnodes[j].id === id) {
                        return node.subnodes[j];
                    }
                }
            } else if (nodes[i].nodes.length > 0) {
                const matching = this.getSubnode(id, nodes[i]);
                if (matching) {
                    return matching;
                }
            }
        }
        return undefined;
    }

    getEdge(source, target) {
        if (this.edges && this.edges.length > 0) {
            const matching = _(this.edges).find((edge) => (
                (source === edge.source) && (target === edge.target)
            ));
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
            if (node.nodes && node.nodes.length > 0) {
                returnArray = returnArray.concat(this.map(fn, context, node.nodes));
            }
        }
        return returnArray;
    }
}


// Handle graphing throws. Exported for Jest tests.
export function GraphException(message, file0, file1) {
    this.message = message;
    if (file0) {
        this.file0 = file0;
    }
    if (file1) {
        this.file1 = file1;
    }
}


// Display the file status legend for the file graph.
const GraphLegend = (props, context) => {
    // Get array of all possible file status strings given the current login state, i.e. logged
    // out, logged in, and logged in as admin.
    const accessLevel = sessionToAccessLevel(context.session, context.session_properties);
    const statusList = getObjectStatuses('File', accessLevel).concat(['status unknown']);

    return (
        <div className="file-status-legend">
            {statusList.map((status) => (
                <Status
                    key={status}
                    item={status}
                    badgeSize="small"
                    css="file-status-legend__status"
                />
            ))}
        </div>
    );
};

GraphLegend.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};


/**
 * Collect CSS styles that apply to the graph and insert them into the given SVG element.
 * @param {domnode} displayedSvg Displayed <svg> node to extract CSS styles.
 * @param {domnode} downloadSvg Downloadable <svg> node to attach extracted CSS styles to.
 */
const attachStyles = (displayedSvg, downloadSvg) => {
    // Get all style sheets matching this domain. This avoids a Chrome crash described in
    // https://medium.com/better-programming/how-to-fix-the-failed-to-read-the-cssrules-property-from-cssstylesheet-error-431d84e4a139
    // This code adapts their solution. `document.styleSheets` is array-like, so convert to
    // array with spread so we can use array methods.
    const sheets = document.styleSheets
        ? (
            [...document.styleSheets].filter((sheet) => (
                !sheet.href || sheet.href.startsWith(window.location.origin)
            ))
        ) : [];

    // Put together a string containing text versions of the CSS rules relevant to the
    // graph by examining CSS style sheets in the DOM.
    const stylesText = sheets.reduce((accStylesText, sheet) => {
        const rules = sheet.cssRules;
        if (rules && rules.length > 0) {
            // Put together a string containing text versions of the CSS rules relevant to the
            // graph by examining the CSS rules in each style sheet. cssRules is array-like, so
            // convert to an array with spread so we can use array methods. Graph-related styles
            // start with '.pipeline-graph'. Leave out '.active' rules so nodes and arrows in the
            // PNG don't show highlights.
            const elementStylesText = [...rules].reduce((accElementStylesText, rule) => {
                if (
                    rule.style
                    && rule.selectorText
                    && rule.selectorText.startsWith('.pipeline-graph')
                    && !rule.selectorText.includes('.active')
                ) {
                    // If any elements use this style, add the style's CSS text to our
                    // style text accumulator.
                    const elems = displayedSvg.querySelectorAll(rule.selectorText);
                    if (elems.length > 0) {
                        return `${accElementStylesText} ${rule.selectorText} { ${rule.style.cssText} } `;
                    }
                }
                return accElementStylesText;
            }, '');
            return `${accStylesText} ${elementStylesText}`;
        }
        return accStylesText;
    }, '');

    // Insert the collected CSS styles into a new style element.
    if (stylesText) {
        const styleEl = document.createElement('style');
        styleEl.setAttribute('type', 'text/css');
        styleEl.innerHTML = `/* <![CDATA[ */\n${stylesText}\n/* ]]> */`;

        // Insert the new style element into the beginning of the given SVG element
        downloadSvg.insertBefore(styleEl, downloadSvg.firstChild);
    }
};


/** Parameter to specify graph drawn for downloading, not for page */
const IS_DOWNLOAD_GRAPH = true;
/** Maximum height of downloadable graph in pixels */
const MAX_DOWNLOAD_GRAPH_HEIGHT = 10000;


/**
 * Display a modal indicating the graph is too tall to download.
 */
const HeightWarning = ({ closeHandler }) => (
    <Modal closeModal={closeHandler}>
        <ModalHeader title="Graph too large" closeModal={closeHandler} />
        <ModalBody>
            <p>The graph is too large to download.</p>
        </ModalBody>
        <ModalFooter closeModal={closeHandler} />
    </Modal>
);

HeightWarning.propTypes = {
    /** Called when the user wants to close the warning */
    closeHandler: PropTypes.func.isRequired,
};


export class Graph extends React.Component {
    /**
     * Take a JsonGraph object and convert it to an SVG graph with the Dagre-D3 library.
     * @param {object} jsonGraph JsonGraph object containing nodes and edges.
     * @param {object} graph Initialized empty Dagre-D3 graph; filled by this function.
     * @param {boolean} hasDecorations True to include any decorations on graph.
     */
    static convertGraph(jsonGraph, graph, hasDecorations) {
        function convertGraphInner(subgraph, parent) {
            // For each node in parent node (or top-level graph)
            parent.nodes.forEach((node) => {
                const nodeOptions = {
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
                };
                if (node.metadata.displayDecoration && hasDecorations) {
                    nodeOptions.decoration = {
                        id: `${node.id}-highlight`,
                        position: 'top',
                        icon: 'arrow-right',
                        class: node.metadata.decorationClass,
                    };
                }
                subgraph.setNode(node.id, nodeOptions);
                if (!parent.root) {
                    subgraph.setParent(node.id, parent.id);
                }
                if (node.nodes.length > 0) {
                    convertGraphInner(subgraph, node);
                }
            });
        }

        // Convert the nodes
        convertGraphInner(graph, jsonGraph);

        // Convert the edges
        jsonGraph.edges.forEach((edge) => {
            graph.setEdge(edge.source, edge.target, { lineInterpolate: 'basis', class: edge.class });
        });
    }

    constructor() {
        super();

        // Set initial React component state.
        this.state = {
            dlDisabled: false, // Download button disabled because of IE
            verticalGraph: false, // True for vertically oriented graph, false for horizontal
            zoomLevel: null, // Graph zoom level; null to indicate not set
            contributingFiles: {}, // List of contributing file objects we've requested; acts as a cache too
            coalescedFiles: [],
            isHeightWarningVisible: false, // True if alert for graph-too-tall visible
        };

        // Component state variables we don't want to cause a rerender.
        this.cv = {
            graph: null, // Currently rendered JSON graph object
            viewBoxWidth: 0, // Width of the SVG's viewBox
            viewBoxHeight: 0, // Height of the SVG's viewBox
            aspectRatio: 0, // Aspect ratio of graph -- width:height
            zoomMouseDown: false, // Mouse currently controlling zoom slider
            dagreLoaded: false, // Dagre JS library has been loaded
            zoomFactor: 0, // Amount zoom slider value changes should change width of graph
        };

        // Bind `this` to non-React methods.
        this.setInitialZoomLevel = this.setInitialZoomLevel.bind(this);
        this.drawGraph = this.drawGraph.bind(this);
        this.bindClickHandlers = this.bindClickHandlers.bind(this);
        this.handleOrientationClick = this.handleOrientationClick.bind(this);
        this.handleDlClick = this.handleDlClick.bind(this);
        this.nodeIdClick = this.nodeIdClick.bind(this);
        this.rangeChange = this.rangeChange.bind(this);
        this.rangeMouseDown = this.rangeMouseDown.bind(this);
        this.rangeMouseUp = this.rangeMouseUp.bind(this);
        this.rangeDoubleClick = this.rangeDoubleClick.bind(this);
        this.changeZoom = this.changeZoom.bind(this);
        this.closeHeightWarning = this.closeHeightWarning.bind(this);
        this.slider = React.createRef();
    }

    componentDidMount() {
        if (this.props.graph) {
            // Delay loading dagre for Jest testing compatibility;
            // Both D3 and Jest have their own conflicting JSDOM instances
            require.ensure(['dagre-d3', 'd3'], (require) => {
                if (this.graphdisplay) {
                    this.d3 = require('d3');
                    this.dagreD3 = require('dagre-d3');

                    const el = this.graphdisplay;

                    // Add SVG element to the graph component, and assign it classes, sizes, and a group
                    const svg = this.d3.select(el).insert('svg', '#graph-node-info')
                        .attr('id', 'pipeline-graph')
                        .attr('class', 'pipeline-graph')
                        .attr('preserveAspectRatio', 'none')
                        .attr('version', '1.1');
                    this.cv.savedSvg = svg;

                    // Draw the graph into the panel; get the graph's view box and save it for
                    // comparisons later
                    const { viewBoxWidth, viewBoxHeight } = this.drawGraph(el, !IS_DOWNLOAD_GRAPH);
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
        }
    }

    // State change; redraw the graph
    /* eslint-disable react/no-did-update-set-state */
    componentDidUpdate() {
        if (this.dagreD3 && !this.cv.zoomMouseDown) {
            const el = this.graphdisplay;
            const { viewBoxWidth, viewBoxHeight } = this.drawGraph(el, !IS_DOWNLOAD_GRAPH);

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
    }
    /* eslint-enable react/no-did-update-set-state */

    handleOrientationClick() {
        this.setState((state) => ({ verticalGraph: !state.verticalGraph }));
    }

    handleDlClick() {
        // Get dimensions of the displayed graph to determine whether it might cause a larger PNG
        // than we can support.
        const { savedSvg } = this.cv;
        const viewBox = savedSvg.attr('viewBox').split(' ');
        const visibleWidth = viewBox[2];
        const visibleHeight = viewBox[3];
        if (visibleHeight > MAX_DOWNLOAD_GRAPH_HEIGHT) {
            // Show an alert for the graph being too big to download.
            this.setState({ isHeightWarningVisible: true });
        } else {
            // Draw a copy of the displayed graph but without decorations into a hidden div at the end
            // of the <body> tag so it can get copied into a <canvas> for downloading. Prepare by
            // inserting a blank temporary SVG into the hidden div.
            const graphDownloadContainer = document.getElementById('graph-download-container');
            this.d3.select(graphDownloadContainer).insert('svg')
                .attr('id', 'graph-download-svg')
                .attr('class', 'pipeline-graph')
                .attr('preserveAspectRatio', 'none')
                .attr('version', '1.1');

            // Copy displayed SVG's coordinates to temporary SVG.
            const downloadSvg = document.getElementById('graph-download-svg');
            downloadSvg.setAttribute('width', visibleWidth);
            downloadSvg.setAttribute('height', visibleHeight);
            downloadSvg.setAttribute('viewBox', viewBox.join(' '));

            // Attach graph CSS to temporary SVG.
            const displayedSvg = savedSvg.node();
            attachStyles(displayedSvg, downloadSvg);

            // Draw graph into hidden div's temporary SVG.
            this.drawGraph(graphDownloadContainer, IS_DOWNLOAD_GRAPH);

            // Turn temporary SVG into a data url and attach to a new Image object. This begins
            // "loading" the image.
            const serializer = new XMLSerializer();
            // https://stackoverflow.com/a/26603875/178550
            const svgXml = unescape(encodeURIComponent(`<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">${serializer.serializeToString(downloadSvg)}`));
            const img = new Image();
            img.onload = () => {
                // Make a new memory-based canvas and draw the temporary SVG into it.
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const canvasContext = canvas.getContext('2d');
                canvasContext.font = '13.6px "Helvetica Neue, sans-serif" bold';
                canvasContext.drawImage(img, 0, 0, img.width, img.height);
                canvas.toBlob((blob) => {
                    // Make the image download by making a fake <a> and pretending to click it.
                    const a = document.createElement('a');
                    a.download = this.props.graph.id ? `${this.props.graph.id}.png` : 'graph.png';
                    a.href = URL.createObjectURL(blob);
                    a.setAttribute('data-bypass', 'true');
                    document.body.appendChild(a);
                    a.click();
                    a.remove();

                    // Empty the hidden div of elements.
                    while (graphDownloadContainer.firstChild) {
                        graphDownloadContainer.removeChild(graphDownloadContainer.firstChild);
                    }
                });
            };

            // Begin the image-loading process. `onload` callback executed when this finishes.
            img.src = `data:image/svg+xml;base64,${window.btoa(svgXml)}`;
        }
    }

    // For the given container element and its svg, calculate an initial zoom level that fits the
    // graph into the container element. Returns the zoom level appropriate for the initial zoom.
    // Also sets component variables for later zoom calculations, and sets the "width" and "height"
    // of the SVG to scale it to fit the container element.
    setInitialZoomLevel(el, svg) {
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
    }

    // Draw the graph on initial draw as well as on state changes. An <svg> element to draw into
    // must already exist in the HTML element in the el parm. This also sets the viewBox of the
    // SVG to its natural height. eslint exception for dagreD3.render call.
    /* eslint new-cap: ["error", { "newIsCap": false }] */
    drawGraph(el, isDownloadGraph) {
        const { d3, dagreD3 } = this;

        // Only clear the old graph if we're updating the displayed graph; not if we're drawing the
        // graph for download.
        if (!isDownloadGraph) {
            d3.selectAll('svg#pipeline-graph > *').remove(); // http://stackoverflow.com/questions/22452112/nvd3-clear-svg-before-loading-new-chart#answer-22453174
        }

        // Clear `width` and `height` attributes if they exist
        const svg = d3.select(el).select('svg');
        svg.attr('width', null).attr('height', null).attr('viewBox', null);

        // Create a new empty graph
        const g = new dagreD3.graphlib.Graph({ multigraph: true, compound: true })
            .setGraph({ rankdir: this.state.verticalGraph ? 'TB' : 'LR' })
            .setDefaultEdgeLabel(() => ({}));
        const render = new dagreD3.render();

        // Convert from given node architecture to the dagre nodes and edges
        Graph.convertGraph(this.props.graph, g, !isDownloadGraph);

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
        svg.attr('viewBox', viewBox.join(' '));

        // Now set the `width` and `height` attributes based on the current zoom level
        if (!isDownloadGraph) {
            // Displayed graph subject to selected zoom factor.
            if (this.state.zoomLevel && this.cv.zoomFactor) {
                const width = (this.state.zoomLevel * this.cv.zoomFactor) + this.cv.minZoomWidth;
                const height = width / this.cv.aspectRatio;
                svg.attr('width', width).attr('height', height);
            }
        } else {
            // Downloaded graph uses unity zoom factor.
            svg.attr('width', viewBoxWidth).attr('height', viewBoxHeight);
        }

        // Return the SVG so callers can do more with this after drawing the unscaled graph
        return { viewBoxWidth, viewBoxHeight };
    }

    nodeIdClick(nodeId, openInfoModal) {
        let node;

        // Find data matching selected node, if any
        if (nodeId) {
            if (nodeId.indexOf('qc:') >= 0) {
                // QC subnode.
                node = this.props.graph.getSubnode(nodeId);
                node.schemas = this.props.schemas;
                this.props.nodeClickHandler(node, openInfoModal);
            } else if (nodeId.indexOf('coalesced:') >= 0) {
                // Coalesced contributing files.
                const coalescedNode = this.props.graph.getNode(nodeId);
                if (coalescedNode) {
                    const currCoalescedFiles = this.state.coalescedFiles;
                    if (currCoalescedFiles[coalescedNode.metadata.contributing]) {
                        // We have the requested coalesced files in the cache, so just display
                        // them.
                        coalescedNode.metadata.coalescedFiles = currCoalescedFiles[coalescedNode.metadata.contributing];
                        this.props.nodeClickHandler(coalescedNode, openInfoModal);
                    } else if (!this.contributingRequestOutstanding) {
                        // We don't have the requested coalesced files in the cache, so we have to
                        // request them from the DB.
                        this.contributingRequestOutstanding = true;
                        requestFiles(coalescedNode.metadata.ref).then((contributingFiles) => {
                            this.contributingRequestOutstanding = false;
                            currCoalescedFiles[coalescedNode.metadata.contributing] = contributingFiles;
                            coalescedNode.metadata.coalescedFiles = contributingFiles;
                            this.props.nodeClickHandler(coalescedNode, openInfoModal);
                        }).catch(() => {
                            this.contributingRequestOutstanding = false;
                            currCoalescedFiles[coalescedNode.metadata.contributing] = [];
                            node = null;
                        });
                    }
                }
            } else {
                // A regular or contributing file.
                node = this.props.graph.getNode(nodeId);
                if (node) {
                    node.schemas = this.props.schemas;
                    if (node.metadata.contributing) {
                        // This is a contributing file, and its @id is in
                        // node.metadata.contributing. See if the file is in the cache.
                        const currContributing = this.state.contributingFiles;
                        if (currContributing[node.metadata.contributing]) {
                            // We have this file's object in the cache, so just display it.
                            node.metadata.ref = currContributing[node.metadata.contributing];
                            this.props.nodeClickHandler(node, openInfoModal);
                        } else if (!this.contributingRequestOutstanding) {
                            // We don't have this file's object in the cache, so request it from
                            // the DB.
                            this.contributingRequestOutstanding = true;
                            requestFiles([node.metadata.contributing]).then((contributingFile) => {
                                this.contributingRequestOutstanding = false;
                                currContributing[node.metadata.contributing] = contributingFile[0];
                                node.metadata.ref = contributingFile[0];
                                this.props.nodeClickHandler(node, openInfoModal);
                            }).catch(() => {
                                this.contributingRequestOutstanding = false;
                                currContributing[node.metadata.contributing] = {};
                            });
                        }
                    } else {
                        this.props.nodeClickHandler(node, openInfoModal);
                    }
                }
            }
        }
    }

    bindClickHandlers(d3, el) {
        // Add click event listeners to each node. The `nodeId` parameters contain the IDs kept in
        // our JSON graph structure, and attached to each node by d3.
        const svg = d3.select(el);
        const nodes = svg.selectAll('g.node > rect, g.node > g.stack');
        const subnodes = svg.selectAll('g.subnode circle');
        const highlights = svg.selectAll('g.node > g.decoration');

        // Attach click handler to arrow-highlighting toggle decorations.
        highlights.on('click', (nodeId) => {
            this.nodeIdClick(nodeId, false);
        });

        // Attach click handler to file and step nodes.
        nodes.on('click', (nodeId) => {
            this.nodeIdClick(nodeId, true);
        });

        // Attach click handler to QC bubbles.
        subnodes.on('click', (subnode) => {
            d3.event.stopPropagation();
            this.nodeIdClick(subnode.id, true);
        });
    }

    rangeChange(e) {
        // Called when the user clicks/drags the zoom slider; value comes from the slider 0-100
        const { value } = e.target;

        // Calculate the new graph width and height for the new zoom value
        const width = (value * this.cv.zoomFactor) + this.cv.minZoomWidth;
        const height = width / this.cv.aspectRatio;

        // Get the SVG in the DOM and update its width and height
        const svgEl = document.getElementById('pipeline-graph');
        svgEl.setAttribute('width', width);
        svgEl.setAttribute('height', height);

        // Remember zoom level as a state -- causes rerender remember!
        this.setState({ zoomLevel: value });
    }

    rangeMouseDown() {
        // Mouse clicked in zoom slider
        this.cv.zoomMouseDown = true;
    }

    rangeMouseUp(e) {
        // Mouse released from zoom slider
        this.cv.zoomMouseDown = false;
        this.rangeChange(e); // Fix for IE11 as onChange doesn't get called; at least call this after dragging
        // For IE11 fix, see https://github.com/facebook/react/issues/554#issuecomment-188288228
    }

    rangeDoubleClick() {
        // Handle a double click in the zoom slider
        const el = this.graphdisplay;
        const zoomLevel = this.setInitialZoomLevel(el, this.cv.savedSvg);
        this.setState({ zoomLevel });
    }

    /**
    * Changes the graph's zoom base on a provided value.
    *
    * @param {Number} change Positive number for increase in range, negative number for a decrease
    * @returns undefined
    * @memberof Graph
    */
    changeZoom(change) {
        const currentValue = Number(this.slider.current.value) || 0;
        let newValue = currentValue + change;

        // normalize value if outside range (0 - 100)
        if (newValue < 0 || newValue > 100) {
            newValue = newValue < 0 ? 0 : 100;
        }
        this.slider.current.value = newValue.toString();
        const event = new Event('input', { bubbles: true });
        this.slider.current.dispatchEvent(event);
    }

    /**
     * Called when the user wants to close the height-warning modal.
     */
    closeHeightWarning() {
        this.setState({ isHeightWarningVisible: false });
    }

    render() {
        const { graph, colorize } = this.props;
        const orientBtnAlt = `Orient graph ${this.state.verticalGraph ? 'horizontally' : 'vertically'}`;
        const currOrientKey = this.state.verticalGraph ? 'orientH' : 'orientV';

        if (graph) {
            return (
                <div>
                    <div className="zoom-control-area">
                        <table className="zoom-control">
                            <tbody>
                                <tr>
                                    <td className="zoom-indicator"><button type="button" onClick={() => this.changeZoom(-6)}><span className="sr-only">Zoom out</span><i className="icon icon-minus" /></button></td>
                                    <td className="zomm-controller"><input type="range" className="zoom-slider" ref={this.slider} min={minZoom} max={maxZoom} value={this.state.zoomLevel === null ? 0 : this.state.zoomLevel} onChange={this.rangeChange} onInput={this.rangeChange} onDoubleClick={this.rangeDoubleClick} onMouseUp={this.rangeMouseUp} onMouseDown={this.rangeMouseDown} /></td>
                                    <td className="zoom-indicator"><button type="button" onClick={() => this.changeZoom(6)}><span className="sr-only">Zoom in</span><i className="icon icon-plus" /></button></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div ref={(div) => { this.graphdisplay = div; }} className="graph-display" onScroll={this.scrollHandler} />
                    {colorize ? <GraphLegend /> : null}
                    <div className="graph-dl">
                        <button type="button" className="btn btn-info btn-sm btn-orient" title={orientBtnAlt} onClick={this.handleOrientationClick}>{svgIcon(currOrientKey)}<span className="sr-only">{orientBtnAlt}</span></button>
                        <button type="button" ref={(button) => { this.dlButton = button; }} className="btn btn-info btn-sm" value="Test" onClick={this.handleDlClick} disabled={this.state.dlDisabled}>Download Graph</button>
                    </div>
                    {this.props.children}
                    <div id="graph-download-container" />
                    {this.state.isHeightWarningVisible ? <HeightWarning closeHandler={this.closeHeightWarning} /> : null}
                </div>
            );
        }

        return <p className="browser-error">Graph not applicable.</p>;
    }
}

Graph.propTypes = {
    graph: PropTypes.object.isRequired, // JsonGraph object representing the graph being rendered.
    nodeClickHandler: PropTypes.func.isRequired, // Function to call to handle clicks in a node
    schemas: PropTypes.object, // Schemas for QC metrics
    colorize: PropTypes.bool, // True if file graph status colorization is turned on, and a legend is needed
    children: PropTypes.node,
};

Graph.defaultProps = {
    schemas: null,
    colorize: false,
    children: null,
};

Graph.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};
