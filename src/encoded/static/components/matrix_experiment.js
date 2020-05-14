import React from 'react';
import PropTypes from 'prop-types';
import queryString from 'query-string';
import _ from 'underscore';
import url from 'url';
import * as encoding from '../libs/query_encoding';
import { Panel, PanelBody } from '../libs/ui/panel';
import { svgIcon } from '../libs/svg-icons';
import { tintColor, isLight } from './datacolors';
import DataTable from './datatable';
import * as globals from './globals';
import { RowCategoryExpander, SearchFilter, MATRIX_VISUALIZE_LIMIT } from './matrix';
import { MatrixInternalTags } from './objectutils';
import { FacetList, ClearFilters, SearchControls } from './search';


/**
 * Number of subcategory items to show when subcategory isn't expanded.
 * @constant
 */
const SUB_CATEGORY_SHORT_SIZE = 5;


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
        const rowDataValues = rowData[columnCategoryType].buckets.map(bucket => bucket.doc_count);
        const prospectiveMax = Math.max(...rowDataValues);
        if (maxSubCategoryValue < prospectiveMax) {
            maxSubCategoryValue = prospectiveMax;
        }
        const prospectiveMin = Math.min(...rowDataValues.filter(value => value));
        if (minSubCategoryValue > prospectiveMin) {
            minSubCategoryValue = prospectiveMin;
        }
    });
    return { subCategorySums, maxSubCategoryValue, minSubCategoryValue: minSubCategoryValue - 1 };
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
 * for the matrix. This is a shim between the experiment or audit data and the data <DataTable>
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

const convertExperimentToDataTable = (context, getRowCategories, getRowSubCategories, mapRowCategoryQueries, mapSubCategoryQueries, expandedRowCategories, expanderClickHandler) => {
    const rowCategory = context.matrix.y.group_by[0];
    const subCategory = context.matrix.y.group_by[1];
    const columnCategoryType = context.matrix.x.group_by;

    // Generate the top-row sideways header labels. First item is null for the empty upper-left
    // cell.
    const colCount = context.matrix.x[context.matrix.x.group_by].buckets.length;
    const colTitleMap = {};
    const colCategoryNames = context.matrix.x[context.matrix.x.group_by].buckets.map((colCategoryBucket, colIndex) => {
        colTitleMap[colCategoryBucket.key] = colIndex;
        return colCategoryBucket.key;
    });
    const searchUrl = [context.search_base.split('&')[0], '&status=released'].join(''); // fancy way of removing query string parameters from URL
    const header = [{ header: null }].concat(colCategoryNames.map(colCategoryName => ({
        header: <a href={`${searchUrl}&${columnCategoryType}=${colCategoryName}`}>{colCategoryName}</a>,
    })));

    // Generate the main table content including the data hierarchy, where the upper level of the
    // hierarchy gets referred to here as "rowCategory" and the lower-level gets referred to as
    // "subCategory." Both these types of rows get collected into `matrixDataTable`.
    // `rowCategoryIndex` doesn't necessarily match the actual table row index because of the
    // inserted spacer rows, so `matrixRow` tracks the actual table row index.
    const { rowCategoryData, rowCategoryColors, rowCategoryNames } = getRowCategories();
    const matrixRowKeys = ['column-categories'];
    let matrixRow = 1;
    const matrixDataTable = rowCategoryData.reduce((accumulatingTable, rowCategoryBucket, rowCategoryIndex) => {
        const subCategoryData = getRowSubCategories(rowCategoryBucket);
        const rowCategoryColor = rowCategoryColors[rowCategoryIndex];
        const rowCategoryTextColor = isLight(rowCategoryColor) ? '#000' : '#fff';
        const expandableRowCategory = subCategoryData.length > SUB_CATEGORY_SHORT_SIZE;
        const mappedRowCategoryQuery = mapRowCategoryQueries(rowCategory, rowCategoryBucket);

        // For the current row category, collect the sum of every column into an array to display
        // on the rowCategory parent row. Also get the minimum and maximum subCategory values
        // within the current rowCategory so we can scale the tints of this rowCategory's color.
        // A log curve gets applied to the tint scale, so prep for that as well.
        const { subCategorySums, minSubCategoryValue, maxSubCategoryValue } = analyzeSubCategoryData(subCategoryData, columnCategoryType, colTitleMap, colCount);
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
                            <a href={`${searchUrl}&${mappedSubCategoryQuery}&${columnCategoryType}=${encoding.encodedURIComponentOLD(colCategoryNames[columnIndex])}`} style={{ color: textColor }}>{cellData.doc_count}</a>
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
                    { header: <a href={`${context.search_base}${context.search_base.includes(mappedSubCategoryQuery) ? '' : ['&', mappedSubCategoryQuery].join('')}`}>{subCategoryBucket.key}</a> },
                ].concat(cells),
                css: 'matrix__row-data',
            };
        });

        // Generate a row for a rowCategory alone, concatenated with the subCategory rows under it,
        // concatenated with an spacer row that might be empty or might have a rowCategory expander
        // button.
        matrixRowKeys[matrixRow] = `${rowCategoryBucket.key}-spacer`;
        matrixRow += 1;
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
                                <a href={`${context['@id']}&${mappedRowCategoryQuery}`} style={{ color: rowCategoryTextColor }} id={categoryNameQuery}>{rowCategoryNames[rowCategoryBucket.key]}</a>
                            </div>
                        ),
                    }].concat(subCategorySums.map((subCategorySum, subCategorySumIndex) => ({
                        content: (
                            subCategorySum > 0 ?
                                <a style={{ backgroundColor: rowCategoryColor, color: rowCategoryTextColor }} href={`${searchUrl}&${mappedRowCategoryQuery}&${columnCategoryType}=${encoding.encodedURIComponentOLD(colCategoryNames[subCategorySumIndex])}`}>
                                    {subCategorySum}
                                </a>
                            :
                                <div style={{ backgroundColor: rowCategoryColor }} />
                        ),
                    }))),
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
const MatrixHeader = ({ context }) => {
    const visualizeDisabledTitle = context.total > MATRIX_VISUALIZE_LIMIT ? `Filter to ${MATRIX_VISUALIZE_LIMIT} to visualize` : '';

    let clearButton;
    const parsedUrl = url.parse(context['@id'], true);
    parsedUrl.query.format = 'json';
    parsedUrl.search = '';
    const searchQuery = url.parse(context['@id']).search;
    if (searchQuery) {
        // If we have a 'type' query string term along with others terms, we need a Clear Filters
        // button.
        const terms = queryString.parse(searchQuery);
        const nonPersistentTerms = _(Object.keys(terms)).any(term => term !== 'type');
        clearButton = nonPersistentTerms && terms.type;
    }

    // Compose a type title for the page if only one type is included in the query string.
    // Currently, only one type is allowed in the query string or the server returns a 400, so this
    // code exists in case more than one type is allowed in future.
    let type = '';
    if (context.filters && context.filters.length > 0) {
        const typeFilters = context.filters.filter(filter => filter.field === 'type');
        if (typeFilters.length === 1) {
            type = typeFilters[0].term;
        }
    }

    return (
        <div className="matrix-header">
            <div className="matrix-header__title">
                <h1>{type ? `${type} ` : ''}{context.title}</h1>
                <div className="matrix-tags">
                    <MatrixInternalTags context={context} />
                </div>
            </div>
            <div className="matrix-header__controls">
                <div className="matrix-header__filter-controls">
                    <ClearFilters searchUri={context.clear_filters} enableDisplay={!!clearButton} />
                    <SearchFilter context={context} />
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


/**
 * Render the vertical facets.
 */
const MatrixVerticalFacets = ({ context }, reactContext) => (
    <FacetList
        context={context}
        facets={context.facets}
        filters={context.filters}
        searchBase={`${url.parse(reactContext.location_href).search}&` || '?'}
        addClasses="matrix-facets"
        supressTitle
    />
);

MatrixVerticalFacets.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};

MatrixVerticalFacets.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};


