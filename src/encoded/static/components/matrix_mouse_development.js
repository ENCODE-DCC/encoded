import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import * as encoding from '../libs/query_encoding';
import QueryString from '../libs/query_string';
import { Panel, PanelBody } from '../libs/ui/panel';
import { svgIcon } from '../libs/svg-icons';
import { tintColor, isLight } from './datacolors';
import DataTable from './datatable';
import * as globals from './globals';
import { RowCategoryExpander, MATRIX_VISUALIZE_LIMIT } from './matrix';
import matrixAssaySortOrder from './matrix_reference_epigenome';
import { MatrixInternalTags } from './objectutils';
import { SearchControls } from './search';


/**
 * Number of subcategory items to show when subcategory isn't expanded.
 * @constant
 */
const ROW_CATEGORY = 'biosample_ontology.term_name';
const ROW_SUBCATEGORY = 'biosample_summary';
const COL_CATEGORY = 'assay_title';
const COL_SUBCATEGORY = 'target.label';

/**
 * All assay columns to not include in matrix.
 */
const excludedAssays = [
    'Control ChIP-seq',
];

/**
 * All assays that have targets but we don't display the target columns, and instead show that data
 * combined in the assay column.
 */
const collapsedAssays = [
    'MeDIP-seq',
];

/**
 * Special colors for mouse matrix
 */
const mouseMatrixColors = {
    hippocampus: '#FCFFC4',
    forebrain: '#EDD982',
    hindbrain: '#568CA3',
    midbrain: '#2E4057',
    'embryonic facial prominence': '#1E5289',
    heart: '#124559',
    lung: '#598392',
    liver: '#AEC3B0',
    stomach: '#51344D',
    intestine: '#6F5060',
    kidney: '#A78682',
    limb: '#104547',
    'neural tube': '#444554',
    'skeletal muscle tissue': '#C191A1',
    'adrenal gland': '#7A3B67',
    spleen: '#404272',
    thymus: '#881600',
    'urinary bladder': '#F4CF90',
};

/**
 * Parse string (longString) on potentially repeated substring (splitString)
 */
function parseString(longString, splitString) {
    return longString.substring(longString.indexOf(splitString) + splitString.length + 1);
}

/**
 * Increment subCategorySums value for bucket keys matching a column name
 */
function updateColumnCount(value, colMap, subCategorySums) {
    let colIndex = 0;
    if (value && value['target.label'] && value['target.label'].buckets.length > 1) {
        value['target.label'].buckets.forEach((bucket) => {
            const newKey = `${value.key}|${bucket.key}`;
            if (bucket.key && colMap[newKey]) {
                colIndex = colMap[newKey].col || 0;
            } else {
                colIndex = colMap[value.key].col || 0;
            }
            subCategorySums[colIndex] = (subCategorySums[colIndex] || 0) + 1;
        });
    } else {
        colIndex = colMap[value.key].col || 0;
        subCategorySums[colIndex] = (subCategorySums[colIndex] || 0) + 1;
    }
    return subCategorySums;
}

/**
  * Collect column counts to display on headers
  * Counts reflect the number of rows which contain data per column, not the number of experiments per column
  * @param {array}    subCategoryData Array of subcategory objects, each containing an array of data
  * @param {string}   columnCategory Column headers variable
  * @param {object}   colMap Keyed column header information
  * @param {number}   colCount Number of columns
  * @param {array}   stageFilter Stage/age filters selected by user
  *
  * @return {array}   subCategorySums Counts per column
  */
const analyzeSubCategoryData = (subCategoryData, columnCategory, colMap, colCount, stageFilter) => {
    let subCategorySums = Array(colCount).fill(0);
    subCategoryData.forEach((rowData) => {
        // `rowData` has all the data for one row. Collect sums of all data for each column.
        rowData[columnCategory].buckets.forEach((value) => {
            if (stageFilter) {
                stageFilter.forEach((singleFilter) => {
                    const filterString = singleFilter.replace(/[()]/g, '');
                    const keyString = rowData.key.replace(/[()]/g, '');
                    if (!filterString || keyString.includes(filterString)) {
                        subCategorySums = updateColumnCount(value, colMap, subCategorySums);
                    }
                });
            } else {
                subCategorySums = updateColumnCount(value, colMap, subCategorySums);
            }
        });
    });
    return subCategorySums;
};

// Sort the rows of the matrix by stage (embryo -> postnatal -> adult) and then by age
// Age can be denoted in days or weeks
// In the future there are likely to be additions to the data which will require updates to this function
// For instance, ages measured by months will likely be added
function sortMouseArray(a, b) {
    const aStage = a.split(' (')[0];
    const bStage = b.split(' (')[0];
    let aNumerical = 0;
    let bNumerical = 0;
    if (aStage === 'embryo') {
        aNumerical = 100;
    } else if (aStage === 'postnatal') {
        aNumerical = 1000;
    } else if (aStage === 'adult') {
        aNumerical = 10000;
    }
    if (a.includes('days')) {
        aNumerical += +a.split(' days)')[0].split('(')[1];
    } else if (a.includes(' weeks')) {
        aNumerical += +a.split(' weeks)')[0].split('(')[1] * 7;
    }
    if (bStage === 'embryo') {
        bNumerical = 100;
    } else if (bStage === 'postnatal') {
        bNumerical = 1000;
    } else if (bStage === 'adult') {
        bNumerical = 10000;
    }
    if (b.includes('days')) {
        bNumerical += +b.split(' days)')[0].split('(')[1];
    } else if (b.includes(' weeks')) {
        bNumerical += +b.split(' weeks)')[0].split('(')[1] * 7;
    }
    return aNumerical - bNumerical;
}

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

