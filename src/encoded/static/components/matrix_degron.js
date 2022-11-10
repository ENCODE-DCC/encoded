import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { encodedURIComponent } from '../libs/query_encoding';
import QueryString from '../libs/query_string';
import { Panel, PanelBody } from '../libs/ui/panel';
import { svgIcon } from '../libs/svg-icons';
import { DataTable } from './datatable';
import { contentViews, itemClass } from './globals';
import { MatrixAddCart, SearchFilter } from './matrix';
import { MatrixBadges } from './objectutils';
import { ClearSearchTerm, SearchControls } from './search';


/**
 * Column subcategory value for experiments with no target.
 */
const NO_TARGET_SUBCATEGORY = 'no_target';


/**
 * Matrix context objects have properties containing the search results for the matrix. These
 * property names can change if the specifications for the matrix search parameters change. This
 * function gets the property names for the Degron matrix search results which have a single level
 * for the row categories and a two-level hierarchy for the column categories. If the search
 * parameters for the Degron matrix change, the search result property names and this function
 * adapt without needing change.
 * @param {object} context Matrix search result object
 * @returns {object} Row and column category and subcategory property names
 */
const getMatrixCategoryNames = (context) => (
    {
        rowCategoryName: context.matrix.y.group_by[0],
        colCategoryName: context.matrix.x.group_by[0],
        colSubcategoryName: context.matrix.x.group_by[1][0],
    }
);


/**
 * Transforms a category title string into a displayable string. Do not use the result for
 * searches -- only use this for display. For now only ChIP-seq gets special treatment.
 * @param {string} colCategoryTitle Column category title to transform
 * @returns {string} Transformed column category title
 */
const transformColCategoryTitle = (colCategoryTitle) => {
    if (colCategoryTitle.includes('ChIP-seq')) {
        return 'ChIP-seq';
    }
    return colCategoryTitle;
};


/**
 * Composes a column category title from the column category and column subcategory buckets. Use
 * this not only for display, but as a key for the matrix column map.
 * @param {object} colCategoryBucket Column category bucket
 * @param {object} colSubcategoryBucket Column subcategory bucket
 * @returns {string} Column category title
 */
const composeColCategoryTitle = (colCategoryBucket, colSubcategoryBucket) => {
    const colCategoryTitle = colCategoryBucket.key;
    const colSubcategoryTitle = colSubcategoryBucket.key;
    return colSubcategoryTitle !== NO_TARGET_SUBCATEGORY
        ? `${colSubcategoryTitle} ${transformColCategoryTitle(colCategoryTitle)}`
        : colCategoryTitle;
};


/**
 * Compose the query string for a column header.
 * @param {object} context Matrix search result object
 * @param {object} colCategoryBucket Bucket for the current column
 * @param {object} colSubcategoryBucket Bucket for the current subcolumn
 * @returns {string} Query string for the column header
 */
const composeColCategoryQuery = (context, colCategoryBucket, colSubcategoryBucket) => {
    const { colCategoryName, colSubcategoryName } = getMatrixCategoryNames(context);

    const colCategoryTitle = colCategoryBucket.key;
    const colSubcategoryTitle = colSubcategoryBucket.key;
    const colCategoryQuery = `&${colCategoryName}=${encodeURIComponent(colCategoryTitle)}`;
    const colSubcategoryHref = colSubcategoryTitle !== NO_TARGET_SUBCATEGORY ? `&${colSubcategoryName}=${colSubcategoryTitle}` : '';
    return `${colCategoryQuery}${colSubcategoryHref}`;
};


/**
 * Compose the query string for the row header.
 * @param {object} context Matrix search result object
 * @param {object} rowCategoryBucket Bucket for the current row
 * @returns {string} Query string for the row header
 */
const composeRowCategoryQuery = (context, rowCategoryBucket) => {
    const { rowCategoryName } = getMatrixCategoryNames(context);
    const rowCategoryTitle = rowCategoryBucket.key;
    return `&${rowCategoryName}=${encodedURIComponent(rowCategoryTitle)}`;
};


/**
 * Defines the sorting order of the assay/target table columns.
 */
const COL_CATEGORY_DATA_SORT_ORDER = [
    'Bru-seq',
    'PRO-seq',
    'PRO-cap',
    'DNase-seq',
    'ATAC-seq',
    'snATAC-seq',
    'CTCF ChIP-seq',
    'H3K4me3 ChIP-seq',
    'H3K4me1 ChIP-seq',
    'H3K27ac ChIP-seq',
    'H3K36me3 ChIP-seq',
    'H3K9me3 ChIP-seq',
    'CTCF ChIA-PET',
    'POLR2A ChIA-PET',
    'in situ Hi-C',
    'intact Hi-C',
];

/**
 * Generate the header row contents for `DataTable`. Also generate a map of header column titles to
 * their indices in the header row so that we can easily place row data into the corresponding
 * column.
 * @param {object} context Matrix search result object
 * @returns {object} Column category row and column map
 */
