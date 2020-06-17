import React from 'react';
import PropTypes, { bool } from 'prop-types';
import _ from 'underscore';
import url from 'url';
import * as encoding from '../libs/query_encoding';
import QueryString from '../libs/query_string';
import { svgIcon } from '../libs/svg-icons';
import { Modal, ModalHeader, ModalBody } from '../libs/ui/modal';
import { Panel, PanelBody, TabPanel } from '../libs/ui/panel';
import { tintColor, isLight } from './datacolors';
import DataTable from './datatable';
import * as globals from './globals';
import { RowCategoryExpander, SearchFilter } from './matrix';
import BodyMap, { initializeBodyMap, CellsList, organField, systemsField, clearBodyMapSelectionsFromUrl } from './body_map';
import BodyDiagram from '../img/bodyMap/Deselected_Body';
import { BatchDownloadControls, ViewControls } from './view_controls';
import { MatrixInternalTags } from './objectutils';


/**
 * Number of subcategory items to show when subcategory isn't expanded.
 * @constant
 */
const SUB_CATEGORY_SHORT_SIZE = 10;

// Organisms for which we display tabs
// Names for the tabs are hard-coded because we want to display disabled tabs for tabs for which there are no results
const organismTerms = ['Homo sapiens', 'Mus musculus'];

// Reference epigenome category properties we use.
const ROW_CATEGORY = 'biosample_ontology.classification';
const ROW_SUBCATEGORY = 'biosample_ontology.term_name';
const COL_CATEGORY = 'assay_title';
const COL_SUBCATEGORY = 'target.label';


const matrixAssaySortOrder = [
    'polyA plus RNA-seq',
    'total RNA-seq',
    'small RNA-seq',
    'microRNA-seq',
    'microRNA counts',
    'RNA microarray',
    'DNase-seq',
    'ATAC-seq',
    'WGBS',
    'RRBS',
    'MeDIP-seq',
    'MRE-seq',
    'TF ChIP-seq',
    'Histone ChIP-seq',
];

export default matrixAssaySortOrder;


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
 * @param {object} context Reference epigenome matrix data
 *
 * @return {object} Keyed column header information
 */
