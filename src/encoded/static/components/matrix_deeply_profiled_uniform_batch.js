import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import QueryString from '../libs/query_string';
import * as encoding from '../libs/query_encoding';
import { Panel, PanelBody } from '../libs/ui/panel';
import { svgIcon } from '../libs/svg-icons';
import { tintColor, isLight } from './datacolors';
import { DataTable } from './datatable';
import * as globals from './globals';
import { RowCategoryExpander, MATRIX_VISUALIZE_LIMIT } from './matrix';
import { FacetList, SearchControls } from './search';
import { CartAddAllElements } from './cart';


/**
 * Number of subcategory items to show when subcategory isn't expanded.
 * @constant
 */
const SUB_CATEGORY_SHORT_SIZE = 3;

/** Page name */
const matrixName = 'deeply-profiled-uniform-batch-matrix';

/**
 * URL query string key for internal tag
 */
const internalTagKey = 'replicates.library.biosample.internal_tags';

/**
 * URL query string value for internal tag
 */
const internalTagValue = 'Deeply Profiled';

/**
 * Mapping of Assay type to assay titles
 */
const assayTypeToAssayTitles = [
    { 'DNA binding': ['Histone ChIP-seq', 'TF ChIP-seq', 'Control ChIP-seq', 'Mint-ChIP-seq', 'Control Mint-ChIP-seq'] },
    { 'RNA binding': ['RNA Bind-n-Seq', 'Control eCLIP', 'RIP-chip', 'eCLIP', 'iCLIP', 'RIP-seq', 'Switchgear'] },
    { 'DNA accessibility': ['DNase-seq', 'FAIRE-seq', 'GM DNase-seq', 'ATAC-seq', 'MNase-seq'] },
    { '3D chromatin structure': ['ChIA-PET', 'Hi-C', 'SPRITE', '5C'] },
    { Transcription: ['polyA plus RNA-seq', 'microRNA counts', 'CRISPR RNA-seq', 'total RNA-seq', 'RAMPAGE', 'shRNA RNA-seq', 'small RNA-seq', 'siRNA RNA-seq', 'microRNA-seq', 'polyA minus RNA-seq', 'RNA microarray', 'BruUV-seq', 'CAGE', 'PAS-seq', 'RNA-PET', 'long read RNA-seq', 'BruChase-seq', 'Bru-seq', 'CRISPRi RNA-seq', 'PRO-seq', '5\' RLM RACE'] },
    { 'DNA methylation': ['DNAme array', 'WGBS', 'RRBS', 'MeDIP-seq', 'MRE-seq', 'TAB-seq'] },
    { 'Replication timing': ['Repli-chip', 'Repli-seq'] },
    { Genotyping: ['genotyping array', 'DNA-PET'] },
    { 'Single cell': ['scRNA-seq', 'snATAC-seq', 'long read scRNA-seq'] },
    { 'DNA sequencing': ['WGS', 'Circulome-seq'] },
    { 'RNA structure': ['icSHAPE', 'icLASER'] },
    { Proteomics: ['MS-MS'] },
];

/**
 * Sort a collection descendingly
 * @param {object} a First item
 * @param {Object} b Second item
 *
 * @returns Sorted collection
 */
const sortByDescending = (a, b) => {
    if (a === b) {
        return 0;
    }
    return a > b ? 1 : -1;
};

/** Page description */
const matrixDescription = 'Cell line samples that were deeply profiled using a set of diverse biochemical approaches, listed with the corresponding batch identifiers.';

/** Determines if user is on All-page or not  */
const isAllDeeplyMatrix = (pageUrl) => pageUrl.includes('deeply-profiled-matrix');

/** Switch page */
const switchDeeplyProfilePageType = (isAll, pageUrl, navigate) => {
    const queryStrings = url.parse(pageUrl, true);
    const query = new QueryString(queryStrings.search);
    query.deleteKeyValue(internalTagKey);
    let pathName = '';

    if (isAll) {
        pathName = 'deeply-profiled-matrix';
    } else {
        pathName = 'deeply-profiled-uniform-batch-matrix';
        query.addKeyValue(internalTagKey, 'Deeply Profiled');
    }
    navigate(`/${pathName}/${query.format()}`);
};

