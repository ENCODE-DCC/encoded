import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody } from '../libs/ui/panel';
import { MATRIX_VISUALIZE_LIMIT } from './matrix';
import { MatrixBadges } from './objectutils';
import { SearchControls } from './search';
import * as globals from './globals';

const fullHeight = 500;
const margin = { top: 40, right: 0, bottom: 50, left: 0 };

const ellipseSettings = [
    { cx: 2, cy: 2, rx: 12, ry: 9, stroke: 'black', 'stroke-width': 1 },
    { cx: 2, cy: 2, rx: 6.5, ry: 6, stroke: 'black', 'stroke-width': 1 },
    { cx: -5, cy: 10, rx: 12, ry: 9, stroke: 'black', 'stroke-width': 1 },
    { cx: -5, cy: 10, rx: 6.5, ry: 5, stroke: 'black', 'stroke-width': 1 },
    { cx: 10, cy: 10, rx: 12, ry: 9, stroke: 'black', 'stroke-width': 1 },
    { cx: 10, cy: 10, rx: 6.5, ry: 5, stroke: 'black', 'stroke-width': 1 },
];

/**
 * Render the area above the matrix itself, including the page title.
 *
 * @param {object} { context }
 * @returns
 */
const MatrixHeader = ({ context }) => {
    const visualizeDisabledTitle = context.total > MATRIX_VISUALIZE_LIMIT ? `Filter to ${MATRIX_VISUALIZE_LIMIT} to visualize` : '';

    return (
        <div className="matrix-header">
            <div className="matrix-header__title">
                <div className="matrix-title-badge">
                    <h1>{context.title}</h1>
                    <MatrixBadges context={context} />
                </div>
                <div className="matrix-description">
                    <div className="matrix-description__text">
                        Project data of the epigenomic profiles of cell types differentiated from the H9 cell line provided by the Southeast Stem Cell Consortium (SESCC).
                    </div>
                </div>
            </div>
            <div className="matrix-header__controls">
                <div className="matrix-header__search-controls-sescc">
                    <SearchControls context={context} visualizeDisabledTitle={visualizeDisabledTitle} hideBrowserSelector showDownloadButton={false} />
                </div>
            </div>
        </div>
    );
};

MatrixHeader.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};


