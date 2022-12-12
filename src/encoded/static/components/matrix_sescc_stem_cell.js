import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import _ from 'underscore';
import * as encoding from '../libs/query_encoding';
import QueryString from '../libs/query_string';
import { drawTree } from '../libs/ui/node_graph';
import { Panel, PanelBody, TabPanel, TabPanelPane } from '../libs/ui/panel';
import { svgIcon } from '../libs/svg-icons';
import { DataTable } from './datatable';
import { MATRIX_VISUALIZE_LIMIT } from './matrix';
import { ClearSearchTerm, SearchControls } from './search';
import * as globals from './globals';


const COL_CATEGORY = 'assay_title';
const COL_SUBCATEGORY = 'target.label';
const DONOR_CELL_WIDTH = 30;


/**
 * Map stem cell key names to their corresponding query string values and page titles.
 */
const scMap = {
    h1: {
        query: 'type=Experiment&replicates.library.biosample.donor.accession=ENCDO000AAW&status=released&biosample_ontology.term_name!=trophoblast+cell&control_type!=*',
        title: 'H1 ESC',
        nodes: require('./node_graph_data/H1_embryonic_stem_cell.json'),
        badgeTitle: 'H1  Stem Cells',
        description: 'Data generated for cell types differentiated from the H1 human embryonic stem cell line.',
    },
    h9: {
        query: 'type=Experiment&replicates.library.biosample.donor.accession=ENCDO222AAA&status=released&control_type!=*',
        title: 'H9 ESC',
        nodes: require('./node_graph_data/H9_embryonic_stem_cell.json'),
        badgeTitle: 'H9 Stem Cells',
        description: 'Data generated for cell types differentiated from the H9 human embryonic stem cell line.',
    },
    pgp: {
        query: 'type=Experiment&replicates.library.biosample.donor.accession=ENCDO336AAA&status=released&control_type!=*',
        title: 'PGP iPSC',
        nodes: require('./node_graph_data/PGP_iPSC.json'),
        badgeTitle: 'PGP Donor',
        description: 'Data generated for cell types differentiated from induced pluripotent stem cells derived from the PGP donor',
    },
    sescc: {
        query: 'type=Experiment&internal_tags=SESCC&status=released',
        title: 'Southeastern Stem Cell Consortium',
        nodes: require('./node_graph_data/sescc.json'),
        badgeTitle: 'Southeast Stem Cell Consortium',
        description: 'Project data of the epigenomic profiles of cell types differentiated from the H9 cell line provided by the Southeast Stem Cell Consortium (SESCC).',
    },
};


/**
 * Formats title, changes "H9" to "H9 Stem Cell"
 *
 * @param {string} title
 */
const formatName = (name, replacement) => {
    if (name === 'H1') {
        return 'h1node';
    }
    if (name === 'brain (30/90/180 days organoid)') {
        return 'brain';
    }
    if (name === 'nephron (21/35/49 days organoid)') {
        return 'nephron';
    }
    if (name === 'brain (90/180 days organoid)') {
        return 'brain';
    }
    // difference between "formatName" here and "nodeKeyName" in node_graph.js is that this function does not drop underscores
    const newName = name.replace(/\s/g, replacement).replace(')', '').replace('(', '').replace('-', '')
        .toLowerCase();
    return newName;
};

/**
 * All assay columns to not include in matrix.
 */
const excludedAssays = ['Control ChIP-seq'];

