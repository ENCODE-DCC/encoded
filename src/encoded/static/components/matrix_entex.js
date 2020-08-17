import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import * as encoding from '../libs/query_encoding';
import { svgIcon } from '../libs/svg-icons';
import { Panel, PanelBody } from '../libs/ui/panel';
import DataTable from './datatable';
import * as globals from './globals';
import { MATRIX_VISUALIZE_LIMIT, SearchFilter } from './matrix';
import { MatrixBadges } from './objectutils';
import { SearchControls } from './search';


/**
 * All assay columns not included in matrix.
 */
const excludedAssays = [
    'Control ChIP-seq',
    'Control eCLIP',
];

/**
 * All assays that have targets but we don't display the target columns, and instead show that data
 * combined in the assay column.
 */
const collapsedAssays = [
    'MeDIP-seq',
];

/**
 * Order in which assay_titles should appear along the horizontal axis of the matrix. Anything not
 * included gets sorted after these.
 */
const matrixAssaySortOrder = [
    'total RNA-seq',
    'RAMPAGE',
    'long read RNA-seq',
    'small RNA-seq',
    'microRNA-seq',
    'microRNA counts',
    'ATAC-seq',
    'DNase-seq',
    'WGBS',
    'DNAme array',
    'TF ChIP-seq',
    'Histone ChIP-seq',
    'eCLIP',
    'Hi-C',
    'genotyping HTS',
    'genotyping array',
];

/**
 * Defines the accessions and other associated display information for each of the four ENTEx
 * donors. The [top-left, top-right, bottom-left, bottom-right] cell render order dictates the
 * order in this array. The properties mean:
 *   accession: Accession of donor
 *   cssSuffix: Suffix to use on all associated CSS style names
 *   voice: Text for a screen reader to speak
 *   legendText: Text to display in legend; UNICODE male/female symbols
 */
const entexDonors = [
    {
        accession: 'ENCDO845WKR',
        cssSuffix: 'male1',
        voice: 'Male 1',
        legendText: '\u26421',
    },
    {
        accession: 'ENCDO793LXB',
        cssSuffix: 'female3',
        voice: 'Female 3',
        legendText: '\u26403',
    },
    {
        accession: 'ENCDO451RUA',
        cssSuffix: 'male2',
        voice: 'Male 2',
        legendText: '\u26422',
    },
    {
        accession: 'ENCDO271OUW',
        cssSuffix: 'female4',
        voice: 'Female 4',
        legendText: '\u26404',
    },
];


/**
 * Displays one row of the donor legend. Each pie slice not specified in `entexDonor` gets its
 * CSS style overridden by "blank" which makes it gray colored. The pie slices otherwise get
 * rendered the same way they do in the actual table.
 */
const DonorLegendRow = ({ entexDonor }) => (
    <div className="donor-legend-row">
        <div className="donor-cell">
            {entexDonors.map(donorQuadrant => (
                <div key={donorQuadrant.accession} className={`donor-quadrant donor-quadrant--${donorQuadrant.cssSuffix}${donorQuadrant.accession !== entexDonor.accession ? ' blank' : ''}`} />
            ))}
        </div>
        <div className="donor-legend-row__label">
            <div className={`donor-legend-row__short-string donor-legend-row__short-string--${entexDonor.cssSuffix}`}>{entexDonor.legendText}</div>
            <a href={`/human-donors/${entexDonor.accession}`} aria-label={`Go to donor page for ${entexDonor.voice} ${entexDonor.accession}`}>{entexDonor.accession}</a>
        </div>
    </div>
);

DonorLegendRow.propTypes = {
    /** Element of `entexDonors` to render */
    entexDonor: PropTypes.object.isRequired,
};


/**
 * Draw a legend of what the quadrants in each matrix cell means.
 */
const DonorLegend = () => (
    <div className="donor-legend">
        {entexDonors.map(entexDonor => (
            <DonorLegendRow key={entexDonor.accession} entexDonor={entexDonor} />
        ))}
    </div>
);


