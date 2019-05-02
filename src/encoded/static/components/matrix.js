/**
 * @fileOverview Render both the experiment and audit matrices whenever their corresponding
 *               endpoints send their JSON.
 */

import React from 'react';
import PropTypes from 'prop-types';
import pluralize from 'pluralize';
import _ from 'underscore';
import url from 'url';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import { svgIcon } from '../libs/svg-icons';
import { tintColor, isLight } from './datacolors';
import DataTable from './datatable';
import * as globals from './globals';
import { MatrixInternalTags } from './objectutils';
import { FacetList, TextFilter, SearchControls, ClearFilters } from './search';


/**
 * Number of subcategory items to show when subcategory isn't expanded.
 * @constant
 */
const SUB_CATEGORY_SHORT_SIZE = 5;


/**
 * Maximum number of selected items that can be visualized.
 * @constant
 */
const VISUALIZE_LIMIT = 500;


/**
 * Render the expander button for a row category, and react to clicks by calling the parent to
 * render the expansion change.
 */
class RowCategoryExpander extends React.Component {
    constructor() {
        super();
        this.handleClick = this.handleClick.bind(this);
    }

    /**
     * Called when the user clicks the expander button to expand or collapse the section.
     */
    handleClick() {
        this.props.expanderClickHandler(this.props.categoryName);
    }

    render() {
        const { categoryId, expanderColor, expanderBgColor, expanded } = this.props;
        return (
            <button
                className="matrix__category-expander"
                aria-expanded={expanded}
                aria-controls={categoryId}
                onClick={this.handleClick}
                style={{ backgroundColor: expanderBgColor }}
            >
                {svgIcon(expanded ? 'chevronUp' : 'chevronDown', { fill: expanderColor })}
            </button>
        );
    }
}

RowCategoryExpander.propTypes = {
    /** Unique ID; should match id of expanded element */
    categoryId: PropTypes.string.isRequired,
    /** Category name; gets passed to click handler */
    categoryName: PropTypes.string.isRequired,
    /** Color to draw the icon or text of the expander button */
    expanderColor: PropTypes.string,
    /** Color to draw the background of the expander button */
    expanderBgColor: PropTypes.string,
    /** True if category is currently expanded */
    expanded: PropTypes.bool,
    /** Function to call to handle clicks in the expander button */
    expanderClickHandler: PropTypes.func.isRequired,
};

RowCategoryExpander.defaultProps = {
    expanderColor: '#000',
    expanderBgColor: 'transparent',
    expanded: false,
};


/**
 * Render and handle the free-text search box. After the user presses the return key, this
 * navigates to the current URL plus the given search term.
 */
class SearchFilter extends React.Component {
    constructor() {
        super();
        this.onChange = this.onChange.bind(this);
    }

    onChange(href) {
        this.context.navigate(href);
    }

    render() {
        const { context } = this.props;
        const parsedUrl = url.parse(this.context.location_href);
        const matrixBase = parsedUrl.search || '';
        const matrixSearch = matrixBase + (matrixBase ? '&' : '?');
        const parsed = url.parse(matrixBase, true);
        const queryStringType = parsed.query.type || '';
        const type = pluralize(queryStringType.toLocaleLowerCase());
        return (
            <div className="matrix-general-search">
                <p>Enter search terms to filter the {type} included in the matrix.</p>
                <div className="general-search-entry">
                    <i className="icon icon-search" />
                    <div className="searchform">
                        <TextFilter filters={context.filters} searchBase={matrixSearch} onChange={this.onChange} />
                    </div>
                </div>
            </div>
        );
    }
}

SearchFilter.propTypes = {
    /** Matrix search results object */
    context: PropTypes.object.isRequired,
};

SearchFilter.contextTypes = {
    navigate: PropTypes.func,
    location_href: PropTypes.string,
};


/**
 * Given one subcategory of matrix data (all the subcategory rows within a category), collect
 * summary information about that data.
 * @param {array}  subCategoryData Array of subcategory objects, each containing an array of data
 * @param {string} columnCategoryType `subCategoryData` property that contains data array
 *
 * @return {object} Summary information about given matrix data:
 *     {
 *         {array} subCategorySums: Column sums for all subcategory rows
 *         {number} maxSubCategoryValue: Maximum value in all cells in all subcategory rows
 *         {number} minSubCategoryValue: Minimum value in all cells in all subcategory rows
 *     }
 */
