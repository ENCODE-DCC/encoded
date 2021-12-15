import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import * as encoding from '../libs/query_encoding';
import { Panel, PanelBody } from '../libs/ui/panel';
import { svgIcon } from '../libs/svg-icons';
import { tintColor, isLight } from './datacolors';
import { DataTable } from './datatable';
import { MatrixBadges, filterFacet } from './objectutils';
import { SearchControls, FacetList } from './search';
import QueryString from '../libs/query_string';
import * as globals from './globals';
import { drawTree, drawThumbnail, nodeKeyName } from '../libs/ui/node_graph';
import getSeriesData from './series_search.js';

const colorLegend = ['T cell', 'B cell', 'NK cell'];
const keepRows = ['T cell', 'B cell', 'NK cell', 'myeloid cell', 'mononuclear cell'];
const colorMap = {
    'T cell': '#2c9659',
    'CD4+ T cell': '#2c9659',
    'CD8+ T cell': '#2c9659',
    'B cell': '#2794bf',
    'NK cell': '#986ea4',
    monocyte: '#36586d',
    'myeloid cell': '#36586d',
    'mononuclear cell': '#36586d',
};

// Keep this constant in sync with $donor-cell-width in _matrix.scss.
const DONOR_CELL_WIDTH = 30;
const COL_CATEGORY = 'assay_title';
const COL_SUBCATEGORY = 'target.label';
const SUB_CATEGORY_SHORT_SIZE = 10000000;

const fullHeight = 1600;
const margin = { top: 80, right: 15, bottom: 140, left: 30 };

// Not all facets are displayed, these are the ones we want to keep
const keepFacets = [
    'replicates.library.biosample.disease_term_name',
];

const matrixAssaySortOrder = [
    'scRNA-seq',
    'Bru-seq',
    'total RNA-seq',
    'polyA plus RNA-seq',
    'polyA minus RNA-seq',
    'small RNA-seq',
    'microRNA-seq',
    'snATAC-seq',
    'ATAC-seq',
    'DNase-seq',
    'TF ChIP-seq',
    'Histone ChIP-seq',
    'Hi-C',
    'ChIA-PET',
    'WGBS',
];

const excludedAssays = [
    'Control ChIP-seq',
    'Control eCLIP',
    'DNAme array',
    'RNA microarray',
    'RRBS',
    'sc-RNAseq',
    'CAGE',
    'Repli-ChIP',
    'genotyping array',
    'DNAme array',
];

const collapsedAssays = [];

const nodeField = 'biosample_ontology.term_name';

// Find element or parent of element with matching tag or class name
const findElement = (el, name, key) => {
    while (el.parentElement) {
        el = el.parentElement;
        if ([...el[key]].includes(name)) {
            return true;
        }
    }
    return null;
};

