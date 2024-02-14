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
import { ClearSearchTerm, FacetList, SearchControls } from './search';


/**
 * Column subcategory value for datasets with no perturbation_type value.
 */
const NO_DATA_SUBCATEGORY = 'no_perturbation';


/**
 * Sorting order for the elements of the row category.
 */
const rowCategorySortingOrder = ['Homo sapiens', 'Mus musculus'];


/**
 * Get the X- and Y-axis property names for the matrix search results configured for this specific
 * matrix type.
 * @param {object} context Matrix search-result object
 * @returns {object} Row and column category and subcategory property names
 */
const getMatrixCategoryNames = (context) => (
    {
        rowCategoryName: context.matrix.y.group_by[0],
        rowSubcategoryName: context.matrix.y.group_by[1],
        colCategoryName: context.matrix.x.group_by[0],
        colSubcategoryName: context.matrix.x.group_by[1][0],
    }
);


/**
 * Render the column category title from the column category and column subcategory buckets. For
 * the Functional Characterization matrix, both the column category and column subcategory names
 * comprise the column title, with the category name used for the main title, and the subcategory
 * name displayed in smaller type to the right of the category name. This gets rotated 90 degrees
 * by the surrounding element CSS.
 * @param {object} colCategoryBucket Column category bucket
 * @param {object} colSubcategoryBucket Column subcategory bucket
 * @returns {string} Column category title
 */
const ColCategoryTitle = ({ colCategoryBucket, colSubcategoryBucket }) => (
    <>
        <div className="header-title__category">{colCategoryBucket.key}</div>
        <div className="header-title__subcategory">
            {colSubcategoryBucket.key !== NO_DATA_SUBCATEGORY
                ? colSubcategoryBucket.key
                : null
            }
        </div>
    </>
);

ColCategoryTitle.propTypes = {
    /** Bucket for the column being rendered */
    colCategoryBucket: PropTypes.object.isRequired,
    /** Bucket for the column subcategory being rendered */
    colSubcategoryBucket: PropTypes.object.isRequired,
};


/**
 * Compose the query string for the column header represented by the column category and column
 * subcategory buckets.
 * @param {object} context Matrix search-result object
 * @param {object} colCategoryBucket Bucket for the current column category
 * @param {object} colSubcategoryBucket Bucket for the current column subcategory
 * @returns {string} Query string for the column header
 */
const composeColCategoryQuery = (context, colCategoryBucket, colSubcategoryBucket) => {
    const { colCategoryName, colSubcategoryName } = getMatrixCategoryNames(context);

    const colCategoryTitle = colCategoryBucket.key;
    const colSubcategoryTitle = colSubcategoryBucket.key;

    const colCategoryQuery = `${colCategoryName}=${encodedURIComponent(colCategoryTitle)}`;
    const perturbationValue = colSubcategoryTitle !== NO_DATA_SUBCATEGORY
        ? `=${encodedURIComponent(colSubcategoryTitle)}`
        : '!=*';
    const perturbationQuery = `${colSubcategoryName}${perturbationValue}`;

    return [colCategoryQuery, perturbationQuery].join('&');
};


/**
 * Get the query string for the species to link to for the column headers. This involves all
 * species in the data.
 * @param {object} context Matrix search-result object
 * @param {array} rowCategoryBuckets Buckets for the row categories containing the species
 * @returns {string} Query string elements for all species in the data
 */
const composeSpeciesQuery = (context, rowCategoryBuckets) => {
    const { rowCategoryName } = getMatrixCategoryNames(context);

    const allSpecies = rowCategoryBuckets.map((rowCategoryBucket) => encodedURIComponent(rowCategoryBucket.key));
    return allSpecies.map((species) => `${rowCategoryName}=${species}`).join('&');
};


/**
 * Compose the category portion of the query string for the row header represented by the row
 * category bucket.
 * @param {object} context Matrix search-result object
 * @param {object} rowCategoryBucket Bucket for the current row
 * @returns {string} Query string for the row header
 */
