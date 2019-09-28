import React from 'react';
import PropTypes from 'prop-types';
import pluralize from 'pluralize';
import queryString from 'query-string';
import _ from 'underscore';
import url from 'url';
import { Panel, PanelBody } from '../libs/ui/panel';
import { svgIcon } from '../libs/svg-icons';
import { tintColor, isLight } from './datacolors';
import DataTable from './datatable';
import * as globals from './globals';
import { MatrixInternalTags } from './objectutils';
import { FacetList, TextFilter, ClearFilters, SearchControls } from './search';


/** Number of subcategory items to show when subcategory isn't expanded. */
const SUB_CATEGORY_SHORT_SIZE = 5;

/** Audit matrix rowCategory colors. */
const auditColors = ['#e0e000', '#ff8000', '#cc0700', '#a0a0a0'];

/**  Sorting order of the audits level category rows. */
const auditOrderKey = [
    'audit.WARNING.category',
    'audit.NOT_COMPLIANT.category',
    'audit.ERROR.category',
    'audit.INTERNAL_ACTION.category',
];

/** Maximum number of selected items that can be visualized. */
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

    /**
     * Called after the user completes entering a search term. Navigate to the resulting query
     * string on this audit matrix page.
     * @param {string} href Query based on user's search term to navigate to
     */
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
 * @param {string} columnCategoryType `subCategoryData` property that contains one row's data array
 *
 * @return {object} Summary information about given matrix data:
 *     {
 *         {number} maxSubCategoryValue: Maximum value in all cells in all subcategory rows
 *         {number} minSubCategoryValue: Minimum value in all cells in all subcategory rows
 *     }
 */
const analyzeSubCategoryData = (subCategoryData, columnCategoryType) => {
    let maxSubCategoryValue = 0;
    let minSubCategoryValue = Number.MAX_VALUE;

    subCategoryData.forEach((rowData) => {
        const rowDataValues = rowData[columnCategoryType].buckets.map(rowItem => rowItem.doc_count);

        // Update min and max values found within all subcategories of the given category.
        const prospectiveMax = Math.max(...rowDataValues);
        if (maxSubCategoryValue < prospectiveMax) {
            maxSubCategoryValue = prospectiveMax;
        }
        const prospectiveMin = Math.min(...rowDataValues.filter(value => value));
        if (minSubCategoryValue > prospectiveMin) {
            minSubCategoryValue = prospectiveMin;
        }
    });
    return { maxSubCategoryValue, minSubCategoryValue: minSubCategoryValue - 1 };
};


/**
 * Remove spaces from id so it can be accepted as an id by HTML.
 * @param {string} id Arbitrary string to sanitize.
 *
 * @return {string} id without space, or dash if id is empty
 */
const sanitizeId = id => (id ? `${id.replace(/\s/g, '_')}` : '-');


let _navbarHeight = null;

/**
 * Get height of the navbar.
 *
 * @return {number} Height of navbar on first call and restores same value until page is garbage
 *                  collected
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
 * @param {array}  expandedRowCategories Names of rowCategories the user has expanded
 * @param {func}   expanderClickHandler Called when the user expands/collapses a row category
 * @param {bool}   loggedIn True if current user is a logged in
 *
 * @return {object} Generated object suitable for passing to <DataTable>
 */