const generateColMap = (context) => {
    const colCategory = context.matrix.x.group_by[0];
    const colSubcategory = context.matrix.x.group_by[1];
    const colMap = {};
    let targetAssays = [];
    let colIndex = 0;

    // Sort column categories according to a specified order, with any items not specified sorted
    // at the end in order of occurrence.
    const colCategoryBuckets = context.matrix.x[colCategory].buckets;
    const sortedColCategoryBuckets = _(colCategoryBuckets).sortBy((colCategoryBucket) => {
        const sortIndex = matrixAssaySortOrder.indexOf(colCategoryBucket.key);
        return sortIndex >= 0 ? sortIndex : colCategoryBuckets.length;
    });

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
    sortedColCategoryBuckets.forEach((sortBucket, sortIdx) => {
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

        sortedColCategoryBuckets[histoneIdx]['target.label'].buckets = newBuckets;
    }

    const colCol = sortedColCategoryBuckets.map((col) => col.key);
    // We want to exclude Mint experiments if there is Histone data and we're not already excluding it
    if ((colCol.indexOf('Histone ChIP-seq') > -1) && (excludedAssays.indexOf('Mint-ChIP-seq') === -1)) {
        excludedAssays.push('Mint-ChIP-seq');
    // We do not want to exclude Mint experiments if there is no Histone data
    } else if (colCol.indexOf('Histone ChIP-seq') === -1) {
        const mints = excludedAssays.indexOf('Mint-ChIP-seq');
        excludedAssays.splice(mints, 1);
    }

    // Generate the column map based on the sorted category buckets.
    sortedColCategoryBuckets.forEach((colCategoryBucket) => {
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

            // Add the mapping of "<assay>|<target>"" key string to column index for those assays that
            // have targets and don't collapse their targets.
            if (!collapsedAssays.includes(colCategoryBucket.key)) {
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
        }
    });

    // If targetAssays only contains nulls, then just empty it so we can skip the targetAssay row.
    if (!targetAssays.some((assay) => assay !== null)) {
        targetAssays = [];
    }

    return { colMap, targetAssays };
};

const convertExperimentToDataTable = (context) => {
    const colCategory = context.matrix.x.group_by[0];
    const colSubcategory = context.matrix.x.group_by[1];
    const rowCategory = context.matrix.y.group_by[0];
    const rowSubcategory = context.matrix.y.group_by[1];
    const rowKeys = [];
    const headerRows = [];

    const colQuery = new QueryString(context.search_base.replace('&config=immune', ''));
    const query = colQuery.clone();

    colQuery.deleteKeyValue('biosample_ontology.cell_slims')
        .deleteKeyValue('biosample_ontology.classification')
        .deleteKeyValue('biosample_ontology.system_slims');
    const colSearchBase = `${colQuery.format()}`;

    query.deleteKeyValue('biosample_ontology.cell_slims')
        .deleteKeyValue('biosample_ontology.classification')
        .deleteKeyValue('biosample_ontology.system_slims')
        .deleteKeyValue(nodeField);
    const searchBase = `${query.format()}`;

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
    const rowCategoryBuckets = context.matrix.y[rowCategory].buckets.filter((bucket) => keepRows.includes(bucket.key));
    const rowCategoryColors = rowCategoryBuckets.map((rowCategoryDatum) => colorMap[rowCategoryDatum.key]);
    const dataTable = rowCategoryBuckets.reduce((accumulatingTable, rowCategoryBucket, rowCategoryIndex) => {
        // Each loop iteration generates all the rows of the row subcategories (biosample term names)
        // under it.
        const rowSubcategoryBuckets = rowCategoryBucket[rowSubcategory].buckets;
        const rowCategoryQuery = `${rowCategory}=${encoding.encodedURIComponent(rowCategoryBucket.key)}`;
        rowKeys[rowCategoryIndex + rowKeysInitialLength] = rowCategoryBucket.key;

        const rowCategoryColor = rowCategoryColors[rowCategoryIndex];
        const rowSubcategoryColor = tintColor(rowCategoryColor, 0.5);
        const rowCategoryTextColor = isLight(rowCategoryColor) ? '#000' : '#fff';
        const expandableRowCategory = rowSubcategoryBuckets.length > SUB_CATEGORY_SHORT_SIZE;

        // Update the row key mechanism.
        rowKeys[matrixRow] = rowCategoryBucket.key;
        matrixRow += 1;

        // No rows are hidden
        const visibleRowSubcategoryBuckets = rowSubcategoryBuckets;

        const cells = Array(colCount);
        const subcategoryRows = visibleRowSubcategoryBuckets.map((rowSubcategoryBucket, rowSubcategoryIndex) => {
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
                    if (rowSubcategoryColSubcategoryBuckets.length > 0 && !collapsedAssays.includes(rowSubcategoryColCategoryBucket.key)) {
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
                css: `matrix__row-data${rowSubcategoryIndex === 0 ? ' matrix__row-data--first' : ''} ${nodeKeyName(rowSubcategoryBucket.key)}`,
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
                    css: `matrix__row-spacer${expandableRowCategory ? ' matrix__row-spacer--expander' : ''}`,
                },
            ],
        );
    }, headerRows);
    return { dataTable, rowKeys };
};

const MatrixHeader = ({ context }) => (
    <div className="matrix-header">
        <div className="matrix-header__title">
            <div className="matrix-title-badge">
                <h1>{context.title}</h1>
                <MatrixBadges context={context} />
            </div>
            <div className="matrix-description">
                <div className="matrix-description__text">
                    Epigenomic profiling of human immune cells at different cellular fates and states, including activation, stimulation, and disease (MS)
                </div>
            </div>
        </div>
        <div className="matrix-header__controls">
            <div className="matrix-header__search-controls-sescc">
                <SearchControls context={context} visualizeDisabledTitle="" hideBrowserSelector showDownloadButton={false} />
            </div>
        </div>
    </div>
);

MatrixHeader.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};