/**
 * Generate an assay:column map that maps from a combined assay and target name to a column index
 * in the matrix. Any determination of column order or inclusion/exclusion happens in this
 * function. Do not rely on the order of the keys. The resulting object has the form:
 * {
 *   'cat1': {col: 0, category: 'cat1'},
 *   'cat1|subcat1': {col: 1, category: 'cat1', subcategory: 'subcat1'},
 *   'cat1|subcat2': {col: 2, category: 'cat1', subcategory: 'subcat2'},
 *   'cat3': {col: 5, category: 'cat3'},
 *   'cat2': {col: 3, category: 'cat2'},
 *   'cat2|subcat3': {col: 4, category: 'cat2', subcategory: 'subcat3'},
 *   ...
 * }
 *
 * To generate the assay labels that group columns of targets, generate an array of assays
 * to help render the table row that contains these assay labels. These labels exist in column
 * order, with null entries for assays with no child targets, and an object for assays with
 * child targets, each containing the starting column for the assay label, the assay's label
 * itself, and the number of child targets it has.
 * [
 *     null,
 *     null,
 *     {col: 2, category: 'cat1', subcategoryCount: 3},
 *     {col: 6, category: 'cat2', subcategoryCount: 0},
 *     null,
 * ]
 * @param {object} context ENTEx matrix data
 *
 * @return {object} Column map object and target assay array.
 */
const generateColMap = (context) => {
    const colCategory = context.matrix.x.group_by[0];
    const colSubcategory = context.matrix.x.group_by[1][0];
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

    // Loop to construct the `colMap` object and `targetAssays` array.
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

            // Add the mapping of "assay|target" key string to column index for those assays that
            // have targets and don't collapse their targets. A target of "no_target" means the
            // assay has no targets.
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
    if (!targetAssays.some(assay => assay !== null)) {
        targetAssays = [];
    }

    return { colMap, targetAssays };
};


/**
 * Render a single cell within the table that contains up to four donors, with each quadrant of the
 * cell devoted to a consistent donor throughout the table.
 */
const DonorCell = ({ donorDatum, rowCategory, rowSubcategory, colCategory, colSubcategory }) => {
    // Construct the screen-reader string with all provided accessions, comma separated.
    const relevantDonors = entexDonors.filter(entexDonor => donorDatum.includes(entexDonor.accession));
    const donorVoice = relevantDonors.map(relevantDonor => relevantDonor.voice).join(', ');

    return (
        <div className="donor-cell">
            {entexDonors.map((entexDonor) => {
                const quadrantStyle = `donor-quadrant donor-quadrant--${donorDatum.includes(entexDonor.accession) ? entexDonor.cssSuffix : 'none'}`;
                return <div key={entexDonor.accession} className={quadrantStyle} />;
            })}
            <div className="sr-only">{donorDatum.length} {donorDatum.length > 1 ? 'donors' : 'donor'}, {donorVoice}.</div>
            <div className="sr-only">Search {rowCategory}, {rowSubcategory} for {colCategory}, {colSubcategory === 'no_target' ? '' : colSubcategory}</div>
        </div>
    );
};

DonorCell.propTypes = {
    /** Donor accessions in cell in no defined order */
    donorDatum: PropTypes.array.isRequired,
    /** Row category text for screen readers */
    rowCategory: PropTypes.string.isRequired,
    /** Row subcategory text for screen readers */
    rowSubcategory: PropTypes.string.isRequired,
    /** Column category text for screen readers */
    colCategory: PropTypes.string.isRequired,
    /** Column subcategory text for screen readers */
    colSubcategory: PropTypes.string.isRequired,
};


// Keep this constant in sync with $donor-cell-width in _matrix.scss.
const DONOR_CELL_WIDTH = 30;


/**
 * Takes matrix data from JSON and generates an object that <DataTable> can use to generate the JSX
 * for the matrix. This is a shim between the incoming matrix data and the object <DataTable>
 * needs.
 * @param {object} context Matrix JSON for the page
 *
 * @return {object} Generated object suitable for passing to <DataTable>
 */
