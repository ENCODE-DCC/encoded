import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Panel, PanelBody } from '../libs/ui/panel';
import { svgIcon } from '../libs/svg-icons';
import { DataTable } from './datatable';
import { MATRIX_VISUALIZE_LIMIT } from './matrix';
import { MatrixBadges } from './objectutils';
import { SearchControls } from './search';
import * as globals from './globals';
import { tintColor, isLight } from './datacolors';

const chartHeight = 500;
const marginVert = 30;
const marginHoriz = 30;

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

// Fetch data from href
function getCSVdata(seriesLink, fetch) {
    return fetch(seriesLink, {
        method: 'GET',
        headers: {
            Accept: '.csv',
        },
    }).then((response) => {
        if (response.ok) {
            return response.csv();
        }
        throw new Error('not ok');
    }).catch((e) => {
        console.log('OBJECT LOAD ERROR: %s', e);
    });
}

// Fetch data from href
function getJsonData(seriesLink, fetch) {
    return fetch(seriesLink, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
        },
    }).then((response) => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('not ok');
    }).catch((e) => {
        console.log('OBJECT LOAD ERROR: %s', e);
    });
}

const drawTree = (d3, treeData, width) => {
    // const tree = d3.layout.tree()
    //     .size([chartHeight, width]);

    // const svg = d3.select('.sescc_matrix__graph').append('svg')
    //     .attr('width', width)
    //     .attr('height', chartHeight)
    //     .attr('viewBox', `0 0 ${width} ${chartHeight}`)
    //     .attr('preserveAspectRatio', 'xMidYMin meet')
    //     .append('g')
    //     .attr('transform', `translate(${marginHoriz},${marginVert})`);
    //
    // let index = 0;
    // const svgContainer = d3.select('.sescc_matrix__graph svg');
    // const nodes = tree.nodes(treeData).reverse();
    // const links = tree.links(nodes);

    console.log(d3);

    const margin = { top: 40, right: 90, bottom: 50, left: 90 };

    const treemap = d3.tree()
        .size([width, chartHeight]);

    let nodes = d3.hierarchy(treeData);
    nodes = treemap(nodes);

    // append the svg obgect to the body of the page
    // appends a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    let svg = d3.select("body").append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", chartHeight + margin.top + margin.bottom),
        g = svg.append("g")
          .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");

    // adds the links between the nodes
    const link = g.selectAll(".link")
        .data( nodes.descendants().slice(1))
      .enter().append("path")
        .attr("class", "link")
        .attr("d", function(d) {
           return "M" + d.x + "," + d.y
             + "C" + d.x + "," + (d.y + d.parent.y) / 2
             + " " + d.parent.x + "," +  (d.y + d.parent.y) / 2
             + " " + d.parent.x + "," + d.parent.y;
           });

    // adds each node as a group
    const node = g.selectAll('.node')
        .data(nodes.descendants())
      .enter().append('g')
        .attr('class', (d) => {
          return "node" +
            (d.children ? " node--internal" : " node--leaf"); })
        .attr("transform", function(d) {
          return "translate(" + d.x + "," + d.y + ")"; });

    // adds the circle to the node
    node.append("circle")
      .attr("r", 10);

    // adds the text to the node
    node.append("text")
      .attr("dy", ".35em")
      .attr("y", function(d) { return d.children ? -20 : 20; })
      .style("text-anchor", "middle")
      .text(function(d) { return d.data.name; });

    // // Normalize for fixed-depth.
    // nodes.forEach((d) => {
    //     d.y = d.depth * 150;
    // });
    //
    // // Declare the nodes…
    // const node = svg.selectAll('g.sescc_matrix__node')
    //     .data(nodes, (d) => {
    //         if (!d.id) {
    //             index += 1;
    //             d.id = index;
    //         }
    //         return d.id;
    //     });
    //
    // // create nodes.
    // const nodeEnter = node.enter().append('g')
    //     .attr('class', 'sescc_matrix__node')
    //     .attr('transform', (d) => `translate(${d.x},${d.y})`)
    //     .style('cursor', 'pointer')
    //     // .on('click', function updater(d) {
    //     //     const element = document.querySelector(`.${elementClass}`);
    //     //
    //     //     if (!element) {
    //     //         return;
    //     //     }
    //     //     const { display } = element.style;
    //     //     element.style.display = display === '' ? 'none' : '';
    //     //     const color = display === '' ? d.deselectedColor : d.selectedColor;
    //     //
    //     //     for (let j = 0; j < this.children.length; j += 1) {
    //     //         const child = this.children[j];
    //     //
    //     //         if (child.tagName === 'ellipse') {
    //     //             child.style.fill = color;
    //     //         }
    //     //     }
    //     // })
    //     .on('mouseover', (d) => {
    //         // const name = formatH9HeaderTitle(d.name);
    //         // const elementClass = formatPebbleNameToCssClassFriendly(name);
    //         // const element = document.querySelector(`.${elementClass} th`);
    //         // const text = document.querySelector(`.${elementClass} th .subcategory-row-text`);
    //         //
    //         // if (element) {
    //         //     const cellColor = tintColor(d.selectedColor, 0.1);
    //         //     const textColor = isLight(cellColor) ? '#000' : '#fff';
    //         //
    //         //     element.style.backgroundColor = cellColor;
    //         //
    //         //     if (text) {
    //         //         text.style.color = textColor;
    //         //     }
    //         // }
    //     })
    //     .on('mouseout', (d) => {
    //         // const name = formatH9HeaderTitle(d.name);
    //         // const elementClass = formatPebbleNameToCssClassFriendly(name);
    //         // const element = document.querySelector(`.${elementClass} th`);
    //         // const text = document.querySelector(`.${elementClass} th .subcategory-row-text`);
    //         //
    //         // if (element) {
    //         //     element.style.backgroundColor = 'white';
    //         //
    //         //     if (text) {
    //         //         text.style.color = 'black';
    //         //     }
    //         // }
    //     });

    // const ellipseSettings = [
    //     { cx: 2, cy: 2, rx: 12, ry: 9, stroke: 'black', 'stroke-width': 1.5 },
    //     { cx: 2, cy: 2, rx: 6.5, ry: 6, stroke: 'black', 'stroke-width': 1.5 },
    //     { cx: -5, cy: 10, rx: 12, ry: 9, stroke: 'black', 'stroke-width': 1.5 },
    //     { cx: -5, cy: 10, rx: 6.5, ry: 5, stroke: 'black', 'stroke-width': 1.5 },
    //     { cx: 10, cy: 10, rx: 12, ry: 9, stroke: 'black', 'stroke-width': 1.5 },
    //     { cx: 10, cy: 10, rx: 6.5, ry: 5, stroke: 'black', 'stroke-width': 1.5 },
    // ];
    //
    // nodeEnter.append('svg:title').text((d) => `Click to toggle matrix row: ${d.name}`);
    //
    // ellipseSettings.forEach((ellipseSetting) => {
    //     nodeEnter.append('ellipse')
    //         .attr('cx', ellipseSetting.cx)
    //         .attr('cy', ellipseSetting.cy)
    //         .attr('rx', ellipseSetting.rx)
    //         .attr('ry', ellipseSetting.ry)
    //         .style('stroke', ellipseSetting.stroke)
    //         .style('stroke-width', ellipseSetting['stroke-width'])
    //         .style('fill', (d) => d.selectedColor)
    //         .attr('class', () => 'js-cell');
    // });
    //
    // nodeEnter.append('text')
    //     .attr('y', () => -18)
    //     .attr('dy', '.35em')
    //     .attr('text-anchor', 'middle')
    //     .attr('transform', 'rotate(310)')
    //     .text((d) => d.name)
    //     .style('fill-opacity', 1);
    //
    // // Declare the link
    // const link = svg.selectAll('path.sescc_matrix__link')
    //     .data(links, (d) => d.target.id);
    //
    // // Update the links.
    // link.enter().insert('path', 'g')
    //     .attr('class', 'sescc_matrix__link')
    //     .style('stroke', (d) => d.target.linkColor)
    //     .attr('d', diagonal);
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

        this.state = {
            scrolledRight: false,
            windowWidth: 0,
        };

        this.togglePebblesGroupVisibilty = this.togglePebblesGroupVisibilty.bind(this);
        this.updateWindowWidth = this.updateWindowWidth.bind(this);
    }

    componentDidMount() {
        this.handleScrollIndicator(this.scrollElement);

        this.updateWindowWidth();
        window.addEventListener('resize', this.updateWindowWidth);

        console.log(this);

        // console.log(require('./immune-cells/immune-cells.csv'));

        // getCSVdata('/immune-cells/immune-cells.csv', this.context.fetch).then((response) => {
        //     console.log(response);
        // });

        // Based on: https://www.codeseek.co/EleftheriaBatsou/the-tree-layout-or-d3-MveNbW
        // A version for d3.js v4 is: https://bl.ocks.org/d3noob/b024fcce8b4b9264011a1c3e7c7d70dc
        // Delay loading dagre for Jest testing compatibility;
        // Both D3 and Jest have their own conflicting JSDOM instances
        require.ensure(['d3'], (require) => {
            this.d3 = require('d3');

            // this.d3.csv('../img/immune/immune-cells.csv', (data) => {
            //     console.log(data);
            // });

            this.d3.csv('https://static.observableusercontent.com/files/e65374209781891f37dea1e7a6e1c5e020a3009b8aedf113b4c80942018887a1176ad4945cf14444603ff91d3da371b3b0d72419fa8d2ee0f6e815732475d5de?response-content-disposition=attachment%3Bfilename*%3DUTF-8%27%27flare-2.json', (data) => {
                console.log(data);
                drawTree(this.d3, data, this.state.windowWidth);
            });
            // update(treeData[0]);
        });
    }

    componentDidUpdate() {
        // Updates only happen for scrolling on this page. Every other update causes an
        // unmount/mount sequence.
        this.handleScrollIndicator(this.scrollElement);
    }

    /**
        * Called when the user scrolls the matrix horizontally within its div to handle scroll
        * indicators
        * @param {object} e React synthetic scroll event
    */
    handleOnScroll(e) {
        this.handleScrollIndicator(e.target);
    }


    /**
        * Show a scroll indicator depending on current scrolled position.
        * @param {object} element DOM element to apply shading to
    */
    handleScrollIndicator(element) {
        if (element) {
            // Have to use a "roughly equal to" test because of an MS Edge bug mentioned here:
            // https://stackoverflow.com/questions/30900154/workaround-for-issue-with-ie-scrollwidth
            const scrollDiff = Math.abs((element.scrollWidth - element.scrollLeft) - element.clientWidth);
            if (scrollDiff < 2 && !this.state.scrolledRight) {
                // Right edge of matrix scrolled into view.
                this.setState({ scrolledRight: true });
            } else if (scrollDiff >= 2 && this.state.scrolledRight) {
                // Right edge of matrix scrolled out of view.
                this.setState({ scrolledRight: false });
            }
        } else if (!this.state.scrolledRight) {
            this.setState({ scrolledRight: true });
        }
    }


    updateWindowWidth() {
        this.setState({
            windowWidth: Math.min(window.screen.width, window.innerWidth),
        });
    }


    /**
     * Toggle matrix row (biosample) visibility of a specified row in the matrix and change corresponding pebble (node)-color in the tree
     *
     * @param {e} event
     * @memberof MatrixPresentation
     */
    togglePebblesGroupVisibilty(visible) {
        const cells = this.d3.selectAll('.js-cell')[0];

        cells.forEach((cell) => {
            const data = cell.__data__;
            cell.style.fill = data[visible ? 'selectedColor' : 'deselectedColor'];
        });

        const elements = document.querySelectorAll('.matrix .matrix__row-data');

        for (let i = 0; i < elements.length; i += 1) {
            const element = elements[i];
            element.style.display = visible ? '' : 'none';
        }
    }


    render() {
        const { context } = this.props;
        const { scrolledRight } = this.state;

        return (
            <div className="matrix__presentation">
                <div className="sescc_matrix__graph-region">
                    <div className="sescc_matrix__graph" />
                    <div className="sescc_matrix__germ-layer">
                        <div>
                            <span className="sescc_matrix__germ-layer-title">Germ Layers</span>
                            <hr />
                            <ul>
                                <li className="endodermColor">Endoderm</li>
                                <li className="mesodermColor">Mesoderm</li>
                                <li className="ectoDermColor">Ectoderm</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

MatrixPresentation.propTypes = {
    /** Reference epigenome matrix object */
    context: PropTypes.object.isRequired,
};

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