/**
 * Given one subcategory of matrix data (all the subcategory rows within a category), collect
 * summary information about that data.
 * @param {array}  subCategoryData Array of subcategory objects, each containing an array of data
 * @param {string} columnCategoryType `subCategoryData` property that contains data array
 * @param {array}  colTitleMap Maps column titles to the column indices they correspond to
 * @param {number} colCount Number of columns in matrix
 *
 * @return {object} Summary information about given matrix data:
 *     {
 *         {array} subCategorySums: Column sums for all subcategory rows
 *         {number} maxSubCategoryValue: Maximum value in all cells in all subcategory rows
 *         {number} minSubCategoryValue: Minimum value in all cells in all subcategory rows
 *     }
 */
const analyzeSubCategoryData = (subCategoryData, columnCategoryType, colTitleMap, colCount) => {
    const subCategorySums = Array(colCount).fill(0);
    let maxSubCategoryValue = 0;
    let minSubCategoryValue = Number.MAX_VALUE;

    subCategoryData.forEach((rowData) => {
        // `rowData` has all the data for one row. Collect sums of all data for each column.
        rowData[columnCategoryType].buckets.forEach((value) => {
            const colIndex = colTitleMap[value.key];
            subCategorySums[colIndex] = (subCategorySums[colIndex] || 0) + value.doc_count;
        });

        // Update min and max values found within all subcategories of the given category.
        const rowDataValues = rowData[columnCategoryType].buckets.map((bucket) => bucket.doc_count);
        const prospectiveMax = Math.max(...rowDataValues);
        if (maxSubCategoryValue < prospectiveMax) {
            maxSubCategoryValue = prospectiveMax;
        }
        const prospectiveMin = Math.min(...rowDataValues.filter((value) => value));
        if (minSubCategoryValue > prospectiveMin) {
            minSubCategoryValue = prospectiveMin;
        }
    });
    return { maxSubCategoryValue, minSubCategoryValue: minSubCategoryValue - 1 };
};


let _navbarHeight = null;

/**
 * Get height of the navbar
 *
 * @returns height of navbar on first call and restores same value until page is garbage collected
 */
const getNavbarHeight = () => {
    if (_navbarHeight === null) {
        const navbar = document.querySelector('#navbar');
        _navbarHeight = navbar ? navbar.getBoundingClientRect().height : 0;
    }
    return _navbarHeight;
};

/**
 * Takes matrix data from JSON and generates an object that <DataTable> can use to generate the JSX
 * for the matrix. This is a shim between the deeply profiled or audit data and the data <DataTable>
 * needs.
 * @param {object} context Matrix JSON for the page
 * @param {func}   getRowCategories Returns rowCategory info including desired display order
 * @param {func}   getRowSubCategories Returns subCategory desired display order
 * @param {func}   mapRowCategoryQueries Callback to map row category query values
 * @param {func}   mapSubCategoryQueries Callback to map subcategory query values
 * @param {array}  expandedRowCategories Names of rowCategories the user has expanded
 * @param {func}   expanderClickHandler Called when the user expands/collapses a row category
 *
 * @return {object} Generated object suitable for passing to <DataTable>
 */