const convertAuditToDataTable = (context, expandedRowCategories, expanderClickHandler, loggedIn) => {
    // Make a couple utility structures -- one (`colTitleMap`) to map column names to the
    // corresponding column index, useful for placing matrix data into the correct column -- the
    // other (`colCategoryNames`) to hold all column category titles in column order.
    const columnCategoryType = context.matrix.x.group_by;
    const colTitleMap = {};
    const colCategoryNames = context.matrix.x[columnCategoryType].buckets.map((colCategoryBucket, colIndex) => {
        colTitleMap[colCategoryBucket.key] = colIndex;
        return colCategoryBucket.key;
    });

    // Generate the top-row sideways header labels. First item is null for the empty upper-left
    // cell.
    const header = [{ header: null }].concat(colCategoryNames.map(colCategoryName => ({
        header: <a href={`${context.search_base}&${columnCategoryType}=${globals.encodedURIComponent(colCategoryName)}`}>{colCategoryName}</a>,
    })));

    // Extract the audit names (levels) from the given row data and sort it according to their
    // presentation order. Use these to get each audit level's data from the matrix data. Changes
    // to the order should happen in the global, `auditOrderKey`. The `x` property in `matrix`
    // holds other data we need later, so that doesn't get included.
    const unsortedRowCategoryNames = Object.keys(context.matrix).filter(auditLevel => auditLevel !== 'x' && (loggedIn || auditLevel !== 'audit.INTERNAL_ACTION.category'));
    const rowCategoryNames = _.sortBy(unsortedRowCategoryNames, rowCategoryName => auditOrderKey.indexOf(rowCategoryName));

    // Generate the main table content including the data hierarchy, where the upper level of the
    // hierarchy with the audit levels gets referred to here as "rowCategory" and the lower-level
    // gets referred to as "subCategory." The JSX for both these types of rows get collected into
    // `matrixDataTable`. `rowCategoryIndex` doesn't necessarily match the actual table row index
    // because of the inserted spacer rows, so `matrixRow` tracks the actual table row index while
    // `matrixRowKeys` tracks the corresponding React component keys for each row.
    const matrixRowKeys = ['column-categories'];
    let matrixRow = 1;
    const colCount = context.matrix.x[context.matrix.x.group_by].buckets.length;
    const matrixDataTable = rowCategoryNames.reduce((accumulatingTable, rowCategoryName, rowCategoryNameIndex) => {
        const subCategoryData = context.matrix[rowCategoryName][rowCategoryName].buckets;
        const rowCategoryColor = auditColors[rowCategoryNameIndex];
        const rowCategoryTextColor = isLight(rowCategoryColor) ? '#000' : '#fff';
        const expandableRowCategory = subCategoryData.length > SUB_CATEGORY_SHORT_SIZE;
        const mappedRowCategoryQuery = `${rowCategoryName}=%2A`;

        // For the current row category (audit level), get the minimum and maximum subCategory
        // values so we can scale the tints of this rowCategory's color. A log curve gets applied
        // to the tint scale.
        const { minSubCategoryValue, maxSubCategoryValue } = analyzeSubCategoryData(subCategoryData, columnCategoryType);
        const logBase = Math.log(1 + maxSubCategoryValue + minSubCategoryValue);

        // Generate one rowCategory's rows of subCategories, adding a header cell for each
        // subCategory on the left of the row. The `cells` array gets reused for each row's data
        // (not including the row header label) for <DataTable>.
        const categoryExpanded = expandedRowCategories.indexOf(rowCategoryName) !== -1;
        const renderedData = categoryExpanded ? subCategoryData : subCategoryData.slice(0, SUB_CATEGORY_SHORT_SIZE);
        matrixRowKeys[matrixRow] = rowCategoryName;
        matrixRow += 1;
        const cells = Array(colCount);
        const subCategoryRows = renderedData.map((subCategoryBucket) => {
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
                            <a href={`${context.search_base}&${rowCategoryName}=${globals.encodedURIComponent(subCategoryBucket.key)}&${columnCategoryType}=${globals.encodedURIComponent(colCategoryNames[columnIndex])}`} style={{ color: textColor }}>{cellData.doc_count}</a>
                        :
                            <div />
                    ),
                    style: { backgroundColor: cellData.doc_count > 0 ? cellColor : 'transparent' },
                };
            });

            // Add a single row's data and left header to the matrix.
            matrixRowKeys[matrixRow] = `${rowCategoryName}-${subCategoryBucket.key}`;
            matrixRow += 1;
            return {
                rowContent: [
                    { header: <a href={`${context.search_base}&${rowCategoryName}=${globals.encodedURIComponent(subCategoryBucket.key)}`}>{subCategoryBucket.key}</a> },
                ].concat(cells),
                css: 'matrix__row-data',
            };
        });

        // Generate a row for a rowCategory alone, concatenated with the subCategory rows under it,
        // concatenated with an spacer row that might be empty or might have a rowCategory expander
        // button.
        const categoryNameQuery = globals.encodedURIComponent(rowCategoryName);
        matrixRowKeys[matrixRow] = `${rowCategoryName}-spacer`;
        matrixRow += 1;
        return accumulatingTable.concat(
            [
                {
                    rowContent: [{
                        header: (
                            <div id={sanitizeId(rowCategoryName)} style={{ backgroundColor: rowCategoryColor }}>
                                {expandableRowCategory ?
                                    <RowCategoryExpander
                                        categoryId={rowCategoryName}
                                        categoryName={rowCategoryName}
                                        expanderColor={rowCategoryTextColor}
                                        expanded={categoryExpanded}
                                        expanderClickHandler={expanderClickHandler}
                                    />
                                : null}
                                <a href={`${context['@id']}&${mappedRowCategoryQuery}`} style={{ color: rowCategoryTextColor }} id={categoryNameQuery}>{context.matrix[rowCategoryName].label}</a>
                            </div>
                        ),
                    },
                    { content: <div style={{ backgroundColor: rowCategoryColor }} />, colSpan: 0 }],
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
                                    categoryName={rowCategoryName}
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
 * Render the title panel and list of experiment internal tags.
 */
const MatrixHeader = ({ context }) => {
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
        <div className="matrix__header">
            <h1>{type ? `${type} ` : ''}{context.title}</h1>
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

        let clearButton;
        const searchQuery = url.parse(context['@id']).search;
        if (searchQuery) {
            // If we have a 'type' query string term along with others terms, we need a Clear Filters
            // button.
            const terms = queryString.parse(searchQuery);
            const nonPersistentTerms = _(Object.keys(terms)).any(term => term !== 'type');
            clearButton = nonPersistentTerms && terms.type;
        }

        return (
            <div className="matrix__facets-vertical">
                <ClearFilters searchUri={context.clear_filters} enableDisplay={!!clearButton} />
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
            const header = document.querySelector(`#${sanitizeId(category)}`);
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
        const { context } = this.props;
        const { scrolledRight } = this.state;
        const visualizeDisabledTitle = context.total > VISUALIZE_LIMIT ? `Filter to ${VISUALIZE_LIMIT} to visualize` : '';
        const loggedIn = !!(this.context.session && this.context.session['auth.userid']);

        // Convert encode matrix data to a DataTable object.
        const { dataTable, rowKeys } = convertAuditToDataTable(context, this.state.expandedRowCategories, this.expanderClickHandler, loggedIn);
        const matrixConfig = {
            rows: dataTable,
            rowKeys,
            tableCss: 'matrix',
        };

        return (
            <div className="matrix__presentation">
                <h4>Showing {context.total} results</h4>
                <SearchControls context={context} visualizeDisabledTitle={visualizeDisabledTitle} />
                <div className={`matrix__label matrix__label--horz${!scrolledRight ? ' horz-scroll' : ''}`}>
                    <span>{context.matrix.x.label}</span>
                    {svgIcon('largeArrow')}
                </div>
                <div className="matrix__presentation-content">
                    <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}AUDIT CATEGORY</div></div>
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
};

MatrixPresentation.contextTypes = {
    session: PropTypes.object,
};


/**
 * Render the vertical facets and the matrix itself.
 */
const MatrixContent = ({ context }) => (
    <div className="matrix__content">
        <MatrixVerticalFacets context={context} />
        <MatrixPresentation context={context} />
    </div>
);

MatrixContent.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};


/**
 * View component for the audit matrix page.
 */
const AuditMatrix = ({ context }) => {
    const itemClass = globals.itemClass(context, 'view-item');

    if (context.total > 0) {
        return (
            <Panel addClasses={itemClass}>
                <PanelBody>
                    <MatrixHeader context={context} />
                    <MatrixContent context={context} />
                </PanelBody>
            </Panel>
        );
    }
    return <h4>No results found</h4>;
};

AuditMatrix.propTypes = {
    context: PropTypes.object.isRequired,
};

AuditMatrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object,
};

globals.contentViews.register(AuditMatrix, 'Audit');