MatrixHeader.contextTypes = {
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

class MatrixPresentation extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            /** True if matrix scrolled all the way to the right; used for flashing arrow */
            scrolledRight: false,
        };
        this.handleOnScroll = this.handleOnScroll.bind(this);
        this.handleScrollIndicator = this.handleScrollIndicator.bind(this);
        this.getClearClassificationsLink = this.getClearClassificationsLink.bind(this);
    }

    componentDidMount() {
        this.handleScrollIndicator(this.scrollElement);
    }

    /* eslint-disable react/no-did-update-set-state */
    componentDidUpdate(prevProps) {
        // If URI changed, we need close any expanded rowCategories in case the URI change results
        // in a huge increase in displayed data. Also update the scroll indicator if needed.
        if (prevProps.context['@id'] !== this.props.context['@id']) {
            this.handleScrollIndicator(this.scrollElement);
        }
    }
    /* eslint-enable react/no-did-update-set-state */

    /**
     * Called when the user scrolls the matrix horizontally within its div to handle scroll
     * indicators.
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
    }

    getClearClassificationsLink() {
        if (this.hasRequestedClassifications) {
            const parsedUrl = url.parse(this.props.context['@id']);
            const query = new QueryString(parsedUrl.query);
            query.deleteKeyValue('biosample_ontology.classification');
            parsedUrl.search = null;
            parsedUrl.query = null;
            const baseMatrixUrl = url.format(parsedUrl);
            return `${baseMatrixUrl}?${query.format()}`;
        }
        return null;
    }

    render() {
        const { context } = this.props;
        const { scrolledRight } = this.state;
        const clearClassifications = this.getClearClassificationsLink();

        // Convert encode matrix data to a DataTable object.
        const { dataTable, rowKeys } = convertExperimentToDataTable(context, clearClassifications);
        const matrixConfig = {
            rows: dataTable,
            rowKeys,
            tableCss: 'matrix',
        };

        return (
            <div className="matrix__presentation" key={this.props.presentationKey}>
                <div className={`matrix__label matrix__label--horz${!scrolledRight ? ' horz-scroll' : ''}`}>
                    <span>{context.matrix.x.label}</span>
                    {svgIcon('largeArrow')}
                </div>
                <div className="matrix__presentation-content">
                    <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}{context.matrix.y.label}</div></div>
                    <div className="matrix__data-wrapper">
                        <div className="matrix__data" onScroll={this.handleOnScroll} ref={(element) => { this.scrollElement = element; }}>
                            <DataTable tableData={matrixConfig} />
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

MatrixPresentation.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
    presentationKey: PropTypes.number.isRequired,
};

class MatrixGraph extends React.Component {
    constructor(props) {
        super(props);

        const immuneCells = require('./node_graph_data/immune_cells.json');
        this.immuneCells = immuneCells[0];

        this.state = {
            windowWidth: 0,
            selectedNodes: props.selectedNodes,
            isThumbnailExpanded: (this.props.context.search_base.indexOf('openModal') > -1),
        };

        this.updateWindowWidth = this.updateWindowWidth.bind(this);
        this.setSelectedNodes = this.setSelectedNodes.bind(this);
        this.toggleThumbnail = this.toggleThumbnail.bind(this);
    }

    componentDidMount() {
        this.updateWindowWidth();
        window.addEventListener('resize', this.updateWindowWidth);

        this.setState({ isThumbnailExpanded: (this.context.location_href.indexOf('openModal') > -1) }, () => {
            require.ensure(['d3v7'], (require) => {
                // eslint-disable-next-line import/no-unresolved
                this.d3 = require('d3v7');

                const chartWidth = this.state.windowWidth;
                const nodesRenamed = this.state.selectedNodes.map((node) => nodeKeyName(node));
                if (!this.state.isThumbnailExpanded) {
                    drawThumbnail(this.d3, '.vertical-node-graph-thumbnail', this.immuneCells, chartWidth, fullHeight, margin, nodesRenamed, this.setSelectedNodes, this.props.availableNodes, 'immune');
                } else {
                    drawTree(this.d3, '.vertical-node-graph-full-width', this.immuneCells, chartWidth, fullHeight, margin, nodesRenamed, this.setSelectedNodes, this.props.availableNodes, 'immune');
                }
            });
        });
    }

    setSelectedNodes(newNode) {
        const nodeClass = document.getElementsByClassName(`js-cell-${nodeKeyName(newNode)}`)[0].classList;

        this.setState((prevState) => {
            let tempNodes = [];
            if (document.getElementsByClassName('active-cell').length > 0) {
                tempNodes = prevState.selectedNodes;
            }
            if ([...nodeClass].indexOf('active-cell') > -1) {
                return { selectedNodes: tempNodes.filter((s) => s !== newNode) };
            }
            return { selectedNodes: [...tempNodes, newNode] };
        }, () => {
            this.props.setFilters(this.state.selectedNodes);
        });
    }

    updateWindowWidth() {
        const windowWidth = document.getElementById('navbar').offsetWidth > 1500 ? document.getElementById('navbar').offsetWidth : 1500;
        this.setState({
            windowWidth,
        }, () => {
            require.ensure(['d3v7'], (require) => {
                // eslint-disable-next-line import/no-unresolved
                this.d3 = require('d3v7');

                const chartWidth = this.state.windowWidth;
                const nodesRenamed = this.state.selectedNodes.map((node) => nodeKeyName(node));
                if (!this.state.isThumbnailExpanded) {
                    drawThumbnail(this.d3, '.vertical-node-graph-thumbnail', this.immuneCells, chartWidth, fullHeight, margin, nodesRenamed, this.setSelectedNodes, this.props.availableNodes, 'immune');
                } else {
                    drawTree(this.d3, '.vertical-node-graph-full-width', this.immuneCells, chartWidth, fullHeight, margin, nodesRenamed, this.setSelectedNodes, this.props.availableNodes, 'immune');
                }
            });
        });
    }

    toggleThumbnail() {
        this.setState((prevState) => ({ isThumbnailExpanded: !prevState.isThumbnailExpanded }), () => {
            require.ensure(['d3v7'], (require) => {
                // eslint-disable-next-line import/no-unresolved
                this.d3 = require('d3v7');
                const chartWidth = this.state.windowWidth;
                const nodesRenamed = this.state.selectedNodes.map((node) => nodeKeyName(node));
                if (!this.state.isThumbnailExpanded) {
                    drawThumbnail(this.d3, '.vertical-node-graph-thumbnail', this.immuneCells, chartWidth, fullHeight, margin, nodesRenamed, this.setSelectedNodes, this.props.availableNodes, 'immune');
                } else {
                    drawTree(this.d3, '.vertical-node-graph-full-width', this.immuneCells, chartWidth, fullHeight, margin, nodesRenamed, this.setSelectedNodes, this.props.availableNodes, 'immune');
                }
            });
        });
    }

    render() {
        return (
            <div className="immune-cells-graph">
                <button
                    type="button"
                    className="body-image-thumbnail"
                    onClick={() => this.toggleThumbnail()}
                >
                    <div className="body-map-expander">Filter results by cell lineage</div>
                    {svgIcon('expandArrows')}
                    <div className="vertical-node-graph vertical-node-graph-thumbnail" />
                </button>
                {this.state.isThumbnailExpanded ?
                    <div className="modal" style={{ display: 'block' }}>
                        <div className={`body-map-container-pop-up immune-cells-graph ${this.state.isThumbnailExpanded ? 'expanded' : 'collapsed'}`}>
                            <button type="button" className="collapse-body-map" onClick={() => this.toggleThumbnail()}>
                                {svgIcon('collapseArrows')}
                                <div className="body-map-collapser">Hide cell lineage</div>
                            </button>
                            <div className="sescc-layer-legend immune-cells-buttons">
                                <button type="button" className="btn btn-sm btn-info" id="showall-popup">Show all</button>
                                <button type="button" className="btn btn-sm btn-info" id="hideall-popup">Hide all</button>
                            </div>
                            <div className="sescc-layer-legend immune-cells-legend">
                                {colorLegend.map((legendEntry) => (
                                    <div className={`layer-element ${legendEntry.replace(/\s/g, '').toLowerCase()}`} key={legendEntry}>
                                        <div className={`layer-bubble ${legendEntry.replace(/\s/g, '').toLowerCase()}`} />
                                        <div className="layer-name">{legendEntry}</div>
                                    </div>
                                ))}
                                <div className="layer-element">
                                    <div className="layer-bubble default" />
                                    <div className="layer-name">Other</div>
                                </div>
                                <div className="layer-element">
                                    <div className="layer-name">ϟ Activated</div>
                                </div>
                                <div className="layer-element">
                                    <div className="layer-name">☆ Stimulated</div>
                                </div>
                            </div>
                            <div className="clickable-diagram-container node-diagram-container">
                                <div className="vertical-node-graph vertical-node-graph-full-width immune-cells-graph" />
                            </div>
                        </div>
                        <div className="modal-backdrop in" />
                    </div>
                : null}

                <div className="sescc__matrix__show-all">
                    <button type="button" className="btn btn-sm btn-info">Show all</button>
                    <button type="button" className="btn btn-sm btn-info">Hide all</button>
                </div>
            </div>
        );
    }
}

MatrixGraph.propTypes = {
    context: PropTypes.object.isRequired,
    setFilters: PropTypes.func.isRequired,
    availableNodes: PropTypes.array.isRequired,
    selectedNodes: PropTypes.array.isRequired,
};

MatrixGraph.contextTypes = {
    navigate: PropTypes.func,
    fetch: PropTypes.func,
    location_href: PropTypes.string.isRequired, // Should be context.location_href from parent
};

/**
 * View component for the experiment matrix page.
 */
