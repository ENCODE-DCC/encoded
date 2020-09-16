import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import QueryString from '../libs/query_string';
import * as encoding from '../libs/query_encoding';
import { Panel, PanelBody } from '../libs/ui/panel';
import { svgIcon } from '../libs/svg-icons';
import DataTable from './datatable';
import * as globals from './globals';
import { MatrixInternalTags } from './objectutils';
import { SearchControls } from './search';


/**
 * Limit the assays to display on the horizontal axis of the main ENCORE matrix to these.
 */
const encoreDisplayedAssays = [
    'shRNA RNA-seq',
    'CRISPR RNA-seq',
    'eCLIP',
    'TF ChIP-seq',
    'RNA Bind-n-Seq',
    'iCLIP',
];

/**
 * Limit the assays to display on the horizontal axis of the inset RNA-seq matrix to these.
 */
const rnaSeqDisplayedAssays = [
    'total RNA-seq',
    'polyA plus RNA-seq',
];

/**
 * Limit the biosample term names to display within each assay to these.
 */
const displayedTermNames = [
    'K562',
    'HepG2',
];

/**
 * Assays in which we don't display a biosample.
 */
const noBiosampleAssays = [
    'RNA Bind-n-Seq',
];


/**
 * The ENCORE matrix does front-end filtering, which means we could have columns we can display
 * according to the `encoreDisplayedAssays` global, but which might only contain data we *don't*
 * display because it doesn’t have data in terms names we display from the `displayedTermNames`
 * global. This function checks `colCategoryKey` (assay_title) to see if it has any data for term
 * names in `displayedTermNames`. If not, we don’t render that column even though it exists in the
 * matrix JSON.
 * @param {object} context Matrix data object for the page
 * @param {string} colCategoryKey Title of assay column we're checking
 * @param {string} colCategory Column category property e.g. assay_title
 * @param {string} colSubCategory Column subcategory property e.g. biosample_ontology.term_name
 * @param {string} rowCategory Row category property e.g. target.label
 *
 * @return {bool} True if we should display the given colCategoryKey column
 */
const doesRowDataExist = (context, colCategoryKey, colCategory, colSubCategory, rowCategory) => {
    const isColCategoryDataFound = context.matrix.y[rowCategory].buckets.find((rowCategoryItem) => {
        const isColCategoryFound = rowCategoryItem[colCategory].buckets.find((rowColCategoryItem) => {
            // See if data contains column category we're looking for.
            if (rowColCategoryItem.key === colCategoryKey) {
                // See if row includes data for a displayed subcategory column.
                return rowColCategoryItem[colSubCategory].buckets.find(rowColSubCategoryItem => (
                    noBiosampleAssays.includes(rowColCategoryItem.key) || displayedTermNames.includes(rowColSubCategoryItem.key)
                ));
            }
            return false;
        });
        return isColCategoryFound;
    });
    return isColCategoryDataFound;
};


/**
 * Takes matrix data from the ENCORE matrix JSON and generates an object that <DataTable> can use to
 * generate the JSX for the matrix. Both the main ENCORE matrix as well as the RNA-seq matrix use
 * this function with slight special cases for each.
 * @param {object} context Matrix JSON for the page
 * @param {array} displayedAssays List of assays to include in the table.
 * @param {string} rowCategoryFilterText Displayed targets must partially match this text
 *
 * @return {object} Generated object suitable for passing to <DataTable>
 */