const composeRowCategoryQuery = (context, rowCategoryBucket) => {
    const { rowCategoryName } = getMatrixCategoryNames(context);
    const rowCategoryTitle = rowCategoryBucket.key;
    return `${rowCategoryName}=${encodedURIComponent(rowCategoryTitle)}`;
};


/**
 * Compose the subcategory portion of the query string for the row header represented by the row
 * category bucket.
 * @param {object} context Matrix search-result object
 * @param {object} rowCategoryBucket Bucket for the current row
 * @returns {string} Query string for the row header
 */
const composeRowSubcategoryQuery = (context, rowSubcategoryBucket) => {
    const { rowSubcategoryName } = getMatrixCategoryNames(context);
    const rowSubcategoryTitle = rowSubcategoryBucket.key;
    return `${rowSubcategoryName}=${encodedURIComponent(rowSubcategoryTitle)}`;
};


/**
 * Generate a URI for a row category. This represents the rows that only hold the organism
 * scientific names. Unlike most other links in the matrix that link to the /search page, this link
 * goes to this matrix page.
 * @param {object} context Matrix search-results object
 * @param {object} rowCategoryBucket Bucket for the row category
 * @returns {string} URI for the row category
 */
const composeRowCategoryUri = (context, rowCategoryBucket) => {
    const parsedUrl = url.parse(context['@id']);
    const query = new QueryString(parsedUrl.query);

    const { rowCategoryName } = getMatrixCategoryNames(context);
    const rowCategoryTitle = rowCategoryBucket.key;
    query.replaceKeyValue(rowCategoryName, rowCategoryTitle);
    return `${parsedUrl.pathname}?${query.format()}`;
};


/**
 * Compose the query-string elements for each data cell in the matrix.
 * @param {object} context Matrix search-result object
 * @param {object} rowCategoryBucket Bucket for the cell's row category
 * @param {object} rowSubcategoryBucket Bucket for the cell's row subcategory
 * @param {object} colCategoryBucket Bucket for the cell's column category
 * @param {object} colSubcategoryBucket Bucket for the cell's column subcategory
 * @returns {string} Query string for the cell
 */
const composeCellQuery = (
    context,
    rowCategoryBucket,
    rowSubcategoryBucket,
    colCategoryBucket,
    colSubcategoryBucket
) => {
    const rowCategoryQuery = composeRowCategoryQuery(context, rowCategoryBucket);
    const rowSubcategoryQuery = composeRowSubcategoryQuery(context, rowSubcategoryBucket);
    const colCategoryQuery = composeColCategoryQuery(context, colCategoryBucket, colSubcategoryBucket);
    return `${rowCategoryQuery}&${rowSubcategoryQuery}&${colCategoryQuery}`;
};


/**
 * The column key gets used to find the column that a cell should appear in. The column key is
 * composed of the column category and column subcategory text, so once you have those two values,
 * you can pass them to this function to generate the key to find the column index using the column
 * map.
 * @param {string} colCategoryKey Text of the column category
 * @param {string} colSubcategoryKey Text of the column subcategory
 * @returns {string} Key for the column
 */
const composeColumnKey = (colCategoryKey, colSubcategoryKey) => (
    `${colCategoryKey}|${colSubcategoryKey}`
);


/**
 * Sort the given array of column elements -- objects containing the column category and column
 * subcategory keys. The sorting algorithm involves a multi-key sort with the arbitrarily defined
 * major sorting key, then the column category key as the secondary sorting key, and finally the
 * column subcategory key as the tertiary sorting key.
 * @param {array} columnElements category key and subcategory key for each column
 * @returns {array} sorted column elements
 */
