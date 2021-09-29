import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import QueryString from '../libs/query_string';
import { svgIcon } from '../libs/svg-icons';
import * as DropdownButton from '../libs/ui/button';
import { getIsCartSearch } from './cart';
import { BatchDownloadActuator, SearchBatchDownloadController } from './batch_download';


/**
 * Displays any of the view type bu†tons, wrapping the actual button title.
 */
const ViewControlButton = ({ viewType, queryString, children }) => (
    <a
        href={`/${viewType.path}/?${queryString}`}
        role="button"
        className="btn btn-info btn-sm"
        id={`search-control-${viewType.type}`}
        data-test={viewType.type}
        aria-label={`${viewType.label}`}
    >
        {svgIcon(viewType.icon)}
        {children}
    </a>
);

ViewControlButton.propTypes = {
    /** Single relevant entry from `viewTypeMap` */
    viewType: PropTypes.object.isRequired,
    /** Current search query string */
    queryString: PropTypes.string.isRequired,
    /** Button title content */
    children: PropTypes.node.isRequired,
};


/**
 * Renders the view type button for the search page.
 */
const SearchViewButton = ({ viewType, query }) => (
    <ViewControlButton viewType={viewType} queryString={query.format()}>
        {viewType.title}
    </ViewControlButton>
);

SearchViewButton.propTypes = {
    /** Single relevant entry from `viewTypeMap` */
    viewType: PropTypes.object.isRequired,
    /** Current search query object */
    query: PropTypes.object.isRequired,
};


/**
 * Renders the view type button for the report page. This renders a normal button like the search
 * and matrix views when one "type=" exists in the query string, but renders a dropdown button when
 * more than one "type=" exists in the query string -- one entry in the dropdown for each "type="
 * in the query string.
 */
const ReportViewButton = ({ viewType, query }, reactContext) => {
    const typeValues = query.getKeyValues('type');
    if (typeValues.length === 1) {
        // One "type=" in the query string so render a regular link to the report page.
        return (
            <ViewControlButton viewType={viewType} queryString={query.format()}>
                {viewType.title}
            </ViewControlButton>
        );
    }

    // More than one "type=" in the query string so render a dropdown button. The menu items
    // display the "type=" value until the <App> component has loaded the human-readable type
    // names.
    const uniqueTypeValues = new Set(typeValues);
    return (
        <DropdownButton.Immediate
            label={
                <div className="view-type-report-dropdown">
                    {svgIcon(viewType.icon)}
                    {viewType.title}
                    {svgIcon('chevronDown')}
                </div>
            }
            id="view-type-report"
            css="view-type-report"
        >
            {_.sortBy([...uniqueTypeValues]).map((typeValue) => {
                query.deleteKeyValue('type').addKeyValue('type', typeValue);
                return (
                    <a key={typeValue} href={`/${viewType.path}/?${query.format()}`}>
                        {reactContext.profilesTitles[typeValue] || typeValue}
                    </a>
                );
            })}
        </DropdownButton.Immediate>
    );
};

ReportViewButton.propTypes = {
    /** Single relevant entry from `viewTypeMap` */
    viewType: PropTypes.object.isRequired,
    /** Current search query object */
    query: PropTypes.object.isRequired,
};

ReportViewButton.contextTypes = {
    profilesTitles: PropTypes.object,
};


/**
 * Some search query-string types (?type={something}) don't have a matrix view and would generate
 * a user-visible error if you tried. This list includes the possible search types to allow a
 * matrix button on the /search/ and /report/ pages. Add to this list for any new object types that
 * should include a matrix button on those pages.
 */
const matrixTypes = ['Experiment', 'Annotation'];


/**
 * Renders the view type button for the matrix pages. The query type gets inserted in the button
 * label.
 */
const MatrixViewButton = ({ viewType, query }) => {
    const typeValues = query.getKeyValues('type');

    return (
        (typeValues.length === 1 && matrixTypes.includes(typeValues[0])) &&
            <ViewControlButton viewType={viewType} queryString={query.format()}>
                {`${typeValues[0]} ${viewType.title}`}
            </ViewControlButton>
    );
};

MatrixViewButton.propTypes = {
    /** Single relevant entry from `viewTypeMap` */
    viewType: PropTypes.object.isRequired,
    /** Current search query object */
    query: PropTypes.object.isRequired,
};


/**
 * Maps the page type to the corresponding view control elements. Extend this array on the rare
 * occasions that a new search view gets implemented.
 *   type: identifier for each element
 *   renderer: React component to render the button for the type
 *   path: goes between slashes in search path /{path}/
 *   icon: variable name of icon in svg-icons.js for icon in button
 *   title: Used in button; matrix prepended by type
 *   label: Used for screen readers
 */
const viewTypeMap = [
    { type: 'search', renderer: SearchViewButton, path: 'search', icon: 'search', title: 'List', label: 'View search results as a list' },
    { type: 'report', renderer: ReportViewButton, path: 'report', icon: 'table', title: 'Report', label: 'View search results as a tabular report' },
    { type: 'matrix', renderer: MatrixViewButton, path: 'matrix', icon: 'matrix', title: 'matrix', label: 'View search results as a matrix' },
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
 * Displays view control buttons appropriate for the given search results.
 */
export const ViewControls = ({ results, additionalFilters }) => {
    // Don't render view controls for cart searches.
    if (!getIsCartSearch(results)) {
        const searchPageType = getSearchPageType(results);
        const parsedUrl = url.parse(results['@id']);
        const query = new QueryString(parsedUrl.query);

        // Add any additional filters to the query from pages that do front-end filtering without
        // doing a new query.
        additionalFilters.forEach((filter) => {
            query.addKeyValue(filter.field, filter.term);
        });

        // Only render these buttons if at least one 'type=' is in the query string.
        return (query.getKeyValues('type').length > 0 &&
            <div className="btn-attached">
                {viewTypeMap.map((viewType) => {
                    // Don't render a view control button linking to the currently viewed page.
                    if (viewType.type !== searchPageType) {
                        const ViewTypeRenderer = viewType.renderer;
                        return (
                            <ViewTypeRenderer
                                key={viewType.type}
                                viewType={viewType}
                                query={query}
                            />
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