const convertEncoreToDataTable = (context, displayedAssays, rowCategoryFilterText) => {
    const colCategory = context.matrix.x.group_by[0];
    const colSubCategory = context.matrix.x.group_by[1];

    // Especially for the RNA-seq matrix, links should only have the column category (assay_title)
    // for the clicked column, not all assay_title that might be in the query string.
    const query = new QueryString(context.search_base);
    query.deleteKeyValue(colCategory);
    const baseUrlWithoutColCategoryType = query.format();

    // The inset RNA-seq matrix has an array of arrays of strings instead of just an array of
    // strings. The ENCORE matrix search view uses this mechanism to let us capture data that has no
    // biosamples.
    const rowCategory = typeof context.matrix.y.group_by[0] === 'string' ? context.matrix.y.group_by[0] : context.matrix.y.group_by[0][0];

    // Collect column header table data and build a map of column category to corresponding table
    // column index. Initialize with an empty corner cell as the first item in each header row.
    const colCategoryData = [null];
    const colSubCategoryData = [null];
    let colIndex = 1;
    let firstColumn = true;
    const colMap = {};
    const spacerIndices = [];
    context.matrix.x[colCategory].buckets.forEach((colCategoryItem) => {
        if (displayedAssays.includes(colCategoryItem.key) && doesRowDataExist(context, colCategoryItem.key, colCategory, colSubCategory, rowCategory)) {
            colMap[colCategoryItem.key] = {};
            const colCategoryUrl = `${baseUrlWithoutColCategoryType}&${colCategory}=${encoding.encodedURIComponent(colCategoryItem.key)}`;

            // Add a spacer between the current and previous biosample term name column if not the
            // first assay column.
            if (!firstColumn) {
                colSubCategoryData.push({ header: <div className="encore-column-spacer" /> });
            }

            // Filter and sort column subcategory buckets according to `displayedTermNames` so
            // that the column subcategories always appear in the same order under each column
            // category.
            const colSubCategoryBuckets = _.sortBy(colCategoryItem[colSubCategory].buckets.filter(bucket => (
                displayedTermNames.includes(bucket.key) || noBiosampleAssays.includes(colCategoryItem.key)
            )), bucket => displayedTermNames.indexOf(bucket.key));

            // Generate the biosample term name column subheaders within one assay column.
            let subCategoryCount = 0;
            colSubCategoryBuckets.forEach((colSubCategoryItem) => {
                // Only include allowed biosample term names.
                if (noBiosampleAssays.includes(colCategoryItem.key)) {
                    // No biosample associated with assay; fill with &nbsp;.
                    colSubCategoryData.push({ header: '\u00A0', css: 'category-subheader category-subheader--none' });
                } else {
                    // K562 or HepG2 biosample associated with assay.
                    colSubCategoryData.push({
                        header: (
                            <a href={`${colCategoryUrl}&${colSubCategory}=${encoding.encodedURIComponent(colSubCategoryItem.key)}`}>
                                {colSubCategoryItem.key}
                            </a>
                        ),
                        css: `category-subheader category-subheader--${colSubCategoryItem.key}`,
                    });
                }

                // Generate the two-level map of categories and subcategories to table column
                // number, then go on to the next column. Each colMap key represents an assay, and
                // its value another object containing the biosample term names as keys, with their
                // values being the column number for that assay/biosample-term-name pair.
                colMap[colCategoryItem.key][colSubCategoryItem.key] = colIndex;
                colIndex += 1;
                subCategoryCount += 1;
            });

            // Add a spacer between the current and previous assay column if not the first assay
            // column.
            if (!firstColumn) {
                // Push the spacer into the column header.
                colCategoryData.push({ header: <div className="encore-column-spacer" /> });

                // Keep track of which columns the spacers exist in so we can insert the same spacers
                // into the row data.
                spacerIndices.push(colIndex);
            } else {
                firstColumn = false;
            }

            // Generate one assay column header.
            colCategoryData.push({
                header: <a href={colCategoryUrl}>{colCategoryItem.key}</a>,
                colSpan: subCategoryCount,
                css: `category-header${subCategoryCount > 1 ? ' category-header--spanned' : ''}`,
            });
            colIndex += 1;
        }
    });

    // Initialize the <DataTable> data with the column headers, or with a message if we have no
    // data available.
    let matrixDataTable;
    if (colCategoryData.length > 1) {
        matrixDataTable = [
            { rowContent: colCategoryData, css: 'matrix__col-category-header' },
            { rowContent: colSubCategoryData, css: 'matrix__col-category-subheader' },
        ];
    } else {
        matrixDataTable = [
            { rowContent: ['No data available'], css: 'matrix__message' },
        ];
    }

    // The search field lets the user filter on the target of the main ENCORE matrix only, and does
    // not result in a query to the server -- just a visual filtering.
    const rowCategoryBuckets = rowCategoryFilterText ? context.matrix.y[rowCategory].buckets.filter((bucket) => {
        const termKey = globals.sanitizedString(bucket.key);
        const typeaheadVal = String(globals.sanitizedString(rowCategoryFilterText));
        return termKey.match(typeaheadVal);
    }) : context.matrix.y[rowCategory].buckets;

    // Fill in the data portion of the table.
    rowCategoryBuckets.forEach((rowCategoryItem) => {
        // Targets without a biosample get the special key "no_term_name."
        let rowCategoryUrl;
        const hasTermName = rowCategoryItem.key !== 'no_term_name';
        if (hasTermName) {
            rowCategoryUrl = `${baseUrlWithoutColCategoryType}&${rowCategory}=${encoding.encodedURIComponent(rowCategoryItem.key)}`;
        } else {
            rowCategoryUrl = `${baseUrlWithoutColCategoryType}&${rowCategory}!=*`;
        }

        // Make a new array for the whole row so we can fill individual cells, and fill in the left
        // header column.
        let usedRowCellCount = 0;
        const cells = new Array(colIndex - 1).fill(null);
        cells[0] = { header: <a href={rowCategoryUrl}>{hasTermName ? rowCategoryItem.key : '(all)'}</a> };
        rowCategoryItem[colCategory].buckets.forEach((rowColCategoryItem) => {
            // Retrieve the column map object containing the biosample term name column numbers for
            // each assay column. Then generate cells for the target row.
            const colMapCategory = colMap[rowColCategoryItem.key];
            if (colMapCategory) {
                rowColCategoryItem[colSubCategory].buckets.forEach((rowColSubCategoryItem) => {
                    const cellIndex = colMapCategory[rowColSubCategoryItem.key];
                    const cellCss = noBiosampleAssays.includes(rowColCategoryItem.key) ? 'none' : rowColSubCategoryItem.key;
                    cells[cellIndex] = {
                        content: (
                            <a
                                href={`${rowCategoryUrl}&${colCategory}=${encoding.encodedURIComponent(rowColCategoryItem.key)}&${colSubCategory}=${encoding.encodedURIComponent(rowColSubCategoryItem.key)}`}
                                className={`encore-cell encore-cell--${cellCss}`}
                            >
                                {'\u00A0'}
                                <div className="sr-only">{`${hasTermName ? rowCategoryItem.key : 'all subcellular localizations'}, ${rowColCategoryItem.key}, ${rowColSubCategoryItem.key}`}</div>
                            </a>
                        ),
                    };
                    usedRowCellCount += 1;
                });
            }
        });

        // Insert the spacer columns.
        spacerIndices.forEach((spacerIndex) => {
            cells[spacerIndex] = { content: '\u00A0', css: 'encore-column-spacer' };
        });

        // Add the completed row to the entire datatable object.
        if (usedRowCellCount > 0) {
            matrixDataTable.push({ rowContent: cells, css: 'matrix__row-data' });
        }
    });

    return { dataTable: matrixDataTable };
};


