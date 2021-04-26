import React from 'react';
import PropTypes from 'prop-types';
import * as encoding from '../libs/query_encoding';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/ui/modal';
import { svgIcon } from '../libs/svg-icons';
import { getIsCartSearch } from './cart';


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
];

/**
 * Search paths that can't display batch download button.
 */
const BATCH_DOWNLOAD_PROHIBITED_PATHS = [
    '/region-search/',
];


/**
 * Displays the modal to initiate downloading files. This modal gets displayed unconditionally in
 * this component, so parent components must keep state on whether this modal is visible or not.
 * The Download button in the modal gets disabled either when told from an external source (e.g. a
 * cart operation is in progress) or when the user clicks the Download button to prevent multiple
 * download requests.
 */
export const BatchDownloadModal = ({ additionalContent, disabled, downloadClickHandler, closeModalHandler, modalText, canDownload }) => {
    /** True to disable the download button in the modal */
    const [isModalDownloadButtonDisabled, setIsModalDownloadButtonDisabled] = React.useState(false);

    const clickHandler = () => {
        setIsModalDownloadButtonDisabled(true);
        downloadClickHandler();
    };

    return (
        <Modal focusId="batch-download-submit" closeModal={closeModalHandler}>
            <ModalHeader title="Using batch download" closeModal={closeModalHandler} />
            <ModalBody>
                {modalText || modalDefaultText}
                <div>{additionalContent}</div>
            </ModalBody>
            <ModalFooter
                closeModal={<button type="button" className="btn btn-default" onClick={closeModalHandler}>Close</button>}
                submitBtn={canDownload ?
                    <button type="button" id="batch-download-submit" className="btn btn-info" disabled={disabled || isModalDownloadButtonDisabled} onClick={clickHandler}>Download</button>
                    : null}
            >
                {isModalDownloadButtonDisabled ?
                    <div className="modal-batch-download__footer-note">
                        Allow time for files.txt to download. You can close this dialog at any time.
                    </div>
                : null}
            </ModalFooter>
        </Modal>
    );
};

BatchDownloadModal.propTypes = {
    /** Additional content in modal as component */
    additionalContent: PropTypes.element,
    /** True to disable Download button */
    disabled: PropTypes.bool,
    /** Called when the user clicks the Download button in the modal */
    downloadClickHandler: PropTypes.func.isRequired,
    /** Called when the user does something to close the modal */
    closeModalHandler: PropTypes.func.isRequired,
    /** Message in modal body */
    modalText: PropTypes.element,
    /** Yes if download option is available, false otherwise */
    canDownload: PropTypes.bool,
};

BatchDownloadModal.defaultProps = {
    additionalContent: null,
    disabled: false,
    modalText: modalDefaultText,
    canDownload: true,
};


/**
 * Display the modal for batch download, and pass back clicks in the Download button
 */
export const BatchDownloadButton = ({ handleDownloadClick, title, additionalContent, disabled, modalText, canDownload }) => {
    const [isModalOpen, setIsModalOpen] = React.useState(false);
    const [onbeforeunload, setOnbeforeunload] = React.useState(null);

    const openModal = () => { setIsModalOpen(true); };
    const closeModal = () => { setIsModalOpen(false); };

    React.useEffect(() => {
        if (!onbeforeunload) {
            // preserve onbeforeunload so it can be restored after modal is closed
            setOnbeforeunload(() => window.onbeforeunload);
        }

        // deactivate onbeforeunload if modal is open, restore otherwise
        window.onbeforeunload = isModalOpen ? null : (window.onbeforeunload || onbeforeunload);
    }, [isModalOpen, onbeforeunload]);

    return (
        <>
            <button type="button" className="btn btn-info btn-sm" onClick={openModal} disabled={disabled} data-test="batch-download">{title}</button>
            {isModalOpen ?
                <BatchDownloadModal additionalContent={additionalContent} disabled={disabled} downloadClickHandler={handleDownloadClick} closeModalHandler={closeModal} modalText={modalText} canDownload={canDownload} />
            : null}
        </>
    );
};

BatchDownloadButton.propTypes = {
    /** Function to call when Download button gets clicked */
    handleDownloadClick: PropTypes.func.isRequired,
    /** Title to override usual actuator "Download" button title */
    title: PropTypes.string,
    /** True to disable Download button */
    disabled: PropTypes.bool,
    /** Additional content in modal as component */
    additionalContent: PropTypes.object,
    /** Message in modal body */
    modalText: PropTypes.element,
    /** Yes if download option is available, false otherwise */
    canDownload: PropTypes.bool,
};

BatchDownloadButton.defaultProps = {
    title: 'Download',
    disabled: false,
    additionalContent: null,
    modalText: modalDefaultText,
    canDownload: true,
};


/**
 * Display batch download button if the search results qualify for one.
 */
export const BatchDownloadControls = ({ results, queryString, additionalFilters, modalText, canDownload }, reactContext) => {
    const filters = results ? results.filters.concat(additionalFilters) : null;

    const handleDownloadClick = () => {
        const downloadQueryString = filters ? getQueryFromFilters(filters) : queryString;
        reactContext.navigate(`/batch_download/?${downloadQueryString}`);
    };

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

    return <BatchDownloadButton handleDownloadClick={handleDownloadClick} modalText={modalText} canDownload={canDownload} />;
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
    /** Query string used directly for /batch_download/ if not using `results` */
    queryString: testBatchDownloadControlsProps,
    /** Filters not included in results.filters */
    additionalFilters: PropTypes.array,
    /** Message in modal body */
    modalText: PropTypes.element,
    /** Yes if download option is available, false otherwise */
    canDownload: PropTypes.bool,
};

BatchDownloadControls.defaultProps = {
    results: null,
    queryString: '',
    additionalFilters: [],
    modalText: modalDefaultText,
    canDownload: true,
};

BatchDownloadControls.contextTypes = {
    navigate: PropTypes.func,
};

/**
 * Display batch download button if the search results qualify for one.
 */
export const BatchDownloadEncyclopedia = ({ results, queryString, additionalFilters, modalText, canDownload, additionalContent }, reactContext) => {
    const filters = results ? results.filters.concat(additionalFilters) : null;

    const handleDownloadClick = () => {
        const downloadQueryString = filters ? getQueryFromFilters(filters) : queryString;
        reactContext.navigate(`/batch_download/?${downloadQueryString}`);
    };

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

    return <BatchDownloadButton
        handleDownloadClick={handleDownloadClick}
        modalText={modalText}
        canDownload={canDownload}
        title={svgIcon('download')}
        additionalContent={additionalContent}
    />;
};

BatchDownloadEncyclopedia.propTypes = {
    /** Search results object */
    results: testBatchDownloadControlsProps,
    /** Query string used directly for /batch_download/ if not using `results` */
    queryString: testBatchDownloadControlsProps,
    /** Filters not included in results.filters */
    additionalFilters: PropTypes.array,
    /** Message in modal body */
    modalText: PropTypes.element,
    /** Yes if download option is available, false otherwise */
    canDownload: PropTypes.bool,
    /** Additional content in modal as component */
    additionalContent: PropTypes.object,

};

BatchDownloadEncyclopedia.defaultProps = {
    results: null,
    queryString: '',
    additionalFilters: [],
    modalText: modalDefaultText,
    canDownload: true,
    additionalContent: null,
};

BatchDownloadEncyclopedia.contextTypes = {
    navigate: PropTypes.func,
};
