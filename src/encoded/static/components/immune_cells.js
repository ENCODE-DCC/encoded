import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody } from '../libs/ui/panel';
import { svgIcon } from '../libs/svg-icons';
import { MATRIX_VISUALIZE_LIMIT } from './matrix';
import { MatrixBadges } from './objectutils';
import { SearchControls } from './search';
import * as globals from './globals';

const chartHeight = 500;
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

const drawTree = (d3, data, width) => {
    const treemap = d3.tree()
        .size([width, chartHeight])
        .separation((a, b) => {
            console.log(a);
            console.log(b);
            return (a.parent === b.parent ? 2 : 4);
        });

    let nodes = d3.hierarchy(data[0]);
    nodes = treemap(nodes);

    const fullWidth = width + margin.left + margin.right;
    const fullHeight = chartHeight + margin.top + margin.bottom;

    const svg = d3.select('.vertical-node-graph').append('svg')
        .attr('width', fullWidth)
        .attr('height', fullHeight)
        .attr('viewBox', `0 0 ${fullWidth} ${fullHeight}`)
        .attr('preserveAspectRatio', 'xMidYMin meet');

    const g = svg.append('g')
        .attr('transform',
            `translate(${margin.left}, ${margin.top})`);

    // adds the links between the nodes
    g.selectAll('.link')
        .data(nodes.descendants().slice(1))
        .enter().append('path')
        .attr('class', 'link')
        .attr('d', (d) => `M${d.x},${d.y}C${d.x},${(d.y + d.parent.y) / 2} ${d.parent.x},${(d.y + d.parent.y) / 2} ${d.parent.x},${d.parent.y}`);

    // adds each node as a group
    const node = g.selectAll('.node')
        .data(nodes.descendants())
        .enter().append('g')
        .attr('class', (d) => `node${d.children ? ' node--internal' : ' node--leaf'}`)
        .attr('transform', (d) => `translate(${d.x},${d.y})`);

    // adds the text to the node
    node.append('text')
        .attr('dy', '.35em')
        .attr('y', (d) => (d.children ? -20 : 30))
        .style('text-anchor', 'middle')
        .text((d) => d.data.name);

    const nodeGroup = node.append('g')
        .attr('class', 'cell-group')
        .on('mouseover', function() {
            d3.select(this).selectAll('ellipse').style('fill', '#d2d2d2');
            d3.select(this).selectAll('ellipse').style('transform', 'scale(1.2)');
        })
        .on('mouseout', function() {
            d3.select(this).selectAll('ellipse').style('fill', 'white');
            d3.select(this).selectAll('ellipse').style('transform', 'scale(1)');
        });

    ellipseSettings.forEach((ellipseSetting) => {
        nodeGroup.append('ellipse')
            .attr('cx', ellipseSetting.cx)
            .attr('cy', ellipseSetting.cy)
            .attr('rx', ellipseSetting.rx)
            .attr('ry', ellipseSetting.ry)
            .style('stroke', ellipseSetting.stroke)
            .style('stroke-width', 1)
            .style('fill', 'white')
            .attr('class', () => 'js-cell');
    });
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

        const immuneCells = require('./immune/data.json');

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