/**
 * Renders the search field that filters the target rows with partial text matches. This search,
 * unlike some other matrices, does not generate a new query, but just visually filters the
 * targets.
 */
const TargetFilter = ({ filterText, textChangeHandler }) => (
    <div className="matrix-general-search">
        <label htmlFor="target-filter">Enter filter terms to filter the targets included in the matrix.</label>
        <div className="general-search-entry">
            <i className="icon icon-filter" />
            <div className="searchform">
                <input
                    type="search"
                    className="search-query"
                    name="target-filter"
                    id="target-filter"
                    onChange={textChangeHandler}
                    value={filterText}
                />
            </div>
        </div>
    </div>
);

TargetFilter.propTypes = {
    /** Current value of filtering text */
    filterText: PropTypes.string,
    /** Called when the user changes a search input field */
    textChangeHandler: PropTypes.func.isRequired,
};

TargetFilter.defaultProps = {
    filterText: '',
};


/**
 * Render the area above the facets and matrix content.
 */
const MatrixHeader = ({ context, targetFilterText, textChangeHandler }) => (
    <div className="matrix-header">
        <div className="matrix-header__title">
            <h1>{context.title}</h1>
            <div className="matrix-tags">
                <MatrixInternalTags context={context} />
                <div className="matrix-description">
                    The ENCORE project aims to study protein-RNA interactions by creating a map of RNA binding proteins (RBPs) encoded in the human genome and identifying the RNA elements that the RBPs bind to.
                </div>
            </div>
        </div>
        <div className="matrix-header__controls">
            <div className="matrix-header__target-filter-controls">
                <TargetFilter filterText={targetFilterText} textChangeHandler={textChangeHandler} />
            </div>
        </div>
    </div>
);

MatrixHeader.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
    /** Current value of filtering text */
    targetFilterText: PropTypes.string,
    /** Called when the user changes a search input field */
    textChangeHandler: PropTypes.func.isRequired,
};

MatrixHeader.defaultProps = {
    targetFilterText: '',
};


