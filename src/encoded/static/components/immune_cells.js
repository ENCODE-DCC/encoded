import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody } from '../libs/ui/panel';
import { MATRIX_VISUALIZE_LIMIT } from './matrix';
import { MatrixBadges } from './objectutils';
import { SearchControls } from './search';
import * as globals from './globals';

const fullHeight = 1000;
const margin = { top: 40, right: 90, bottom: 50, left: 90 };

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
    const chartWidth = fullWidth - margin.left - margin.right;
    const chartHeight = fullHeight - margin.top - margin.bottom;

    // append svg to graph div
    const svg = d3.select('.vertical-node-graph').append('svg')
        .attr('width', fullWidth)
        .attr('height', fullHeight)
        .attr('viewBox', `0 0 ${fullWidth} ${fullHeight}`)
        .attr('preserveAspectRatio', 'xMidYMin meet');

    svg.append('g')
        .attr('transform',
            `translate(${margin.left}, ${margin.top})`);

    // declare tree layout
    const treemap = d3.tree()
        .size([fullHeight, fullWidth]);
        // .separation((a, b) => {
        //     // console.log(a);
        //     // console.log(b);
        //     return (a.parent === b.parent ? 1 : 2);
        // });

    let index = 0;
    const duration = 10;
    const root = d3.hierarchy(data[0], (d) => d.children);
    root.x0 = fullWidth / 2;
    root.y0 = 200;

    console.log(root);

    // collapse after second level
    // root.children.forEach(collapse);

    const update = (source) => {
        // Toggle children on click.
        function click(d) {
            console.log('click');
            if (d && d.children) {
                console.log(d.children);
            } else {
                console.log('no children');
            }
            if (d.children) {
                d._children = d.children;
                d.children = null;
            } else {
                d.children = d._children;
                d._children = null;
            }
            update(d);
        }

        // Assigns the x and y position for the nodes
        const treeData = treemap(root);

        // Compute the new tree layout.
        const nodes = treeData.descendants();
        const links = treeData.descendants().slice(1);

        console.log('nodes');
        console.log(nodes);

        console.log('links');
        console.log(links);

        // Normalize for fixed-depth.
        nodes.forEach((d) => { d.y = d.depth * 180; });

        // ****************** Nodes section ***************************

        const node = svg.selectAll('g.node')
            .data(nodes, (d) => {
                return d.id || (d.id = ++index);
            });


        // Enter any new modes at the parent's previous position.
        const nodeEnter = node.enter().append('g')
            .attr('class', 'node')
            .attr('transform', (d) => {`translate(${source.x0},${source.y0})` } )
            .on('click', click);

        // adds the text to the node
        nodeEnter.append('text')
            .attr('dy', '.35em')
            .attr('y', (d) => (d.children ? -20 : 30))
            .style('text-anchor', 'middle')
            .text((d) => d.data.name);

        nodeEnter.append('circle')
            .attr('class', 'node')
            .attr('r', 1e-6)
            .style('fill', (d) => (d._children ? 'lightsteelblue' : '#fff'));

        // const nodeGroup = nodeEnter.append('g')
        //     .attr('class', 'cell-group')
        //     .on('mouseover', function() {
        //         d3.select(this).selectAll('ellipse').style('fill', '#d2d2d2');
        //         d3.select(this).selectAll('ellipse').style('transform', 'scale(1.2)');
        //     })
        //     .on('mouseout', function() {
        //         d3.select(this).selectAll('ellipse').style('fill', 'white');
        //         d3.select(this).selectAll('ellipse').style('transform', 'scale(1)');
        //     });
        //
        // ellipseSettings.forEach((ellipseSetting) => {
        //     nodeGroup.append('ellipse')
        //         .attr('cx', ellipseSetting.cx)
        //         .attr('cy', ellipseSetting.cy)
        //         .attr('rx', ellipseSetting.rx)
        //         .attr('ry', ellipseSetting.ry)
        //         .style('stroke', ellipseSetting.stroke)
        //         .style('stroke-width', 1)
        //         // .style('fill', 'white')
        //         .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; })
        //         .attr('class', () => 'js-cell');
        // });

        // update
        const nodeUpdate = nodeEnter.merge(node)
            .attr("fill", "#fff")
            .attr("stroke", "steelblue")
            .attr("stroke-width", "3px;")
            .style('font', '12px sans-serif')

        // Transition to the proper position for the node
        nodeUpdate.transition()
            .duration(duration)
            .attr('transform', (d) => {
                return `translate(${d.x},${d.y})`;
             });

         // Update the node attributes and style
         nodeUpdate.select('circle.node')
           .attr('r', 10)
           .style("fill", function(d) {
               return d._children ? "lightsteelblue" : "#fff";
           })
           .attr('cursor', 'pointer');

        // Remove any exiting nodes
        const nodeExit = node.exit().transition()
            .duration(duration)
            .attr('transform', (d) => {
                return `translate(${source.x},${source.y})`;
            })
            .remove();

        // On exit reduce the node circles size to 0
        nodeExit.select('circle')
            .attr('r', 1e-6);

        // On exit reduce the opacity of text labels
        nodeExit.select('text')
            .style('fill-opacity', 1e-6);

        // ****************** links section ***************************

        // Update the links...
        const link = svg.selectAll('path.link')
            .data(links, (d) => d.id);

        // Enter any new links at the parent's previous position.
        const linkEnter = link.enter().insert('path', 'g')
            .attr('class', 'link')
            .attr('d', (d) => {
                const o = { x: source.x0, y: source.y0 }
                return diagonal(o, o);
            });

        // UPDATE
        const linkUpdate = linkEnter.merge(link);

        // Transition back to the parent element position
        linkUpdate.transition()
            .duration(duration)
            .attr('d', function(d){ return diagonal(d, d.parent) });

        // Remove any exiting links
        const linkExit = link.exit().transition()
            .duration(duration)
            .attr('d', (d) => {
                const o = { x: source.x, y: source.y }
                return diagonal(o, o)
            })
            .remove();

        // Store the old positions for transition.
        nodes.forEach((d) => {
            d.x0 = d.x;
            d.y0 = d.y;
        });
    };

    root.children.forEach(collapse);
    console.log('root after collapsing');
    console.log(root);
    update(root);
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
            windowWidth: Math.min(window.screen.width, window.innerWidth),
        });
    }

    render() {
        return (
            <div className="matrix__presentation">
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
