import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import * as encoding from '../libs/query_encoding';
import { svgIcon } from '../libs/svg-icons';
import { Panel, PanelBody } from '../libs/ui/panel';
import DataTable from './datatable';
import * as globals from './globals';
import { matrixAssaySortOrder, MATRIX_VISUALIZE_LIMIT, SearchFilter } from './matrix';
import { MatrixInternalTags } from './objectutils';
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
        legendText: '\u2642 1',
    },
    {
        accession: 'ENCDO793LXB',
        cssSuffix: 'female3',
        voice: 'Female 3',
        legendText: '\u2640 3',
    },
    {
        accession: 'ENCDO451RUA',
        cssSuffix: 'male2',
        voice: 'Male 2',
        legendText: '\u2642 2',
    },
    {
        accession: 'ENCDO271OUW',
        cssSuffix: 'female4',
        voice: 'Female 4',
        legendText: '\u2640 4',
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
 *   'cat1': {col: 0, category: 'cat1', hasSubcategories: true},
 *   'cat1|subcat1': {col: 1, category: 'cat1', subcategory: 'subcat1'},
 *   'cat1|subcat2': {col: 2, category: 'cat1', subcategory: 'subcat2'},
 *   'cat3': {col: 5, category: 'cat3', hasSubcategories: false},
 *   'cat2': {col: 3, category: 'cat2', hasSubcategories: true},
 *   'cat2|subcat3': {col: 4, category: 'cat2', subcategory: 'subcat3'},
 *   ...
 * }
 * TODO: Convert the reference-epigenome matrix to use the same no_targets method we use in the
 * ENTEx matrix, allowing us to share this function between the two matrix implementations.
 * @param {object} context ENTEx matrix data
 *
 * @return {object} Keyed column header information
 */
const generateColMap = (context) => {
    const colCategory = context.matrix.x.group_by[0];
    const colSubcategory = context.matrix.x.group_by[1][0];
    const colMap = {};
    let colIndex = 0;

    // Sort column categories according to a specified order, with any items not specified sorted
    // at the end in order of occurrence.
    const colCategoryBuckets = context.matrix.x[colCategory].buckets;
    const sortedColCategoryBuckets = _(colCategoryBuckets).sortBy((colCategoryBucket) => {
        const sortIndex = matrixAssaySortOrder.indexOf(colCategoryBucket.key);
        return sortIndex >= 0 ? sortIndex : colCategoryBuckets.length;
    });

    // Loop to construct the `colMap object.
    sortedColCategoryBuckets.forEach((colCategoryBucket) => {
        if (!excludedAssays.includes(colCategoryBucket.key)) {
            const colSubcategoryBuckets = colCategoryBucket[colSubcategory].buckets;

            // Add the mapping of "assay" key string to column index.
            colMap[colCategoryBucket.key] = {
                col: colIndex,
                category: colCategoryBucket.key,
                hasSubcategories: colSubcategoryBuckets.length > 0 && colSubcategoryBuckets[0].key !== 'no_target',
            };
            colIndex += 1;

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
    return colMap;
};


/**
 * Display a disabled cell in the matrix. Used to reduce a bit of code per cell when matrices can
 * be very large.
 */
const DisabledCell = () => <div className="matrix__disabled-cell" />;


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

    // Generate the mapping of column categories and subcategories.
    const colMap = generateColMap(context);
    const colCount = Object.keys(colMap).length;

    // Convert column map to an array of column map values sorted by column number for displaying
    // in the matrix header.
    const sortedCols = Object.keys(colMap).map(assayColKey => colMap[assayColKey]).sort((colInfoA, colInfoB) => colInfoA.col - colInfoB.col);

    // Generate array of names of assays that have targets and don't collapse their targets, for
    // rendering those columns as disabled.
    const colCategoriesWithSubcategories = Object.keys(colMap).filter(colCategoryName => colMap[colCategoryName].hasSubcategories && !collapsedAssays.includes(colCategoryName));

    // Generate the hierarchical top-row sideways header label cells. The first cell has the
    // legend for the cell data. At the end of this loop, rendering `{header}` shows this header
    // row. The `sortedCols` array gets mutated in this loop, acquiring a `query` property in each
    // of its objects that gets used later to generate cell hrefs.
    const header = [
        { content: <DonorLegend />, css: 'matrix__entex-corner' },
    ].concat(sortedCols.map((colInfo) => {
        const categoryQuery = `${colCategory}=${encoding.encodedURIComponent(colInfo.category)}`;
        if (!colInfo.subcategory) {
            // Add the category column links.
            colInfo.query = categoryQuery;
            return { header: <a href={`${context.search_base}&${categoryQuery}`}>{colInfo.category} <div className="sr-only">{context.matrix.x.label}</div></a> };
        }

        // Add the subcategory column links.
        const subCategoryQuery = `${colSubcategory}=${encoding.encodedURIComponent(colInfo.subcategory)}`;
        colInfo.query = `${categoryQuery}&${subCategoryQuery}`;
        return { header: <a className="sub" href={`${context.search_base}&${categoryQuery}&${subCategoryQuery}`}>{colInfo.subcategory} <div className="sr-only">target for {colInfo.category} {context.matrix.x.label} </div></a> };
    }));

    // Generate the main table content including the data hierarchy, where the upper level of the
    // hierarchy gets referred to here as "rowCategory" and the lower level gets referred to as
    // "rowSubcategory." Both these types of rows get collected into `dataTable` which gets passed
    // to <DataTable>. Also generate an array of React keys to use with <DataTable>.
    const rowKeys = ['column-categories'];
    const rowCategoryBuckets = context.matrix.y[rowCategory].buckets;

    const dataTable = rowCategoryBuckets.reduce((accumulatingTable, rowCategoryBucket, rowCategoryIndex) => {
        // Each loop iteration generates all the rows of the row subcategories (biosample term names)
        // under it.
        const rowSubcategoryBuckets = rowCategoryBucket[rowSubcategory].buckets;
        const rowCategoryQuery = `${rowCategory}=${encoding.encodedURIComponent(rowCategoryBucket.key)}`;
        rowKeys[rowCategoryIndex + 1] = rowCategoryBucket.key;

        const cells = Array(colCount);
        const subcategoryRows = rowSubcategoryBuckets.map((rowSubcategoryBucket, rowSubcategoryIndex) => {
            const subCategoryQuery = `${rowSubcategory}=${encoding.encodedURIComponent(rowSubcategoryBucket.key)}`;

            // Each biosample term name's row reuses the same `cells` array of cell components.
            cells.fill(null);
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
                            };
                        }
                    });
                }
            });

            // Show assay columns as disabled (i.e. nothing to see here) if those columns have
            // target columns.
            colCategoriesWithSubcategories.forEach((colCategoryName) => {
                cells[colMap[colCategoryName].col] = { content: <DisabledCell /> };
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
    }, [{ rowContent: header, css: 'matrix__col-category-header' }]);
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
                <h1>{context.title}</h1>
                <div className="matrix-tags">
                    <MatrixInternalTags context={context} />
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