const generateNewColMap = (context) => {
    const colCategory = context.matrix.x.group_by[0];
    const colSubcategory = context.matrix.x.group_by[1];
    const colMap = {};
    let colIndex = 0;

    // Sort column categories according to a specified order, with any items not specified sorted
    // at the end in order of occurrence.
    const colCategoryBuckets = context.matrix.x[colCategory].buckets;
    const sortedColCategoryBuckets = _(colCategoryBuckets).sortBy((colCategoryBucket) => {
        const sortIndex = matrixAssaySortOrder.indexOf(colCategoryBucket.key);
        return sortIndex >= 0 ? sortIndex : colCategoryBuckets.length;
    });

    // Generate the column map based on the sorted category buckets.
    sortedColCategoryBuckets.forEach((colCategoryBucket) => {
        if (!excludedAssays.includes(colCategoryBucket.key)) {
            const colSubcategoryBuckets = colCategoryBucket[colSubcategory].buckets;
            if (colSubcategoryBuckets.length === 0) {
                // Add the mapping of "<assay>" key string to column index.
                colMap[colCategoryBucket.key] = { col: colIndex, category: colCategoryBucket.key, hasSubcategories: colSubcategoryBuckets.length > 0 };
                colIndex += 1;
            }

            // Add the mapping of "<assay>|<target>"" key string to column index for those assays that
            // have targets and don't collapse their targets.
            if (!collapsedAssays.includes(colCategoryBucket.key)) {
                colSubcategoryBuckets.forEach((colSubcategoryBucket) => {
                    colMap[`${colCategoryBucket.key}|${colSubcategoryBucket.key}`] = {
                        col: colIndex,
                        category: colCategoryBucket.key,
                        subcategory: colSubcategoryBucket.key,
                    };
                    colIndex += 1;
                });
            }
        }
    });
    return colMap;
};

/**
 * Takes matrix data from JSON and generates an object that <DataTable> can use to generate the JSX
 * for the matrix.
 * @param {object} context Matrix JSON for the page
 * @param {func}   getRowCategories Returns rowCategory info including desired display order
 * @param {func}   mapRowCategoryQueries Callback to map row category query values
 * @param {array}  expandedRowCategories Names of rowCategories the user has expanded
 * @param {func}   expanderClickHandler Called when the user expands/collapses a row category
 * @param {func}   stageFilter Stage/age filters selected by user
 *
 * @return {object} Generated object suitable for passing to <DataTable>
 */

