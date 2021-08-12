import PropTypes from 'prop-types';
import * as encoding from '../libs/query_encoding';
import { svgIcon } from '../libs/svg-icons';
import { getIsCartSearch } from './cart';
import { BatchDownloadActuator, SearchBatchDownloadController } from './batch_download';
import QueryString from '../libs/query_string';


/**
 * Maps the page type to the corresponding view control elements. Extend this array on the rare
 * occasions that a new search view gets implemented.
 *   type: identifier for each element
 *   path: goes between slashes in search path /{path}/
 *   icon: variable name of icon in svg-icons.js for icon in button
 *   title: Used in button; matrix prepended by type
 *   label: Used for screen readers
 */
const viewTypeMap = [
    { type: 'search', path: 'search', icon: 'search', title: 'List', label: 'View search results as a list' },
    { type: 'report', path: 'report', icon: 'table', title: 'Report', label: 'View search results as a tabular report' },
    { type: 'matrix', path: 'matrix', icon: 'matrix', title: 'matrix', label: 'View search results as a matrix' },
];


/**
 * Based on the search-result context, determine which of the three types of search-result pages
 * the user currently views. For this to work, matrix JSON has to have a `matrix` property at the
 * top level of the JSON. If no criteria gets met, this returns an empty string. The "Summary"
 * entry exists because the summary page shows the view controls though no view controls link to
 * the summary page.
 * @param {object} context Object currently in view.
 *
 * @return {string} Type of search page currently in view: list, report, matrix, summary.
 */
const getSearchPageType = (context) => {
    const atType = context['@type'][0];
    if (atType === 'Search') {
        return 'search';
    }
    if (atType === 'Report') {
        return 'report';
    }
    if (atType === 'Summary') {
        return 'summary';
    }
    if (context.matrix) {
        return 'matrix';
    }
    return '';
};


/**
 * Some search query-string types (?type={something}) don't have a matrix view and would generate
 * a user-visible error if you tried. This list includes the possible search types to allow a
 * matrix button on the /search/ and /report/ pages. Add to this list for any new object types that
 * should include a matrix button on those pages.
 */
const matrixTypes = ['Experiment', 'Annotation'];


const modalDefaultText = (
    <>
        <p>
            Click the &ldquo;Download&rdquo; button below to download a &ldquo;files.txt&rdquo; file that contains a list of URLs to a file containing all the experimental metadata and links to download the file.
            The first line of the file has the URL or command line to download the metadata file.
        </p>
        <p>
            Further description of the contents of the metadata file are described in the <a href="/help/batch-download/">Batch Download help doc</a>.
        </p>
        <p>
            The &ldquo;files.txt&rdquo; file can be copied to any server.<br />
            The following command using cURL can be used to download all the files in the list:
        </p>
        <code>xargs -L 1 curl -O -J -L &lt; files.txt</code><br />
    </>);


/**
 * Generate a query string from the elements of the `filters` property of search results. All
 * "type" queries come first, followed by other fields, followed by "searchTerm" queries.
 * @param {array} filters From `filters` property of search results
 *
 * @return {string} Ampersand-separated query string, not including initial question mark.
 */
const getQueryFromFilters = (filters) => {
    const typeQueries = filters.filter((searchFilter) => searchFilter.field === 'type');
    const termQueries = filters.filter((searchFilter) => searchFilter.field !== 'type' && searchFilter.field !== 'searchTerm');
    const searchTermQueries = filters.filter((searchFilter) => searchFilter.field === 'searchTerm');
    const queryElements = typeQueries.concat(termQueries, searchTermQueries).map((searchFilter) => `${searchFilter.field}=${encoding.encodedURIComponentOLD(searchFilter.term)}`);
    return `${queryElements.join('&')}`;
};


/**
 * Displays view control buttons appropriate for the given search results.
 */