const convertDeeplyProfileDatatToDataTable = (context, getRowCategories, getRowSubCategories, mapRowCategoryQueries, mapSubCategoryQueries, expandedRowCategories, expanderClickHandler) => {
    const rowCategory = context.matrix.y.group_by[0];
    const subCategory = context.matrix.y.group_by[1];
    const columnCategoryType = context.matrix.x.group_by[0];
    const biosampleTermId = 'replicates.library.biosample.biosample_ontology.term_id';

    const assayTitleSortOrder = [];

    assayTypeToAssayTitles.forEach((typeToTitle) => {
        const assayTypes = Object.values(typeToTitle)[0]?.sort((assayType1, assayTypes2) => sortByDescending(assayType1, assayTypes2));
        assayTitleSortOrder.push(...assayTypes);
    });

    // Generate the top-row sideways header labels. First item is null for the empty upper-left
    // cell.
    const xBucket = context.matrix.x[columnCategoryType].buckets
        .sort((x1, x2) => assayTitleSortOrder.indexOf(x1.key) - assayTitleSortOrder.indexOf(x2.key));
    const colCount = xBucket.length;
    const colTitleMap = {};
    const colCategoryNames = xBucket
        .map((colCategoryBucket, colIndex) => {
            colTitleMap[colCategoryBucket.key] = colIndex;
            return colCategoryBucket.key;
        });

    // Set specific base urls, in different combinations
    let query = new QueryString(context.search_base);
    query.deleteKeyValue(subCategory);
    query.deleteKeyValue(biosampleTermId); // this may be injected in the url link from Navbar
    query.deleteKeyValue(columnCategoryType);
    const baseUrlWithoutSubNorColCategoriesType = query.format();

    query = new QueryString(context.search_base);
    query.deleteKeyValue(columnCategoryType);

    const baseUrlWithoutColCategoryType = query.format();

    const header = [{ header: null }].concat(colCategoryNames.map((colCategoryName) => ({
        header: <a href={`${baseUrlWithoutColCategoryType}&${columnCategoryType}=${colCategoryName}`}>{colCategoryName}</a>,
    })));

    // Generate the main table content including the data hierarchy, where the upper level of the
    // hierarchy gets referred to here as "rowCategory" and the lower-level gets referred to as
    // "subCategory." Both these types of rows get collected into `matrixDataTable`.
    // `rowCategoryIndex` doesn't necessarily match the actual table row index because of the
    // inserted spacer rows, so `matrixRow` tracks the actual table row index.
    const { rowCategoryData, rowCategoryColors, rowCategoryNames } = getRowCategories();
    const matrixRowKeys = ['column-categories'];
    let matrixRow = 1;
    const matrixDataTable = rowCategoryData.sort((a, b) => sortByDescending(a.key, b.key)).reduce((accumulatingTable, rowCategoryBucket, rowCategoryIndex) => {
        const subCategoryData = getRowSubCategories(rowCategoryBucket);
        const rowCategoryColor = rowCategoryColors[rowCategoryIndex];
        const rowCategoryTextColor = isLight(rowCategoryColor) ? '#000' : '#fff';
        const expandableRowCategory = subCategoryData.length > SUB_CATEGORY_SHORT_SIZE;
        const mappedRowCategoryQuery = mapRowCategoryQueries(rowCategory, rowCategoryBucket);

        // For the current row category, collect the sum of every column into an array to display
        // on the rowCategory parent row. Also get the minimum and maximum subCategory values
        // within the current rowCategory so we can scale the tints of this rowCategory's color.
        // A log curve gets applied to the tint scale, so prep for that as well.
        const { minSubCategoryValue, maxSubCategoryValue } = analyzeSubCategoryData(subCategoryData, columnCategoryType, colTitleMap, colCount);
        const logBase = Math.log(1 + maxSubCategoryValue + minSubCategoryValue);

        // Generate one rowCategory's rows of subCategories, adding a header cell for each
        // subCategory on the left of the row.
        const categoryNameQuery = encoding.encodedURIComponentOLD(rowCategoryBucket.key);
        const categoryExpanded = expandedRowCategories.indexOf(rowCategoryBucket.key) !== -1;
        const renderedData = categoryExpanded ? subCategoryData : subCategoryData.slice(0, SUB_CATEGORY_SHORT_SIZE);
        matrixRowKeys[matrixRow] = rowCategoryBucket.key;
        matrixRow += 1;

        const cells = Array(colCount);
        const subCategoryRows = renderedData.map((subCategoryBucket) => {
            // If needed, map the current subcategory queries to a query-string component.
            const mappedSubCategoryQuery = mapSubCategoryQueries(subCategory, subCategoryBucket.key);

            const biosampleQuery = new QueryString(context.search_base);
            biosampleQuery.deleteKeyValue(subCategory);
            biosampleQuery.deleteKeyValue(biosampleTermId); // this may be injected in the url link from Navbar
            biosampleQuery.deleteKeyValue(columnCategoryType);

            const baseUrlWithoutSubcategoryTypeBiosampleQuery = biosampleQuery.format();

            // Generate an array of data cells for a single subCategory row's data.
            cells.fill(null);
            subCategoryBucket[columnCategoryType].buckets.forEach((cellData) => {
                const columnIndex = colTitleMap[cellData.key];

                // Generate one data cell with a color tint that varies based on its value within
                // the range of data in this category.
                let tintFactor = 0;
                if (cellData.doc_count > 0) {
                    // Generate a tint from 0 (no change) to 1 (white) with a log curve over the
                    // range of data.
                    tintFactor = maxSubCategoryValue > minSubCategoryValue ? 1 - (Math.log(1 + (cellData.doc_count - minSubCategoryValue)) / logBase) : 0.5;
                }
                const cellColor = tintColor(rowCategoryColor, tintFactor);
                const textColor = isLight(cellColor) ? '#000' : '#fff';
                cells[columnIndex] = {
                    content: (
                        cellData.doc_count > 0 ?
                            <a href={`${baseUrlWithoutSubNorColCategoriesType}&${mappedSubCategoryQuery}&${columnCategoryType}=${encoding.encodedURIComponentOLD(colCategoryNames[columnIndex])}&${rowCategory}=${rowCategoryBucket.key}`} style={{ color: textColor }}>{cellData.doc_count}</a>
                        :
                            <div />
                    ),
                    style: { backgroundColor: cellData.doc_count > 0 ? cellColor : 'transparent' },
                };
            });

            // Add a single row's data and left header to the matrix.
            matrixRowKeys[matrixRow] = `${rowCategoryBucket.key}-${subCategoryBucket.key}`;
            matrixRow += 1;
            return {
                rowContent: [
                    { header: <a href={`${baseUrlWithoutSubcategoryTypeBiosampleQuery}${mappedSubCategoryQuery ? `&${mappedSubCategoryQuery}` : ''}`}>{subCategoryBucket.key.replace('/biosamples/', '').replace('/', '')}</a> },
                ].concat(cells),
                css: 'matrix__row-data',
            };
        });

        // Generate a row for a rowCategory alone, concatenated with the subCategory rows under it,
        // concatenated with an spacer row that might be empty or might have a rowCategory expander
        // button.
        matrixRowKeys[matrixRow] = `${rowCategoryBucket.key}-spacer`;
        matrixRow += 1;

        const rowHeaderQuery = new QueryString(context['@id']);
        rowHeaderQuery.deleteKeyValue(biosampleTermId);
        const rowHeaderUrl = rowHeaderQuery.format();

        const rowHeaderCountQuery = new QueryString(context.search_base);
        rowHeaderCountQuery.deleteKeyValue(columnCategoryType);
        rowHeaderCountQuery.deleteKeyValue(biosampleTermId); // this may be injected in the url link from Navbar
        const baseUrlWithoutColCategoryTypeForQueryCount = rowHeaderCountQuery.format();

        return accumulatingTable.concat(
            [
                {
                    rowContent: [{
                        header: (
                            <div id={globals.sanitizeId(rowCategoryBucket.key)} style={{ backgroundColor: rowCategoryColor }}>
                                {expandableRowCategory ?
                                    <RowCategoryExpander
                                        categoryId={rowCategoryBucket.key}
                                        categoryName={rowCategoryBucket.key}
                                        expanderColor={rowCategoryTextColor}
                                        expanded={categoryExpanded}
                                        expanderClickHandler={expanderClickHandler}
                                    />
                                : null}
                                <a href={`${rowHeaderUrl}&${mappedRowCategoryQuery}`} style={{ color: rowCategoryTextColor }} id={categoryNameQuery}>{rowCategoryNames[rowCategoryBucket.key]}</a>
                            </div>
                        ),
                    }].concat(colCategoryNames.map((col) => {
                        const rowCategoryBuckets = (context.matrix.x.assay_title.buckets.find((b) => b.key === col) || {})[rowCategory]?.buckets.find((b) => b.key === rowCategoryBucket.key);
                        const docCounts = (rowCategoryBuckets || {})['@id']?.buckets.map((b) => b.doc_count);
                        const docCount = docCounts?.reduce((a, b) => a + b) || 0;

                        return {
                            content: (
                                docCount > 0 ?
                                    <a style={{ backgroundColor: rowCategoryColor, color: rowCategoryTextColor }} href={`${baseUrlWithoutColCategoryTypeForQueryCount}&${mappedRowCategoryQuery}&${columnCategoryType}=${encoding.encodedURIComponentOLD(col)}`}>
                                        {docCount}
                                    </a>
                                :
                                    <div style={{ backgroundColor: rowCategoryColor }} />
                            ),
                        };
                    })),
                    css: 'matrix__row-category',
                },
            ],
            subCategoryRows,
            [{
                rowContent: [
                    {
                        content: (
                            expandableRowCategory ?
                                <RowCategoryExpander
                                    categoryId={categoryNameQuery}
                                    categoryName={rowCategoryBucket.key}
                                    expanded={categoryExpanded}
                                    expanderClickHandler={expanderClickHandler}
                                    expanderColor={rowCategoryTextColor}
                                    expanderBgColor={rowCategoryColor}
                                />
                            : null
                        ),
                    },
                    {
                        content: null,
                        colSpan: 0,
                    },
                ],
                css: `matrix__row-spacer${expandableRowCategory ? ' matrix__row-spacer--expander' : ''}`,
            }]
        );
    }, [{ rowContent: header, css: 'matrix__col-category-header' }]);
    return { dataTable: matrixDataTable, rowKeys: matrixRowKeys };
};