class ImmuneCells extends React.Component {
    constructor(props) {
        super(props);

        this.baseUrl = '?type=Experiment&replicates.library.biosample.donor.organism.scientific_name=Homo+sapiens&biosample_ontology.cell_slims=hematopoietic+cell&biosample_ontology.classification=primary+cell&biosample_ontology.cell_slims=myeloid+cell&control_type!=*&status=released&biosample_ontology.system_slims=immune+system&biosample_ontology.system_slims=circulatory+system&config=immune';

        const originalNodes = this.props.context.facets.filter((f) => f.field === 'biosample_ontology.term_name')[0].terms.map((term) => term.key);

        this.originalNodes = originalNodes;

        const query = new QueryString(this.baseUrl);
        query.deleteKeyValue(nodeField);
        originalNodes.forEach((node) => {
            query.addKeyValue(nodeField, node);
        });
        this.defaultUrl = `${query.format()}`;

        const availableNodes = this.props.context.facets.filter((f) => f.field === 'biosample_ontology.term_name')[0].terms.map((term) => term.key);

        this.state = {
            pageContext: this.props.context,
            nodes: originalNodes,
            hiddenUrl: this.defaultUrl,
            availableNodes,
            facetsOpen: true,
        };

        this.getRowCategories = this.getRowCategories.bind(this);
        this.getRowSubCategories = this.getRowSubCategories.bind(this);
        this.setNodeFilters = this.setNodeFilters.bind(this);
        this.redirectClick = this.redirectClick.bind(this);
        this.refreshContext = this.refreshContext.bind(this);
        this.toggleFacets = this.toggleFacets.bind(this);
    }