const analyzeSubCategoryData = (subCategoryData, columnCategoryType) => {
    const subCategorySums = [];
    let maxSubCategoryValue = 0;
    let minSubCategoryValue = Number.MAX_VALUE;

    subCategoryData.forEach((rowData) => {
        // `rowData` has all the data for one row. Collect sums of all data for each column.
        rowData[columnCategoryType].forEach((value, colIndex) => {
            subCategorySums[colIndex] = (subCategorySums[colIndex] || 0) + value;
        });

        // Update min and max values found within all subcategories of the given category.
        const prospectiveMax = Math.max(...rowData[columnCategoryType]);
        if (maxSubCategoryValue < prospectiveMax) {
            maxSubCategoryValue = prospectiveMax;
        }
        const prospectiveMin = Math.min(...rowData[columnCategoryType].filter(value => value));
        if (minSubCategoryValue > prospectiveMin) {
            minSubCategoryValue = prospectiveMin;
        }
    });
    return { subCategorySums, maxSubCategoryValue, minSubCategoryValue: minSubCategoryValue - 1 };
};


/**
 * Takes matrix data from JSON and generates an object that <DataTable> can use to generate the JSX
 * for the matrix. This is a shim between the experiment or audit data and the data <DataTable>
 * needs.
 * @param {object} context Matrix JSON for the page
 * @param {func}   getRowCategories Returns rowCategory info including desired display order
 * @param {func}   getRowSubCategories Returns subCategory desired display order
 * @param {func}   mapQueries Map a row/cell query values if needed
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
    const colCategoryNames = context.matrix.x.buckets.map(colCategoryBucket => colCategoryBucket.key);
    const header = [{ header: null }].concat(colCategoryNames.map(colCategoryName => ({
        header: <a href={`${context.matrix.search_base}&${columnCategoryType}=${colCategoryName}`}>{colCategoryName}</a>,
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
        const { subCategorySums, minSubCategoryValue, maxSubCategoryValue } = analyzeSubCategoryData(rowCategoryBucket[subCategory].buckets, columnCategoryType);
        const logBase = Math.log(1 + maxSubCategoryValue + minSubCategoryValue);

        // Generate one rowCategory's rows of subCategories, adding a header cell for each
        // subCategory on the left of the row.
        const categoryNameQuery = globals.encodedURIComponent(rowCategoryBucket.key);
        const categoryExpanded = expandedRowCategories.indexOf(rowCategoryBucket.key) !== -1;
        const renderedData = categoryExpanded ? subCategoryData : subCategoryData.slice(0, SUB_CATEGORY_SHORT_SIZE);
        matrixRowKeys[matrixRow] = rowCategoryBucket.key;
        matrixRow += 1;
        const subCategoryRows = renderedData.map((subCategoryBucket) => {
            // If needed, map the current subcategory queries to something besides what they are.
            // Currently just for audit matrix.
            const mappedSubCategoryQuery = mapSubCategoryQueries(subCategory, subCategoryBucket.key, rowCategoryBucket);

            // Generate an array of data cells for a single subCategory row's data.
            const cells = subCategoryBucket[columnCategoryType].map((cellData, columnIndex) => {
                // Generate one data cell with a color tint that varies based on its value within
                // the range of data in this category.
                let tintFactor = 0;
                if (cellData > 0) {
                    // Generate a tint from 0 (no change) to 1 (white) with a log curve over the
                    // range of data.
                    tintFactor = maxSubCategoryValue > minSubCategoryValue ? 1 - (Math.log(1 + (cellData - minSubCategoryValue)) / logBase) : 0.5;
                }
                const cellColor = tintColor(rowCategoryColor, tintFactor);
                const textColor = isLight(cellColor) ? '#000' : '#fff';
                return {
                    content: (
                        cellData > 0 ?
                            <a href={`${context.matrix.search_base}&${mappedSubCategoryQuery}&${columnCategoryType}=${globals.encodedURIComponent(colCategoryNames[columnIndex])}`} style={{ color: textColor }}>{cellData}</a>
                        :
                            <div />
                    ),
                    style: { backgroundColor: cellData > 0 ? cellColor : 'transparent' },
                };
            });

            // Add a single row's data and left header to the matrix.
            matrixRowKeys[matrixRow] = `${rowCategoryBucket.key}-${subCategoryBucket.key}`;
            matrixRow += 1;
            return {
                rowContent: [
                    { header: <a href={`${context.matrix.search_base}&${mappedSubCategoryQuery}`}>{subCategoryBucket.key}</a> },
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
                            <div style={{ backgroundColor: rowCategoryColor }}>
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
                                <a style={{ backgroundColor: rowCategoryColor, color: rowCategoryTextColor }} href={`${context.matrix.search_base}&${mappedRowCategoryQuery}&${columnCategoryType}=${globals.encodedURIComponent(colCategoryNames[subCategorySumIndex])}`}>
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
                            : <div />
                        ),
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
 * Render the title panel and list of experiment internal tags.
 */