/**
 * Render the area above the facets and matrix content.
 */
const MatrixHeader = ({ context }, reactContext) => {
    const visualizeDisabledTitle = context.total > MATRIX_VISUALIZE_LIMIT ? `Filter to ${MATRIX_VISUALIZE_LIMIT} to visualize` : '';
    const pageUrl = context['@id'];

    return (
        <div className="matrix-header">
            <div className="matrix-header__title">
                <div className="matrix-title-badge">
                    <h1>{context.title}</h1>
                </div>
                <div className="matrix-description">
                    <div className="matrix-description__text">{matrixDescription}</div>
                </div>
            </div>
            <div className="matrix-header__controls">
                <div className="matrix-header__filter-controls">
                    <div className="test-project-selector">
                        <input type="radio" id="allDeeplyProfiled2" name="data-selection" value="All" checked={isAllDeeplyMatrix(pageUrl)} onChange={() => switchDeeplyProfilePageType(true, pageUrl, reactContext.navigate)} />
                        <label htmlFor="allDeeplyProfiled2">All</label> &nbsp; &nbsp;
                        <input type="radio" id="deeplyProfiled" name="data-selection" value="DeeplyProfiled" checked={!isAllDeeplyMatrix(pageUrl)} onChange={() => switchDeeplyProfilePageType(false, pageUrl, reactContext.navigate)} />
                        <label htmlFor="deeplyProfiled">Uniform batch growth</label>
                    </div>
                </div>
                <div className="matrix-header__search-controls">
                    <h4>Showing {context.total} results</h4>
                    <SearchControls context={context} visualizeDisabledTitle={visualizeDisabledTitle} />
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

const MatrixAddCart = ({ context, fetch, pageName }) => {
    const [experimentData, setExperimentData] = React.useState(null);
    const link = [context['@id'].replace(pageName, 'search'), '&limit=all'].join('');

    React.useEffect(() => {
        fetch(link, {
            headers: { Accept: 'application/json' },
        }).then((response) => {
            if (response.ok) {
                return response.json();
            }
            return [];
        }).then((data) => {
            const experimentIds = data['@graph']?.map((experiment) => experiment['@id']);
            setExperimentData(experimentIds || []);
        });
    }, [context]);

    return (
        experimentData !== null ?
            <>
                <div className="matrix-cell-line__cart-button">
                    <CartAddAllElements elements={experimentData} />
                </div>
                <div className="matrix-cell-line__cart-clear" />
            </> :
            <button type="button" className="btn btn-info btn-sm deeply-profiled-matrix-spinner-label deeply-profiled-matrix-spinner--loading">
                Loading &nbsp;
            </button>
    );
};

MatrixAddCart.propTypes = {
    context: PropTypes.object.isRequired,
    fetch: PropTypes.func.isRequired,
    pageName: PropTypes.string.isRequired,
};

/**
 * Render the vertical facets.
 */
const MatrixVerticalFacets = ({ context }) => (
    <FacetList
        context={context}
        facets={context.facets}
        filters={context.filters}
        addClasses="matrix-facets"
        supressTitle
    />
);

MatrixVerticalFacets.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};


/**
 * Display the matrix and associated controls above them.
 */
class MatrixPresentation extends React.Component {
    constructor(props) {
        super(props);

        const query = new QueryString(this.props.context['@id']);
        const tagKey = query.getKeyValues(internalTagKey);
        const hasDeeplyProfiledTag = tagKey[0] === internalTagValue;

        this.state = {
            /** Categories the user has expanded */
            expandedRowCategories: hasDeeplyProfiledTag ? props.context.matrix.y['replicates.library.biosample.biosample_ontology.term_name'].buckets.map((termName) => termName.key) : [],
            /** True if matrix scrolled all the way to the right; used for flashing arrow */
            scrolledRight: false,
        };
        this.expanderClickHandler = this.expanderClickHandler.bind(this);
        this.handleOnScroll = this.handleOnScroll.bind(this);
        this.handleScrollIndicator = this.handleScrollIndicator.bind(this);
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
            this.setState({ expandedRowCategories: [] });
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

    /**
     * Called when the user clicks on the expander button on a category to collapse or expand it.
     * @param {string} category Key for the category
     */
    expanderClickHandler(category) {
        this.setState((prevState) => {
            const matchingCategoryIndex = prevState.expandedRowCategories.indexOf(category);
            if (matchingCategoryIndex === -1) {
                // Category doesn't exist in array, so add it.
                return { expandedRowCategories: prevState.expandedRowCategories.concat(category) };
            }

            // Category does exist in array
            // Move close to header
            const header = document.querySelector(`#${globals.sanitizeId(category)}`);
            const headerToPageTopDistance = header ? header.getBoundingClientRect().top : 0;
            const buffer = 20; // extra space between navbar and header
            const top = headerToPageTopDistance - (getNavbarHeight() + buffer);
            window.scrollBy({
                top,
                left: 0,
                behavior: 'smooth',
            });

            // Remove category.
            const expandedCategories = prevState.expandedRowCategories;
            return { expandedRowCategories: [...expandedCategories.slice(0, matchingCategoryIndex), ...expandedCategories.slice(matchingCategoryIndex + 1)] };
        });
    }

    render() {
        const { context, rowCategoryGetter, rowSubCategoryGetter, mapRowCategoryQueries, mapSubCategoryQueries } = this.props;
        const { scrolledRight } = this.state;

        // Convert encode matrix data to a DataTable object.
        const { dataTable, rowKeys } = convertDeeplyProfileDatatToDataTable(context, rowCategoryGetter, rowSubCategoryGetter, mapRowCategoryQueries, mapSubCategoryQueries, this.state.expandedRowCategories, this.expanderClickHandler);
        const matrixConfig = {
            rows: dataTable,
            rowKeys,
            tableCss: 'matrix',
        };

        return (
            <div className="matrix__presentation">
                <div className={`matrix__label matrix__label--horz${!scrolledRight ? ' horz-scroll' : ''}`}>
                    <span>{context.matrix.x.label}</span>
                    {svgIcon('largeArrow')}
                </div>
                <div className="matrix__presentation-content">
                    <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}Cell Line (batch identifier)</div></div>
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
    /** Callback to retrieve row categories */
    rowCategoryGetter: PropTypes.func.isRequired,
    /** Callback to retrieve subcategories */
    rowSubCategoryGetter: PropTypes.func.isRequired,
    /** Callback to map row category query values */
    mapRowCategoryQueries: PropTypes.func.isRequired,
    /** Callback to map subcategory query values */
    mapSubCategoryQueries: PropTypes.func.isRequired,
};


/**
 * Render the vertical facets and the matrix itself.
 */
const MatrixContent = ({ context, rowCategoryGetter, rowSubCategoryGetter, mapRowCategoryQueries, mapSubCategoryQueries }) => (
    <div className="matrix__content">
        <MatrixVerticalFacets context={context} />
        <MatrixPresentation context={context} rowCategoryGetter={rowCategoryGetter} rowSubCategoryGetter={rowSubCategoryGetter} mapRowCategoryQueries={mapRowCategoryQueries} mapSubCategoryQueries={mapSubCategoryQueries} />
    </div>
);

MatrixContent.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
    /** Callback to retrieve row categories from matrix data */
    rowCategoryGetter: PropTypes.func.isRequired,
    /** Callback to retrieve subcategories from matrix data */
    rowSubCategoryGetter: PropTypes.func.isRequired,
    /** Callback to map row category query values */
    mapRowCategoryQueries: PropTypes.func.isRequired,
    /** Callback to map subcategory query values */
    mapSubCategoryQueries: PropTypes.func.isRequired,
};


/**
 * Map query values to a query-string component actually used in deeply profiled matrix row category
 * link queries.
 * @param {string} rowCategory row category value to map
 * @param {object} rowCategoryBucket Matrix search result row bucket object
 *
 * @return {string} mapped row category query
 */
const mapRowCategoryQueriesExperiment = (rowCategory, rowCategoryBucket) => (
    `${rowCategory}=${encoding.encodedURIComponentOLD(rowCategoryBucket.key)}`
);


/**
 * Map query values to a query-string component actually used in deeply profiled matrix subcategory link
 * queries.
 * @param {string} subCategory subcategory value to map
 * @param {string} subCategoryQuery subcategory query value to map
 * @param {object} rowCategoryBucket Matrix search result row bucket object
 *
 * @return {string} mapped subcategory query
 */
const mapSubCategoryQueriesExperiment = (subCategory, subCategoryQuery) => (
    `${subCategory}=${encoding.encodedURIComponentOLD(subCategoryQuery)}`
);


/**
 * View component for the deeply profiled matrix page.
 */
class DeeplyProfiledUniformBatchMatrix extends React.Component {
    constructor() {
        super();
        this.getRowCategories = this.getRowCategories.bind(this);
        this.getRowSubCategories = this.getRowSubCategories.bind(this);
    }

    /**
     * Called to retrieve row category data for the deeply profiled matrix.
     */
    getRowCategories() {
        const rowCategory = this.props.context.matrix.y.group_by[0];
        const rowCategoryData = this.props.context.matrix.y[rowCategory].buckets.filter((rowCategoryItem) => globals.DeeplyProfiledCellLineList.includes(rowCategoryItem.key));
        const rowCategoryColors = globals.DeeplyProfiledCellLineListColors.colorList(rowCategoryData.map((rowCategoryDatum) => rowCategoryDatum.key));
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

    /**
     * Called to retrieve subcategory data for the deeply profiled matrix.
     */
    getRowSubCategories(rowCategoryBucket) {
        const subCategoryName = this.props.context.matrix.y.group_by[1];
        return rowCategoryBucket[subCategoryName].buckets;
    }

    render() {
        const { context } = this.props;
        const itemClass = globals.itemClass(context, 'view-item');

        if (context.total > 0) {
            return (
                <Panel addClasses={itemClass}>
                    <PanelBody>
                        <MatrixHeader context={context} />
                        <MatrixAddCart context={context} fetch={this.context.fetch} pageName={matrixName} />
                        <MatrixContent context={context} rowCategoryGetter={this.getRowCategories} rowSubCategoryGetter={this.getRowSubCategories} mapRowCategoryQueries={mapRowCategoryQueriesExperiment} mapSubCategoryQueries={mapSubCategoryQueriesExperiment} />
                    </PanelBody>
                </Panel>
            );
        }
        return <h4>No results found</h4>;
    }
}

DeeplyProfiledUniformBatchMatrix.propTypes = {
    context: PropTypes.object.isRequired,
};

DeeplyProfiledUniformBatchMatrix.contextTypes = {
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
    fetch: PropTypes.func,
};

globals.contentViews.register(DeeplyProfiledUniformBatchMatrix, 'DeeplyProfiledUniformBatchMatrix');

export {
    matrixDescription,
    isAllDeeplyMatrix,
    switchDeeplyProfilePageType,
    MatrixAddCart,
};
