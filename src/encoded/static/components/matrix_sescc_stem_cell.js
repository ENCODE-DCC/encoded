import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Panel, PanelBody } from '../libs/ui/panel';
import { svgIcon } from '../libs/svg-icons';
import DataTable from './datatable';
import { BrowserFeat } from './browserfeat';
import { MATRIX_VISUALIZE_LIMIT } from './matrix';
import { MatrixBadges } from './objectutils';
import { SearchControls } from './search';
import * as globals from './globals';
import { tintColor, isLight } from './datacolors';


/**
 * Formats title, changes "H9" to "H9 Stem Cell"
 *
 * @param {string} title
 */
const formatH9HeaderTitle = (title) => (title && title.trim() !== 'H9' ? title.trim() : 'H9 Stem Cell');

const formatPebbleNameToCssClassFriendly = (name) => (!name ? '' : name.toLowerCase().replace(/ /g, '_').replace(/-/g, '_'));

/**
 * All assay columns to not include in matrix.
 */
const excludedAssays = ['Control ChIP-seq'];

/**
 * Stores data on the tree (graph, pebble collection)
 *
 */
const treeData = [{
    name: 'H9 Stem Cell',
    linkColor: '',
    selectedColor: '#808080',
    deselectedColor: '#D1D1D1',
    children: [
        {
            name: 'Hepatocyte',
            linkColor: 'blue',
            selectedColor: '#808080',
            deselectedColor: '#D1D1D1',
            children: null,
        }, {
            name: 'Splanchnic Mesodermal Cell',
            linkColor: 'green',
            selectedColor: '#008000',
            deselectedColor: '#E3FAE1',
            children: [
                {
                    name: 'Smooth Muscle Cell',
                    linkColor: 'green',
                    selectedColor: '#008000',
                    deselectedColor: '#E3FAE1',
                    children: null,
                },
                {
                    name: 'Mesothelial Cell',
                    linkColor: 'green',
                    selectedColor: '#008000',
                    deselectedColor: '#E3FAE1',
                    children: null,
                },
            ],
        },
        {
            name: 'Lateral Mesodermal Cell',
            linkColor: 'green',
            selectedColor: '#008000',
            deselectedColor: '#E3FAE1',
            children: null,
        },
        {
            name: 'Neural Crest Cell',
            linkColor: 'green',
            selectedColor: '#008000',
            deselectedColor: '#E3FAE1',
            parent: 'H9 Stem Cell',
            children: [
                {
                    name: 'Mesenchymal Stem Cell',
                    linkColor: 'purple',
                    selectedColor: '#EDCF09',
                    deselectedColor: '#FAFA98',
                    children: null,
                },
            ],
        },
        {
            name: 'Neural Progenitor Cell',
            linkColor: 'purple',
            selectedColor: '#800080',
            deselectedColor: '#E4C6f7',
            children: null,
        },
        {
            name: 'Ecto Neural Progenitor Cell',
            linkColor: 'purple',
            selectedColor: '#800080',
            deselectedColor: '#E4C6f7',
            children: null,
        },
    ],
}];


const headerDataOrder = [
    'polyA plus RNA-seq',
    'total RNA-seq',
    'small RNA-seq',
    'microRNA-seq',
    'microRNA counts',
    'RNA microarray',
    'DNase-seq',
    'ATAC-seq',
    'WGBS',
    'RRBS',
    'MeDIP-seq',
    'MRE-seq',
    'Repli-chip',
    'DNAme array',
    'genotyping array',
    'RAMPAGE',
    'TF ChIP-seq',
    'Histone ChIP-seq',
];


const rowDataOrder = [
    'H9 Stem Cell',
    'hepatocyte',
    'splanchnic mesodermal cell',
    'lateral mesodermal cell',
    'neural crest cell',
    'neural progenitor cell',
    'ecto neural progenitor cell',
    'smooth muscle cell',
    'mesothelial cell',
    'mesenchymal stem cell',
];


/**
 * Transforms context object into a format DataTable object can understand
 *
 * @param {object} context
 * @returns Object
 */