/**
 * Display the matrix and associated controls above them.
 */
class MatrixPresentation extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            /** Categories the user has expanded */
            expandedRowCategories: [],
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

    componentDidUpdate(prevProps) {
        // If URI changed, we need close any expanded rowCategories in case the URI change results
        // in a huge increase in displayed data. Also update the scroll indicator if needed.
        if (prevProps.context['@id'] !== this.props.context['@id']) {
            this.handleScrollIndicator(this.scrollElement);
            this.setState({ expandedRowCategories: [] });
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

    render() {
        const { context, rowCategoryGetter, rowSubCategoryGetter, mapRowCategoryQueries, mapSubCategoryQueries } = this.props;
        const { scrolledRight } = this.state;

        // Convert encode matrix data to a DataTable object.
        const { dataTable, rowKeys } = convertExperimentToDataTable(context, rowCategoryGetter, rowSubCategoryGetter, mapRowCategoryQueries, mapSubCategoryQueries, this.state.expandedRowCategories, this.expanderClickHandler);
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
 * Map query values to a query-string component actually used in experiment matrix row category
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
 * Map query values to a query-string component actually used in experiment matrix subcategory link
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
 * View component for the experiment matrix page.
 */
class ExperimentMatrix extends React.Component {
    constructor() {
        super();
        this.getRowCategories = this.getRowCategories.bind(this);
        this.getRowSubCategories = this.getRowSubCategories.bind(this);
    }

    /**
     * Called to retrieve row category data for the experiment matrix.
     */
    getRowCategories() {
        const rowCategory = this.props.context.matrix.y.group_by[0];
        const rowCategoryData = this.props.context.matrix.y[rowCategory].buckets;
        const rowCategoryColors = globals.biosampleTypeColors.colorList(rowCategoryData.map(rowCategoryDatum => rowCategoryDatum.key));
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
     * Called to retrieve subcategory data for the experiment matrix.
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
                        <MatrixContent context={context} rowCategoryGetter={this.getRowCategories} rowSubCategoryGetter={this.getRowSubCategories} mapRowCategoryQueries={mapRowCategoryQueriesExperiment} mapSubCategoryQueries={mapSubCategoryQueriesExperiment} />
                    </PanelBody>
                </Panel>
            );
        }
        return <h4>No results found</h4>;
    }
}

ExperimentMatrix.propTypes = {
    context: PropTypes.object.isRequired,
};

ExperimentMatrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
};

globals.contentViews.register(ExperimentMatrix, 'Matrix');