    componentDidMount() {
        this.refreshContext();
    }

    getRowCategories() {
        const rowCategory = this.context.matrix.y.group_by[0];
        const rowCategoryData = this.context.matrix.y[rowCategory].buckets;
        const rowCategoryColors = globals.biosampleTypeColors.colorList(rowCategoryData.map((rowCategoryDatum) => rowCategoryDatum.key));
        const rowCategoryNames = {};
        rowCategoryData.forEach((datum) => {
            rowCategoryNames[datum.key] = datum.key;
        });
        return {
            rowCategoryData,
            rowCategoryColors,
            rowCategoryNames,
        };
    }

    getRowSubCategories(rowCategoryBucket) {
        const subCategoryName = this.context.matrix.y.group_by[1];
        return rowCategoryBucket[subCategoryName].buckets;
    }

    setNodeFilters(newNodes) {
        this.setState((prevState) => {
            const query = new QueryString(prevState.hiddenUrl);
            query.deleteKeyValue(nodeField);
            newNodes.forEach((node) => {
                const nodeIdx = this.state.availableNodes.indexOf(node);
                if (nodeIdx !== -1) {
                    query.addKeyValue(nodeField, node);
                }
            });
            return {
                hiddenUrl: `${query.format()}`,
            };
        });
    }

    refreshContext() {
        getSeriesData(this.state.hiddenUrl, this.context.fetch).then((response) => {
            const termIds = response.filters.filter((f) => f.field === 'biosample_ontology.term_name');
            const selectedNodes = termIds.length > 0 ? termIds.map((term) => term.term) : [];

            let availableNodes = [];
            if (response.facets.filter((f) => f.field === 'biosample_ontology.term_name')[0].terms.length > this.originalNodes.length) {
                availableNodes = selectedNodes;
            } else {
                availableNodes = response.facets.filter((f) => f.field === 'biosample_ontology.term_name')[0].terms.map((term) => term.key);
            }
            const availableSelectedNodes = selectedNodes.filter((node) => (availableNodes.indexOf(node) > -1));

            this.setState({
                pageContext: response,
                nodes: availableSelectedNodes,
                availableNodes,
            });
        });
    }