const convertToDataTableFormat = (context) => {
    if (!context || !context.matrix || !context.matrix.y || !context.matrix.x) {
        return {
            rows: [],
            rowKeys: [],
            tableCss: 'matrix',
        };
    }

    const targetLabels = [];

    const assayTitles = _.sortBy(
        context.matrix.x.assay_title.buckets
            .map((assayTitle) => {
                const assay = {
                    key: assayTitle.key,
                    doc_count: assayTitle.doc_count,
                };

                if (assayTitle['target.label'].buckets.length !== 0) {
                    targetLabels.push(assay.key);
                    assay.targetLabel = assayTitle['target.label'].buckets;
                }
                return assay;
            })
            .filter((assayTitle) => !excludedAssays.includes(assayTitle.key)),
        (assayTitle) => headerDataOrder.indexOf(assayTitle.key)
    );

    const headerData = [];

    assayTitles.forEach((assay) => {
        headerData.push({
            key: assay.key,
            doc_count: assay.doc_count,
            type: 'assay_title',
        });

        if (targetLabels.indexOf(assay.key) !== -1) {
            assay.targetLabel.forEach((target) => {
                headerData.push({
                    key: target.key,
                    doc_count: target.doc_count,
                    type: 'target.label',
                });
            });
        }
    });

    const disabledCellIndices = headerData.reduce((headers, header, index) => {
        const headerDatum = [...headers];
        if (targetLabels.includes(header.key)) {
            headerDatum.push(index);
        }
        return headerDatum;
    }, []);

    const rowData = _.sortBy(
        context.matrix.y['biosample_ontology.classification'].buckets
            .map((biosampleOntologyClassification) => biosampleOntologyClassification['biosample_ontology.term_name'].buckets)
            .reduce((termNames, termName) => termNames.concat(termName), [])
            .map((x) => {
                const m = { key: x.key,
                    doc_count: x.doc_count,
                    xHeaders: x.assay_title.buckets
                        .reduce((a, b) => a.concat([{ key: b.key, doc_count: b.doc_count, type: 'assay_title' },
                            ...b['target.label'].buckets
                                .map((targetLabel) => ({
                                    key: targetLabel.key,
                                    doc_count: targetLabel.doc_count,
                                    type: 'target.label',
                                }))]), []) };
                return m;
            }),
        (y) => rowDataOrder.indexOf(y.key),
    );

    // subCategoryKeys used for determining when to apply "sub" css class in x-header
    const subCategoryKeys = context.matrix.x.assay_title.buckets
        .map((x) => ({
            key: x.key,
            hasSubCategory: x['target.label'].buckets.length > 1,
        }))
        .filter((x) => x.hasSubCategory)
        .map((x) => x.key);

    let rows = [];
    const edgeColor = '1px solid #f0f0f0';
    const headerBorderBottom = edgeColor;
    const searchBase = context.search_base;

    const headerRow = headerData.map((x) => ({
        header: (
            <a href={`${searchBase}&${x.type}=${x.key}`} className={`${subCategoryKeys.includes(x.key) ? 'sub' : ''}`} title={`${x.key}`}>
                <div className="subcategory-row-text">{x.key}</div>
            </a>),
        style: { borderBottom: headerBorderBottom },
    }));

    rows.push({
        rowContent: [{ header: null }, ...headerRow],
        css: 'matrix__col-category-header',
    });

    const headerDataKeys = headerData.map((x) => x.key);
    const headerDataKeysLength = headerDataKeys.length;

    const biosamples = rowData.map((row) => {
        const rowContent = [...Array(headerDataKeysLength + 1)].map(() => ({
            content: '',
            style: '',
            css: '',
        }));

        const title = formatH9HeaderTitle(row.key);

        rowContent[0] = {
            header: (
                <a href={`${searchBase}&assay_title!=Control%20ChIP-seq&biosample_ontology.term_name=${row.key}`} title={`${row.key}`}>
                    <div className="subcategory-row-text">
                        { title }
                    </div>
                </a>),
            style: {},
        };

        disabledCellIndices.forEach((index) => {
            rowContent[index + 1].css = 'matrix__disabled-cell';
        });

        row.xHeaders.forEach((assayTitle) => {
            const index = headerDataKeys.indexOf(assayTitle.key) + 1; // +1 added because 0 position is reserved for header-entry

            // targetLabels list previously added, no need to add it again
            // exclude index == 0, previously set
            if (!targetLabels.includes(assayTitle.key) && index !== 0) {
                const backgroundColor = assayTitle.doc_count > 0 ? '#e8b425' : ''; // determined if box is colored or not
                const borderRight = index === headerDataKeysLength ? edgeColor : ''; // add border color to right-most rows
                const borderBottom = edgeColor; // add border color to topmost rows
                const borderLeft = edgeColor;

                rowContent[index].content = (
                    <a href={`${searchBase}&biosample_ontology.term_name=${row.key}&${assayTitle.type}=${assayTitle.key}`} title={`${assayTitle.doc_count}`}>
                        {' '}
                    </a>
                );
                rowContent[index].style = { backgroundColor, borderRight, borderBottom, borderLeft };
            }
        });

        const fixedH9 = formatH9HeaderTitle(row.key);

        return {
            rowContent,
            css: `matrix__row-data ${formatPebbleNameToCssClassFriendly(fixedH9)}`,
        };
    });

    rows = rows.concat(biosamples);

    const matrixData = {
        rows,
        tableCss: 'matrix',
    };

    return matrixData;
};

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

        this.togglePebblesGroupVisibilty = this.togglePebblesGroupVisibilty.bind(this);
        this.state = {
            scrolledRight: false,
        };
    }

    componentDidMount() {
        this.handleScrollIndicator(this.scrollElement);

        // Based on: https://www.codeseek.co/EleftheriaBatsou/the-tree-layout-or-d3-MveNbW
        // A version for d3.js v4 is: https://bl.ocks.org/d3noob/b024fcce8b4b9264011a1c3e7c7d70dc
        if (BrowserFeat.getBrowserCaps('svg')) {
            // Delay loading dagre for Jest testing compatibility;
            // Both D3 and Jest have their own conflicting JSDOM instances
            require.ensure(['d3'], (require) => {
                this.d3 = require('d3');
                const margin = { top: 70, left: 50 };
                const width = 600;
                const height = 480;
                const aspect = width / height;

                const tree = this.d3.layout.tree()
                    .size([height, width]);

                const diagonal = this.d3.svg.diagonal()
                    .projection((d) => [d.x, d.y]);

                const svg = this.d3.select('.sescc_matrix__graph').append('svg')
                    .attr('width', width)
                    .attr('height', height)
                    .attr('viewBox', `0 0 ${width} ${height}`)
                    .attr('preserveAspectRatio', 'xMidYMin meet')
                    .append('g')
                    .attr('transform', `translate(${margin.left},${margin.top})`);

                let index = 0;
                const svgContainer = this.d3.select('.sescc_matrix__graph svg');

                const resize = () => {
                    const targetWidth = window.innerWidth < width ? window.innerWidth : width;
                    const targetHeight = Math.round(targetWidth / aspect) < width ? Math.round(targetWidth / aspect) : width;

                    // adjust the group (g) as a whole
                    svg
                        .attr('width', targetWidth)
                        .attr('height', targetHeight);

                    // adjust svg container (of the group [g])
                    svgContainer
                        .attr('width', targetWidth)
                        .attr('height', targetHeight);
                };

                resize(); // important for adjusting the graph to fix screen size onload
                globals.bindEvent(window, 'resize', resize);

                const update = (root) => {
                    // Compute the new tree layout.
                    const nodes = tree.nodes(root).reverse();
                    const links = tree.links(nodes);

                    // Normalize for fixed-depth.
                    nodes.forEach((d) => {
                        d.y = d.depth * 150;
                    });

                    // Declare the nodes…
                    const node = svg.selectAll('g.sescc_matrix__node')
                        .data(nodes, (d) => {
                            if (!d.id) {
                                index += 1;
                                d.id = index;
                            }
                            return d.id;
                        });

                    // create nodes.
                    const nodeEnter = node.enter().append('g')
                        .attr('class', 'sescc_matrix__node')
                        .attr('transform', (d) => `translate(${d.x},${d.y})`)
                        .style('cursor', 'pointer')
                        .on('click', function updater(d) {
                            const name = formatH9HeaderTitle(d.name);
                            const elementClass = formatPebbleNameToCssClassFriendly(name);
                            const element = document.querySelector(`.${elementClass}`);

                            if (!element) {
                                return;
                            }
                            const { display } = element.style;
                            element.style.display = display === '' ? 'none' : '';
                            const color = display === '' ? d.deselectedColor : d.selectedColor;

                            for (let j = 0; j < this.children.length; j += 1) {
                                const child = this.children[j];

                                if (child.tagName === 'ellipse') {
                                    child.style.fill = color;
                                }
                            }
                        })
                        .on('mouseover', (d) => {
                            const name = formatH9HeaderTitle(d.name);
                            const elementClass = formatPebbleNameToCssClassFriendly(name);
                            const element = document.querySelector(`.${elementClass} th`);
                            const text = document.querySelector(`.${elementClass} th .subcategory-row-text`);

                            if (element) {
                                const cellColor = tintColor(d.selectedColor, 0.1);
                                const textColor = isLight(cellColor) ? '#000' : '#fff';

                                element.style.backgroundColor = cellColor;

                                if (text) {
                                    text.style.color = textColor;
                                }
                            }
                        })
                        .on('mouseout', (d) => {
                            const name = formatH9HeaderTitle(d.name);
                            const elementClass = formatPebbleNameToCssClassFriendly(name);
                            const element = document.querySelector(`.${elementClass} th`);
                            const text = document.querySelector(`.${elementClass} th .subcategory-row-text`);

                            if (element) {
                                element.style.backgroundColor = 'white';

                                if (text) {
                                    text.style.color = 'black';
                                }
                            }
                        });

                    const ellipseSettings = [
                        { cx: 2, cy: 2, rx: 12, ry: 9, stroke: 'black', 'stroke-width': 1.5 },
                        { cx: 2, cy: 2, rx: 6.5, ry: 6, stroke: 'black', 'stroke-width': 1.5 },
                        { cx: -5, cy: 10, rx: 12, ry: 9, stroke: 'black', 'stroke-width': 1.5 },
                        { cx: -5, cy: 10, rx: 6.5, ry: 5, stroke: 'black', 'stroke-width': 1.5 },
                        { cx: 10, cy: 10, rx: 12, ry: 9, stroke: 'black', 'stroke-width': 1.5 },
                        { cx: 10, cy: 10, rx: 6.5, ry: 5, stroke: 'black', 'stroke-width': 1.5 },
                    ];

                    nodeEnter.append('svg:title').text((d) => `Click to toggle matrix row: ${d.name}`);

                    ellipseSettings.forEach((ellipseSetting) => {
                        nodeEnter.append('ellipse')
                            .attr('cx', ellipseSetting.cx)
                            .attr('cy', ellipseSetting.cy)
                            .attr('rx', ellipseSetting.rx)
                            .attr('ry', ellipseSetting.ry)
                            .style('stroke', ellipseSetting.stroke)
                            .style('stroke-width', ellipseSetting['stroke-width'])
                            .style('fill', (d) => d.selectedColor)
                            .attr('class', () => 'js-cell');
                    });

                    nodeEnter.append('text')
                        .attr('y', () => -18)
                        .attr('dy', '.35em')
                        .attr('text-anchor', 'middle')
                        .attr('transform', 'rotate(310)')
                        .text((d) => d.name)
                        .style('fill-opacity', 1);

                    // Declare the link
                    const link = svg.selectAll('path.sescc_matrix__link')
                        .data(links, (d) => d.target.id);

                    // Update the links.
                    link.enter().insert('path', 'g')
                        .attr('class', 'sescc_matrix__link')
                        .style('stroke', (d) => d.target.linkColor)
                        .attr('d', diagonal);
                };
                update(treeData[0]);
            });
        }
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
                <div className="sescc_matrix__show-all">
                    <button type="button" className="btn btn-sm btn-info" onClick={() => this.togglePebblesGroupVisibilty(true)}>Show All</button>
                    <button type="button" className="btn btn-sm btn-info" onClick={() => this.togglePebblesGroupVisibilty(false)}>Hide All</button>
                </div>

                <div className={`matrix__label matrix__label--horz${!scrolledRight ? ' horz-scroll' : ''}`}>
                    <span>{context.matrix.x.label}</span>
                    {svgIcon('largeArrow')}
                </div>
                <div className="matrix__presentation-content">
                    <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}{context.matrix.y.label}</div></div>
                    <div className="sescc_matrix__data" onScroll={this.handleOnScroll} ref={(element) => { this.scrollElement = element; }}>
                        <DataTable tableData={convertToDataTableFormat(context)} />
                    </div>
                </div>
            </div>);
    }
}

MatrixPresentation.propTypes = {
    /** Reference epigenome matrix object */
    context: PropTypes.object.isRequired,
};

MatrixPresentation.contextTypes = {
    navigate: PropTypes.func,
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


const SESCCStemCellMatrix = ({ context }) => {
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

SESCCStemCellMatrix.propTypes = {
    context: PropTypes.object.isRequired,
};

SESCCStemCellMatrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};

globals.contentViews.register(SESCCStemCellMatrix, 'SESCCStemCellMatrix');