const sortColumnElements = (columnElements) => (
    _.chain(columnElements)
        .sortBy((columnElement) => columnElement.colSubcategoryKey)
        .sortBy((columnElement) => columnElement.colCategoryKey)
        .sortBy((columnElement) => {
            let majorFactor = 100;
            if (columnElement.colCategoryKey.includes('CRISPR screen')) {
                if (columnElement.colSubcategoryKey !== NO_DATA_SUBCATEGORY) {
                    majorFactor = 1;
                } else {
                    majorFactor = 2;
                }
            } else if (columnElement.colCategoryKey.includes('pooled clone sequencing')) {
                majorFactor = 3;
            } else if (columnElement.colCategoryKey.includes('perturbation followed by')) {
                majorFactor = 4;
            }
            return majorFactor;
        })
        .value()
);


/**
 * Sort the row categories by a defined order. Any row categories not in the defined order get
 * sorted to the end of the list.
 * @param {array} rowCategoryBuckets Holds the row category buckets from the matrix data
 * @returns {array} row category buckets sorted
 */
const sortRowCategoryBuckets = (rowCategoryBuckets) => (
    _.sortBy(rowCategoryBuckets, (rowCategoryBucket) => {
        const sortingValue = rowCategorySortingOrder.indexOf(rowCategoryBucket.key);
        return sortingValue !== -1 ? sortingValue : rowCategorySortingOrder.length;
    })
);


/**
 * Generate a map of header column keys to the column indices in the header row so that we can
 * easily place data cells into the corresponding column.
 * @param {object} context Matrix search result object
 * @returns {object} Column category row and column map
 */
const generateColumnMap = (context) => {
    const { colCategoryName, colSubcategoryName } = getMatrixCategoryNames(context);

    // Go through matrix x-axis data and collect all column category and subcategory labels for the
    // matrix data. Put them into an array of objects, each containing a column category key and a
    // column subcategory key to make sorting easy.
    const colCategoryBuckets = context.matrix.x[colCategoryName].buckets;
    const columnElements = colCategoryBuckets.reduce((columnKeyAcc, colCategoryBucket) => {
        const colSubcategoryBuckets = colCategoryBucket[colSubcategoryName].buckets;
        const subcategoryElements = colSubcategoryBuckets.reduce((subcategoryKeyAcc, colSubcategoryBucket) => {
            const colCategoryElement = {
                colCategoryKey: colCategoryBucket.key,
                colSubcategoryKey: colSubcategoryBucket.key,
            };
            return subcategoryKeyAcc.concat(colCategoryElement);
        }, []);
        return columnKeyAcc.concat(subcategoryElements);
    }, []);

    // Sort the column elements and then convert the array of objects into an array of column keys.
    const sortedColumnElements = sortColumnElements(columnElements);
    const columnKeys = sortedColumnElements.map((columnElement) => (
        composeColumnKey(columnElement.colCategoryKey, columnElement.colSubcategoryKey)
    ));

    // Generate a map from column key to column index.
    const columnMap = {};
    columnKeys.forEach((columnKey, columnIndex) => {
        // Make a mapping from the column title to the index of the column in the matrix.
        columnMap[columnKey] = columnIndex + 1;
    });

    return columnMap;
};


/**
 * Generate the header row for the matrix in a format `<DataTable>` can use. The header row
 * contains the column category and column subcategory labels that link to corresponding searches.
 * @param {object} context Matrix search-result object
 * @param {object} columnMap Map of column keys to column indices
 * @returns {array} Header row that we can pass to the <DataTable> component
 */