const convertExperimentToDataTable = (context, getRowCategories, mapRowCategoryQueries, expandedRowCategories, expanderClickHandler, stageFilter) => {
    const rowCategory = context.matrix.y.group_by[0];
    const rowSubcategory = context.matrix.y.group_by[1];

    // Generate the mapping of column categories and subcategories.
    const colCategory = context.matrix.x.group_by[0];
    const colSubcategory = context.matrix.x.group_by[1];

    // Generate the mapping of column categories and subcategories.
    const colMap = generateNewColMap(context);
    const colCount = Object.keys(colMap).length;

    // Convert column map to an array of column map values sorted by column number for displaying
    // in the matrix header.
    const sortedCols = Object.keys(colMap).map(assayColKey => colMap[assayColKey]).sort((colInfoA, colInfoB) => colInfoA.col - colInfoB.col);

    const colCategoryNames = [];
    sortedCols.forEach((col) => {
        if (col.subcategory) {
            colCategoryNames.push(`${col.category}|${col.subcategory}`);
        } else if (col.hasSubcategories !== true) {
            colCategoryNames.push(col.category);
        }
    });

    // Generate array of names of assays that have targets and don't collapse their targets, for
    // rendering those columns as disabled.
    const colCategoriesWithSubcategories = Object.keys(colMap).filter(colCategoryName => colMap[colCategoryName].hasSubcategories && !collapsedAssays.includes(colCategoryName));

    const { rowCategoryData, rowCategoryNames } = getRowCategories();
    const rowKeys = ['column-categories'];

    // loop through row data to combine gendered mouse stage/ages into single row
    const combinedRowCategoryData = JSON.parse(JSON.stringify(rowCategoryData));
    rowCategoryData.forEach((row, rowIdx) => {
        const newRowAgeArray = [];
        row.biosample_summary.buckets.forEach((bucket) => {
            const newAge = parseString(bucket.key, row.key).replace('male ', '').replace('female ', '');
            if (newRowAgeArray.indexOf(newAge) === -1) {
                newRowAgeArray.push(newAge);
            }
        });
        newRowAgeArray.sort(sortMouseArray);
        const fullRowAgeArray = [];
        row.biosample_summary.buckets.forEach((bucket) => {
            const newAge = parseString(bucket.key, row.key);
            if (fullRowAgeArray.indexOf(newAge) === -1) {
                fullRowAgeArray.push(newAge);
            }
        });
        const newRowBuckets = [];
        const newRowBucketsNames = [];
        row.biosample_summary.buckets.forEach((bucket) => {
            let temp;
            // if there is already a bucket, add to it
            const bucketName = parseString(bucket.key, row.key).replace('male ', '').replace('female ', '');
            if (newRowBucketsNames.indexOf(bucketName) > -1) {
                newRowBuckets.forEach((bucket2) => {
                    const bucket2Key = parseString(bucket2.key, row.key);
                    if (bucket2Key === bucketName) {
                        const comboBuckets = [];
                        bucket.assay_title.buckets.forEach((b) => {
                            comboBuckets.push(b);
                        });
                        bucket2.assay_title.buckets.forEach((b2) => {
                            comboBuckets.forEach((combo) => {
                                let comboExists = 0;
                                if (combo.key === b2.key) {
                                    comboExists = 1;
                                }
                                if (comboExists === 0) {
                                    comboBuckets.push(b2);
                                }
                            });
                        });
                        bucket2.assay_title.buckets = comboBuckets;
                    }
                });
            // if not, push new bucket to bucket list
            } else {
                temp = Object.assign({}, bucket);
                temp.key = temp.key.replace('male ', '').replace('female ', '');
                newRowBuckets.push(temp);
                newRowBucketsNames.push(parseString(temp.key, row.key));
            }
        });
        combinedRowCategoryData[rowIdx].biosample_summary.buckets = newRowBuckets;
    });

    // loop through row data to sort buckets by sorted mouse stage/age
    const newRowCategoryData = JSON.parse(JSON.stringify(combinedRowCategoryData));
    combinedRowCategoryData.forEach((row, rowIdx) => {
        const rowAgeArray = [];
        row.biosample_summary.buckets.forEach((bucket) => {
            rowAgeArray.push(parseString(bucket.key, row.key));
        });
        rowAgeArray.sort(sortMouseArray);
        const newBuckets = [];
        rowAgeArray.forEach((age) => {
            row.biosample_summary.buckets.forEach((bucket, idx) => {
                const ageKey = parseString(bucket.key, row.key);
                if (age === ageKey) {
                    newBuckets.push(row.biosample_summary.buckets[idx]);
                }
            });
        });
        newRowCategoryData[rowIdx].biosample_summary.buckets = newBuckets;
    });

    let matrixRow = 1;

    // Generate the hierarchical top-row sideways header label cells. The first cell is null unless
    // it contains a link to clear the currently selected classification. At the end of this loop,
    // rendering `{header}` shows this header row. The `sortedCols` array gets mutated in this loop,
    // acquiring a `query` property in each of its objects that gets used later to generate cell
    // hrefs.

    // add selected filters to column header links
    let selectedFilters = '';
    if (stageFilter) {
        stageFilter.forEach((f) => {
            if (['adult', 'postnatal', 'embryo'].includes(f)) {
                selectedFilters += `replicates.library.biosample.life_stage=${f === 'embroyo' ? 'embryonic' : f}&`;
            } else {
                const stageTerm = f.split(' ')[0] === 'embryo' ? 'embryonic' : f.split(' ')[0];
                const ageTerm = f.split(' ').slice(1).join(' ');
                selectedFilters += `replicates.library.biosample.life_stage=${stageTerm}&`;
                selectedFilters += `replicates.library.biosample.age_display=${ageTerm}&`;
            }
        });
        selectedFilters = selectedFilters.substring(0, selectedFilters.length - 1);
    }

    const header = [{ header: null }].concat(sortedCols.map((colInfo) => {
        const categoryQuery = `${COL_CATEGORY}=${encoding.encodedURIComponent(colInfo.category)}`;
        if (!colInfo.subcategory) {
            // Add the category column links.
            colInfo.query = categoryQuery;
            return { header: <a href={`${context.search_base}&${categoryQuery}&${selectedFilters}`}>{colInfo.category}</a> };
        }

        // Add the subcategory column links.
        const subCategoryQuery = `${COL_SUBCATEGORY}=${encoding.encodedURIComponent(colInfo.subcategory)}`;
        colInfo.query = `${categoryQuery}&${subCategoryQuery}`;
        return { header: <a className="sub" href={`${context.search_base}&${categoryQuery}&${subCategoryQuery}&${selectedFilters}`}>{colInfo.subcategory} {colInfo.category.replace('Histone ', '')}</a> };
    }));

    let dataTableCount = 0;
    newRowCategoryData.forEach((rowCategoryBucket) => {
        const rowSubcategoryBuckets = rowCategoryBucket[rowSubcategory].buckets;
        const subCategorySums = analyzeSubCategoryData(rowSubcategoryBuckets, COL_CATEGORY, colMap, colCount, stageFilter);
        dataTableCount += subCategorySums.reduce((a, b) => a + b);
    });

    // Generate the main table content including the data hierarchy, where the upper level of the
    // hierarchy gets referred to here as "rowCategory" and the lower-level gets referred to as
    // "rowSubcategory." Both these types of rows get collected into `dataTable` which gets passed
    // to <DataTable>. Also generate an array of React keys to use with <DataMatrix> by using an
    // array index that's independent of the reduce-loop index because of spacer/expander row
    // insertion.
    const dataTable = newRowCategoryData.reduce((accumulatingTable, rowCategoryBucket) => {
        // Each loop iteration generates one biosample classification row as well as the rows of
        // biosample term names under it.
        let rowCategoryColor = '#2E4057'; // mouseMatrixColors[rowCategoryBucket.key];
        if (!rowCategoryColor) {
            rowCategoryColor = '#f2f2f2';
        }
        const zeroRowColor = '#C5C3C6';
        const rowSubcategoryColor = tintColor(rowCategoryColor, 0.5);
        const rowCategoryTextColor = isLight(rowCategoryColor) ? '#000' : '#fff';
        const zeroRowTextColor = isLight(zeroRowColor) ? '#000' : '#fff';
        const rowSubcategoryBuckets = rowCategoryBucket[rowSubcategory].buckets;
        const expandableRowCategory = false;
        const rowCategoryQuery = `${ROW_CATEGORY}=${encoding.encodedURIComponent(rowCategoryBucket.key)}`;

        const subCategorySums = analyzeSubCategoryData(rowSubcategoryBuckets, COL_CATEGORY, colMap, colCount, stageFilter);

        // Update the row key mechanism.
        rowKeys[matrixRow] = rowCategoryBucket.key;
        matrixRow += 1;

        const mappedRowCategoryQuery = mapRowCategoryQueries(rowCategory, rowCategoryBucket);

        // Get the list of subcategory names, or the first items of the list if the category isn't
        // expanded.
        const categoryExpanded = expandedRowCategories.indexOf(rowCategoryBucket.key) !== -1;
        const visibleRowSubcategoryBuckets = rowSubcategoryBuckets;

        // filter rows if needed
        let filteredRowSubcategoryBuckets = [];
        if (stageFilter) {
            filteredRowSubcategoryBuckets = visibleRowSubcategoryBuckets.filter((bucket) => {
                let success = null;
                stageFilter.forEach((singleFilter) => {
                    const filterString = singleFilter.replace(/[()]/g, '');
                    const bucketString = bucket.key.replace(/[()]/g, '');
                    if (bucketString.includes(filterString)) {
                        success = bucket;
                    }
                });
                return success;
            });
        } else {
            filteredRowSubcategoryBuckets = visibleRowSubcategoryBuckets;
        }

        const categoryNameQuery = encoding.encodedURIComponent(rowCategoryBucket.key);

        // Generate one classification's rows of term names.
        const cells = Array(colCount);
        const subcategoryRows = filteredRowSubcategoryBuckets.map((rowSubcategoryBucket) => {
            const maleSubcategoryBucketKey = `${rowSubcategoryBucket.key.split(rowCategoryBucket.key)[0]}${categoryNameQuery} male${rowSubcategoryBucket.key.split(rowCategoryBucket.key)[1]}`;
            const femaleSubcategoryBucketKey = `${rowSubcategoryBucket.key.split(rowCategoryBucket.key)[0]}${categoryNameQuery} female${rowSubcategoryBucket.key.split(rowCategoryBucket.key)[1]}`;
            const subCategoryQuery = `${ROW_SUBCATEGORY}=${encoding.encodedURIComponent(rowSubcategoryBucket.key)}&${ROW_SUBCATEGORY}=${encoding.encodedURIComponent(maleSubcategoryBucketKey)}&${ROW_SUBCATEGORY}=${encoding.encodedURIComponent(femaleSubcategoryBucketKey)}`;

            // Generate an array of data cells for a single term-name row.
            cells.fill(null);
            rowSubcategoryBucket[colCategory].buckets.forEach((rowSubcategoryColCategoryBucket) => {
                // Skip any excluded assay columns.
                if (!excludedAssays.includes(rowSubcategoryColCategoryBucket.key) && rowSubcategoryColCategoryBucket[colSubcategory]) {
                    const rowSubcategoryColSubcategoryBuckets = rowSubcategoryColCategoryBucket[colSubcategory].buckets;
                    if (rowSubcategoryColSubcategoryBuckets.length > 0 && !collapsedAssays.includes(rowSubcategoryColCategoryBucket.key)) {
                        // The assay has targets and doesn't collapse them, so put relevant colored
                        // cells in the subcategory columns. Each cell has no visible content, but
                        // has hidden text for screen readers.
                        rowSubcategoryColSubcategoryBuckets.forEach((cellData) => {
                            const colMapKey = `${rowSubcategoryColCategoryBucket.key}|${cellData.key}`;
                            const colIndex = colMap[colMapKey].col;
                            cells[colIndex] = {
                                content: (
                                    <React.Fragment>
                                        <a href={`${context.search_base}&${rowCategoryQuery}&${subCategoryQuery}&${colMap[colMapKey].query}`} style={{ color: rowCategoryTextColor }}>
                                            <span className="sr-only">Search {rowCategoryBucket.key}, {rowSubcategoryBucket.key} for {rowSubcategoryColCategoryBucket.key}, {cellData.key}</span>
                                        </a>
                                    </React.Fragment>
                                ),
                                style: { backgroundColor: rowSubcategoryColor },
                            };
                        });
                    } else {
                        // The assay does not have targets, or it does but collapses them, so just
                        // add a colored cell for the column category.
                        const colIndex = colMap[rowSubcategoryColCategoryBucket.key].col;
                        cells[colIndex] = {
                            content: (
                                <React.Fragment>
                                    <a href={`${context.search_base}&${rowCategoryQuery}&${subCategoryQuery}&${colMap[rowSubcategoryColCategoryBucket.key].query}`} style={{ color: rowCategoryTextColor }}>
                                        <span className="sr-only">Search {rowCategoryBucket.key}, {rowSubcategoryBucket.key} for {rowSubcategoryColCategoryBucket.key}</span>
                                    </a>
                                </React.Fragment>
                            ),
                            style: { backgroundColor: rowSubcategoryColor },
                        };
                    }
                }
            });

            // Show assay columns as disabled (i.e. nothing to see here) if those columns have
            // target columns.
            colCategoriesWithSubcategories.forEach((colCategoryName) => {
                cells[colMap[colCategoryName].col] = { css: 'matrix__disabled-cell' };
            });

            // Add a single term-name row's data and left header to the matrix.
            rowKeys[matrixRow] = `${rowCategoryBucket.key}|${rowSubcategoryBucket.key}`;
            matrixRow += 1;
            const newLabel = parseString(rowSubcategoryBucket.key, rowCategoryBucket.key);
            const labelStage = newLabel.split(' (')[0];
            const labelLength = newLabel.split('(')[1].slice(0, -1);
            return {
                rowContent: [
                    {
                        header: (
                            <a
                                href={`${context.search_base}&${rowCategoryQuery}&${subCategoryQuery}`}
                                className={`label-stage ${labelStage}`}
                            >
                                <div className="subcategory-row-text-mouse">
                                    <div className="label-stage">{labelStage}</div>
                                    <div className="label-length">{labelLength}</div>
                                </div>
                            </a>
                        ),
                    },
                ].concat(cells),
                css: 'matrix__row-data',
            };
        });

        // Generate a row for a rowCategory alone, concatenated with the subCategory rows under it,
        // concatenated with an spacer row that might be empty or might have a rowCategory expander
        // button.
        rowKeys[matrixRow] = `${rowCategoryBucket.key}-spacer`;
        matrixRow += 1;
        const rowSum = subCategorySums.reduce((a, b) => a + b);
        return accumulatingTable.concat(
            [
                {
                    rowContent: [{
                        header: (
                            <div id={globals.sanitizeId(rowCategoryBucket.key)} style={{ backgroundColor: (rowSum > 0) ? rowCategoryColor : zeroRowColor }}>
                                {expandableRowCategory ?
                                    <RowCategoryExpander
                                        categoryId={rowCategoryBucket.key}
                                        categoryName={rowCategoryBucket.key}
                                        expanderColor={rowCategoryTextColor}
                                        expanded={categoryExpanded}
                                        expanderClickHandler={expanderClickHandler}
                                    />
                                : null}
                                <div style={{ color: (rowSum > 0) ? rowCategoryTextColor : zeroRowTextColor }} id={categoryNameQuery}>{rowCategoryNames[rowCategoryBucket.key]}</div>
                            </div>
                        ),
                    }].concat(subCategorySums.map((subCategorySum, subCategorySumIndex) => ({
                        content: (
                            subCategorySum > 0 ?
                                <a style={{ backgroundColor: (rowSum > 0) ? rowCategoryColor : zeroRowColor, color: rowCategoryTextColor }} href={`${context.search_base}&${mappedRowCategoryQuery}&${!(colCategoryNames[subCategorySumIndex].includes('|')) ? `${COL_CATEGORY}=${encoding.encodedURIComponent(colCategoryNames[subCategorySumIndex])}` : `${COL_SUBCATEGORY}=${encoding.encodedURIComponent(colCategoryNames[subCategorySumIndex].split('|')[1])}`}`}>
                                    {subCategorySum}
                                </a>
                            :
                                <div style={{ backgroundColor: (rowSum > 0) ? rowCategoryColor : zeroRowColor }} />
                        ),
                    }))),
                    css: 'matrix__row-category',
                },
            ],
            subcategoryRows,
            [{
                rowContent: [
                    {
                        content: (
                            expandableRowCategory ?
                                <RowCategoryExpander
                                    categoryId={colCategoriesWithSubcategories}
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
    return { dataTable, rowKeys, dataTableCount };
};


/**
 * Render the area above the facets and matrix content.
 */
const MatrixHeader = ({ context }) => (
    <div className="matrix-header">
        <div className="matrix-header__title">
            <h1>{context.title}</h1>
            <div className="matrix-tags">
                <MatrixInternalTags context={context} />
                <div className="matrix-description">
                    The mouse development matrix displays embryonic to postnatal mouse developmental time course data across several tissues organized as reference epigenomes.
                </div>
            </div>
        </div>
    </div>
);

MatrixHeader.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};

const MouseStageButton = (props) => {
    const { keyWord, idString, activeClass, onClick, buttonWidth } = props;
    const newIdString = idString.replace(/\s+/g, '-');
    return (
        <button
            id={newIdString}
            className={`legend-option ${idString} ${newIdString} ${activeClass ? 'active' : ''}`}
            onClick={onClick}
            style={{ width: `${buttonWidth}px` }}
        >
            {keyWord.replace('days', 'd')}
        </button>
    );
};

MouseStageButton.propTypes = {
    keyWord: PropTypes.string.isRequired,
    idString: PropTypes.string.isRequired,
    activeClass: PropTypes.bool.isRequired,
    onClick: PropTypes.func.isRequired,
    buttonWidth: PropTypes.number.isRequired,
};


/**
 * Display the matrix and associated controls above them.
 */
class MatrixPresentation extends React.Component {
    constructor(props) {
        super(props);

        this.parsedUrl = url.parse(props.context['@id']);
        this.query = new QueryString(this.parsedUrl.query);
        this.getQueryValues = this.getQueryValues.bind(this);

        // Determine whether biosample classifications have been specified in the query string to
        // determine which matrix row sections to initially expand.
        const requestedClassifications = this.getQueryValues(ROW_CATEGORY);

        // Gather the biosample classifications actually in the data and filter the requested
        // classifications down to the actual data.
        const classificationBuckets = props.context.matrix.y[props.context.matrix.y.group_by[0]].buckets;
        const actualClassifications = classificationBuckets.map(bucket => bucket.key);
        const filteredClassifications = requestedClassifications.filter(classification => actualClassifications.includes(classification));

        this.state = {
            /** Categories the user has expanded */
            expandedRowCategories: filteredClassifications,
            /** True if matrix scrolled all the way to the right; used for flashing arrow */
            scrolledRight: false,
            /** User selected mouse stage or age */
            developmentStageClick: [],
            /** Window width, used to determine how many colummns to display */
            windowWidth: 0,
        };
        this.expanderClickHandler = this.expanderClickHandler.bind(this);
        this.handleOnScroll = this.handleOnScroll.bind(this);
        this.handleScrollIndicator = this.handleScrollIndicator.bind(this);
        this.selectMouseDevelopmentStage = this.selectMouseDevelopmentStage.bind(this);
        this.hasRequestedClassifications = filteredClassifications.length > 0;
        this.clearFilters = this.clearFilters.bind(this);
        this.updateWindowWidth = this.updateWindowWidth.bind(this);
    }

    componentDidMount() {
        this.handleScrollIndicator(this.scrollElement);
        this.updateWindowWidth();
        window.addEventListener('resize', this.updateWindowWidth);
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
     * Get an array of all values in the current query string corresponding to the given `key`.
     * @param {string} key Query string key whose values this retrieves.
     *
     * @return {array} Values for each occurence of `key` in the query string.
     */
    getQueryValues(key) {
        return this.query.getKeyValues(key);
    }

    updateWindowWidth() {
        this.setState({
            windowWidth: Math.min(screen.width, window.innerWidth),
        });
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

    selectMouseDevelopmentStage(e) {
        const targetId = e.target.id.replace(/-/g, ' ');
        // selected something that was already selected so just de-select
        if (this.state.developmentStageClick.indexOf(targetId) > -1) {
            const newSelections = this.state.developmentStageClick.filter(stage => stage !== targetId);
            this.setState({ developmentStageClick: newSelections });
        // selected a particular age so need to disable the stage
        } else if (targetId.split(' ').length > 1) {
            let newSelections = [];
            if (targetId.includes('embryo')) {
                newSelections = this.state.developmentStageClick.filter(stage => stage !== 'embryo');
            } else if (targetId.includes('postnatal')) {
                newSelections = this.state.developmentStageClick.filter(stage => stage !== 'postnatal');
            } else {
                newSelections = this.state.developmentStageClick.filter(stage => stage !== 'adult');
            }
            newSelections = [...newSelections, targetId];
            this.setState({ developmentStageClick: newSelections });
        // selected a stage but there are also ages selected so disable those
        } else if (targetId === 'embryo') {
            let newSelections = this.state.developmentStageClick.filter(stage => (!(stage.includes('embryo') && (stage.split(' ').length > 1))));
            newSelections = [...newSelections, targetId];
            this.setState({ developmentStageClick: newSelections });
        } else if (targetId === 'postnatal') {
            let newSelections = this.state.developmentStageClick.filter(stage => (!(stage.includes('postnatal') && (stage.split(' ').length > 1))));
            newSelections = [...newSelections, targetId];
            this.setState({ developmentStageClick: newSelections });
        } else {
            let newSelections = this.state.developmentStageClick.filter(stage => (!(stage.includes('adult') && (stage.split(' ').length > 1))));
            newSelections = [...newSelections, targetId];
            this.setState({ developmentStageClick: newSelections });
        }
    }

    clearFilters() {
        // reset button selections
        this.setState({ developmentStageClick: [] });
        const currentUrl = this.props.context['@id'];
        // if user has entered a search, refresh page with no search term
        if (currentUrl.includes('searchTerm=')) {
            const parsedUrl = url.parse(this.props.context['@id']);
            const query = new QueryString(parsedUrl.query);
            query.deleteKeyValue('searchTerm');
            parsedUrl.search = null;
            parsedUrl.query = null;
            const baseMatrixUrl = url.format(parsedUrl);
            const newUrl = `${baseMatrixUrl}?${query.format()}`;
            this.context.navigate(newUrl);
        }
    }

    render() {
        const { context, rowCategoryGetter, mapRowCategoryQueries } = this.props;
        const { scrolledRight } = this.state;

        // Apply filter from buttons
        let stageFilter = null;
        if (this.state.developmentStageClick.length > 0) {
            stageFilter = this.state.developmentStageClick;
        }

        // Convert matrix data to a DataTable object.
        const { dataTable, rowKeys } = convertExperimentToDataTable(context, rowCategoryGetter, mapRowCategoryQueries, this.state.expandedRowCategories, this.expanderClickHandler, stageFilter);
        // If we have a wide window, split the table in two
        let matrixConfig;
        let matrixConfig2;
        if (this.state.windowWidth > 1160) {
            // Determining best index for splitting the matrix
            const spacerRowIndices = dataTable.map((d, i) => (d.css === 'matrix__row-spacer' ? i : '')).filter(String);
            const distanceFromCenter = spacerRowIndices.map(d => Math.abs(d - (dataTable.length / 2)));
            const bestCenter = spacerRowIndices[distanceFromCenter.findIndex(d => d === Math.min(...distanceFromCenter))];
            matrixConfig = {
                rows: dataTable.slice(0, bestCenter),
                rowKeys,
                tableCss: 'matrix',
            };
            matrixConfig2 = {
                rows: [dataTable[0], ...dataTable.slice(bestCenter, dataTable.length)],
                rowKeys,
                tableCss: 'matrix',
            };
        // If we have a narrow window, do not split the table into two
        } else {
            matrixConfig = {
                rows: dataTable,
                rowKeys,
                tableCss: 'matrix',
            };
        }

        const visualizeDisabledTitle = context.total > MATRIX_VISUALIZE_LIMIT ? `Filter to ${MATRIX_VISUALIZE_LIMIT} to visualize` : '';

        const parsedUrl = url.parse(context['@id'], true);
        parsedUrl.query.format = 'json';
        parsedUrl.search = '';

        const rowCategory = context.matrix.y.group_by[0];
        const rowCategoryData = context.matrix.y[rowCategory].buckets;
        const mouseAgeFullArray = [];
        rowCategoryData.forEach((datum) => {
            datum.biosample_summary.buckets.forEach((bucket) => {
                mouseAgeFullArray.push(parseString(bucket.key, datum.key).replace('male ', '').replace('female ', ''));
            });
        });
        mouseAgeFullArray.sort(sortMouseArray);
        const uniqueAgeArray = [...new Set(mouseAgeFullArray)];
        const mouseAgeObject = {
            embryo: uniqueAgeArray.filter(age => age.includes('embryo')).map(age => age.replace('embryo (', '').replace(')', '')),
            postnatal: uniqueAgeArray.filter(age => age.includes('postnatal')).map(age => age.replace('postnatal (', '').replace(')', '')),
            adult: uniqueAgeArray.filter(age => age.includes('adult')).map(age => age.replace('adult (', '').replace(')', '')),
        };
        const embryoDefault = 50;
        const defaultWidth = 75;
        const embryoWidth = (mouseAgeObject.embryo.length * (embryoDefault + 2)) - 2;
        const postnatalWidth = (mouseAgeObject.postnatal.length * (defaultWidth + 2)) - 2;
        const adultWidth = (mouseAgeObject.adult.length * (defaultWidth + 2)) - 2;

        // check if embryo width is greater than window width and if so, split in two
        let embryoSplitRows = false;
        let embryoFirstRowWidth = 0;
        let embryoSecondRowWidth = 0;
        let countEmbryoFirstRow;
        let countEmbryoSecondRow;
        let embryoFirstRow;
        let embryoSecondRow;
        // 40 is container padding
        if ((embryoWidth + 40) > this.state.windowWidth) {
            embryoSplitRows = true;
            countEmbryoFirstRow = Math.floor((this.state.windowWidth - 40) / (embryoDefault + 2));
            embryoFirstRow = mouseAgeObject.embryo.slice(0, countEmbryoFirstRow);
            embryoFirstRowWidth = (countEmbryoFirstRow * (embryoDefault + 2)) - 2;
            countEmbryoSecondRow = mouseAgeObject.embryo.length - countEmbryoFirstRow;
            embryoSecondRow = mouseAgeObject.embryo.slice(countEmbryoFirstRow, mouseAgeObject.embryo.length);
            embryoSecondRowWidth = (countEmbryoSecondRow * (embryoDefault + 2)) - 2;
        }

        // Calculate additional filters for the to view control button links
        const additionalFilters = [];
        this.state.developmentStageClick.forEach((f) => {
            if (['adult', 'postnatal', 'embryo'].includes(f)) {
                const stageTerm = f === 'embryo' ? 'embryonic' : f;
                const stageFilterExists = additionalFilters.filter(f2 => f2.term === stageTerm).length > 0;
                if (!stageFilterExists) {
                    additionalFilters.push({
                        term: f === 'embryo' ? 'embryonic' : f,
                        remove: '',
                        field: 'replicates.library.biosample.life_stage',
                    });
                }
            } else {
                const stageTerm = f.split(' ')[0] === 'embryo' ? 'embryonic' : f.split(' ')[0];
                const ageTerm = f.split(' ').slice(1).join(' ');
                const stageFilterExists = additionalFilters.filter(f2 => f2.term === stageTerm).length > 0;
                const ageFilterExists = additionalFilters.filter(f2 => f2.term === ageTerm).length > 0;
                if (!stageFilterExists) {
                    additionalFilters.push({
                        term: stageTerm,
                        remove: '',
                        field: 'replicates.library.biosample.life_stage',
                    });
                }
                if (!ageFilterExists) {
                    additionalFilters.push({
                        term: ageTerm,
                        remove: '',
                        field: 'replicates.library.biosample.age_display',
                    });
                }
            }
        });

        return (
            <React.Fragment>
                <div className="matrix-header">
                    <SearchControls context={context} visualizeDisabledTitle={visualizeDisabledTitle} additionalFilters={additionalFilters} />
                    <div className="matrix-header__controls">
                        <div className="matrix-header__filter-controls">
                            <div className="mouse-dev-legend">
                                <p>Select mouse development stages to filter results:</p>
                                <div className="outer-button-container">
                                    {embryoSplitRows ?
                                        <React.Fragment>
                                            <div className="stage-container">
                                                <MouseStageButton
                                                    keyWord={'embryo'}
                                                    idString={'embryo'}
                                                    activeClass={this.state.developmentStageClick.indexOf('embryo') > -1}
                                                    onClick={e => this.selectMouseDevelopmentStage(e)}
                                                    buttonWidth={embryoFirstRowWidth}
                                                />
                                                <div className="age-container">
                                                    {embryoFirstRow.map(age => <MouseStageButton keyWord={age} idString={`embryo ${age}`} activeClass={(this.state.developmentStageClick.indexOf(`embryo ${age}`) > -1) || (this.state.developmentStageClick.indexOf('embryo') > -1)} onClick={e => this.selectMouseDevelopmentStage(e)} buttonWidth={embryoDefault} key={`embryo ${age}`} />)}
                                                </div>
                                            </div>
                                            <div className="stage-container">
                                                <MouseStageButton
                                                    keyWord={'embryo'}
                                                    idString={'embryo'}
                                                    activeClass={this.state.developmentStageClick.indexOf('embryo') > -1}
                                                    onClick={e => this.selectMouseDevelopmentStage(e)}
                                                    buttonWidth={embryoSecondRowWidth}
                                                />
                                                <div className="age-container">
                                                    {embryoSecondRow.map(age => <MouseStageButton keyWord={age} idString={`embryo ${age}`} activeClass={(this.state.developmentStageClick.indexOf(`embryo ${age}`) > -1) || (this.state.developmentStageClick.indexOf('embryo') > -1)} onClick={e => this.selectMouseDevelopmentStage(e)} buttonWidth={embryoDefault} key={`embryo ${age}`} />)}
                                                </div>
                                            </div>
                                        </React.Fragment>
                                    :
                                        <div className="stage-container">
                                            <MouseStageButton
                                                keyWord={'embryo'}
                                                idString={'embryo'}
                                                activeClass={this.state.developmentStageClick.indexOf('embryo') > -1}
                                                onClick={e => this.selectMouseDevelopmentStage(e)}
                                                buttonWidth={embryoWidth}
                                            />
                                            <div className="age-container">
                                                {mouseAgeObject.embryo.map(age => <MouseStageButton keyWord={age} idString={`embryo ${age}`} activeClass={(this.state.developmentStageClick.indexOf(`embryo ${age}`) > -1) || (this.state.developmentStageClick.indexOf('embryo') > -1)} onClick={e => this.selectMouseDevelopmentStage(e)} buttonWidth={embryoDefault} key={`embryo ${age}`} />)}
                                            </div>
                                        </div>
                                    }
                                    <div className="stage-container">
                                        <MouseStageButton
                                            keyWord={'postnatal'}
                                            idString={'postnatal'}
                                            activeClass={this.state.developmentStageClick.indexOf('postnatal') > -1}
                                            onClick={e => this.selectMouseDevelopmentStage(e)}
                                            buttonWidth={postnatalWidth}
                                        />
                                        <div className="age-container">
                                            {mouseAgeObject.postnatal.map(age => <MouseStageButton keyWord={age} idString={`postnatal ${age}`} activeClass={(this.state.developmentStageClick.indexOf(`postnatal ${age}`) > -1) || (this.state.developmentStageClick.indexOf('postnatal') > -1)} onClick={e => this.selectMouseDevelopmentStage(e)} buttonWidth={defaultWidth} key={`postnatal ${age}`} />)}
                                        </div>
                                    </div>
                                    <div className="stage-container">
                                        <MouseStageButton
                                            keyWord={'adult'}
                                            idString={'adult'}
                                            activeClass={this.state.developmentStageClick.indexOf('adult') > -1}
                                            onClick={e => this.selectMouseDevelopmentStage(e)}
                                            buttonWidth={adultWidth}
                                        />
                                        <div className="age-container">
                                            {mouseAgeObject.adult.map(age => <MouseStageButton keyWord={age} idString={`adult ${age}`} activeClass={(this.state.developmentStageClick.indexOf(`adult ${age}`) > -1) || (this.state.developmentStageClick.indexOf('adult') > -1)} onClick={e => this.selectMouseDevelopmentStage(e)} buttonWidth={defaultWidth} key={`adult ${age}`} />)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <button className="clear-filters" onClick={this.clearFilters} >Clear Filters <i className="icon icon-times-circle" aria-label="Clear search terms and selected mouse development stages and ages" /></button>
                        </div>
                    </div>
                </div>
                <div className="matrix__presentation mouse-dev-matrix">
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
                        {matrixConfig2 ?
                            <div className="matrix__data-wrapper">
                                <div className="matrix__data" onScroll={this.handleOnScroll} ref={(element) => { this.scrollElement = element; }}>
                                    <DataTable tableData={matrixConfig2} />
                                </div>
                            </div>
                        : null}
                    </div>
                </div>
            </React.Fragment>
        );
    }
}

MatrixPresentation.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
    /** Callback to retrieve row categories */
    rowCategoryGetter: PropTypes.func.isRequired,
    /** Callback to map row category query values */
    mapRowCategoryQueries: PropTypes.func.isRequired,
};

MatrixPresentation.contextTypes = {
    navigate: PropTypes.func,
};


/**
 * Render the vertical facets and the matrix itself.
 */
const MatrixContent = ({ context, rowCategoryGetter, mapRowCategoryQueries }) => (
    <div className="matrix__content">
        <MatrixPresentation context={context} rowCategoryGetter={rowCategoryGetter} mapRowCategoryQueries={mapRowCategoryQueries} />
    </div>
);

MatrixContent.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
    /** Callback to retrieve row categories from matrix data */
    rowCategoryGetter: PropTypes.func.isRequired,
    /** Callback to map row category query values */
    mapRowCategoryQueries: PropTypes.func.isRequired,
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
    `${rowCategory}=${encoding.encodedURIComponent(rowCategoryBucket.key)}`
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
    `${subCategory}=${encoding.encodedURIComponent(subCategoryQuery)}`
);


/**
 * View component for the experiment matrix page.
 */
class MouseDevelopmentMatrix extends React.Component {
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
        const rowCategoryNames = {};
        rowCategoryData.forEach((datum) => {
            rowCategoryNames[datum.key] = datum.key;
        });
        return {
            rowCategoryData,
            mouseMatrixColors,
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

MouseDevelopmentMatrix.propTypes = {
    context: PropTypes.object.isRequired,
};

MouseDevelopmentMatrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
};

globals.contentViews.register(MouseDevelopmentMatrix, 'MouseDevelopmentMatrix');