/**
 * Custom react hook to handle matrix scrolling.
 * @param {node} Ref to scrolling matrix element
 *
 * @return {array} States and actions usable to this hook's clients
 */
const useMatrixScrollHandler = (scrollElement) => {
    const [scrolledRight, setScrolledRight] = React.useState(true);

    /**
     * Show a scroll indicator depending on current scrolled position.
     * @param {object} element DOM element to apply shading to
     */
    const handleScrollIndicator = React.useCallback((element) => {
        // Have to use a "roughly equal to" test because of an MS Edge bug mentioned here:
        // https://stackoverflow.com/questions/30900154/workaround-for-issue-with-ie-scrollwidth
        const scrollDiff = Math.abs((element.scrollWidth - element.scrollLeft) - element.clientWidth);
        if (scrollDiff < 2 && !scrolledRight) {
            // Right edge of matrix scrolled into view.
            setScrolledRight(true);
        } else if (scrollDiff >= 2 && scrolledRight) {
            // Right edge of matrix scrolled out of view.
            setScrolledRight(false);
        }
    }, [scrolledRight]);

    React.useEffect(() => {
        if (scrollElement.current) {
            // Install the scroll and resize event handlers.
            const handleScrollEvent = event => handleScrollIndicator(event.target);
            const handleResizeEvent = () => handleScrollIndicator(scrollElement.current);

            // Cache the reference to the scrollable matrix <div> so that we can remove the "scroll"
            // event handler on unmount, when scrollElement.current might no longer point at this <div>.
            const matrixNode = scrollElement.current;

            // Attach the scroll- and resize- event handlers, then force the initial calculation of
            // `scrolledRight`.
            scrollElement.current.addEventListener('scroll', handleScrollEvent);
            window.addEventListener('resize', handleResizeEvent);
            handleScrollIndicator(scrollElement.current);

            // Callback called when unmounting component.
            return () => {
                matrixNode.removeEventListener('scroll', handleScrollEvent);
                window.removeEventListener('resize', handleResizeEvent);
            };
        }

        // To make both ESLint (consistent-return rule) and React (return undefined or nothing if
        // no clean-up) happy...
        return undefined;
    }, [handleScrollIndicator, scrollElement]);

    /**
     * Called when the user scrolls the matrix horizontally within its div to handle scroll
     * indicators.
     * @param {object} e React synthetic scroll event
     */
    const handleOnScroll = (e) => {
        handleScrollIndicator(e.target);
    };

    return [
        // State indicating whether the user scrolled the matrix all the way to the right edge.
        scrolledRight,
        // Callback to handle scroll events
        handleOnScroll,
    ];
};


/**
 * Display the RNA-seq inset matrix. This data gets loaded after page render, so `rnaSeqData` has a
 * null SSR value.
 */
const RnaSeqMatrixContent = ({ rnaSeqData }) => {
    const scrollElement = React.useRef(null);
    const [scrolledRight, handleOnScroll] = useMatrixScrollHandler(scrollElement);

    if (rnaSeqData) {
        const { dataTable } = convertEncoreToDataTable(rnaSeqData, rnaSeqDisplayedAssays);
        const matrixConfig = {
            rows: dataTable,
            tableCss: 'matrix matrix--rna-seq',
        };

        return (
            <div className="matrix__rna-seq">
                <div className={`matrix__label matrix__label--horz${!scrolledRight ? ' horz-scroll' : ''}`}>
                    <span>{rnaSeqData.matrix.x.label}</span>
                    {svgIcon('largeArrow')}
                </div>
                <div className="matrix__presentation-content">
                    <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}{rnaSeqData.matrix.y.label}</div></div>
                    <div className="matrix__data-wrapper">
                        <div className="matrix__data" onScroll={handleOnScroll} ref={scrollElement}>
                            <DataTable tableData={matrixConfig} />
                        </div>
                    </div>
                </div>
            </div>
        );
    }
    return null;
};

RnaSeqMatrixContent.propTypes = {
    /** Matrix search results for the RNA-seq inset matrix */
    rnaSeqData: PropTypes.object,
};

RnaSeqMatrixContent.defaultProps = {
    rnaSeqData: null,
};