const generateHeaderRow = (context, columnMap) => {
    const { colCategoryName, colSubcategoryName, rowCategoryName } = getMatrixCategoryNames(context);

    // Generate a row with enough empty cells to hold all the column headers.
    const columnCount = Object.keys(columnMap).length;
    const headerRow = {
        rowContent: Array(columnCount + 1),
        css: 'matrix__col-category-header',
    };

    context.matrix.x[colCategoryName].buckets.forEach((colCategoryBucket) => {
        const colSubcategoryBuckets = colCategoryBucket[colSubcategoryName].buckets;
        const rowCategoryBuckets = context.matrix.y[rowCategoryName].buckets;
        const speciesQuery = composeSpeciesQuery(context, rowCategoryBuckets);
        colSubcategoryBuckets.forEach((colSubcategoryBucket) => {
            const colCategoryQuery = composeColCategoryQuery(context, colCategoryBucket, colSubcategoryBucket);
            const colCategoryKey = composeColumnKey(colCategoryBucket.key, colSubcategoryBucket.key);
            const columnIndex = columnMap[colCategoryKey];

            headerRow.rowContent[columnIndex] = {
                header: (
                    <a
                        href={`${context.search_base}&${colCategoryQuery}&${speciesQuery}`}
                        className="header-title"
                    >
                        <ColCategoryTitle
                            colCategoryBucket={colCategoryBucket}
                            colSubcategoryBucket={colSubcategoryBucket}
                        />
                    </a>
                ),
            };
        });
    });

    headerRow.rowContent[0] = {
        content: <span />,
    };
    return headerRow;
};


/**
 * Render the header label cell for a row of data.
 */
const RowSubcategoryLabel = ({ context, categoryBucket, subcategoryBucket, children }) => {
    const rowCategoryQuery = composeRowCategoryQuery(context, categoryBucket);
    const rowSubcategoryQuery = composeRowSubcategoryQuery(context, subcategoryBucket);
    return (
        <a
            href={`${context.search_base}&${rowCategoryQuery}&${rowSubcategoryQuery}`}
            className="header-title"
        >
            {children}
        </a>
    );
};

RowSubcategoryLabel.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
    /** Row category bucket */
    categoryBucket: PropTypes.object.isRequired,
    /** Row subcategory bucket */
    subcategoryBucket: PropTypes.object.isRequired,
    /** Subcategory label */
    children: PropTypes.node.isRequired,
};


/**
 * Takes a matrix data object and generates an object that `<DataTable>` can use to generate the JSX
 * for the matrix. This serves as a shim between the dataset data and the objects `DataTable` needs.
 * @param {object} context Matrix JSON for the page
 * @return {object} Generated mapping suitable for passing to <DataTable>
 */