const generateColMap = (context) => {
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

            // Add the mapping of "<assay>" key string to column index.
            colMap[colCategoryBucket.key] = { col: colIndex, category: colCategoryBucket.key, hasSubcategories: colSubcategoryBuckets.length > 0 };
            colIndex += 1;

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
 * for the matrix. This is a shim between the incoming matrix data and the object <DataTable>
 * needs.
 * @param {object} context Matrix JSON for the page
 * @param {array}  expandedRowCategories Names of rowCategories the user has expanded
 * @param {func}   expanderClickHandler Called when the user expands/collapses a row category
 * @param {string} clearClassification URI to use to clear classification filter; null for none
 *
 * @return {object} Generated object suitable for passing to <DataTable>
 */

const convertReferenceEpigenomeToDataTable = (context, expandedRowCategories, expanderClickHandler, clearClassifications) => {
    const colCategory = context.matrix.x.group_by[0];
    const colSubcategory = context.matrix.x.group_by[1];
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

    // Generate the hierarchical top-row sideways header label cells. The first cell is null unless
    // it contains a link to clear the currently selected classification. At the end of this loop,
    // rendering `{header}` shows this header row. The `sortedCols` array gets mutated in this loop,
    // acquiring a `query` property in each of its objects that gets used later to generate cell
    // hrefs.
    const header = [
        {
            header: (
                clearClassifications ?
                    <div className="matrix__clear-classifications">
                        <a href={clearClassifications}><i className="icon icon-times-circle" /> Clear classifications</a>
                    </div>
                : null
            ),
        },
    ].concat(sortedCols.map((colInfo) => {
        const categoryQuery = `${COL_CATEGORY}=${encoding.encodedURIComponent(colInfo.category)}`;
        if (!colInfo.subcategory) {
            // Add the category column links.
            colInfo.query = categoryQuery;
            return { header: <a href={`${context.search_base}&${categoryQuery}`}>{colInfo.category}</a> };
        }

        // Add the subcategory column links.
        const subCategoryQuery = `${COL_SUBCATEGORY}=${encoding.encodedURIComponent(colInfo.subcategory)}`;
        colInfo.query = `${categoryQuery}&${subCategoryQuery}`;
        return { header: <a className="sub" href={`${context.search_base}&${categoryQuery}&${subCategoryQuery}`}>{colInfo.subcategory}</a> };
    }));

    // Generate the main table content including the data hierarchy, where the upper level of the
    // hierarchy gets referred to here as "rowCategory" and the lower-level gets referred to as
    // "rowSubcategory." Both these types of rows get collected into `dataTable` which gets passed
    // to <DataTable>. Also generate an array of React keys to use with <DataMatrix> by using an
    // array index that's independent of the reduce-loop index because of spacer/expander row
    // insertion.
    let matrixRow = 1;
    const rowKeys = ['column-categories'];
    const rowCategoryBuckets = context.matrix.y[rowCategory].buckets;
    const rowCategoryColors = globals.biosampleTypeColors.colorList(rowCategoryBuckets.map(rowCategoryDatum => rowCategoryDatum.key));
    const dataTable = rowCategoryBuckets.reduce((accumulatingTable, rowCategoryBucket, rowCategoryIndex) => {
        // Each loop iteration generates one biosample classification row as well as the rows of
        // biosample term names under it.
        const rowCategoryColor = rowCategoryColors[rowCategoryIndex];
        const rowSubcategoryColor = tintColor(rowCategoryColor, 0.5);
        const rowCategoryTextColor = isLight(rowCategoryColor) ? '#000' : '#fff';
        const rowSubcategoryBuckets = rowCategoryBucket[rowSubcategory].buckets;
        const expandableRowCategory = rowSubcategoryBuckets.length > SUB_CATEGORY_SHORT_SIZE;
        const rowCategoryQuery = `${ROW_CATEGORY}=${encoding.encodedURIComponent(rowCategoryBucket.key)}`;

        // Update the row key mechanism.
        rowKeys[matrixRow] = rowCategoryBucket.key;
        matrixRow += 1;

        // Get the list of subcategory names, or the first items of the list if the category isn't
        // expanded.
        const categoryExpanded = expandedRowCategories.indexOf(rowCategoryBucket.key) !== -1;
        const visibleRowSubcategoryBuckets = categoryExpanded ? rowSubcategoryBuckets : rowSubcategoryBuckets.slice(0, SUB_CATEGORY_SHORT_SIZE);

        // Generate one classification's rows of term names.
        const cells = Array(colCount);
        const subcategoryRows = visibleRowSubcategoryBuckets.map((rowSubcategoryBucket) => {
            const subCategoryQuery = `${ROW_SUBCATEGORY}=${encoding.encodedURIComponent(rowSubcategoryBucket.key)}`;

            // Generate an array of data cells for a single term-name row.
            cells.fill(null);
            rowSubcategoryBucket[colCategory].buckets.forEach((rowSubcategoryColCategoryBucket) => {
                // Skip any excluded assay columns.
                if (!excludedAssays.includes(rowSubcategoryColCategoryBucket.key)) {
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
                                        <a href={`${context.search_base}&${rowCategoryQuery}&${subCategoryQuery}&${colMap[colMapKey].query}`}>
                                            <span className="sr-only">Search {rowCategoryBucket.key}, {rowSubcategoryBucket.key} for {rowSubcategoryColCategoryBucket.key}, {cellData.key}</span>
                                            &nbsp;
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
                                    <a href={`${context.search_base}&${rowCategoryQuery}&${subCategoryQuery}&${colMap[rowSubcategoryColCategoryBucket.key].query}`}>
                                        <span className="sr-only">Search {rowCategoryBucket.key}, {rowSubcategoryBucket.key} for {rowSubcategoryColCategoryBucket.key}</span>
                                        &nbsp;
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
            return {
                rowContent: [
                    {
                        header: (
                            <a href={`${context.search_base}&${rowCategoryQuery}&${subCategoryQuery}`}>
                                <div className="subcategory-row-text">{rowSubcategoryBucket.key}</div>
                            </a>
                        ),
                    },
                ].concat(cells),
                css: 'matrix__row-data',
            };
        });

        // Generate a row for a classification concatenated with the term-name rows under it,
        // concatenated with an spacer row that might be empty or might have a rowCategory expander
        // button.
        rowKeys[matrixRow] = `${rowCategoryBucket.key}-spacer`;
        matrixRow += 1;
        const categoryId = globals.sanitizeId(rowCategoryBucket.key);
        return accumulatingTable.concat(
            [
                {
                    rowContent: [{
                        header: (
                            <div id={categoryId} style={{ backgroundColor: rowCategoryColor }}>
                                {expandableRowCategory ?
                                    <RowCategoryExpander
                                        categoryId={categoryId}
                                        categoryName={rowCategoryBucket.key}
                                        expanderColor={rowCategoryTextColor}
                                        expanded={categoryExpanded}
                                        expanderClickHandler={expanderClickHandler}
                                    />
                                : null}
                                {clearClassifications ?
                                    <div style={{ color: rowCategoryTextColor }}>{rowCategoryBucket.key}</div>
                                :
                                    <a href={`${context['@id']}&${rowCategoryQuery}`} style={{ color: rowCategoryTextColor }}>{rowCategoryBucket.key}</a>
                                }
                            </div>
                        ),
                    },
                    { content: <div style={{ backgroundColor: rowCategoryColor }} />, colSpan: 0 }],
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
                                    categoryId={categoryId}
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
    return { dataTable, rowKeys };
};


/**
 * Render the area above the matrix itself, including the page title.
 */
const MatrixHeader = ({ context, showProjects, project }, reactContext) => {
    const projectSelect = (e, baseUrl) => {
        const selectedProject = e.target.value;
        const awardRfa = selectedProject === 'All' ? '' : `&award.rfa${selectedProject === 'Roadmap' ? '=' : '!='}Roadmap`;
        const parseUrl = url.parse(baseUrl);
        const query = new QueryString(parseUrl.query);

        // search query string parameters and others need to be preserved across different projects but the
        // project parameter (award.rfa) may differ. So satisfy both conditions, project is removed from the url
        // and re-added or not added, as needed.
        query.deleteKeyValue('award.rfa');
        const link = `?${query.format()}${awardRfa}`;
        reactContext.navigate(link);
    };

    const query = new QueryString(context.search_base);
    let organism = '';
    if (query.getKeyValues('replicates.library.biosample.donor.organism.scientific_name').includes('Mus musculus')) {
        organism = 'mouse';
    } else if (query.getKeyValues('replicates.library.biosample.donor.organism.scientific_name').includes('Homo sapiens')) {
        organism = 'human';
    }
    const matrixDescription = organism ?
        <span>Project data from {organism} tissue, cell line, primary cell, and in vitro differentiated cell biosamples organized as reference epigenomes following guidelines set out by IHEC.</span>
    : null;

    return (
        <div className="matrix-header">
            <div className="matrix-header__title">
                <h1>{context.title}</h1>
                <div className="matrix-tags">
                    <MatrixInternalTags context={context} />
                    {matrixDescription ?
                        <div className="matrix-description">{matrixDescription}</div>
                    : null}
                </div>
            </div>
            {showProjects ?
                <div className="test-project-selector">
                    <input type="radio" id="all" name="project" value="All" checked={project === null} onChange={e => projectSelect(e, context['@id'])} />
                    <label htmlFor="all">All</label> &nbsp; &nbsp;
                    <input type="radio" id="roadmap" name="project" value="Roadmap" checked={project === 'Roadmap'} onChange={e => projectSelect(e, context['@id'])} />
                    <label htmlFor="roadmap">Roadmap</label> &nbsp; &nbsp;
                    <input type="radio" id="nonroadmap" name="project" value="Nonroadmap" checked={project !== 'Roadmap' && project !== null} onChange={e => projectSelect(e, context['@id'])} />
                    <label htmlFor="nonroadmap">Non-Roadmap</label>
                </div>
            : null}
        </div>
    );
};

MatrixHeader.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
    showProjects: bool,
    project: PropTypes.string,
};

MatrixHeader.defaultProps = {
    showProjects: false,
    project: null,
};

MatrixHeader.contextTypes = {
    navigate: PropTypes.func,
};

const ClickableThumbnail = (props) => {
    // "isThumbnailExpanded" checks if the pop-up should be displayed
    const isThumbnailExpanded = props.isThumbnailExpanded;
    // "toggleThumbnail" toggles whether or not the pop-up is displayed
    const toggleThumbnail = props.toggleThumbnail;
    return (
        <button
            className={`body-image-thumbnail ${isThumbnailExpanded ? 'expanded' : 'collapsed'}`}
            onClick={() => toggleThumbnail()}
        >
            <div className="body-map-expander">Filter results by body diagram</div>
            {svgIcon('expandArrows')}
            <BodyDiagram />
            <div className="body-list body-list-narrow">
                <ul className="body-list-inner">
                    {Object.keys(CellsList).map(image =>
                        <div
                            className={`body-inset ${image}`}
                            id={image}
                            key={image}
                        >
                            <img className="active-image" src={`/static/img/bodyMap/insetSVGs/${image.replace(' ', '_')}.svg`} alt={image} />
                            <img className="inactive-image" src={`/static/img/bodyMap/insetSVGs/${image.replace(' ', '_')}_deselected.svg`} alt={image} />
                            <div className="overlay" />
                        </div>
                    )}
                </ul>
            </div>
        </button>
    );
};

ClickableThumbnail.propTypes = {
    isThumbnailExpanded: PropTypes.bool.isRequired,
    toggleThumbnail: PropTypes.func.isRequired,
};

const SelectedFilters = (props) => {
    const selectedFilters = props.filters;
    const organTerms = selectedFilters.filter(f => f.field === organField);
    const systemsTerms = selectedFilters.filter(f => f.field === systemsField);
    const freeSearchTerms = selectedFilters.filter(f => f.field === 'searchTerm');
    const selectedTerms = [...organTerms, ...systemsTerms, ...freeSearchTerms];
    return (
        <React.Fragment>
            {(selectedTerms.length > 0) ?
                <div className="filter-container">
                    <div className="filter-hed">Selected filters:</div>
                    {selectedTerms.map(filter =>
                        <a href={filter.remove} key={filter.term} className={(filter.field.indexOf('!') !== -1) ? 'negation-filter' : ''}>
                            <div className="filter-link"><i className="icon icon-times-circle" /> {filter.term}</div>
                        </a>
                    )}
                </div>
            : null}
        </React.Fragment>
    );
};

SelectedFilters.propTypes = {
    filters: PropTypes.array.isRequired,
};

const BodyMapModal = (props) => {
    const isThumbnailExpanded = props.isThumbnailExpanded;
    const toggleThumbnail = props.toggleThumbnail;
    const context = props.context;
    return (
        <div className="modal" style={{ display: 'block' }}>
            <div className={`epigenome-body-map-container ${isThumbnailExpanded ? 'expanded' : 'collapsed'}`}>
                <button className="collapse-body-map" onClick={() => toggleThumbnail()}>
                    {svgIcon('collapseArrows')}
                    <div className="body-map-collapser">Hide body diagram</div>
                </button>
                <div className="clickable-diagram-container">
                    <BodyMap context={context} />
                </div>
            </div>
            <div className="modal-backdrop in" />
        </div>
    );
};

BodyMapModal.propTypes = {
    isThumbnailExpanded: PropTypes.bool.isRequired,
    toggleThumbnail: PropTypes.func.isRequired,
    context: PropTypes.object.isRequired,
};

/**
 * Display the matrix and associated controls above them.
 */
class MatrixPresentation extends React.Component {
    constructor(props) {
        super(props);

        this.parsedUrl = url.parse(props.context['@id']);
        this.query = new QueryString(this.parsedUrl.query);

        this.getAvailableOrganisms = this.getAvailableOrganisms.bind(this);
        this.getQueryValues = this.getQueryValues.bind(this);
        this.getOrganismTabs = this.getOrganismTabs.bind(this);
        this.getInitialSelectedTab = this.getInitialSelectedTab.bind(this);
        this.getClearClassificationsLink = this.getClearClassificationsLink.bind(this);
        this.expanderClickHandler = this.expanderClickHandler.bind(this);
        this.handleOnScroll = this.handleOnScroll.bind(this);
        this.handleScrollIndicator = this.handleScrollIndicator.bind(this);
        this.handleTabClick = this.handleTabClick.bind(this);
        this.toggleThumbnail = this.toggleThumbnail.bind(this);
        this.clearOrgans = this.clearOrgans.bind(this);

        // Determine whether biosample classifications have been specified in the query string to
        // determine which matrix row sections to initially expand.
        const requestedClassifications = this.getQueryValues('biosample_ontology.classification');

        // Gather the biosample classifications actually in the data and filter the requested
        // classifications down to the actual data.
        const classificationBuckets = props.context.matrix.y[props.context.matrix.y.group_by[0]].buckets;
        const actualClassifications = classificationBuckets.map(bucket => bucket.key);
        const filteredClassifications = requestedClassifications.filter(classification => actualClassifications.includes(classification));

        this.state = {
            /** Categories to display expanded */
            expandedRowCategories: filteredClassifications,
            /** True if matrix scrolled all the way to the right; used for flashing arrow */
            scrolledRight: false,
            /** True to view the organism chooser modal; only set to true when mounted */
            organismChooserVisible: false,
            isThumbnailExpanded: false,
        };

        this.initialSelectedTab = this.getInitialSelectedTab();
        this.hasRequestedClassifications = filteredClassifications.length > 0;
    }

    componentDidMount() {
        this.handleScrollIndicator(this.scrollElement);

        // Highlight body map selections based on url
        const searchQuery = url.parse(this.props.context['@id']).search;
        initializeBodyMap(searchQuery);
        const query = new QueryString(searchQuery);
        const terms = query.getKeyValues(organField);
        terms.forEach((term) => {
            if (CellsList[term] && document.getElementById(term)) {
                document.getElementById(term).classList.add('active');
            }
        });

        this.setState({
            // Display the organism-chooser modal if the query string doesn't specify an organism to
            // display.
            organismChooserVisible: this.initialSelectedTab === null,
            // Check if modal should be open
            isThumbnailExpanded: this.context.location_href.includes('#openModal'),
        });
    }

    componentDidUpdate() {
        // Updates only happen for scrolling on this page. Every other update causes an
        // unmount/mount sequence.
        this.handleScrollIndicator(this.scrollElement);
    }

    /**
     * Get a list of organism scientific names that exist in the given matrix data.
     * @return {array} Organisms in data; empty array if none
     */
    getAvailableOrganisms() {
        const { context } = this.props;
        const organismFacet = context.facets && context.facets.find(facet => facet.field === 'replicates.library.biosample.donor.organism.scientific_name');
        if (organismFacet) {
            return organismFacet.terms.map(term => term.key);
        }
        return [];
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

    /**
     * Generate React components to render the tabs with <TabPanel>. These components correspond
     * to the organisms available in the given matrix data.
     *
     * @return {object} React components for each tab; null if no organisms
     */
    getOrganismTabs() {
        // We use "organisms" to determine if a tab should be disabled or not
        const organisms = this.getAvailableOrganisms();
        const organismTabs = {};
        organismTerms.forEach((organismName) => {
            organismTabs[organismName] = <div className={`organism-button ${organismName.replace(' ', '-')} ${this.initialSelectedTab === organismName ? 'active' : ''} ${!(organisms.includes(organismName)) ? 'disabled' : ''}`}><img src={`/static/img/bodyMap/organisms/${organismName.replace(' ', '-')}.png`} alt={organismName} /><span>{organismName}</span></div>;
        });
        return organismTabs;
    }

    /**
     * Get the ID of the organism tab that should be selected on page load. With no organism
     * specified in the query string, null gets returned which causes the organism-selector modal
     * to appear.
     *
     * @return {string} ID of the tab that should be selected; null if none specified
     */
    getInitialSelectedTab() {
        const organisms = this.getAvailableOrganisms();
        const selectedOrganisms = this.getQueryValues('replicates.library.biosample.donor.organism.scientific_name');
        if (selectedOrganisms.length === 1) {
            // Query string specifies exactly one organism. Select the corresponding tab if it
            // exists, otherwise don't select a tab.
            return organisms.includes(selectedOrganisms[0]) ? selectedOrganisms[0] : null;
        }
        return null;
    }

    /**
     * Get the URL to clear the currently selected classification in the query string, if any.
     *
     * @return {string} URL used to clear classifications from the query string.
     */
    getClearClassificationsLink() {
        if (this.hasRequestedClassifications) {
            const parsedUrl = url.parse(this.props.context['@id']);
            const query = new QueryString(parsedUrl.query);
            query.deleteKeyValue('biosample_ontology.classification');
            parsedUrl.search = null;
            parsedUrl.query = null;
            const baseMatrixUrl = url.format(parsedUrl);
            return `${baseMatrixUrl}?${query.format()}`;
        }
        return null;
    }

    /**
     * Called when the user clicks on the expander button on a category to collapse or expand it.
     * @param {string} category Key for the clicked category
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
            const navbar = document.querySelector('#navbar');
            const headerToPageTopDistance = header ? header.getBoundingClientRect().top : 0;
            const buffer = 20; // extra space between navbar and header
            const top = headerToPageTopDistance - ((navbar ? navbar.getBoundingClientRect().height : 0) + buffer);
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
        if (element) {
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
        } else if (!this.state.scrolledRight) {
            this.setState({ scrolledRight: true });
        }
    }

    /**
     * Handle a click on a tab by navigating to the reference epigenome matrix URL that includes
     * the organism for the clicked tab.
     * @param {string} Text of tab that the user clicked
     */
    handleTabClick(tab) {
        // Parse and extract from the context URI instead of using this.parsedUrl and this.query
        // because we mutate both of these in this method.
        const parsedUrl = url.parse(this.props.context['@id']);
        const query = new QueryString(parsedUrl.query);
        query.replaceKeyValue('replicates.library.biosample.donor.organism.scientific_name', tab);
        parsedUrl.search = null;
        parsedUrl.query = null;
        const baseMatrixUrl = url.format(parsedUrl);
        this.context.navigate(`${baseMatrixUrl}?${query.format()}`);
    }

    toggleThumbnail() {
        this.setState(prevState => ({
            isThumbnailExpanded: !prevState.isThumbnailExpanded,
        }));
    }

    clearOrgans() {
        const href = clearBodyMapSelectionsFromUrl(this.props.context['@id']);
        this.context.navigate(href);
    }

    render() {
        const { context } = this.props;
        const { scrolledRight } = this.state;
        const organismTabs = this.getOrganismTabs();
        const clearClassifications = this.getClearClassificationsLink();

        // Convert reference epigenome matrix data to a DataTable object.
        let dataTable;
        let rowKeys;
        let matrixConfig;
        if (this.initialSelectedTab) {
            ({ dataTable, rowKeys } = convertReferenceEpigenomeToDataTable(context, this.state.expandedRowCategories, this.expanderClickHandler, clearClassifications));
            matrixConfig = {
                rows: dataTable,
                rowKeys,
                tableCss: 'matrix',
            };
        }

        const rowCount = matrix => matrix.y['biosample_ontology.classification'].buckets.reduce((currentTotalCount, termName) => currentTotalCount + termName['biosample_ontology.term_name'].buckets.length, 0);

        return (
            <React.Fragment>
                <div className="view-controls-container">
                    <ViewControls results={this.props.context} alternativeNames={['Search list', 'Tabular report', 'Summary matrix']} />
                    <BatchDownloadControls results={context} />
                </div>
                <div className="results-count">Showing <b className="bold-total">{rowCount(context.matrix)}</b> result{rowCount(context.matrix) > 1 ? 's' : ''}.</div>
                <TabPanel tabs={organismTabs} selectedTab={this.initialSelectedTab} handleTabClick={this.handleTabClick} tabPanelCss="matrix__data-wrapper">
                    {(this.initialSelectedTab === 'Homo sapiens') ?
                        <React.Fragment>
                            <div className="header-clear-links">
                                <button className="clear-organs" onClick={this.clearOrgans}>
                                    <i className="icon icon-times-circle" />
                                    Clear all body map selections
                                </button>
                            </div>
                            <SelectedFilters filters={context.filters} />
                        </React.Fragment>
                    :
                        <SelectedFilters filters={context.filters} />
                    }
                    <div className="matrix-facet-container">
                        {(this.initialSelectedTab === 'Homo sapiens') ?
                            <React.Fragment>
                                <ClickableThumbnail isThumbnailExpanded={this.state.isThumbnailExpanded} toggleThumbnail={this.toggleThumbnail} />
                                {this.state.isThumbnailExpanded ?
                                    <BodyMapModal isThumbnailExpanded={this.state.isThumbnailExpanded} toggleThumbnail={this.toggleThumbnail} context={context} />
                                : null}
                            </React.Fragment>
                        : null}
                        <div className="matrix__presentation">
                            <div className={`matrix__label matrix__label--horz${!scrolledRight ? ' horz-scroll' : ''}`}>
                                <span>{context.matrix.x.label}</span>
                                {svgIcon('largeArrow')}
                            </div>
                            <div className="matrix__presentation-content">
                                <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}{context.matrix.y.label}</div></div>
                                {!this.state.organismChooserVisible ?
                                    <div className="matrix__data" onScroll={this.handleOnScroll} ref={(element) => { this.scrollElement = element; }}>
                                        {matrixConfig ?
                                            <DataTable tableData={matrixConfig} />
                                        : null}
                                    </div>
                                :
                                    <React.Fragment>
                                        <div className="matrix__data--empty" />
                                        <Modal>
                                            <ModalHeader closeModal={false} addCss="matrix__modal-header">
                                                <h2>Reference epigenome &mdash; choose organism</h2>
                                            </ModalHeader>
                                            <ModalBody addCss="matrix-reference-epigenome__organism-selector">
                                                <div>Organism to view in matrix:</div>
                                                <div className="selectors">
                                                    {Object.keys(organismTabs).map(organism => (
                                                        // Encode the organism name into the <a> class for BDD testing.
                                                        <a key={organism} className={`btn btn-info btn__selector--${organism.replace(/ /g, '-')}`} href={`${context['@id']}&replicates.library.biosample.donor.organism.scientific_name=${encoding.encodedURIComponent(organism)}`}>{organism}</a>
                                                    ))}
                                                </div>
                                            </ModalBody>
                                        </Modal>
                                    </React.Fragment>
                                }
                            </div>
                        </div>
                    </div>
                </TabPanel>
            </React.Fragment>
        );
    }
}

MatrixPresentation.propTypes = {
    /** Reference epigenome matrix object */
    context: PropTypes.object.isRequired,
};

MatrixPresentation.contextTypes = {
    navigate: PropTypes.func,
    location_href: PropTypes.string,
};


/**
 * Render the area containing the matrix.
 */
const MatrixContent = ({ context }) => (
    <div className="matrix__content matrix__content--reference-epigenome">
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
const ReferenceEpigenomeMatrix = ({ context }) => {
    const itemClass = globals.itemClass(context, 'view-item');
    const parsedUrl = url.parse(context['@id']);
    const query = new QueryString(parsedUrl.query);
    const species = query.getKeyValues('replicates.library.biosample.donor.organism.scientific_name')[0];
    const showProjects = species === 'Homo sapiens';
    const project = query.getKeyValues('award.rfa')[0] || query.getKeyValues('award.rfa', true)[0] ?
        query.getKeyValues('award.rfa')[0] ? 'Roadmap' : 'Nonroadmap' :
        null;

    if (context.total > 0) {
        return (
            <Panel addClasses={itemClass}>
                <PanelBody>
                    <MatrixHeader context={context} showProjects={showProjects} project={project} />
                    <MatrixContent context={context} />
                </PanelBody>
            </Panel>
        );
    }
    return <h4>No results found</h4>;
};

ReferenceEpigenomeMatrix.propTypes = {
    context: PropTypes.object.isRequired,
};

ReferenceEpigenomeMatrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
};

globals.contentViews.register(ReferenceEpigenomeMatrix, 'ReferenceEpigenomeMatrix');