const MatrixHeader = (props) => {
    const { context } = props;

    return (
        <div className="matrix__header">
            <h1>{context.title}</h1>
            <MatrixInternalTags context={context} />
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
class MatrixVerticalFacets extends React.Component {
    constructor() {
        super();
        this.onFilter = this.onFilter.bind(this);
    }

    /**
     * Called when the user filters the data using a facet. Navigate to the URL of the clicked
     * facet term.
     * @param {object} e React synthetic event containing the filtering URL.
     */
    onFilter(e) {
        const search = e.currentTarget.getAttribute('href');
        this.context.navigate(search);
        e.stopPropagation();
        e.preventDefault();
    }

    render() {
        const { context } = this.props;

        // Calculate the searchBase, which is the current search query string fragment that can
        // have terms added to it.
        const searchBase = `${url.parse(this.context.location_href).search}&` || '?';

        return (
            <div className="matrix__facets-vertical">
                <ClearFilters searchUri={context.matrix.clear_matrix} enableDisplay={context.filters.length > 0} />
                <SearchFilter context={context} />
                <FacetList
                    facets={context.facets}
                    filters={context.filters}
                    searchBase={searchBase}
                    onFilter={this.onFilter}
                    addClasses="matrix-facets"
                />
            </div>
        );
    }
}

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
            expandedRowCategories: [],
            leftShadingShowing: false,
            rightShadingShowing: false,
        };
        this.expanderClickHandler = this.expanderClickHandler.bind(this);
        this.handleOnScroll = this.handleOnScroll.bind(this);
        this.handleScrollShading = this.handleScrollShading.bind(this);
    }

    componentDidMount() {
        // Establish initial matrix scroll shading.
        this.handleScrollShading(this.scrollElement);
    }

    componentDidUpdate(prevProps) {
        // If URI changed, we need to update the scroll shading in case the width of the table
        // changed. Also close any expanded rowCategories in case the URI change results in a huge
        // increase in displayed data.
        if (prevProps.context['@id'] !== this.props.context['@id']) {
            this.handleScrollShading(this.scrollElement);
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

            // Category does exist in array, so remove it.
            const expandedCategories = prevState.expandedRowCategories;
            return { expandedRowCategories: [...expandedCategories.slice(0, matchingCategoryIndex), ...expandedCategories.slice(matchingCategoryIndex + 1)] };
        });
    }

    /**
     * Called when the user scrolls the matrix horizontally within its div to handle the shading on
     * the left and right edges.
     * @param {object} e React synthetic scroll event
     */
    handleOnScroll(e) {
        this.handleScrollShading(e.target);
    }

    /**
     * Apply shading along the left or right of the scrolling matrix DOM element based on its
     * current scrolled position.
     * @param {object} element DOM element to apply shading to
     */
    handleScrollShading(element) {
        if (element.scrollLeft === 0 && this.state.leftShadingShowing) {
            // Left edge of matrix scrolled into view.
            this.setState({ leftShadingShowing: false });
        } else if (element.scrollLeft > 0 && !this.state.leftShadingShowing) {
            // Left edge of matrix scrolled out of view.
            this.setState({ leftShadingShowing: true });
        } else {
            // For right-side shaded area, have to use a "roughly equal to" test because of an
            // MS Edge bug mentioned here:
            // https://stackoverflow.com/questions/30900154/workaround-for-issue-with-ie-scrollwidth
            const scrollDiff = Math.abs((element.scrollWidth - element.scrollLeft) - element.clientWidth);
            if (scrollDiff < 2 && this.state.rightShadingShowing) {
                // Right edge of matrix scrolled into view.
                this.setState({ rightShadingShowing: false });
            } else if (scrollDiff >= 2 && !this.state.rightShadingShowing) {
                // Right edge of matrix scrolled out of view.
                this.setState({ rightShadingShowing: true });
            }
        }
    }

    render() {
        const { context, rowCategoryGetter, rowSubCategoryGetter, mapRowCategoryQueries, mapSubCategoryQueries } = this.props;
        const { leftShadingShowing, rightShadingShowing } = this.state;
        const visualizeDisabledTitle = context.matrix.doc_count > VISUALIZE_LIMIT ? `Filter to ${VISUALIZE_LIMIT} to visualize` : '';

        // Convert encode matrix data to a DataTable object.
        const { dataTable, rowKeys } = convertExperimentToDataTable(context, rowCategoryGetter, rowSubCategoryGetter, mapRowCategoryQueries, mapSubCategoryQueries, this.state.expandedRowCategories, this.expanderClickHandler);
        const matrixConfig = {
            rows: dataTable,
            rowKeys,
            tableCss: 'matrix',
        };

        return (
            <div className="matrix__presentation">
                <h4>Showing {context.matrix.doc_count} results</h4>
                <SearchControls context={context} visualizeDisabledTitle={visualizeDisabledTitle} onFilter={this.onFilter} />
                <div className={`matrix__label matrix__label--horz${rightShadingShowing ? ' horz-scroll' : ''}`}>
                    <span>{context.matrix.x.label}</span>
                    {svgIcon('largeArrow')}
                </div>
                <div className="matrix__presentation-content">
                    <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}{context.matrix.y.label}</div></div>
                    <div className="matrix__data-wrapper">
                        <div className="matrix__data" onScroll={this.handleOnScroll} ref={(element) => { this.scrollElement = element; }}>
                            <DataTable tableData={matrixConfig} />
                        </div>
                        <div className={`matrix-shading matrix-shading--left${leftShadingShowing ? ' showing' : ''}`} />
                        <div className={`matrix-shading matrix-shading--right${rightShadingShowing ? ' showing' : ''}`} />
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
    `${rowCategory}=${globals.encodedURIComponent(rowCategoryBucket.key)}`
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
    `${subCategory}=${globals.encodedURIComponent(subCategoryQuery)}`
);