const EncoreMatrixContent = ({ encoreData, targetFilterText }) => {
    const scrollElement = React.useRef(null);
    const [scrolledRight, handleOnScroll] = useMatrixScrollHandler(scrollElement);

    // Convert encode matrix data to a DataTable object.
    const { dataTable } = convertEncoreToDataTable(encoreData, encoreDisplayedAssays, targetFilterText);
    const matrixConfig = {
        rows: dataTable,
        tableCss: 'matrix matrix--encore',
    };

    return (
        <div className="matrix__encore">
            <div className={`matrix__label matrix__label--horz${!scrolledRight ? ' horz-scroll' : ''}`}>
                <span>{encoreData.matrix.x.label}</span>
                {svgIcon('largeArrow')}
            </div>
            <div className="matrix__presentation-content">
                <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}{encoreData.matrix.y.label}</div></div>
                <div className="matrix__data-wrapper">
                    <div className="matrix__data" onScroll={handleOnScroll} ref={scrollElement}>
                        <DataTable tableData={matrixConfig} />
                    </div>
                </div>
            </div>
        </div>
    );
};

EncoreMatrixContent.propTypes = {
    /** ENCORE matrix data */
    encoreData: PropTypes.object.isRequired,
    /** Text used to filter target list */
    targetFilterText: PropTypes.string,
};

EncoreMatrixContent.defaultProps = {
    targetFilterText: '',
};


/**
 * Display the matrix and associated controls above them.
 */
const MatrixPresentation = ({ context, targetFilterText }) => {
    const [rnaSeqData, setRnaSeqData] = React.useState(null);

    React.useEffect(() => {
        // Request the RNA-seq ENCORE sub-matrix by taking the existing URI and modifying it to
        // form the RNA-seq URI that includes the RNA-seq matrix path and filters down to the
        // needed assay titles. Any other assay_title query-string parameters get removed.
        const parsedUrl = url.parse(context['@id']);
        const query = new QueryString(parsedUrl.query);
        query.replaceKeyValue('assay_title', 'total RNA-seq').addKeyValue('assay_title', 'polyA plus RNA-seq');
        parsedUrl.search = `?${query.format()}`;
        parsedUrl.pathname = '/encore-rna-seq-matrix/';
        const updatedUrl = parsedUrl.format();
        fetch(updatedUrl, {
            method: 'GET',
            headers: {
                Accept: 'application/json',
            },
        }).then((response) => {
            // Convert the response to JSON.
            if (response.ok) {
                return response.json();
            }
            return Promise.resolve(null);
        }).then((response) => {
            setRnaSeqData(response);
        });
    }, [context]);

    return (
        <div className="matrix__presentation">
            <RnaSeqMatrixContent rnaSeqData={rnaSeqData} />
            <EncoreMatrixContent encoreData={context} targetFilterText={targetFilterText} />
        </div>
    );
};

MatrixPresentation.propTypes = {
    /** Matrix data object for the page */
    context: PropTypes.object.isRequired,
    /** Text used to filter target list */
    targetFilterText: PropTypes.string,
};

MatrixPresentation.defaultProps = {
    targetFilterText: '',
};


/**
 * Render the vertical facets and the matrix itself.
 */
const MatrixContent = ({ context, targetFilterText }) => (
    <div className="matrix__content matrix__content--encore">
        <MatrixPresentation context={context} targetFilterText={targetFilterText} />
    </div>
);

MatrixContent.propTypes = {
    /** Matrix data object for the page */
    context: PropTypes.object.isRequired,
    /** Text used to filter target list */
    targetFilterText: PropTypes.string,
};

MatrixContent.defaultProps = {
    targetFilterText: '',
};


/**
 * View component for the experiment matrix page.
 */
const EncoreMatrix = ({ context }) => {
    const [targetFilterText, setTargetFilterText] = React.useState('');
    const itemClass = globals.itemClass(context, 'view-item');

    // Called when the user changes the contents of the target filter text field.
    const handleTextChange = React.useCallback((e) => {
        setTargetFilterText(e.target.value);
    }, []);

    if (context.total > 0) {
        return (
            <Panel addClasses={itemClass}>
                <PanelBody>
                    <MatrixHeader context={context} targetFilterText={targetFilterText} textChangeHandler={handleTextChange} />
                    <MatrixContent context={context} targetFilterText={targetFilterText} />
                </PanelBody>
            </Panel>
        );
    }
    return <h4>No results found</h4>;
};

EncoreMatrix.propTypes = {
    /** Matrix data object for the page */
    context: PropTypes.object.isRequired,
};

EncoreMatrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object,
};

globals.contentViews.register(EncoreMatrix, 'EncoreMatrix');