const convertContextToDataTable = (context) => {
    // Retrieve the bucket property names for the different levels of the hierarchical matrix data.
    const colCategory = context.matrix.x.group_by[0];
    const colSubcategory = context.matrix.x.group_by[1][0];
    const cellCategory = context.matrix.x.group_by[2];
    const cellSubcategory = context.matrix.x.group_by[3];
    const rowCategory = context.matrix.y.group_by[0];
    const rowSubcategory = context.matrix.y.group_by[1];
    const rowKeys = [];
    const headerRows = [];

    // Generate the mapping of column categories and subcategories.
    const { colMap, targetAssays } = generateColMap(context);
    const colCount = Object.keys(colMap).length;

    // Convert column map to an array of column map values sorted by column number for displaying
    // in the matrix header.
    const sortedCols = Object.keys(colMap).map(assayColKey => colMap[assayColKey]).sort((colInfoA, colInfoB) => colInfoA.col - colInfoB.col);

    // Generate the matrix header row labels for the assays with targets. Need a max-width inline
    // style so that wide labels don't make the target columns expand.
    if (targetAssays.length > 0) {
        const targetAssayHeader = [{ css: 'matrix__col-category-targetassay-corner' }].concat(targetAssays.map(((targetAssayElement) => {
            if (targetAssayElement) {
                // Add cell with assay title and span for the number of targets it has.
                const categoryQuery = `${colCategory}=${encoding.encodedURIComponent(targetAssayElement.category)}`;
                return {
                    header: <a href={`${context.search_base}&${categoryQuery}`}>{targetAssayElement.category} <div className="sr-only">{targetAssayElement.category}</div></a>,
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

    // Generate the hierarchical top-row sideways header label cells. The first cell has the
    // legend for the cell data. At the end of this loop, rendering `{header}` shows this header
    // row. The `sortedCols` array gets mutated in this loop, acquiring a `query` property in each
    // of its objects that gets used later to generate cell hrefs. Also generate a boolean array
    // of columns that indicate which ones need to have dividers rendered for columns of assays
    // with targets.
    let prevCategory;
    let prevSubcategory;
    const dividerCss = [];
    const header = [
        { content: <DonorLegend />, css: 'matrix__entex-corner' },
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

        const categoryQuery = `${colCategory}=${encoding.encodedURIComponent(colInfo.category)}`;
        if (!colInfo.subcategory) {
            // Add the category column links.
            colInfo.query = categoryQuery;
            return {
                header: <a href={`${context.search_base}&${categoryQuery}`}>{colInfo.category} <div className="sr-only">{context.matrix.x.label}</div></a>,
                css: dividerCss[colInfo.col],
            };
        }

        // Add the subcategory column links and column dividers when the category changes as we go
        // left to right across the columns.
        const subCategoryQuery = `${colSubcategory}=${encoding.encodedURIComponent(colInfo.subcategory)}`;
        colInfo.query = `${categoryQuery}&${subCategoryQuery}`;
        return {
            header: <a className="sub" href={`${context.search_base}&${categoryQuery}&${subCategoryQuery}`}>{colInfo.subcategory} <div className="sr-only">target for {colInfo.category} {context.matrix.x.label} </div></a>,
            css: `category-base${dividerCss[colInfo.col] ? ` ${dividerCss[colInfo.col]}` : ''}`,
        };
    }));

    // Generate the main table content including the data hierarchy, where the upper level of the
    // hierarchy gets referred to here as "rowCategory" and the lower level gets referred to as
    // "rowSubcategory." Both these types of rows get collected into `dataTable` which gets passed
    // to <DataTable>. Also generate an array of React keys to use with <DataTable>.
    rowKeys.push('column-categories');
    headerRows.push({ rowContent: header, css: 'matrix__col-category-header' });
    const rowKeysInitialLength = rowKeys.length;
    const rowCategoryBuckets = context.matrix.y[rowCategory].buckets;

    const dataTable = rowCategoryBuckets.reduce((accumulatingTable, rowCategoryBucket, rowCategoryIndex) => {
        // Each loop iteration generates all the rows of the row subcategories (biosample term names)
        // under it.
        const rowSubcategoryBuckets = rowCategoryBucket[rowSubcategory].buckets;
        const rowCategoryQuery = `${rowCategory}=${encoding.encodedURIComponent(rowCategoryBucket.key)}`;
        rowKeys[rowCategoryIndex + rowKeysInitialLength] = rowCategoryBucket.key;

        const cells = Array(colCount);
        const subcategoryRows = rowSubcategoryBuckets.map((rowSubcategoryBucket, rowSubcategoryIndex) => {
            const subCategoryQuery = `${rowSubcategory}=${encoding.encodedURIComponent(rowSubcategoryBucket.key)}`;

            // Each biosample term name's row reuses the same `cells` array of cell components.
            // Until we fill it with actual data below, we initialize the row with empty cells,
            // with a CSS class to render a divider for columns of assays with targets.
            dividerCss.forEach((divider, colIndex) => {
                cells[colIndex] = { css: divider };
            });
            rowSubcategoryBucket[colCategory].buckets.forEach((rowSubcategoryColCategoryBucket) => {
                // Skip any excluded assay columns.
                if (!excludedAssays.includes(rowSubcategoryColCategoryBucket.key)) {
                    // Loop to generate each cell in one biosample term name row.
                    rowSubcategoryColCategoryBucket[colSubcategory].buckets.forEach((rowSubcategoryColSubcategoryBucket) => {
                        // Make an array of all the donor accessions relevant to one biosample
                        // term name and assay/target.
                        const donorData = [];
                        rowSubcategoryColSubcategoryBucket[cellCategory].buckets.forEach((cellCategoryBucket) => {
                            cellCategoryBucket[cellSubcategory].buckets.forEach((cellSubcategoryBucket) => {
                                donorData.push(cellSubcategoryBucket.key);
                            });
                        });

                        if (rowSubcategoryColSubcategoryBucket.key === 'no_target' || collapsedAssays.includes(rowSubcategoryColCategoryBucket.key)) {
                            // The assay does not have targets, or it does but collapses them, so just
                            // add a donor cell for the column category.
                            const colIndex = colMap[rowSubcategoryColCategoryBucket.key].col;
                            cells[colIndex] = {
                                content: (
                                    <a href={`${context.search_base}&${rowCategoryQuery}&${subCategoryQuery}&${colMap[rowSubcategoryColCategoryBucket.key].query}`}>
                                        <DonorCell
                                            donorDatum={donorData}
                                            rowCategory={rowCategoryBucket.key}
                                            rowSubcategory={rowSubcategoryBucket.key}
                                            colCategory={rowSubcategoryColCategoryBucket.key}
                                            colSubcategory={rowSubcategoryColSubcategoryBucket.key}
                                        />
                                    </a>
                                ),
                                css: dividerCss[colIndex],
                            };
                        } else {
                            // Assay has non-collapsed targets, so render the donor cell for the
                            // current target.
                            const colMapKey = `${rowSubcategoryColCategoryBucket.key}|${rowSubcategoryColSubcategoryBucket.key}`;
                            const colIndex = colMap[colMapKey].col;
                            cells[colIndex] = {
                                content: (
                                    <a href={`${context.search_base}&${rowCategoryQuery}&${subCategoryQuery}&${colMap[colMapKey].query}`}>
                                        <DonorCell
                                            donorDatum={donorData}
                                            rowCategory={rowCategoryBucket.key}
                                            rowSubcategory={rowSubcategoryBucket.key}
                                            colCategory={rowSubcategoryColCategoryBucket.key}
                                            colSubcategory={rowSubcategoryColSubcategoryBucket.key}
                                        />
                                    </a>
                                ),
                                css: dividerCss[colIndex],
                            };
                        }
                    });
                }
            });

            // Add a single term-name row's data and left header to the matrix.
            rowKeys[rowCategoryIndex + 1] = `${rowCategoryBucket.key}|${rowSubcategoryBucket.key}`;
            return {
                rowContent: [
                    {
                        header: (
                            <a href={`${context.search_base}&${rowCategoryQuery}&${subCategoryQuery}`}>
                                <div className="subcategory-row-text">{rowSubcategoryBucket.key} <div className="sr-only">{context.matrix.y.label}</div></div>
                            </a>
                        ),
                    },
                ].concat(cells),
                css: `matrix__row-data${rowSubcategoryIndex === 0 ? ' matrix__row-data--first' : ''}`,
            };
        });

        // Continue adding rendered rows to the matrix.
        return accumulatingTable.concat(subcategoryRows);
    }, headerRows);
    return { dataTable, rowKeys };
};


/**
 * Render the area above the matrix itself, including the page title.
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
                    ENTEx is a collaboration with the GTEx Consortium to profile approximately 30 overlapping tissues from four donors.
                </div>
            </div>
            <div className="matrix-header__controls">
                <div className="matrix-header__filter-controls">
                    <SearchFilter context={context} />
                </div>
                <div className="matrix-header__search-controls">
                    <h4>Showing {context.total} results</h4>
                    <SearchControls context={context} visualizeDisabledTitle={visualizeDisabledTitle} hideBrowserSelector />
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
 * Display the matrix and associated controls above them.
 */
const MatrixPresentation = ({ context }) => {
    const [scrolledRight, setScrolledRight] = React.useState(false);
    const ref = React.useRef(null);

    // Memoized (prevents function creation on every render -- function only gets recreated when
    // `scrolledRight` value changes) callback to calculate whether the ASSAY arrow needs to flash
    // (`scrolledRight` === false) or not (`scrolledRight` === true). Called in response to both
    // "scroll" and "resize" events.
    const handleScroll = React.useCallback((target) => {
        // Have to use a "roughly equal to" test because of an MS Edge bug mentioned here:
        // https://stackoverflow.com/questions/30900154/workaround-for-issue-with-ie-scrollwidth
        const scrollDiff = Math.abs((target.scrollWidth - target.scrollLeft) - target.clientWidth);
        if (scrollDiff < 2 && !scrolledRight) {
            // Right edge of matrix scrolled into view.
            setScrolledRight(true);
        } else if (scrollDiff >= 2 && scrolledRight) {
            // Right edge of matrix scrolled out of view.
            setScrolledRight(false);
        }
    }, [scrolledRight]);

    // Callback called after component mounts to add the "scroll" and "resize" event listeners.
    // Both events can cause a recalculation of `scrolledRight`. People seem to prefer using the
    // "scroll" event listener with hooks as opposed to the onScroll property, but I don't yet know
    // why.
    React.useEffect(() => {
        // Direct callbacks not memoized because of their small size.
        const handleScrollEvent = event => handleScroll(event.target);
        const handleResizeEvent = () => handleScroll(ref.current);

        // Cache the reference to the scrollable matrix <div> so that we can remove the "scroll"
        // event handler on unmount, when ref.current might no longer point at this <div>.
        const matrixNode = ref.current;

        // Attach the scroll- and resize- event handlers, then force the initial calculation of
        // `scrolledRight`.
        ref.current.addEventListener('scroll', handleScrollEvent);
        window.addEventListener('resize', handleResizeEvent);
        handleScroll(ref.current);

        // Callback called when unmounting component.
        return () => {
            matrixNode.removeEventListener('scroll', handleScrollEvent);
            window.removeEventListener('resize', handleResizeEvent);
        };
    }, [handleScroll]);

    // Convert ENTEx matrix data to a DataTable object. I'd like to memoize this but determining if
    // the incoming, deeply nested matrix data has changed would be very complicated.
    const { dataTable, rowKeys } = convertContextToDataTable(context);
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
                <div className="matrix__data" ref={ref}>
                    <DataTable tableData={matrixConfig} />
                </div>
            </div>
        </div>
    );
};

MatrixPresentation.propTypes = {
    /** ENTEx matrix object */
    context: PropTypes.object.isRequired,
};


/**
 * Render the area containing the matrix.
 */
const MatrixContent = ({ context }) => (
    <div className="matrix__content matrix__content--entex">
        <MatrixPresentation context={context} />
    </div>
);

MatrixContent.propTypes = {
    /** ENTEx matrix object */
    context: PropTypes.object.isRequired,
};


/**
 * View component for the ENTEx matrix page.
 */
const EntexMatrix = ({ context }) => {
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

EntexMatrix.propTypes = {
    /** ENTEx matrix object */
    context: PropTypes.object.isRequired,
};

EntexMatrix.contextTypes = {
    location_href: PropTypes.string,
};

globals.contentViews.register(EntexMatrix, 'EntexMatrix');