    toggleFacets() {
        this.setState((prevState) => ({ facetsOpen: !prevState.facetsOpen }));
    }

    redirectClick(e) {
        const clickedLink = e.target.closest('a');
        const isCollapseButton = findElement(e.target, 'collapse-body-map', 'classList');
        e.preventDefault();
        if (clickedLink && clickedLink.href && ((clickedLink.href.indexOf('/search/') > -1) || (clickedLink.href.indexOf('/report/') > -1))) {
            this.context.navigate(clickedLink.href.replace('&config=immune', ''));
        } else if (clickedLink && clickedLink.href) {
            getSeriesData(clickedLink.href, this.context.fetch).then((response) => {
                const termIds = response.filters.filter((f) => f.field === 'biosample_ontology.term_name');
                const selectedNodes = termIds.length > 0 ? termIds.map((term) => term.term) : [];
                this.setState({
                    pageContext: response,
                    nodes: selectedNodes,
                    hiddenUrl: clickedLink.href,
                }, () => {
                    this.refreshContext();
                });
            });
        } else if (isCollapseButton) {
            this.refreshContext();
        } else if (e.target.id === 'hideall-popup') {
            this.setNodeFilters([]);
            const cells = document.querySelectorAll('.js-cell');
            cells.forEach((cell) => cell.classList.remove('active-cell'));
        } else if (e.target.id === 'showall-popup') {
            this.setNodeFilters(this.state.availableNodes);
            const cells = document.querySelectorAll('.js-cell');
            cells.forEach((cell) => cell.classList.add('active-cell'));
        } else if (e.target.innerHTML === 'Hide all') {
            this.setState((prevState) => {
                const query = new QueryString(prevState.hiddenUrl);
                query.deleteKeyValue(nodeField);
                return {
                    hiddenUrl: `${query.format()}`,
                    nodes: [],
                };
            }, () => {
                this.refreshContext();
            });
        } else if (e.target.innerHTML === 'Show all') {
            this.setState((prevState) => {
                const query = new QueryString(prevState.hiddenUrl);
                query.deleteKeyValue(nodeField);
                prevState.availableNodes.forEach((node) => {
                    query.addKeyValue(nodeField, node);
                });
                return {
                    hiddenUrl: `${query.format()}`,
                    nodes: prevState.availableNodes,
                };
            }, () => {
                this.refreshContext();
            });
        }
    }