const generateHeaderRowAndColumnMap = (context) => {
    const { colCategoryName, colSubcategoryName } = getMatrixCategoryNames(context);

    const colCategoryData = [];
    const colCategoryBuckets = context.matrix.x[colCategoryName].buckets;
    colCategoryBuckets.forEach((categoryBucket) => {
        const colSubcategoryBuckets = categoryBucket[colSubcategoryName].buckets;
        colSubcategoryBuckets.forEach((subcategoryBucket) => {
            const colCategoryTitle = composeColCategoryTitle(categoryBucket, subcategoryBucket);
            const colHeaderQuery = composeColCategoryQuery(context, categoryBucket, subcategoryBucket);
            const colHeaderHref = `${context.search_base}${colHeaderQuery}`;

            // Generate a column for the matrix header row containing the column category titles.
            colCategoryData.push({
                title: colCategoryTitle,
                href: colHeaderHref,
            });
        });
    });

    // Sort the colCategoryData by a predefined order.
    // Sort the lot reviews by their status according to our predefined order
    // given in the statusOrder array we imported from globals.js.
    const sortedColCategoryData = _.sortBy(colCategoryData, (colCategory) => {
        const order = COL_CATEGORY_DATA_SORT_ORDER.indexOf(colCategory.title);
        return order !== -1 ? order : COL_CATEGORY_DATA_SORT_ORDER.length;
    });

    const colCategoryColumnMap = {};
    const colCategoryRow = [null];
    sortedColCategoryData.forEach((colCategoryDatum, columnIndex) => {
        // Make a mapping from the column title to the index of the column in the matrix.
        colCategoryColumnMap[colCategoryDatum.title] = columnIndex + 1;
        colCategoryRow.push({ header: <a href={colCategoryDatum.href}>{colCategoryDatum.title}</a> });
    });

    // Within that loop, push onto an array the titles and queries -- not the <a> tag.
    // Then, after the loop, sort the array.
    // Then, in a second loop, push the <a> tag onto the header row.
    return { colCategoryRow, colCategoryColumnMap };
};


/**
 * Count the number of columns in the matrix. Each column represents a column category, and each
 * column category can have multiple subcategories. You probably have to add one to the result to
 * account for the row header.
 * @param {object} context Matrix search result object
 * @returns {number} Number of columns in the matrix
 */
const getColumnCount = (context) => {
    const { colCategoryName, colSubcategoryName } = getMatrixCategoryNames(context);
    const colCategoryBuckets = context.matrix.x[colCategoryName].buckets;
    return colCategoryBuckets.reduce((count, categoryBucket) => count + categoryBucket[colSubcategoryName].buckets.length, 0);
};


/**
 * Takes a matrix data object and generates an object that `DataTable` can use to generate the JSX
 * for the matrix. This serves as a shim between the experiment data and the objects `DataTable`
 * needs.
 * @param {object} context Matrix JSON for the page
 * @return {object} Generated mapping suitable for passing to <DataTable>
 */
const convertExperimentToDataTable = (context) => {
    const { colCategoryRow, colCategoryColumnMap } = generateHeaderRowAndColumnMap(context);
    const { rowCategoryName, colCategoryName, colSubcategoryName } = getMatrixCategoryNames(context);

    const rowCategoryBuckets = context.matrix.y[rowCategoryName].buckets;
    const colCount = getColumnCount(context);

    // Generate the data rows of the matrix. Each `rowCategoryBucket` contains the data for a row.
    const dataTableRows = [];
    const dataTableKeys = [];
    rowCategoryBuckets.forEach((rowCategoryBucket) => {
        const rowCategoryTitle = rowCategoryBucket.key;
        const colCategoryBuckets = rowCategoryBucket[colCategoryName].buckets;

        // Make a complete, empty data row for the matrix and set the row header.
        const rowCells = Array(colCount + 1).fill(null);
        const rowHeaderQuery = composeRowCategoryQuery(context, rowCategoryBucket);
        const rowHeaderLink = `${context.search_base}${rowHeaderQuery}`;
        rowCells[0] = { header: <a href={rowHeaderLink}>{rowCategoryTitle}</a> };

        // Each `colCategoryBucket` contains the data for the current row, including the data for a
        // column category which itself contains the column subcategories.
        colCategoryBuckets.forEach((colCategoryBucket) => {
            const colSubcategoryBuckets = colCategoryBucket[colSubcategoryName].buckets;

            // Each `colSubcategoryBucket` contains the data for a column subcategory. Combine this
            // with the column category to get the column title, and that lets us get the column
            // this single data item belongs in.
            colSubcategoryBuckets.forEach((colSubcategoryBucket) => {
                const colCategoryTitle = composeColCategoryTitle(colCategoryBucket, colSubcategoryBucket);
                const colCategoryIndex = colCategoryColumnMap[colCategoryTitle];

                // Compose the cell query string and href given the row and column category query strings.
                const colCategoryQuery = composeColCategoryQuery(context, colCategoryBucket, colSubcategoryBucket);
                const cellQuery = `${colCategoryQuery}${rowHeaderQuery}`;
                const cellHref = `${context.search_base}${cellQuery}`;

                // Now we have a cell's data (the experiment count) as well as the column it
                // belongs in. Place the cell data in the corresponding column.
                const populatedClass = colSubcategoryBucket.doc_count > 1 ? 'matrix__populated-badge--full' : 'matrix__populated-badge--partial';
                rowCells[colCategoryIndex] = {
                    content: (
                        <a href={cellHref} className={`matrix__populated-badge ${populatedClass}`} aria-label={`${rowCategoryTitle} and ${colCategoryTitle}`}>
                            <span className="sr-only">{colSubcategoryBucket.doc_count}</span>
                        </a>
                    ),
                };
            });
        });

        dataTableRows.push({ rowContent: rowCells, css: 'matrix__row-data' });
        dataTableKeys.push(rowCategoryTitle);
    });

    const degronTableData = [
        { rowContent: colCategoryRow, css: 'matrix__col-category-header' },
    ].concat(dataTableRows);

    return { degronTableData, rowKeys: ['header'].concat(dataTableKeys) };
};