MatrixHeader.contextTypes = {
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

// Collapse node and its children
function collapse(d) {
    if (d.children) {
        d._children = d.children;
        d._children.forEach(collapse);
        d.children = null;
    }
}

// Creates a curved (diagonal) path from parent to the child nodes
function diagonal(d, s) {
    const path = `M${d.x},${d.y}C${d.x},${(d.y + s.y) / 2} ${s.x},${(d.y + s.y) / 2} ${s.x},${s.y}`;
    return path;
}

// function diagonal(s, d) {
//     const path = `M ${s.y} ${s.x}
//             C ${(s.y + d.y) / 2} ${s.x},
//               ${(s.y + d.y) / 2} ${d.x},
//               ${d.y} ${d.x}`;
//     return path;
// }

// function update(source) {
//     // adds the links between the nodes
//     g.selectAll('.link')
//         .data(nodes.descendants().slice(1))
//         .enter().append('path')
//         .attr('class', 'link')
//         .attr('d', (d) => `M${d.x},${d.y}C${d.x},${(d.y + d.parent.y) / 2} ${d.parent.x},${(d.y + d.parent.y) / 2} ${d.parent.x},${d.parent.y}`);
//
//     // adds each node as a group
//     const node = g.selectAll('.node')
//         .data(nodes.descendants())
//         .enter().append('g')
//         .attr('class', (d) => `node${d.children ? ' node--internal' : ' node--leaf'}`)
//         .attr('transform', (d) => `translate(${d.x},${d.y})`);
//
//     // adds the text to the node
//     node.append('text')
//         .attr('dy', '.35em')
//         .attr('y', (d) => (d.children ? -20 : 30))
//         .style('text-anchor', 'middle')
//         .text((d) => d.data.name);
//
//     const nodeGroup = node.append('g')
//         .attr('class', 'cell-group')
//         .on('mouseover', function() {
//             d3.select(this).selectAll('ellipse').style('fill', '#d2d2d2');
//             d3.select(this).selectAll('ellipse').style('transform', 'scale(1.2)');
//         })
//         .on('mouseout', function() {
//             d3.select(this).selectAll('ellipse').style('fill', 'white');
//             d3.select(this).selectAll('ellipse').style('transform', 'scale(1)');
//         });
//
//     ellipseSettings.forEach((ellipseSetting) => {
//         nodeGroup.append('ellipse')
//             .attr('cx', ellipseSetting.cx)
//             .attr('cy', ellipseSetting.cy)
//             .attr('rx', ellipseSetting.rx)
//             .attr('ry', ellipseSetting.ry)
//             .style('stroke', ellipseSetting.stroke)
//             .style('stroke-width', 1)
//             .style('fill', 'white')
//             .attr('class', () => 'js-cell');
//     });
// }

const drawTree = (d3, data, fullWidth) => {
    const treeData = data[0];

    // Set the dimensions and margins of the diagram
    const width = fullWidth - margin.left - margin.right;
    const height = fullHeight - margin.top - margin.bottom;

    // append the svg object to the body of the page
    // appends a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    const svg = d3.select('.vertical-node-graph').append('svg')
        .attr('width', fullWidth)
        .attr('height', fullHeight)
        .attr('viewBox', `0 0 ${fullWidth} ${fullHeight}`)
        .attr('preserveAspectRatio', 'xMidYMin meet')
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    let i = 0;
    const duration = 750;

    // declares a tree layout and assigns the size
    const treemap = d3.tree().size([width, height]);

    // Assigns parent, children, height, depth
    const root = d3.hierarchy(treeData, (d) => d.children);
    root.x0 = width / 2;
    root.y0 = 100;

    // Collapse after the second level
    root.children.forEach(collapse);
    update(root);

    function update(source) {
        // Assigns the x and y position for the nodes
        const treeData = treemap(root);

        // Compute the new tree layout.
        const nodes = treeData.descendants();
        const links = treeData.descendants().slice(1);
        const nodeDepth = nodes.map((n) => n.depth);
        const maxNodeDepth = Math.max(...nodeDepth);

        // Normalize for fixed-depth.
        nodes.forEach(function(d) {
            if (d.depth === 0) {
                d.y = d.depth * 100;
            } else {
                d.y = d.depth * height / maxNodeDepth;
            }
        });

        const node = svg.selectAll('g.node')
            .data(nodes, function(d) {return d.id || (d.id = ++i); });

        // Enter any new modes at the parent's previous position.
        const nodeEnter = node.enter().append('g')
            .attr('class', 'node')
            .attr('transform', function(d) {
                return "translate(" + source.x0 + "," + source.y0 + ")";
            })
            .on('click', click);

        const nodeGroup = nodeEnter.append('g')
            .attr('class', (d) => (d._children ? 'js-cell parent-cell' : 'js-cell'))
            .on('mouseover', function() {
                d3.select(this).selectAll('ellipse').style('transform', 'scale(1.2)');
                d3.select(this).selectAll('ellipse').attr('class', 'hover-class');
            })
            .on('mouseout', function() {
                d3.select(this).selectAll('ellipse').style('transform', 'scale(1)');
                d3.select(this).selectAll('ellipse').attr('class', '');
            });

        ellipseSettings.forEach((ellipseSetting) => {
            nodeGroup.append('ellipse')
                .attr('cx', ellipseSetting.cx)
                .attr('cy', ellipseSetting.cy)
                .attr('rx', ellipseSetting.rx)
                .attr('ry', ellipseSetting.ry)
                .style('stroke', ellipseSetting.stroke)
                .style('stroke-width', 1)
                // .style('fill', (d) => (d._children ? 'lightsteelblue' : '#fff'))
                .attr('class', () => 'js-cell');
        });

        // adds the text to the node
        nodeEnter.append('text')
            .attr('dy', '.35em')
            .attr('y', (d) => (d.children ? -20 : 30))
            .style('text-anchor', 'middle')
            .text((d) => d.data.name);

        // UPDATE
        const nodeUpdate = nodeEnter.merge(node);

        // Transition to the proper position for the node
        nodeUpdate.transition()
            .duration(duration)
            .attr('transform', function(d) {
                return "translate(" + d.x + "," + d.y + ")";
             });

        // Update the node attributes and style
        nodeUpdate.select('g.js-cell')
            .attr('class', (d) => (d._children ? 'js-cell parent-cell' : 'js-cell'));

        // Remove any exiting nodes
        const nodeExit = node.exit().transition()
            .duration(duration)
            .attr("transform", function(d) {
                return "translate(" + source.x + "," + source.y + ")";
            })
            .remove();

        nodeExit.select('circle')
            .attr('r', 1e-6);

        nodeExit.select('text')
            .style('fill-opacity', 1e-6);

        const link = svg.selectAll('path.link')
            .data(links, function(d) { return d.id; });

        // Enter any new links at the parent's previous position.
        const linkEnter = link.enter().insert('path', "g")
            .attr("class", "link")
            .attr('d', function(d){
                const o = {x: source.x0, y: source.y0}
                return diagonal(o, o)
            });

        const linkUpdate = linkEnter.merge(link);

        linkUpdate.transition()
            .duration(duration)
            .attr('d', function(d){ return diagonal(d, d.parent) });

        const linkExit = link.exit().transition()
            .duration(duration)
            .attr('d', function(d) {
                const o = {x: source.x, y: source.y}
                return diagonal(o, o)
            })
            .remove();

        nodes.forEach((d) => {
            d.x0 = d.x;
            d.y0 = d.y;
        });

        function click(event, d) {
            if (d.children) {
                d._children = d.children;
                d.children = null;
            } else {
                d.children = d._children;
                d._children = null;
            }
            update(d);
        }
    }
};

/**
 * Presentation
 *
 * @class MatrixPresentation
 * @extends {React.Component}
 */
class MatrixPresentation extends React.Component {
    constructor(props) {
        super(props);

        const immuneCells = require('./node_graph_data/immune_cells.json');

        this.state = {
            windowWidth: 0,
        };

        this.immuneCells = immuneCells;
        this.updateWindowWidth = this.updateWindowWidth.bind(this);
    }

    componentDidMount() {
        this.updateWindowWidth();
        window.addEventListener('resize', this.updateWindowWidth);

        require.ensure(['d3'], (require) => {
            this.d3 = require('d3');

            const chartWidth = this.state.windowWidth;
            drawTree(this.d3, this.immuneCells, chartWidth);
        });
    }

    updateWindowWidth() {
        this.setState({
            windowWidth: document.getElementById('immune_cells_wrapper').offsetWidth,
        });
    }

    render() {
        return (
            <div className="matrix__presentation" id="immune_cells_wrapper">
                <div className="sescc_matrix__graph-region">
                    <div className="vertical-node-graph" />
                </div>
            </div>
        );
    }
}

MatrixPresentation.contextTypes = {
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};


/**
 * Render the area containing the matrix.
 */
const MatrixContent = ({ context }) => (
    <div className="matrix__content matrix__content--reference-epigenome">
        <MatrixPresentation context={context} />
    </div>
);

MatrixContent.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};


const ImmuneCells = ({ context }) => {
    const itemClass = globals.itemClass(context, 'view-item');

    return (
        <Panel addClasses={itemClass}>
            <PanelBody>
                <MatrixHeader context={context} />
                <MatrixContent context={context} />
            </PanelBody>
        </Panel>
    );
};

ImmuneCells.propTypes = {
    context: PropTypes.object.isRequired,
};

ImmuneCells.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};

globals.contentViews.register(ImmuneCells, 'ImmuneCells');