    render() {
        const { context } = this.props;
        const itemClass = globals.itemClass(context, 'view-item');
        const newFacets = filterFacet(this.state.pageContext.facets.filter((facet) => facet.field !== 'assembly'), keepFacets);
        const emptyNodeSelections = this.state.nodes.length < 1;

        if (context.total > 0) {
            return (
                <Panel addClasses={itemClass} onClick={(e) => this.redirectClick(e)}>
                    <PanelBody>
                        <MatrixHeader context={context} />
                        <div className="immune-cells-matrix matrix__content">
                            <div className={`file-gallery-facets ${this.state.facetsOpen ? 'expanded' : 'collapsed'}`}>
                                <button type="button" className="show-hide-facets" onClick={this.toggleFacets}>
                                    <i className={`${this.state.facetsOpen ? 'icon icon-chevron-left' : 'icon icon-chevron-right'}`} />
                                </button>
                                {(this.state.facetsOpen && newFacets.length > 0) ?
                                    <FacetList
                                        context={this.state.pageContext}
                                        facets={newFacets}
                                        filters={this.state.pageContext.filters}
                                        searchBase={this.state.hiddenUrl ? `${this.state.hiddenUrl}&` : `${this.state.hiddenUrl}?`}
                                        hideDocType
                                        additionalFacet={
                                            <MatrixGraph context={this.state.pageContext} setFilters={this.setNodeFilters} availableNodes={this.state.availableNodes} key={this.state.nodes.length} selectedNodes={this.state.nodes} />
                                        }
                                        key={this.state.availableNodes.length}
                                    />
                                : (this.state.facetsOpen) ?
                                    <MatrixGraph context={this.state.pageContext} setFilters={this.setNodeFilters} availableNodes={this.state.availableNodes} key={this.state.nodes.length} selectedNodes={this.state.nodes} />
                                : null}
                            </div>
                            {!emptyNodeSelections ?
                                <div className="matrix__content matrix__content--entex immune-cells-matrix">
                                    <MatrixPresentation context={this.state.pageContext} presentationKey={this.state.pageContext.total} />
                                </div>
                            :
                                <div className="immune-cells-error-message">
                                    Select a node from the graph to see results.
                                </div>
                            }
                        </div>
                    </PanelBody>
                </Panel>
            );
        }
        return <h4>No results found</h4>;
    }
}

ImmuneCells.propTypes = {
    context: PropTypes.object.isRequired,
};

ImmuneCells.contextTypes = {
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
    fetch: PropTypes.func,
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};

globals.contentViews.register(ImmuneCells, 'ImmuneCells');
