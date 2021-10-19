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
import drawTree from '../libs/ui/node_graph';


/**
 * Formats title, changes "H9" to "H9 Stem Cell"
 *
 * @param {string} title
 */
const formatH9HeaderTitle = (title) => (title && title.trim() !== 'H9' ? title.trim() : 'H9 Stem Cell');
const formatPebbleNameToCssClassFriendly = (name) => (!name ? '' : name.toLowerCase().replace(/ /g, '_').replace(/-/g, '_'));
const formatName = (name, replacement) => name.replace(/\s/g, replacement).toLowerCase();

const fullHeight = 400;
const mobileLimit = 400;
const data = require('./node_graph_data/sescc.json');

const treeData = data[0];

/**
 * All assay columns to not include in matrix.
 */
const excludedAssays = ['Control ChIP-seq'];

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

        this.layers = ['Endoderm', 'Mesoderm', 'Ectoderm'];

        this.state = {
            scrolledRight: false,
            windowWidth: 0,
            selectedNodes: rowDataOrder.map((row) => formatName(row, '')),
            margin: { top: 0, bottom: 0, right: 0, left: 0 },
        };

        this.selectAll = this.selectAll.bind(this);
        this.setMatrixRows = this.setMatrixRows.bind(this);
        this.setSelectedNodes = this.setSelectedNodes.bind(this);
    }

    componentDidMount() {
        this.handleScrollIndicator(this.scrollElement);
        this.updateWindowWidth();
        window.addEventListener('resize', this.updateWindowWidth);
        this.setMatrixRows();

        // Based on: https://www.codeseek.co/EleftheriaBatsou/the-tree-layout-or-d3-MveNbW
        // A version for d3.js v4 is: https://bl.ocks.org/d3noob/b024fcce8b4b9264011a1c3e7c7d70dc
        // Delay loading dagre for Jest testing compatibility;
        // Both D3 and Jest have their own conflicting JSDOM instances
        require.ensure(['d3v7'], (require) => {
            // eslint-disable-next-line import/no-unresolved
            this.d3 = require('d3v7');
            const chartWidth = this.state.windowWidth;
            drawTree(this.d3, '.sescc-matrix-graph', treeData, chartWidth, fullHeight, this.state.margin, this.state.selectedNodes, this.setSelectedNodes);
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

    setSelectedNodes(newNode) {
        this.setState((prevState) => {
            const matrixSelection = formatName(newNode, '_');
            const newSelection = formatName(newNode, '');
            const matrixRows = document.getElementsByClassName(matrixSelection);
            if (prevState.selectedNodes.indexOf(newSelection) > -1 && prevState.selectedNodes.length > 1) {
                for (let idx = 0; idx < matrixRows.length; idx += 1) {
                    matrixRows[idx].classList.add('hide');
                }
                return { selectedNodes: prevState.selectedNodes.filter((s) => s !== newSelection) };
            }
            if (prevState.selectedNodes.indexOf(newSelection) > -1) {
                for (let idx = 0; idx < matrixRows.length; idx += 1) {
                    matrixRows[idx].classList.add('hide');
                }
                return { selectedNodes: [] };
            }
            for (let idx = 0; idx < matrixRows.length; idx += 1) {
                matrixRows[idx].classList.remove('hide');
            }
            return { selectedNodes: [...prevState.selectedNodes, newSelection] };
        });
    }

    setMatrixRows() {
        const matrixRows = document.getElementsByClassName('matrix__row-data');
        for (let idx = 0; idx < matrixRows.length; idx += 1) {
            const rowClass = matrixRows[idx].classList[1].replace(/_/g, '');
            if (this.state.selectedNodes.indexOf(rowClass) === -1) {
                matrixRows[idx].classList.add('hide');
            } else {
                matrixRows[idx].classList.remove('hide');
            }
        }
    }

    updateWindowWidth() {
        this.setState({
            windowWidth: document.getElementsByClassName('matrix__presentation')[0].offsetWidth,
        }, () => {
            let margin = { top: 50, left: 3, bottom: 80, right: 3 };
            if (this.state.windowWidth > mobileLimit) {
                margin = { top: 50, left: 20, bottom: 70, right: 20 };
            }
            this.setState(margin);
        });
    }

    selectAll(selection) {
        if (selection === 'all') {
            this.setState({
                selectedNodes: rowDataOrder.map((row) => formatName(row, '')),
            }, () => {
                require.ensure(['d3v7'], () => {
                    const chartWidth = this.state.windowWidth;
                    drawTree(this.d3, '.sescc-matrix-graph', treeData, chartWidth, fullHeight, this.state.margin, this.state.selectedNodes, this.setSelectedNodes);
                    this.setMatrixRows();
                });
            });
        } else {
            this.setState({
                selectedNodes: [],
            }, () => {
                require.ensure(['d3v7'], () => {
                    const chartWidth = this.state.windowWidth;
                    drawTree(this.d3, '.sescc-matrix-graph', treeData, chartWidth, fullHeight, this.state.margin, this.state.selectedNodes, this.setSelectedNodes);
                    this.setMatrixRows();
                });
            });
        }
    }

    render() {
        const { context } = this.props;
        const { scrolledRight } = this.state;

        return (
            <div className="matrix__presentation">
                <div className="sescc__matrix-graph-container">
                    <div className="sescc-layer-legend">
                        {this.layers.map((layer) => (
                            <div className={`layer-element ${layer}`} key={layer}>
                                <div className={`layer-bubble ${layer.toLowerCase()}`} />
                                <div className="layer-name">{layer}</div>
                            </div>
                        ))}
                    </div>
                    <div className="sescc-matrix-graph vertical-node-graph" />
                </div>

                <div className="sescc__matrix__show-all">
                    <button type="button" className="btn btn-sm btn-info" onClick={() => this.selectAll('all')}>Show All</button>
                    <button type="button" className="btn btn-sm btn-info" onClick={() => this.selectAll('none')}>Hide All</button>
                </div>

                <div className={`matrix__label matrix__label--horz${!scrolledRight ? ' horz-scroll' : ''}`}>
                    <span>{context.matrix.x.label}</span>
                    {svgIcon('largeArrow')}
                </div>
                <div className="matrix__presentation-content">
                    <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}{context.matrix.y.label}</div></div>
                    <div className="sescc__matrix__data" onScroll={this.handleOnScroll} ref={(element) => { this.scrollElement = element; }}>
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