export const ViewControls = ({ results, additionalFilters }) => {
    // Don't render view controls for cart searches.
    if (getIsCartSearch(results)) {
        return null;
    }

    const filters = results.filters.concat(additionalFilters);
    const searchPageType = getSearchPageType(results);

    // Get all "type=" in query string. We only display controls when URL has exactly one "type=".
    const typeFilters = filters.filter((filter) => filter.field === 'type');
    if (typeFilters.length === 1) {
        const queryString = getQueryFromFilters(filters);
        const typeQuery = typeFilters[0].term;
        return (
            <div className="btn-attached">
                {viewTypeMap.map((viewType) => {
                    // Don't render a view control button linking to the viewed page, and only
                    // include a matrix button if the `type=` query string parameter value allows
                    // a matrix view.
                    if (viewType.type !== searchPageType && (viewType.type !== 'matrix' || matrixTypes.includes(typeQuery))) {
                        return (
                            <a
                                key={viewType.path}
                                href={`/${viewType.path}/?${queryString}`}
                                role="button"
                                className="btn btn-info btn-sm"
                                id={`search-control-${viewType.type}`}
                                data-test={viewType.type}
                                aria-label={`${viewType.label}`}
                            >
                                {svgIcon(viewType.icon)}
                                {viewType.type === 'matrix' ? `${typeQuery} ${viewType.title}` : viewType.title}
                            </a>
                        );
                    }
                    return null;
                })}
            </div>
        );
    }
    return null;
};

ViewControls.propTypes = {
    /** Displayed search result object; @type[0] === 'Search', 'Report', etc */
    results: PropTypes.object.isRequired,
    /** Filters to add to `results.filters` for views that filter without modifying query string */
    additionalFilters: PropTypes.array,
};

ViewControls.defaultProps = {
    additionalFilters: [],
};


/**
 * List of query string types that allow batch download.
 */
const BATCH_DOWNLOAD_DOC_TYPES = [
    'Experiment',
    'Annotation',
    'FunctionalCharacterizationExperiment',
    'SingleCellUnit',
];

/**
 * Search paths that can't display batch download button.
 */
const BATCH_DOWNLOAD_PROHIBITED_PATHS = [
    '/region-search/',
];


/**
 * Convert the filters from the file-gallery facets to QueryString form.
 * @param {object} filters Filters from file gallery facets
 * @param {string} fileQueryKey Query-string key to specify file facet query-string parameters
 * @param {boolean} inclusionOn True if "Include deprecated" checked
 * @returns {object} QueryString containing equivalent selections
 */
const convertFiltersToQuery = (filters) => {
    const query = new QueryString();
    filters.forEach((filter) => {
        const negativeFilter = filter.field.slice(-1) === '!';
        const field = negativeFilter ? filter.field.slice(0, -1) : filter.field;
        query.addKeyValue(field, filter.term, negativeFilter);
    });
    return query;
};


/**
 * Display batch download button if the search results qualify for one.
 */
export const BatchDownloadControls = ({ results, additionalFilters, modalText, canDownload }) => {
    const filters = results ? results.filters.concat(additionalFilters) : null;

    if (results) {
        // No Download button if the search path is prohibited.
        const hasProhibitedPath = BATCH_DOWNLOAD_PROHIBITED_PATHS.some((path) => results['@id'].startsWith(path));
        if (hasProhibitedPath) {
            return null;
        }

        // No download button if "type=" for an allowed type doesn't exist in query string.
        const hasDownloadDocType = filters.some((filter) => filter.field === 'type' && BATCH_DOWNLOAD_DOC_TYPES.includes(filter.term));
        if (!hasDownloadDocType) {
            return null;
        }

        // No download button if no files.
        const hasFiles = results.facets.some((facet) => facet.field === 'files.file_type' && facet.total > 0);
        if (!hasFiles) {
            return null;
        }
    }

    // Prepare the batch download controller. Because of earlier tests, at this point we know we
    // have exactly one allowed "type={something}" in the filters.
    const viewedType = filters.find((filter) => filter.field === 'type').term;
    const query = convertFiltersToQuery(filters);
    const controller = new SearchBatchDownloadController(viewedType, query);
    return <BatchDownloadActuator controller={controller} modalContent={modalText} disabled={!canDownload} />;
};

const testBatchDownloadControlsProps = (props, propName, componentName) => {
    if (!(props.results || props.queryString) || (props.results && props.queryString)) {
        return new Error(`Props 'results' or 'queryString' but not both required in '${componentName}'.`);
    }
    return null;
};

BatchDownloadControls.propTypes = {
    /** Search results object */
    results: testBatchDownloadControlsProps,
    /** Filters not included in results.filters */
    additionalFilters: PropTypes.array,
    /** Message in modal body */
    modalText: PropTypes.element,
    /** Yes if download option is available, false otherwise */
    canDownload: PropTypes.bool,
};

BatchDownloadControls.defaultProps = {
    results: null,
    additionalFilters: [],
    modalText: modalDefaultText,
    canDownload: true,
};