const generateColMap = (context) => {
    const colCategory = context.matrix.x.group_by[0];
    const colSubcategory = context.matrix.x.group_by[1];
    const colMap = {};
    let targetAssays = [];
    let colIndex = 0;

    // Sort column categories according to a specified order, with any items not specified sorted
    // at the end in order of occurrence.
    const colCategoryBuckets = context.matrix.x[colCategory].buckets;

    // Combining Histone and Mint columns into one column category
    const newBuckets = [];
    let histoneBuckets = [];
    let mintBuckets = [];
    let histoneKeys = [];
    let mintKeys = [];
    let histoneIdx = null;
    let mintIdx = null;
    colCategoryBuckets.forEach((sortBucket) => {
        if (sortBucket.key === 'Histone ChIP-seq') {
            histoneBuckets = sortBucket['target.label'].buckets;
            histoneKeys = histoneBuckets.map((b) => b.key);
        } else if (sortBucket.key === 'Mint-ChIP-seq') {
            mintBuckets = sortBucket['target.label'].buckets;
            mintKeys = mintBuckets.map((b) => b.key);
        }
    });
    colCategoryBuckets.forEach((sortBucket, sortIdx) => {
        if (sortBucket.key === 'Histone ChIP-seq') {
            histoneIdx = sortIdx;
        }
        if (sortBucket.key === 'Mint-ChIP-seq') {
            mintIdx = sortIdx;
        }
    });

    if (!histoneIdx) {
        histoneIdx = mintIdx;
    }

    if (histoneIdx !== null) {
        const comboKeys = _.uniq([...histoneKeys, ...mintKeys]);
        let newIdx = 0;
        comboKeys.forEach((column) => {
            const mintKey = mintBuckets.filter((b) => b.key === column);
            const histoneKey = histoneBuckets.filter((b) => b.key === column);
            newBuckets[newIdx] =
                {
                    key: column,
                    doc_count: (mintKey.length > 0 ? mintKey[0].doc_count : 0) + (histoneKey.length > 0 ? histoneKey[0].doc_count : 0),
                };
            newIdx += 1;
        });

        colCategoryBuckets[histoneIdx]['target.label'].buckets = newBuckets;
    }

    const colCol = colCategoryBuckets.map((col) => col.key);
    // We want to exclude Mint experiments if there is Histone data and we're not already excluding it
    if ((colCol.indexOf('Histone ChIP-seq') > -1) && (excludedAssays.indexOf('Mint-ChIP-seq') === -1)) {
        excludedAssays.push('Mint-ChIP-seq');
    // We do not want to exclude Mint experiments if there is no Histone data
    } else if (colCol.indexOf('Histone ChIP-seq') === -1) {
        const mints = excludedAssays.indexOf('Mint-ChIP-seq');
        excludedAssays.splice(mints, 1);
    }

    // Generate the column map based on the category buckets.
    colCategoryBuckets.forEach((colCategoryBucket) => {
        if (!excludedAssays.includes(colCategoryBucket.key)) {
            const colSubcategoryBuckets = colCategoryBucket[colSubcategory].buckets;

            // Add the mapping of "assay" key string to column index.
            if (!(colSubcategoryBuckets.length > 0 && colSubcategoryBuckets[0].key !== 'no_target')) {
                // Assay doesn't have subcategories, so render the assay label into the column
                // header.
                colMap[colCategoryBucket.key] = {
                    col: colIndex,
                    category: colCategoryBucket.key,
                };
                targetAssays.push(null);
                colIndex += 1;
            } else {
                // Assay has subcategories, so generate information so we know how many columns the
                // assay's label should take up and which column it starts at so we can render the
                // assay label across several target columns.
                targetAssays.push({ col: colIndex, category: colCategoryBucket.key, subcategoryCount: colSubcategoryBuckets.length });
            }
            colSubcategoryBuckets.forEach((colSubcategoryBucket) => {
                if (colSubcategoryBucket.key !== 'no_target') {
                    colMap[`${colCategoryBucket.key}|${colSubcategoryBucket.key}`] = {
                        col: colIndex,
                        category: colCategoryBucket.key,
                        subcategory: colSubcategoryBucket.key,
                    };
                    colIndex += 1;
                }
            });
        }
    });


    // If targetAssays only contains nulls, then just empty it so we can skip the targetAssay row.
    if (!targetAssays.some((assay) => assay !== null)) {
        targetAssays = [];
    }

    return { colMap, targetAssays };
};


/**
 * Transforms context object into a format DataTable object can understand
 *
 * @param {object} context
 * @returns Object
 */