/**
 * Render the area above the facets and matrix content.
 */
const MatrixHeader = ({ context }) => {
    const parsedUrl = url.parse(context['@id'], true);
    parsedUrl.query.format = 'json';
    parsedUrl.search = '';

    // Compose a type title for the page if only one type is included in the query string.
    // Currently, only one type is allowed in the query string or the server returns a 400, so this
    // code exists in case more than one type is allowed in future.
    let type = '';
    if (context.filters && context.filters.length > 0) {
        const typeFilters = context.filters.filter((filter) => filter.field === 'type');
        if (typeFilters.length === 1) {
            type = typeFilters[0].term;
        }
    }

    // If the user has requested an ENCORE matrix, generate a matrix description.
    const query = new QueryString(context.search_base);
    const matrixDescription = query.getKeyValues('internal_tags').includes('ENCORE') ?
        'The ENCORE project aims to study protein-RNA interactions by creating a map of RNA binding proteins (RBPs) encoded in the human genome and identifying the RNA elements that the RBPs bind to.'
    : '';

    return (
        <div className="matrix-header">
            <div className="matrix-header__banner">
                <div className="matrix-header__title">
                    <h1>{context.title}</h1>
                    <ClearSearchTerm searchUri={context['@id']} />
                </div>
                <div className="matrix-header__details">
                    <div className="matrix-title-badge">
                        <MatrixBadges context={context} type={type} />
                    </div>
                    <div className="matrix-description">
                        {matrixDescription &&
                            <div className="matrix-description__text">{matrixDescription}</div>
                        }
                    </div>
                </div>
            </div>
            <div className="matrix-header__controls">
                <div className="matrix-header__filter-controls">
                    <SearchFilter context={context} css="matrix-general-search--degron" />
                </div>
                <div className="matrix-header__search-controls">
                    <h4>Showing {context.total} results</h4>
                    <SearchControls context={context} hideBrowserSelector />
                </div>
            </div>
            <div className="matrix-header__cart">
                <MatrixAddCart context={context} />
            </div>
        </div>
    );
};

MatrixHeader.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};


/**
 * Display the matrix and associated controls above them.
 */
const MatrixPresentation = ({ context }) => {
    // Convert encode matrix data to a DataTable object.
    const { degronTableData, rowKeys } = React.useMemo(() => convertExperimentToDataTable(context), [context]);

    const matrixConfig = {
        rows: degronTableData,
        rowKeys,
        tableCss: 'matrix',
    };

    return (
        <div className="matrix__presentation">
            <div className="matrix__label matrix__label--horz">
                <span>{context.matrix.x.label}</span>
                {svgIcon('largeArrow')}
            </div>
            <div className="matrix__presentation-content">
                <div className="matrix__label matrix__label--vert">
                    <div>{svgIcon('largeArrow')}{context.matrix.y.label}</div>
                </div>
                <div className="matrix__data-wrapper">
                    <div className="matrix__data">
                        <DataTable tableData={matrixConfig} />
                    </div>
                </div>
            </div>
        </div>
    );
};

MatrixPresentation.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};


/**
 * Render the vertical facets and the matrix itself.
 */
const MatrixContent = ({ context }) => (
    <div className="matrix__content matrix__content--degron">
        <MatrixPresentation context={context} />
    </div>
);

MatrixContent.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};


/**
 * View component for the experiment matrix page.
 */
const DegronMatrix = ({ context }) => {
    const matrixPanelClass = itemClass(context, 'view-item');
    if (context.total > 0) {
        return (
            <Panel addClasses={matrixPanelClass}>
                <PanelBody>
                    <MatrixHeader context={context} />
                    <MatrixContent context={context} />
                </PanelBody>
            </Panel>
        );
    }
    return <h4>No results found</h4>;
};

DegronMatrix.propTypes = {
    context: PropTypes.object.isRequired,
};

DegronMatrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
};

contentViews.register(DegronMatrix, 'DegronMatrix');