const convertDatasetToDataTable = (context) => {
    const {
        rowCategoryName,
        rowSubcategoryName,
        colCategoryName,
        colSubcategoryName,
    } = getMatrixCategoryNames(context);

    // Generate the header row and column map.
    const columnMap = generateColumnMap(context);
    const columnCount = Object.keys(columnMap).length;
    const headerRow = generateHeaderRow(context, columnMap);

    // Generate the contents of the matrix itself, aside from the header row.
    const sortedRowCategoryBuckets = sortRowCategoryBuckets(context.matrix.y[rowCategoryName].buckets);
    const dataTable = sortedRowCategoryBuckets.reduce((accumulatingTable, rowCategoryBucket, index) => {
        // Generate the row category label row.
        const rowCategoryClassModifier = rowCategoryBucket.key.replace(/ /g, '-').toLowerCase();
        const rowCategoryUri = composeRowCategoryUri(context, rowCategoryBucket);
        const categoryRow = [{
            rowContent: [
                { header: <a href={`${rowCategoryUri}`}>{rowCategoryBucket.key}</a> },
                { content: <span />, colSpan: columnCount },
            ],
            css: `matrix__row-category matrix__row-category--${rowCategoryClassModifier}`,
        }];

        const subcategoryRowCount = rowCategoryBucket[rowSubcategoryName].buckets.length;
        const subcategoryRows = rowCategoryBucket[rowSubcategoryName].buckets.reduce((accumulatingRows, rowSubcategoryBucket, subcategoryIndex) => {
            // Generate an empty subcategory row with enough empty cells for the entire row.
            const subcategoryRow = {
                rowContent: Array(columnCount + 1).fill(null),
                css: `matrix__row-data matrix__row-data--${rowCategoryClassModifier}`,
            };

            // Generate the data cells for the subcategory row starting with the subcategory header.
            subcategoryRow.rowContent[0] = {
                header: (
                    <RowSubcategoryLabel context={context} categoryBucket={rowCategoryBucket} subcategoryBucket={rowSubcategoryBucket}>
                        {rowSubcategoryBucket.key}
                    </RowSubcategoryLabel>
                ),
                css: subcategoryIndex === subcategoryRowCount - 1 ? 'subcategory-header-last-of-section' : null,
            };
            rowSubcategoryBucket[colCategoryName].buckets.forEach((colCategoryBucket) => {
                // Generate the data cells for the row using the column categories and
                // subcategories to find the correct column to place the data into.
                colCategoryBucket[colSubcategoryName].buckets.forEach((colSubcategoryBucket) => {
                    const columnKey = composeColumnKey(colCategoryBucket.key, colSubcategoryBucket.key);
                    const columnIndex = columnMap[columnKey];
                    const cellQuery = composeCellQuery(
                        context,
                        rowCategoryBucket,
                        rowSubcategoryBucket,
                        colCategoryBucket,
                        colSubcategoryBucket
                    );

                    // Set the contents of a cell to the number of datasets in that cell.
                    subcategoryRow.rowContent[columnIndex] = {
                        content: (
                            <a href={`${context.search_base}&${cellQuery}`}>
                                {colSubcategoryBucket.doc_count}
                            </a>
                        ),
                    };
                });
            });

            // Add the subcategory header and data rows to a species section of the table.
            return accumulatingRows.concat(subcategoryRow);
        }, []);

        // Output one species section of the table, adding a blank row after the first one.
        const acc = accumulatingTable.concat(categoryRow).concat(subcategoryRows);
        return index === 0
            ? acc.concat([
                {
                    rowContent: [{ content: <div />, colSpan: 0 }],
                    css: 'matrix__horizontal-divider',
                },
            ])
            : acc;
    }, []);
    const tableData = [headerRow].concat(dataTable);
    return { tableData, rowKeys: [] };
};


/**
 * Render the area above the facets and matrix content.
 */
const MatrixHeader = ({ context }) => (
    <div className="matrix-header">
        <div className="matrix-header__banner">
            <div className="matrix-header__title">
                <h1>{context.title}</h1>
                <ClearSearchTerm searchUri={context['@id']} />
            </div>
        </div>
        <div className="matrix-header__controls">
            <div className="matrix-header__filter-controls">
                <SearchFilter context={context} type="functional characterizations" css="matrix-general-search--degron" />
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

MatrixHeader.propTypes = {
    /** Matrix search-result object */
    context: PropTypes.object.isRequired,
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
    /** Matrix search-result object */
    context: PropTypes.object.isRequired,
};


/**
 * Display the matrix and associated controls above them.
 */
const MatrixPresentation = ({ context }) => {
    // Convert encode matrix data to a DataTable object.
    const { tableData } = React.useMemo(() => convertDatasetToDataTable(context), [context]);

    const matrixConfig = {
        rows: tableData,
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
    /** Matrix search-result object */
    context: PropTypes.object.isRequired,
};


/**
 * Render the vertical facets and the matrix itself.
 */
const MatrixContent = ({ context }) => (
    <div className="matrix__content matrix__content--functional-characterization">
        <MatrixVerticalFacets context={context} />
        <MatrixPresentation context={context} />
    </div>
);

MatrixContent.propTypes = {
    /** Matrix search-result object */
    context: PropTypes.object.isRequired,
};


/**
 * View component for the functional characterization matrix page.
 */
const FunctionalCharacterizationMatrix = ({ context }) => {
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

FunctionalCharacterizationMatrix.propTypes = {
    /** Matrix search-result object */
    context: PropTypes.object.isRequired,
};

FunctionalCharacterizationMatrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};

contentViews.register(FunctionalCharacterizationMatrix, 'FunctionalCharacterizationMatrix');