const convertExperimentToDataTable = (context) => {
    const colCategory = context.matrix.x.group_by[0];
    const colSubcategory = context.matrix.x.group_by[1];
    const rowCategory = context.matrix.y.group_by[0];
    const rowSubcategory = context.matrix.y.group_by[1];
    const rowKeys = [];
    const headerRows = [];

    const colSearchBase = context.search_base;
    const searchBase = context.search_base;

    // Generate the mapping of column categories and subcategories.
    const { colMap, targetAssays } = generateColMap(context);
    const colCount = Object.keys(colMap).length;
    const colCat = Object.keys(colMap).map((key) => key.split('|')[0]);

    // Convert column map to an array of column map values sorted by column number for displaying
    // in the matrix header.
    const sortedCols = Object.keys(colMap).map((assayColKey) => colMap[assayColKey]).sort((colInfoA, colInfoB) => colInfoA.col - colInfoB.col);

    // Generate the matrix header row labels for the assays with targets. Need a max-width inline
    // style so that wide labels don't make the target columns expand.
    if (targetAssays.length > 0) {
        const targetAssayHeader = [{ css: 'matrix__col-category-targetassay-corner' }].concat(targetAssays.map(((targetAssayElement) => {
            if (targetAssayElement) {
                // Add cell with assay title and span for the number of targets it has.
                const categoryName = (targetAssayElement.category === 'Histone ChIP-seq') || (targetAssayElement.category === 'Mint-ChIP-seq') ? 'Histone and Mint ChIP-seq' : targetAssayElement.category;
                const categoryQuery = `${colCategory}=${encoding.encodedURIComponent(targetAssayElement.category)}`;
                let extraQuery = '';
                if (targetAssayElement.category === 'Histone ChIP-seq') {
                    extraQuery = `&${COL_CATEGORY}=${encoding.encodedURIComponent('Mint-ChIP-seq')}`;
                }
                if (targetAssayElement.category === 'Mint-ChIP-seq') {
                    extraQuery = `&${COL_CATEGORY}=${encoding.encodedURIComponent('Histone ChIP-seq')}`;
                }
                return {
                    header: <a href={`${colSearchBase}${extraQuery}&${categoryQuery}`}>{categoryName} <div className="sr-only">{categoryName}</div></a>,
                    colSpan: targetAssayElement.subcategoryCount,
                    css: 'matrix__col-category-targetassay',
                    style: { maxWidth: DONOR_CELL_WIDTH * targetAssayElement.subcategoryCount },
                };
            }

            // Render empty cell for assays with no targets.
            return { header: null };
        })));

        // Add the key and row content for the target assay labels.
        rowKeys.push('target-assay-categories');
        headerRows.push({ rowContent: targetAssayHeader, css: 'matrix__col-category-targetassay-header' });
    }

    // Generate array of names of assays that have targets and don't collapse their targets, for
    // rendering those columns as disabled.
    // const colCategoriesWithSubcategories = Object.keys(colMap).filter((colCategoryName) => colMap[colCategoryName].hasSubcategories && !collapsedAssays.includes(colCategoryName));

    // Generate the hierarchical top-row sideways header label cells. The first cell is null unless
    // it contains a link to clear the currently selected classification. At the end of this loop,
    // rendering `{header}` shows this header row. The `sortedCols` array gets mutated in this loop,
    // acquiring a `query` property in each of its objects that gets used later to generate cell
    // hrefs.
    let prevCategory;
    let prevSubcategory;
    const dividerCss = [];
    const header = [
        {
            header: null,
        },
    ].concat(sortedCols.map((colInfo) => {
        // Determine the CSS classes for the dividers in the columns of assay and target labels.
        const dividerCssAccumulator = [];
        if ((colInfo.category !== prevCategory) && (prevSubcategory || colInfo.subcategory)) {
            // Need divider on left edge of start of assays with targets.
            dividerCssAccumulator.push('divider--start');
        }
        if (colInfo.subcategory && colInfo.col === sortedCols.length - 1) {
            // Need divider on right edge if subcategory column is at right edge of matrix.
            dividerCssAccumulator.push('divider--end');
        }
        dividerCss[colInfo.col] = dividerCssAccumulator.join(' ');
        prevCategory = colInfo.category;
        prevSubcategory = colInfo.subcategory;

        const categoryQuery = `${COL_CATEGORY}=${encoding.encodedURIComponent(colInfo.category)}`;
        let extraQuery = '';
        if (colInfo.category === 'Histone ChIP-seq') {
            extraQuery = `&${COL_CATEGORY}=${encoding.encodedURIComponent('Mint-ChIP-seq')}`;
        }
        if (colInfo.category === 'Mint-ChIP-seq') {
            extraQuery = `&${COL_CATEGORY}=${encoding.encodedURIComponent('Histone ChIP-seq')}`;
        }
        const categoryName = colInfo.category === 'Histone ChIP-seq' ? 'Histone and Mint ChIP-seq' : colInfo.category;
        if (!colInfo.subcategory) {
            // Add the category column links.
            colInfo.query = categoryQuery;
            return {
                header: <a href={`${colSearchBase}&${categoryQuery}${extraQuery}`}>{categoryName} <div className="sr-only">{context.matrix.x.label}</div></a>,
                css: dividerCss[colInfo.col],
            };
        }

        // Add the subcategory column links.
        const subCategoryQuery = `${COL_SUBCATEGORY}=${encoding.encodedURIComponent(colInfo.subcategory)}`;
        colInfo.query = `${categoryQuery}&${subCategoryQuery}`;

        return {
            header: <a className="sub" href={`${colSearchBase}&${categoryQuery}${extraQuery}&${subCategoryQuery}`}>{colInfo.subcategory} <div className="sr-only">target for {categoryName} {context.matrix.x.label} </div></a>,
            css: `category-base${dividerCss[colInfo.col] ? ` ${dividerCss[colInfo.col]}` : ''}`,
        };
    }));

    // Generate the main table content including the data hierarchy, where the upper level of the
    // hierarchy gets referred to here as "rowCategory" and the lower-level gets referred to as
    // "rowSubcategory." Both these types of rows get collected into `dataTable` which gets passed
    // to <DataTable>. Also generate an array of React keys to use with <DataMatrix> by using an
    // array index that's independent of the reduce-loop index because of spacer/expander row
    // insertion.
    let matrixRow = 1;
    rowKeys.push('column-categories');
    headerRows.push({ rowContent: header, css: 'matrix__col-category-header' });
    const rowKeysInitialLength = rowKeys.length;
    const rowCategoryBuckets = context.matrix.y[rowCategory].buckets;
    const rowCategoryColors = rowCategoryBuckets.map(() => '#d1d1d1');
    const dataTable = rowCategoryBuckets.reduce((accumulatingTable, rowCategoryBucket, rowCategoryIndex) => {
        // Each loop iteration generates all the rows of the row subcategories (biosample term names)
        // under it.
        const rowSubcategoryBuckets = rowCategoryBucket[rowSubcategory].buckets;
        const rowCategoryQuery = `${rowCategory}=${encoding.encodedURIComponent(rowCategoryBucket.key)}`;
        rowKeys[rowCategoryIndex + rowKeysInitialLength] = rowCategoryBucket.key;

        const rowCategoryColor = rowCategoryColors[rowCategoryIndex];
        const rowSubcategoryColor = '#d1d1d1';
        const rowCategoryTextColor = '#000';

        // Update the row key mechanism.
        rowKeys[matrixRow] = rowCategoryBucket.key;
        matrixRow += 1;

        // No rows are hidden
        const visibleRowSubcategoryBuckets = rowSubcategoryBuckets;

        const cells = Array(colCount);
        const subcategoryRows = visibleRowSubcategoryBuckets.map((rowSubcategoryBucket) => {
            const subCategoryQuery = `${rowSubcategory}=${encoding.encodedURIComponent(rowSubcategoryBucket.key)}`;
            let extraQuery = '';

            cells.fill(null);

            // Each biosample term name's row reuses the same `cells` array of cell components.
            // Until we fill it with actual data below, we initialize the row with empty cells,
            // with a CSS class to render a divider for columns of assays with targets.
            dividerCss.forEach((divider, colIndex) => {
                cells[colIndex] = { css: divider };
            });
            rowSubcategoryBucket[colCategory].buckets.forEach((rowSubcategoryColCategoryBucket) => {
                const tempExcludedAssays = [...excludedAssays];
                if (tempExcludedAssays.indexOf('Mint-ChIP-seq') > -1) {
                    const mints = excludedAssays.indexOf('Mint-ChIP-seq');
                    tempExcludedAssays.splice(mints, 1);
                }
                // Skip any excluded assay columns.
                if (!tempExcludedAssays.includes(rowSubcategoryColCategoryBucket.key)) {
                    const rowSubcategoryColSubcategoryBuckets = rowSubcategoryColCategoryBucket[colSubcategory].buckets;
                    if (rowSubcategoryColSubcategoryBuckets.length > 0) {
                        // The assay has targets and doesn't collapse them, so put relevant colored
                        // cells in the subcategory columns. Each cell has no visible content, but
                        // has hidden text for screen readers.
                        rowSubcategoryColSubcategoryBuckets.forEach((cellData) => {
                            let colMapKey = `${rowSubcategoryColCategoryBucket.key}|${cellData.key}`;
                            if (rowSubcategoryColCategoryBucket.key === 'Mint-ChIP-seq' && colCat.indexOf('Mint-ChIP-seq') === -1) {
                                colMapKey = `Histone ChIP-seq|${cellData.key}`;
                            }

                            if (colMapKey.indexOf('Histone ChIP-seq') > -1) {
                                extraQuery = `&${COL_CATEGORY}=${encoding.encodedURIComponent('Mint-ChIP-seq')}`;
                            }
                            if (colMapKey.indexOf('Mint-ChIP-seq') > -1) {
                                extraQuery = `&${COL_CATEGORY}=${encoding.encodedURIComponent('Histone ChIP-seq')}`;
                            }
                            const colIndex = colMap[colMapKey].col;
                            cells[colIndex] = {
                                content: (
                                    <>
                                        <a href={`${searchBase}&${rowCategoryQuery}&${subCategoryQuery}${extraQuery}&${colMap[colMapKey].query}`}>
                                            <span className="sr-only">Search {rowCategoryBucket.key}, {rowSubcategoryBucket.key} for {rowSubcategoryColCategoryBucket.key}, {cellData.key}</span>
                                            &nbsp;
                                        </a>
                                    </>
                                ),
                                css: dividerCss[colIndex],
                                style: { backgroundColor: rowSubcategoryColor },
                            };
                        });
                    } else if (colMap[rowSubcategoryColCategoryBucket.key]) {
                        const colIndex = colMap[rowSubcategoryColCategoryBucket.key].col;
                        cells[colIndex] = {
                            content: (
                                <>
                                    <a href={`${searchBase}&${rowCategoryQuery}&${subCategoryQuery}&${colMap[rowSubcategoryColCategoryBucket.key].query}`}>
                                        <span className="sr-only">Search {rowCategoryBucket.key}, {rowSubcategoryBucket.key} for {rowSubcategoryColCategoryBucket.key}</span>
                                        &nbsp;
                                    </a>
                                </>
                            ),
                            css: dividerCss[colIndex],
                            style: { backgroundColor: rowSubcategoryColor },
                        };
                    }
                }
            });

            // Add a single term-name row's data and left header to the matrix.
            rowKeys[rowCategoryIndex + 1] = `${rowCategoryBucket.key}|${rowSubcategoryBucket.key}`;
            return {
                rowContent: [
                    {
                        header: (
                            <a href={`${searchBase}&${rowCategoryQuery}&${subCategoryQuery}`}>
                                <div className="subcategory-row-text">{rowSubcategoryBucket.key} <div className="sr-only">{context.matrix.y.label}</div></div>
                            </a>
                        ),
                    },
                ].concat(cells),
                css: `matrix__row-data ${formatName(rowSubcategoryBucket.key, '_')}`,
            };
        });

        // Continue adding rendered rows to the matrix.
        rowKeys[matrixRow] = `${rowCategoryBucket.key}-spacer`;
        matrixRow += 1;
        const categoryId = globals.sanitizeId(rowCategoryBucket.key);
        return accumulatingTable.concat(
            [
                {
                    rowContent: [{
                        header: (
                            <div id={categoryId} style={{ backgroundColor: rowCategoryColor }}>
                                <a href={`${context['@id']}&${rowCategoryQuery}`} style={{ color: rowCategoryTextColor }}>{rowCategoryBucket.key}</a>
                            </div>
                        ),
                    },
                    { content: <div style={{ backgroundColor: rowCategoryColor }} />, colSpan: 0 }],
                    css: 'matrix__row-category',
                },
            ],
            subcategoryRows,
            [
                {
                    rowContent: [
                        {
                            content: null,
                        },
                        {
                            content: null,
                            colSpan: 0,
                        },
                    ],
                    css: 'matrix__row-spacer',
                },
            ],
        );
    }, headerRows);
    return { dataTable, rowKeys };
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
            <div className="matrix-header__banner">
                <div className="matrix-header__title">
                    <h1>{context.title}</h1>
                    <ClearSearchTerm searchUri={context['@id']} />
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
 * Determine which tab of the stem-cell page to select based on the current path. The returned
 * string matches the keys of the `scMap` global. If the path doesn't match any of the keys,
 * return the first key of the `scMap` global.
 * @param {string} path Current stem-cell page path
 * @returns {string} Type of stemp-cell matrix to display; matches keys of `scMap` global
 */
const determineSelectedTab = (path) => {
    // Get the query string from the URL and determine which tab it selects.
    const pathQuery = new QueryString(url.parse(path).query);
    const matchingScType = Object.keys(scMap).find((scType) => {
        const scTypeQuery = new QueryString(scMap[scType].query);
        return QueryString.equal(scTypeQuery, pathQuery, false);
    });
    return matchingScType || Object.keys(scMap)[0];
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
        const biosampleFacet = props.context.facets.find((elem) => elem.field === 'biosample_ontology.term_name');

        const biosampleTerms = biosampleFacet ? biosampleFacet.terms : [];
        const availableRows = biosampleTerms.length > 0 ? biosampleTerms.map((term) => formatName(term.key, '')) : [];

        this.h1Layers = ['Endoderm', 'Mesoderm', 'Ectoderm', 'Stem', 'Mesoderm + Endoderm'];
        this.h9Layers = ['Endoderm', 'Mesoderm', 'Ectoderm', 'Stem', 'Mesoderm + Ectoderm'];
        this.pgpLayers = ['Mesoderm', 'Ectoderm'];
        this.sesccLayers = ['Endoderm', 'Mesoderm', 'Ectoderm', 'Stem'];

        this.state = {
            availableRows,
            windowWidth: 0,
            selectedNodes: availableRows,
            margin: { top: 60, bottom: 120, right: 22, left: 22 },
            mobileLimit: 400,
        };

        this.handleTabClick = this.handleTabClick.bind(this);
        this.updateWindowWidth = this.updateWindowWidth.bind(this);
        this.selectOrHideAll = this.selectOrHideAll.bind(this);
        this.setMatrixRows = this.setMatrixRows.bind(this);
        this.setSelectedNodes = this.setSelectedNodes.bind(this);
    }

    componentDidMount() {
        this.updateWindowWidth();
        window.addEventListener('resize', this.updateWindowWidth);
        // this.setMatrixRows();

        // Based on: https://www.codeseek.co/EleftheriaBatsou/the-tree-layout-or-d3-MveNbW
        // A version for d3.js v4 is: https://bl.ocks.org/d3noob/b024fcce8b4b9264011a1c3e7c7d70dc
        // Delay loading dagre for Jest testing compatibility;
        // Both D3 and Jest have their own conflicting JSDOM instances
        require.ensure(['d3v7'], (require) => {
            // eslint-disable-next-line import/no-unresolved
            this.d3 = require('d3v7');
            const chartWidth = this.state.windowWidth;
            const selectedTab = determineSelectedTab(this.props.context['@id']);
            const fullHeight = selectedTab === 'h9' ? 530 : selectedTab === 'pgp' ? 500 : 300;
            const treeData = scMap[selectedTab].nodes[0];
            drawTree(this.d3, '.sescc-matrix-graph', treeData, chartWidth, fullHeight, this.state.margin, this.state.selectedNodes, this.setSelectedNodes, null, 'sescc');
        });
    }

    componentDidUpdate() {
        const biosampleFacet = this.props.context.facets.find((elem) => elem.field === 'biosample_ontology.term_name');
        const biosampleTerms = biosampleFacet ? biosampleFacet.terms : [];
        const availableRows = biosampleTerms.length > 0 ? biosampleTerms.map((term) => formatName(term.key, '')) : [];
        const selectedTab = determineSelectedTab(this.props.context['@id']);
        const deviceWidth = document.getElementsByClassName('matrix__presentation')[0].offsetWidth;
        const windowWidth = deviceWidth > this.state.mobileLimit ? deviceWidth : selectedTab === 'h9' ? 1300 : 700;
        if (this.state.availableRows.length !== availableRows.length) {
            this.setState({
                availableRows,
                selectedNodes: availableRows,
                windowWidth,
            });
        }

        require.ensure(['d3v7'], (require) => {
            // eslint-disable-next-line import/no-unresolved
            this.d3 = require('d3v7');
            const chartWidth = windowWidth;
            const treeData = scMap[selectedTab].nodes[0];
            const fullHeight = selectedTab === 'h9' ? 530 : selectedTab === 'pgp' ? 500 : 300;
            drawTree(this.d3, '.sescc-matrix-graph', treeData, chartWidth, fullHeight, this.state.margin, this.state.selectedNodes, this.setSelectedNodes, null, 'sescc');
        });
    }

    handleTabClick(tab) {
        this.setState({ selectedNodes: [] });
        // Get the current URL and replace the query string with the one for the clicked tab in `scMap`. Then navigate to that URL.
        const currentParsedUrl = url.parse(this.props.context['@id']);
        const updatedParsedUrl = { ...currentParsedUrl, ...{ search: `?${scMap[tab].query}` } };
        const newUrl = url.format(updatedParsedUrl);
        this.context.navigate(newUrl);
    }

    setSelectedNodes(newNode, activeBool) {
        this.setState((prevState) => {
            const matrixSelection = formatName(newNode, '_');
            const newSelection = formatName(newNode, '');
            const matrixRows = document.getElementsByClassName(matrixSelection);
            if (activeBool) {
                for (let idx = 0; idx < matrixRows.length; idx += 1) {
                    matrixRows[idx].classList.add('hide');
                }
                return { selectedNodes: prevState.selectedNodes.filter((s) => s !== newSelection) };
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
        const windowWidth = document.getElementsByClassName('matrix__presentation')[0].offsetWidth;
        const selectedTab = determineSelectedTab(this.props.context['@id']);
        this.setState((prevState) => ({
            windowWidth: windowWidth > prevState.mobileLimit ? windowWidth : selectedTab === 'h9' ? 1300 : 700,
        }), () => {
            let margin = { top: 50, left: 3, bottom: 80, right: 3 };
            if (this.state.windowWidth > this.state.mobileLimit) {
                margin = { top: 50, left: 20, bottom: 70, right: 20 };
            }
            this.setState(margin);
        });
    }

    selectOrHideAll(selection) {
        if (selection === 'all') {
            this.setState((prevState) => ({
                selectedNodes: prevState.availableRows,
            }), () => {
                require.ensure(['d3v7'], () => {
                    const chartWidth = this.state.windowWidth;
                    const selectedTab = determineSelectedTab(this.props.context['@id']);
                    const fullHeight = selectedTab === 'h9' ? 530 : selectedTab === 'pgp' ? 500 : 300;
                    const treeData = scMap[selectedTab].nodes[0];
                    drawTree(
                        this.d3,
                        '.sescc-matrix-graph',
                        treeData,
                        chartWidth,
                        fullHeight,
                        this.state.margin,
                        this.state.selectedNodes,
                        this.setSelectedNodes,
                        false,
                        'sescc'
                    );
                    this.setMatrixRows();
                });
            });
        } else {
            this.setState({
                selectedNodes: [],
            }, () => {
                require.ensure(['d3v7'], () => {
                    const chartWidth = this.state.windowWidth;
                    const selectedTab = determineSelectedTab(this.props.context['@id']);
                    const fullHeight = selectedTab === 'h9' ? 530 : selectedTab === 'pgp' ? 500 : 300;
                    const treeData = scMap[selectedTab].nodes[0];
                    drawTree(
                        this.d3,
                        '.sescc-matrix-graph',
                        treeData,
                        chartWidth,
                        fullHeight,
                        this.state.margin,
                        this.state.selectedNodes,
                        this.setSelectedNodes,
                        false,
                        'sescc'
                    );
                    this.setMatrixRows();
                });
            });
        }
    }

    render() {
        const { context } = this.props;
        const selectedTab = determineSelectedTab(context['@id']);

        const { dataTable, rowKeys } = convertExperimentToDataTable(context);
        const matrixConfig = {
            rows: dataTable,
            rowKeys,
            tableCss: 'matrix',
        };

        return (
            <div className="matrix__presentation">
                <TabPanel
                    selectedTab={selectedTab}
                    tabs={{ h1: 'H1', h9: 'H9', pgp: 'PGP', sescc: 'SESCC' }}
                    handleTabClick={this.handleTabClick}
                >
                    <TabPanelPane key="h1">
                        <div className="sescc__matrix-graph-container">
                            <div className="badge-group">
                                <div className="title">{scMap[selectedTab].badgeTitle}</div>
                                <div className="description">{scMap[selectedTab].description}</div>
                            </div>
                            <div className="sescc-layer-legend">
                                {this.h1Layers.map((layer) => (
                                    <div className={`layer-element ${layer.replace('Mesoderm + Endoderm', 'mesendoderm').replace('Mesoderm + Ectoderm', 'mesectoderm')}`} key={layer}>
                                        <div className={`layer-bubble ${layer.replace('Mesoderm + Endoderm', 'mesendoderm').replace('Mesoderm + Ectoderm', 'mesectoderm').toLowerCase()}`} />
                                        <div className="layer-name">{layer}</div>
                                    </div>
                                ))}
                            </div>
                            <div className="sescc-matrix-graph vertical-node-graph" />
                            <div className="sescc__matrix__show-all">
                                <button type="button" className="btn btn-sm btn-info" onClick={() => this.selectOrHideAll('all')}>Show All</button>
                                <button type="button" className="btn btn-sm btn-info" onClick={() => this.selectOrHideAll('none')}>Hide All</button>
                            </div>

                            <div className="matrix__label matrix__label--horz">
                                <span>{context.matrix.x.label}</span>
                                {svgIcon('largeArrow')}
                            </div>
                            <div className="matrix__presentation-content">
                                <div className="matrix__label matrix__label--vert">
                                    <div>
                                        {svgIcon('largeArrow')}{context.matrix.y.label}
                                    </div>
                                </div>
                                <div className="sescc__matrix__data">
                                    <DataTable tableData={matrixConfig} />
                                </div>
                            </div>
                        </div>
                    </TabPanelPane>

                    <TabPanelPane key="h9">
                        <div className="sescc__matrix-graph-container">
                            <div className="badge-group">
                                <div className="title">{scMap[selectedTab].badgeTitle}</div>
                                <div className="description">{scMap[selectedTab].description}</div>
                            </div>
                            <div className="sescc-layer-legend">
                                {this.h9Layers.map((layer) => (
                                    <div className={`layer-element ${layer.replace('Mesoderm + Endoderm', 'mesendoderm').replace('Mesoderm + Ectoderm', 'mesectoderm')}`} key={layer}>
                                        <div className={`layer-bubble ${layer.replace('Mesoderm + Endoderm', 'mesendoderm').replace('Mesoderm + Ectoderm', 'mesectoderm').toLowerCase()}`} />
                                        <div className="layer-name">{layer}</div>
                                    </div>
                                ))}
                            </div>
                            <div className="sescc-matrix-graph vertical-node-graph" />
                            <div className="sescc__matrix__show-all">
                                <button type="button" className="btn btn-sm btn-info" onClick={() => this.selectOrHideAll('all')}>Show All</button>
                                <button type="button" className="btn btn-sm btn-info" onClick={() => this.selectOrHideAll('none')}>Hide All</button>
                            </div>

                            <div className="matrix__label matrix__label--horz">
                                <span>{context.matrix.x.label}</span>
                                {svgIcon('largeArrow')}
                            </div>
                            <div className="matrix__presentation-content">
                                <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}{context.matrix.y.label}</div></div>
                                <div className="sescc__matrix__data">
                                    <DataTable tableData={matrixConfig} />
                                </div>
                            </div>
                        </div>
                    </TabPanelPane>

                    <TabPanelPane key="pgp">
                        <div className="sescc__matrix-graph-container">
                            <div className="badge-group">
                                <div className="title">{scMap[selectedTab].badgeTitle}</div>
                                <div className="description">{scMap[selectedTab].description}</div>
                            </div>
                            <div className="sescc-layer-legend">
                                {this.pgpLayers.map((layer) => (
                                    <div className={`layer-element ${layer.replace('Mesoderm + Endoderm', 'mesendoderm').replace('Mesoderm + Ectoderm', 'mesectoderm')}`} key={layer}>
                                        <div className={`layer-bubble ${layer.replace('Mesoderm + Endoderm', 'mesendoderm').replace('Mesoderm + Ectoderm', 'mesectoderm').toLowerCase()}`} />
                                        <div className="layer-name">{layer}</div>
                                    </div>
                                ))}
                            </div>
                            <div className="sescc-matrix-graph vertical-node-graph" />
                            <div className="sescc__matrix__show-all">
                                <button type="button" className="btn btn-sm btn-info" onClick={() => this.selectOrHideAll('all')}>Show All</button>
                                <button type="button" className="btn btn-sm btn-info" onClick={() => this.selectOrHideAll('none')}>Hide All</button>
                            </div>

                            <div className="matrix__label matrix__label--horz">
                                <span>{context.matrix.x.label}</span>
                                {svgIcon('largeArrow')}
                            </div>
                            <div className="matrix__presentation-content">
                                <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}{context.matrix.y.label}</div></div>
                                <div className="sescc__matrix__data">
                                    <DataTable tableData={matrixConfig} />
                                </div>
                            </div>
                        </div>
                    </TabPanelPane>

                    <TabPanelPane key="sescc">
                        <div className="sescc__matrix-graph-container">
                            <div className="badge-group">
                                <div className="title">{scMap[selectedTab].badgeTitle}</div>
                                <div className="description">{scMap[selectedTab].description}</div>
                            </div>
                            <div className="sescc-layer-legend">
                                {this.sesccLayers.map((layer) => (
                                    <div className={`layer-element ${layer.replace('Mesoderm + Endoderm', 'mesendoderm').replace('Mesoderm + Ectoderm', 'mesectoderm')}`} key={layer}>
                                        <div className={`layer-bubble ${layer.replace('Mesoderm + Endoderm', 'mesendoderm').replace('Mesoderm + Ectoderm', 'mesectoderm').toLowerCase()}`} />
                                        <div className="layer-name">{layer}</div>
                                    </div>
                                ))}
                            </div>
                            <div className="sescc-matrix-graph vertical-node-graph" />
                            <div className="sescc__matrix__show-all">
                                <button type="button" className="btn btn-sm btn-info" onClick={() => this.selectOrHideAll('all')}>Show All</button>
                                <button type="button" className="btn btn-sm btn-info" onClick={() => this.selectOrHideAll('none')}>Hide All</button>
                            </div>

                            <div className="matrix__label matrix__label--horz">
                                <span>{context.matrix.x.label}</span>
                                {svgIcon('largeArrow')}
                            </div>
                            <div className="matrix__presentation-content">
                                <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}{context.matrix.y.label}</div></div>
                                <div className="sescc__matrix__data">
                                    <DataTable tableData={matrixConfig} />
                                </div>
                            </div>
                        </div>
                    </TabPanelPane>
                </TabPanel>
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
