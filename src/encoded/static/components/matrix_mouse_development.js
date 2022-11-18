import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import * as encoding from '../libs/query_encoding';
import QueryString from '../libs/query_string';
import { Panel, PanelBody } from '../libs/ui/panel';
import { svgIcon } from '../libs/svg-icons';
import { tintColor, isLight } from './datacolors';
import { DataTable } from './datatable';
import * as globals from './globals';
import matrixAssaySortOrder from './matrix_reference_epigenome';
import { MatrixBadges } from './objectutils';
import { SearchControls } from './search';


/**
 * Number of subcategory items to show when subcategory isn't expanded.
 * @constant
 */
const ROW_CATEGORY = 'biosample_ontology.term_name';
const ROW_SUBCATEGORY = 'life_stage_age';
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
 * Increment subCategorySums value for bucket keys matching a column name
 */
function updateColumnCount(value, colMap, subCategorySums) {
    let colIndex = 0;
    if (value && value['target.label'] && value['target.label'].buckets.length >= 1) {
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
  * Collect column counts to display on headers. Counts reflect the number of rows which contain
  * data per column, not the number of experiments per column.
  * @param {array}  subCategoryData Array of subcategory objects, each containing an array of data
  * @param {string} columnCategory Column headers variable
  * @param {object} colMap Keyed column header information
  * @param {number} colCount Number of columns
  * @param {array} stageFilter Stage/age filters selected by user
  *
  * @return {array}   subCategorySums Counts per column
  */
const analyzeSubCategoryData = (subCategoryData, columnCategory, colMap, colCount, stageFilter) => {
    let subCategorySums = Array(colCount).fill(0);
    subCategoryData.forEach((rowData) => {
        // `rowData` has all the data for one row. Collect sums of all data for each column.
        const allowedRowDataBuckets = rowData[columnCategory].buckets.filter((bucket) => (
            !excludedAssays.includes(bucket.key)
        ));
        allowedRowDataBuckets.forEach((value) => {
            if (stageFilter) {
                stageFilter.forEach((singleFilter) => {
                    if (!singleFilter || rowData.key.includes(singleFilter)) {
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

/**
 * Convert an array of ages with units into an array of normalized ages where each array element is
 * an object with this form:
 * {
 *   stage: life stage, one of 'embryonic', 'postnatal', 'adult'
 *   min: <minimum age of a range in days>,
 *   max: <maximum age of a range in days; same as min if single value>,
 *   original: <original age string>,
 * }
 * @param {array} ages Age strings with a mix of units, e.g. ['1 week', '2 weeks', '3 days', '4 days']
 * @returns {array} Normalized age objects
 */
const normalizeAges = (ages) => (
    ages.map((age) => {
        let min;
        let max;
        const [stage, value, units] = age.split(' ');

        // Get numeric age or age range.
        if (value.includes('-')) {
            // Age range.
            const [minString, maxString] = value.split('-');
            min = Number(minString);
            max = Number(maxString);
        } else {
            // Single age.
            min = Number(value);
            max = min;
        }

        // Convert age to days.
        if (units === 'weeks' || units === 'week') {
            min *= 7;
            max *= 7;
        } else if (units === 'months' || units === 'month') {
            min *= 30;
            max *= 30;
        } else if (units === 'years' || units === 'year') {
            min *= 365;
            max *= 365;
        }

        return {
            stage,
            min,
            max,
            original: age,
        };
    })
);

/**
 * Sorting iteratee function for sorting an array of normalized age objects. If the age contains a
 * range, the minimum age gets emphasized, and the maximum age gets added as a fractionalized
 * tiebreaker.
 * @param {object} normalizedAge Normalized age object
 * @returns {number} Sorting value for underscore
 */
const stageMap = ['embryonic', 'postnatal', 'adult'];
const normalizedAgeIteratee = (normalizedAge) => {
    let ageSortValue;
    if (normalizedAge.min === normalizedAge.max) {
        ageSortValue = normalizedAge.min;
    } else {
        ageSortValue = normalizedAge.min + (normalizedAge.max / 100);
    }

    // Sort age ranges by emphasizing the minimum age, and adding a fractionalized maximum age as
    // a tiebreaker. Factor in the stage as the primary sort key.
    return (stageMap.indexOf(normalizedAge.stage) * 10000) + ageSortValue;
};

/**
 * Generate object listing all ages corresponding to a mouse stage based on rowCategoryData.
 */
const getMouseAgeObject = (rowCategoryData) => {
    const mouseAgeFullArray = [];
    rowCategoryData.forEach((datum) => {
        datum.life_stage_age.buckets.forEach((bucket) => {
            mouseAgeFullArray.push(bucket.key);
        });
    });
    const uniqueAgeArray = [...new Set(mouseAgeFullArray)];
    let embryonic = uniqueAgeArray.filter((age) => age.includes('embryonic'));
    let postnatal = uniqueAgeArray.filter((age) => age.includes('postnatal'));
    let adult = uniqueAgeArray.filter((age) => age.includes('adult'));
    embryonic = _(normalizeAges(embryonic)).sortBy(normalizedAgeIteratee);
    postnatal = _(normalizeAges(postnatal)).sortBy(normalizedAgeIteratee);
    adult = _(normalizeAges(adult)).sortBy(normalizedAgeIteratee);
    return {
        embryonic: embryonic.map((normalized) => normalized.original),
        postnatal: postnatal.map((normalized) => normalized.original),
        adult: adult.map((normalized) => normalized.original),
    };
};

/**
 * Convert array of filters into search query. For life stage filters, we must append search terms
 * for all corresponding ages.
 * @param {array} stageFilter Array of life stage and age filters
 * @param {object} mouseAgeObject Lists all ages corresponding to a life stage
 * @param {string} searchQuery Search query string corresponding to selected filters
 */
const generateFilterQuery = (stageFilter, mouseAgeObject) => {
    let selectedFilters = '';
    if (stageFilter) {
        stageFilter.forEach((stage) => {
            if (['adult', 'postnatal', 'embryonic'].includes(stage)) {
                mouseAgeObject[stage].forEach((mouseAge) => {
                    selectedFilters += `life_stage_age=${stage}${mouseAge}&`;
                });
            } else {
                selectedFilters += `life_stage_age=${stage}&`;
            }
        });
        selectedFilters = selectedFilters.substring(0, selectedFilters.length - 1);
    }
    return selectedFilters;
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
    const sortedCols = Object.keys(colMap).map((assayColKey) => colMap[assayColKey]).sort((colInfoA, colInfoB) => colInfoA.col - colInfoB.col);

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
    const colCategoriesWithSubcategories = Object.keys(colMap).filter((colCategoryName) => colMap[colCategoryName].hasSubcategories && !collapsedAssays.includes(colCategoryName));

    const { rowCategoryData, rowCategoryNames } = getRowCategories();
    const rowKeys = ['column-categories'];

    // loop through row data to sort buckets by sorted mouse stage/age
    const newRowCategoryData = JSON.parse(JSON.stringify(rowCategoryData));
    rowCategoryData.forEach((row, rowIdx) => {
        let rowAgeArray = [];
        row.life_stage_age.buckets.forEach((bucket) => {
            rowAgeArray.push(bucket.key);
        });

        // Sort rows by stage and then age, then convert back to the original age string.
        rowAgeArray = _(normalizeAges(rowAgeArray)).sortBy(normalizedAgeIteratee);
        rowAgeArray = rowAgeArray.map((normalizedAge) => normalizedAge.original);

        const newBuckets = [];
        rowAgeArray.forEach((age) => {
            row.life_stage_age.buckets.forEach((bucket, idx) => {
                const ageKey = bucket.key;
                if (age === ageKey) {
                    newBuckets.push(row.life_stage_age.buckets[idx]);
                }
            });
        });
        newRowCategoryData[rowIdx].life_stage_age.buckets = newBuckets;
    });

    let matrixRow = 1;

    // Generate the hierarchical top-row sideways header label cells. The first cell is null unless
    // it contains a link to clear the currently selected classification. At the end of this loop,
    // rendering `{header}` shows this header row. The `sortedCols` array gets mutated in this loop,
    // acquiring a `query` property in each of its objects that gets used later to generate cell
    // hrefs.

    // add selected filters to column header links
    const mouseAgeObject = getMouseAgeObject(rowCategoryData);
    const selectedFilters = generateFilterQuery(stageFilter, mouseAgeObject);

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
        return {
            header: (
                <a
                    className="sub"
                    href={`${context.search_base}&${categoryQuery}&${subCategoryQuery}&${selectedFilters}`}
                >
                    {colInfo.subcategory} {colInfo.category.replace('Histone ', '')}
                </a>
            ),
        };
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
        const rowCategoryQuery = `${ROW_CATEGORY}=${encoding.encodedURIComponent(rowCategoryBucket.key)}`;

        const subCategorySums = analyzeSubCategoryData(rowSubcategoryBuckets, COL_CATEGORY, colMap, colCount, stageFilter);

        // Update the row key mechanism.
        rowKeys[matrixRow] = rowCategoryBucket.key;
        matrixRow += 1;

        const mappedRowCategoryQuery = mapRowCategoryQueries(rowCategory, rowCategoryBucket);

        // filter rows if needed
        let filteredRowSubcategoryBuckets = [];
        if (stageFilter) {
            filteredRowSubcategoryBuckets = rowSubcategoryBuckets.filter((bucket) => {
                let success = null;
                stageFilter.forEach((singleFilter) => {
                    if (bucket.key.includes(singleFilter)) {
                        success = bucket;
                    }
                });
                return success;
            });
        } else {
            filteredRowSubcategoryBuckets = rowSubcategoryBuckets;
        }

        const categoryNameQuery = encoding.encodedURIComponent(rowCategoryBucket.key);

        // Generate one classification's rows of term names.
        const cells = Array(colCount);
        const subcategoryRows = filteredRowSubcategoryBuckets.map((rowSubcategoryBucket) => {
            const subCategoryQuery = `${ROW_SUBCATEGORY}=${encoding.encodedURIComponent(rowSubcategoryBucket.key)}`;

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
                                    <a
                                        href={`${context.search_base}&${rowCategoryQuery}&${subCategoryQuery}&${colMap[colMapKey].query}`}
                                        style={{ color: rowCategoryTextColor }}
                                        title={`${cellData.key} ${rowSubcategoryColCategoryBucket.key.replace('Histone ', '')}`}
                                    >
                                        <span className="sr-only">Search {rowCategoryBucket.key}, {rowSubcategoryBucket.key} for {rowSubcategoryColCategoryBucket.key}, {cellData.key}</span>
                                    </a>
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
                                <a
                                    href={`${context.search_base}&${rowCategoryQuery}&${subCategoryQuery}&${colMap[rowSubcategoryColCategoryBucket.key].query}`}
                                    style={{ color: rowCategoryTextColor }}
                                    title={rowSubcategoryColCategoryBucket.key}
                                >
                                    <span className="sr-only">Search {rowCategoryBucket.key}, {rowSubcategoryBucket.key} for {rowSubcategoryColCategoryBucket.key}</span>
                                </a>
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
            const labelStage = rowSubcategoryBucket.key.split(/ (.+)/)[0];
            const labelLength = rowSubcategoryBucket.key.split(/ (.+)/)[1];
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
        );
    }, [{ rowContent: header, css: 'matrix__col-category-header' }]);
    return { dataTable, rowKeys, dataTableCount };
};


/**
 * Render the area above the facets and matrix content.
 */
const MatrixHeader = ({ context }) => (
    <div className="matrix-header">
        <div className="matrix-header__banner">
            <div className="matrix-header__title">
                <h1>{context.title}</h1>
            </div>
            <div className="matrix-header__details">
                <div className="matrix-title-badge">
                    <MatrixBadges context={context} type="MouseDevelopment" />
                </div>
                <div className="matrix-description">
                    <div className="matrix-description__text">
                        The mouse development matrix displays embryonic to postnatal mouse developmental time course data across several tissues organized as reference epigenomes.
                    </div>
                </div>
            </div>
        </div>
    </div>
);

MatrixHeader.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};

/**
 * Displays the age, stage, and age-range selection buttons.
 */
const MouseStageButton = ({
    keyWord,
    idString,
    stageClass,
    isActive,
    onClick,
    isAgeDisplay,
}) => {
    let buttonLabel;
    if (isAgeDisplay) {
        const [, value, unit] = keyWord.split(' ');
        buttonLabel = `${value} ${unit}`;
    } else {
        buttonLabel = keyWord;
    }

    return (
        <button
            type="button"
            id={idString.replace(/ /g, '_')}
            className={`legend-option ${stageClass} ${isActive ? 'active' : ''}`}
            onClick={onClick}
        >
            {buttonLabel}
        </button>
    );
};

MouseStageButton.propTypes = {
    // Text to display in the button
    keyWord: PropTypes.string.isRequired,
    // Button element id
    idString: PropTypes.string.isRequired,
    // CSS class to apply to the button
    stageClass: PropTypes.string.isRequired,
    // True if the button is selected
    isActive: PropTypes.bool.isRequired,
    // Called when the user clicks the button
    onClick: PropTypes.func.isRequired,
    // True if displaying age; false if displaying stage; age gets stage stripped off
    isAgeDisplay: PropTypes.bool,
};

MouseStageButton.defaultProps = {
    isAgeDisplay: false,
};

/**
 * Displays the buttons that jump to particular tissue sections of the matrix.
 */
const TissueJumper = ({ tissues }) => {
    const sortedTissues = _.sortBy(tissues);
    return (
        <div className="tissue-jumper">
            <div className="tissue-jumper__title">Jump to tissue</div>
            <div className="tissue-jumper__tissues">
                {sortedTissues.map((tissue) => (
                    <a
                        key={tissue}
                        className="btn btn-success btn-xs"
                        href={`#${globals.sanitizeId(tissue)}`}
                    >
                        {tissue}
                    </a>
                ))}
            </div>
        </div>
    );
};

TissueJumper.propTypes = {
    /** Array of tissue names */
    tissues: PropTypes.array.isRequired,
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
        const actualClassifications = classificationBuckets.map((bucket) => bucket.key);
        const filteredClassifications = requestedClassifications.filter((classification) => actualClassifications.includes(classification));

        this.state = {
            /** Categories the user has expanded */
            expandedRowCategories: filteredClassifications,
            /** True if matrix scrolled all the way to the right; used for flashing arrow */
            scrolledRight: false,
            /** All currently selected ages or stages */
            selectedDevelopmentStages: [],
        };
        this.expanderClickHandler = this.expanderClickHandler.bind(this);
        this.selectMouseDevelopmentStage = this.selectMouseDevelopmentStage.bind(this);
        this.hasRequestedClassifications = filteredClassifications.length > 0;
        this.clearFilters = this.clearFilters.bind(this);
    }

    /**
     * Get an array of all values in the current query string corresponding to the given `key`.
     * @param {string} key Query string key whose values this retrieves.
     *
     * @return {array} Values for each occurrence of `key` in the query string.
     */
    getQueryValues(key) {
        return this.query.getKeyValues(key);
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

    selectMouseDevelopmentStage(e) {
        const targetId = e.target.id.replace(/_/g, ' ');
        // selected something that was already selected so just de-select
        if (this.state.selectedDevelopmentStages.indexOf(targetId) > -1) {
            this.setState((state) => {
                const newSelections = state.selectedDevelopmentStages.filter((stage) => stage !== targetId);
                return { selectedDevelopmentStages: newSelections };
            });
        // selected a particular age so need to disable the stage
        } else if (targetId.split(' ').length > 1) {
            let newSelections = [];
            if (targetId.includes('embryonic')) {
                newSelections = this.state.selectedDevelopmentStages.filter((stage) => stage !== 'embryonic');
            } else if (targetId.includes('postnatal')) {
                newSelections = this.state.selectedDevelopmentStages.filter((stage) => stage !== 'postnatal');
            } else {
                newSelections = this.state.selectedDevelopmentStages.filter((stage) => stage !== 'adult');
            }
            newSelections = [...newSelections, targetId];
            this.setState({ selectedDevelopmentStages: newSelections });
        // selected a stage but there are also ages selected so disable those
        } else if (targetId === 'embryonic') {
            this.setState((state) => {
                let newSelections = state.selectedDevelopmentStages.filter((stage) => (!(stage.includes('embryonic') && (stage.split(' ').length > 1))));
                newSelections = [...newSelections, targetId];
                return { selectedDevelopmentStages: newSelections };
            });
        } else if (targetId === 'postnatal') {
            this.setState((state) => {
                let newSelections = state.selectedDevelopmentStages.filter((stage) => (!(stage.includes('postnatal') && (stage.split(' ').length > 1))));
                newSelections = [...newSelections, targetId];
                return { selectedDevelopmentStages: newSelections };
            });
        } else {
            this.setState((state) => {
                let newSelections = state.selectedDevelopmentStages.filter((stage) => (!(stage.includes('adult') && (stage.split(' ').length > 1))));
                newSelections = [...newSelections, targetId];
                return { selectedDevelopmentStages: newSelections };
            });
        }
    }

    clearFilters() {
        // reset button selections
        this.setState({ selectedDevelopmentStages: [] });
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
        if (this.state.selectedDevelopmentStages.length > 0) {
            stageFilter = this.state.selectedDevelopmentStages;
        }

        // Convert matrix data to a DataTable object.
        const { dataTable, rowKeys } = convertExperimentToDataTable(context, rowCategoryGetter, mapRowCategoryQueries, this.state.expandedRowCategories, this.expanderClickHandler, stageFilter);
        // If we have a wide window, split the table in two
        const matrixConfig = {
            rows: dataTable,
            rowKeys,
            tableCss: 'matrix',
        };

        const parsedUrl = url.parse(context['@id'], true);
        parsedUrl.query.format = 'json';
        parsedUrl.search = '';

        const rowCategory = context.matrix.y.group_by[0];
        const rowCategoryData = context.matrix.y[rowCategory].buckets;
        const mouseAgeObject = getMouseAgeObject(rowCategoryData);

        // Calculate additional filters for the to view control button links
        const additionalFilters = [];
        this.state.selectedDevelopmentStages.forEach((stage) => {
            if (['adult', 'postnatal', 'embryonic'].includes(stage)) {
                mouseAgeObject[stage].forEach((mouseAge) => {
                    additionalFilters.push({
                        term: `${mouseAge}`,
                        remove: '',
                        field: 'life_stage_age',
                    });
                });
            } else {
                additionalFilters.push({
                    term: stage,
                    remove: '',
                    field: 'life_stage_age',
                });
            }
        });

        return (
            <>
                <div className="matrix-header">
                    <SearchControls context={context} additionalFilters={additionalFilters} hideBrowserSelector />
                    <div className="matrix-header__controls">
                        <div className="matrix-header__filter-controls">
                            <div className="mouse-dev-legend">
                                <div className="filter-title">Stage filters</div>
                                <div className="stage-selector">
                                    <MouseStageButton
                                        keyWord="embryonic"
                                        idString="embryonic"
                                        stageClass="embryonic"
                                        isActive={this.state.selectedDevelopmentStages.includes('embryonic')}
                                        onClick={this.selectMouseDevelopmentStage}
                                    />
                                    <MouseStageButton
                                        keyWord="postnatal"
                                        idString="postnatal"
                                        stageClass="postnatal"
                                        isActive={this.state.selectedDevelopmentStages.includes('postnatal')}
                                        onClick={this.selectMouseDevelopmentStage}
                                    />
                                    <MouseStageButton
                                        keyWord="adult"
                                        idString="adult"
                                        stageClass="adult"
                                        isActive={this.state.selectedDevelopmentStages.includes('adult')}
                                        onClick={this.selectMouseDevelopmentStage}
                                    />
                                </div>
                                <div className="age-selectors">
                                    {mouseAgeObject.embryonic?.length > 0 && (
                                        <div>
                                            <div className="filter-title">embryonic</div>
                                            <div className="stage-container">
                                                {mouseAgeObject.embryonic.map((age) => (
                                                    <MouseStageButton
                                                        keyWord={age}
                                                        idString={age}
                                                        stageClass="embryonic"
                                                        isActive={
                                                            (this.state.selectedDevelopmentStages.includes(age))
                                                            || (this.state.selectedDevelopmentStages.includes('embryonic'))
                                                        }
                                                        isAgeDisplay
                                                        onClick={this.selectMouseDevelopmentStage}
                                                        key={`embryonic-${age}`}
                                                    />
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                    {mouseAgeObject.postnatal?.length > 0 && (
                                        <div>
                                            <div className="filter-title">postnatal</div>
                                            <div className="stage-container">
                                                {mouseAgeObject.postnatal.map((age) => (
                                                    <MouseStageButton
                                                        keyWord={age}
                                                        idString={age}
                                                        stageClass="postnatal"
                                                        isActive={
                                                            (this.state.selectedDevelopmentStages.includes(age))
                                                            || (this.state.selectedDevelopmentStages.includes('postnatal'))
                                                        }
                                                        isAgeDisplay
                                                        onClick={this.selectMouseDevelopmentStage}
                                                        key={`postnatal-${age}`}
                                                    />
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                    {mouseAgeObject.adult?.length > 0 && (
                                        <div>
                                            <div className="filter-title">adult</div>
                                            <div className="stage-container">
                                                {mouseAgeObject.adult.map((age) => (
                                                    <MouseStageButton
                                                        keyWord={age}
                                                        idString={age}
                                                        stageClass="adult"
                                                        isActive={
                                                            (this.state.selectedDevelopmentStages.includes(age))
                                                            || (this.state.selectedDevelopmentStages.includes('adult'))
                                                        }
                                                        isAgeDisplay
                                                        onClick={this.selectMouseDevelopmentStage}
                                                        key={`adult-${age}`}
                                                    />
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                            <TissueJumper tissues={rowCategoryData.map((tissue) => tissue.key)} />
                            <button
                                type="button"
                                className="clear-filters"
                                onClick={this.clearFilters}
                            >
                                Clear Filters <i className="icon icon-times-circle" aria-label="Clear search terms and selected mouse development stages and ages" />
                            </button>
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
                    </div>
                </div>
            </>
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
                        <MatrixContent
                            context={context}
                            rowCategoryGetter={this.getRowCategories}
                            rowSubCategoryGetter={this.getRowSubCategories}
                            mapRowCategoryQueries={mapRowCategoryQueriesExperiment}
                            mapSubCategoryQueries={mapSubCategoryQueriesExperiment}
                        />
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