/**
 * View component for the experiment matrix page.
 */
class Matrix extends React.Component {
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
        const rowCategoryColors = globals.biosampleTypeColors.colorList(rowCategoryData.map(rowDataValue => rowDataValue.key));
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

        if (context.matrix.doc_count > 0) {
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

Matrix.propTypes = {
    context: React.PropTypes.object.isRequired,
};

Matrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
};

globals.contentViews.register(Matrix, 'Matrix');


/**
 * Determines the sorting order of the audits as they appear in the matrix.
 */
const auditOrderKey = [
    'no_audits',
    'audit.WARNING.category',
    'audit.NOT_COMPLIANT.category',
    'audit.ERROR.category',
    'audit.INTERNAL_ACTION.category',
];

/**
 * Determines the sorting order of the "No audits" subcategories.
 */
const noAuditOrderKey = [
    'no errors, compliant, and no warnings',
    'no errors and compliant',
    'no errors',
    'no audits',
];

/**
 * Audit matrix rowCategory colors.
 */
const auditColors = ['#009802', '#e0e000', '#ff8000', '#cc0700', '#a0a0a0'];

/**
 * Maps audit keys to human-readable names.
 */
const auditNames = {
    no_audits: 'No audits',
    'audit.WARNING.category': 'Warning',
    'audit.NOT_COMPLIANT.category': 'Not Compliant',
    'audit.ERROR.category': 'Error',
    'audit.INTERNAL_ACTION.category': 'Internal Action',
};


/**
 * Map query values to a query-string component actually used in audit matrix row category link
 * queries.
 * @param {string} rowCategory row category value to map
 * @param {object} rowCategoryBucket Matrix search result row bucket object
 *
 * @return {string} mapped row category query
 */
const mapRowCategoryQueriesAudit = (rowCategory, rowCategoryBucket) => {
    if (rowCategoryBucket.key === 'no_audits') {
        return 'audit.ERROR.category%21=%2A&audit.NOT_COMPLIANT.category%21=%2A&audit.WARNING.category%21=%2A&audit.INTERNAL_ACTION.category%21=%2A';
    }
    return `${rowCategoryBucket.key}=%2A`;
};


/**
 * Map query values to a query-string component actually used in audit matrix subcategory link
 * queries.
 * @param {string} subCategory subcategory value to map
 * @param {string} subCategoryQuery subcategory query value to map
 * @param {object} rowCategoryBucket Matrix search result row bucket object
 *
 * @return {string} mapped subcategory query
 */
const mapSubCategoryQueriesAudit = (subCategory, subCategoryQuery, rowCategoryBucket) => {
    let query;
    if (rowCategoryBucket.key === 'no_audits') {
        switch (subCategoryQuery) {
        case 'no audits':
            query = 'audit.WARNING.category%21=%2A&audit.NOT_COMPLIANT.category%21=%2A&audit.ERROR.category%21=%2A&audit.INTERNAL_ACTION.category%21=%2A';
            break;
        case 'no errors':
            query = 'audit.ERROR.category%21=%2A';
            break;
        case 'no errors, compliant, and no warnings':
            query = 'audit.ERROR.category%21=%2A&audit.NOT_COMPLIANT.category%21=%2A&audit.WARNING.category%21=%2A';
            break;
        case 'no errors and compliant':
            query = 'audit.ERROR.category%21=%2A&audit.NOT_COMPLIANT.category%21=%2A';
            break;
        default:
            query = '';
            break;
        }
    } else {
        query = `${rowCategoryBucket.key}=${globals.encodedURIComponent(subCategoryQuery)}`;
    }
    return query;
};


/**
 * View component for the audit matrix page.
 */
class AuditMatrix extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.getRowCategories = this.getRowCategories.bind(this);
        this.getRowSubCategories = this.getRowSubCategories.bind(this);
    }

    // Called to sort the audit row categories by the order in `auditOrderKey`.
    getRowCategories() {
        const rowCategory = this.props.context.matrix.y.group_by[0];
        const rowCategories = this.props.context.matrix.y[rowCategory].buckets;
        const rowCategoryData = _.sortBy(rowCategories, (categoryBucket =>
            auditOrderKey.indexOf(categoryBucket.key)
        ));
        return {
            rowCategoryData,
            rowCategoryColors: auditColors,
            rowCategoryNames: auditNames,
        };
    }

    /**
     * Called to retrieve subcategory data for the experiment matrix.
     */
    getRowSubCategories(rowCategoryBucket) {
        const subCategoryName = this.props.context.matrix.y.group_by[1];
        let subCategoryData = rowCategoryBucket[subCategoryName].buckets;
        if (rowCategoryBucket.key === 'no_audits') {
            subCategoryData = _.sortBy(subCategoryData, subCategoryDataBucket =>
                noAuditOrderKey.indexOf(subCategoryDataBucket.key)
            );
        }
        return subCategoryData;
    }

    render() {
        const { context } = this.props;
        const itemClass = globals.itemClass(context, 'view-item');

        if (context.matrix.doc_count) {
            return (
                <Panel addClasses={itemClass}>
                    <PanelBody>
                        <MatrixHeader context={context} />
                        <MatrixContent context={context} rowCategoryGetter={this.getRowCategories} rowSubCategoryGetter={this.getRowSubCategories} mapRowCategoryQueries={mapRowCategoryQueriesAudit} mapSubCategoryQueries={mapSubCategoryQueriesAudit} />
                    </PanelBody>
                </Panel>
            );
        }
        return <h4>No results found</h4>;
    }
}

AuditMatrix.propTypes = {
    context: React.PropTypes.object.isRequired,
};

AuditMatrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
};

globals.contentViews.register(AuditMatrix, 'AuditMatrix');
