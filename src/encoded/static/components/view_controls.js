/**
 * Module to support the registration and display of view-control buttons used at the top of
 * various search-result displays that allow people to view the same search results as a list,
 * matrix, etc.
 *
 * REGISTRATION
 * Specific kinds of objects (e.g. Experiment) can optionally register predefined view button
 * types. For example, Experiments support all currently supported types: search (list), report,
 * matrix, and summary.
 *
 * This function call in the module space of experiment.js registers those four views and an
 * optional type filter:
 *
 * ViewControlRegistry.register('Experiment', [
 *     ViewControlTypes.SEARCH,
 *     ViewControlTypes.MATRIX,
 *     ViewControlTypes.REPORT,
 *     ViewControlTypes.SUMMARY,
 * ], typeFilter);
 *
 * When any of /search/, /matrix/, /report/, or /summary/ specify type=Experiment and no other
 * types in the query string, the three view buttons for the search results pages not currently
 * viewed get displayed.
 *
 * Any object types not registered still display search and report buttons on search-result pages
 * specifying only that type, as these two buttons get displayed for all type=<whatever> search
 * results when only one type= exists in the query string.
 *
 * The optional type filter lets you alter the list of returned views from what you specified in
 * the array parameter. You pass a function that takes two parameters:
 * - Array of views -- the same array as you passed in the second parameter to the `register`
 *   method.
 * - Search results object for the current page.
 * This type-filter function returns the actual list of views to display, so that specific searches
 * can alter the available views.
 *
 * DISPLAY
 * To display the buttons at the top of any search results, use the <ViewControls> component,
 * passing it the search results object received in React props.context. <SearchControls> includes
 * <ViewControls> and might serve as the better option.
 */
import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import * as encoding from '../libs/query_encoding';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/ui/modal';
import { svgIcon } from '../libs/svg-icons';


/**
 * Specifies the possible types of view controls. Extend this object with new view-control types
 * on the rare occasions that a new search view gets implemented. The string value matches the
 * @type of the search-view JSON. This object is visible externally to this module, so enforce its
 * immutability.
 */
export const ViewControlTypes = {
    SEARCH: 'Search',
    REPORT: 'Report',
    MATRIX: 'Matrix',
    SUMMARY: 'Summary',
};
Object.freeze(ViewControlTypes);


/**
 * Maps search result @type[0] to corresponding view control path link components. Extend this
 * object with new pairs on the rare occasions that a new search view gets implemented. The keys
 * correspond to the values in `ViewControlTypes`, and the values fit in the view-control link
 * paths, e.g. the Matrix value, 'matrix', would fit between the slashes in the path "/matrix/" for
 * the matrix view control button.
 */
const viewPathMap = {
    Search: { path: 'search', icon: 'search', label: 'View results as a list' },
    Report: { path: 'report', icon: 'table', label: 'View tabular report' },
    Matrix: { path: 'matrix', icon: 'matrix', label: 'View summary matrix' },
    Summary: { path: 'summary', icon: 'summary', label: 'View summary report' },
};


/**
 * Specifies the order of the view buttons in the UI. Extend this array if you add new views.
 */
const viewOrder = [
    'Search',
    'Report',
    'Matrix',
    'Summary',
];


/**
 * Object types that have child object types, and therefore cannot display /report/ views.
 */
const parentTypes = [
    'Characterization',
    'Dataset',
    'Donor',
    'FileSet',
    'QualityMetric',
    'Series',
];

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
 * Manages the view-control registry. Objects (e.g. Experiment) register with a global object of
 * this class to indicate what kinds of view buttons that search results that specify that "type="
 * of object should display.
 */
class ViewControl {
    constructor() {
        this._registry = {};
    }

    /**
     * Register a list of views available for an object @type. Add Search view, and Report view if
     * not disallowed by the object type.
     * @param {string} type @type of object to register
     * @param {array} controlTypes Elements of ViewControlTypes to register
     * @param {func} typeFilter Callback for type-specific filtering of views
     */
    register(type, controlTypes, typeFilter) {
        const defaultViewControlTypes = [ViewControlTypes.SEARCH];
        if (!parentTypes.includes(type)) {
            // Add report view if object type has no child types.
            defaultViewControlTypes.push(ViewControlTypes.REPORT);
        }
        this._registry[type] = { types: new Set(controlTypes.concat(defaultViewControlTypes)) };
        if (typeFilter) {
            this._registry[type].typeFilter = typeFilter;
        }
    }

    /**
     * Look up the views available for the given object @type. If the given @type was never
     * registered, an array of the default types gets returned. Mostly this gets used internally
     * but available for external use if needed.
     * @param {string} resultType `type` property of search result `filters` property.
     *
     * @return {array} Array of available/registered views for the given type.
     */
    lookup(resultType) {
        if (this._registry[resultType]) {
            // Registered search result type. Sort and return saved views for that type.
            return {
                types: _.sortBy(Array.from(this._registry[resultType].types), viewName => viewOrder.indexOf(viewName)),
                typeFilter: this._registry[resultType].typeFilter,
            };
        }

        // Unregistered search result type. Return all default views that apply to the type.
        const defaultViewControlTypes = { types: [ViewControlTypes.SEARCH] };
        if (!parentTypes.includes(resultType)) {
            // Add report view if object type has no child types.
            defaultViewControlTypes.types.push(ViewControlTypes.REPORT);
        }
        return defaultViewControlTypes;
    }
}


/**
 * Global ViewControl object that other modules import to register for the kinds of views their
 * object types support.
 */
const ViewControlRegistry = new ViewControl();
export default ViewControlRegistry;


/**
 * Generate a query string from the elements of the `filters` property of search results. All
 * "type" queries come first, followed by other fields, followed by "searchTerm" quries.
 * @param {array} filters From `filters` property of search results
 *
 * @return {string} Ampersand-separated query string, not including initial question mark.
 */
const getQueryFromFilters = (filters) => {
    const typeQueries = filters.filter(searchFilter => searchFilter.field === 'type');
    const termQueries = filters.filter(searchFilter => searchFilter.field !== 'type' && searchFilter.field !== 'searchTerm');
    const searchTermQueries = filters.filter(searchFilter => searchFilter.field === 'searchTerm');
    const queryElements = typeQueries.concat(termQueries, searchTermQueries).map(searchFilter => `${searchFilter.field}=${encoding.encodedURIComponentOLD(searchFilter.term)}`);
    return `${queryElements.join('&')}`;
};


/**
 * Displays view control buttons appropriate for the given search results.
 */
export const ViewControls = ({ results, filterTerm, activeFilters, alternativeNames }) => {
    // Add the hard-coded type filter if given.
    let filters = [];
    if (filterTerm) {
        filters = results.filters.concat({ field: 'type', term: filterTerm });
    } else {
        filters = results.filters;
    }

    // if we have 'activeFilters' set on mouse development matrix page, append these to view control button links
    if (activeFilters) {
        activeFilters.forEach((f) => {
            if (['adult', 'postnatal', 'embryo'].includes(f)) {
                const stageTerm = f === 'embryo' ? 'embryonic' : f;
                const stageFilterExists = filters.filter(f2 => f2.term === stageTerm).length > 0;
                if (!stageFilterExists) {
                    filters.push({
                        term: f === 'embryo' ? 'embryonic' : f,
                        remove: '',
                        field: 'replicates.library.biosample.life_stage',
                    });
                }
            } else {
                const stageTerm = f.split(' ')[0] === 'embryo' ? 'embryonic' : f.split(' ')[0];
                const ageTerm = f.split(' ').slice(1).join(' ');
                const stageFilterExists = filters.filter(f2 => f2.term === stageTerm).length > 0;
                const ageFilterExists = filters.filter(f2 => f2.term === ageTerm).length > 0;
                if (!stageFilterExists) {
                    filters.push({
                        term: stageTerm,
                        remove: '',
                        field: 'replicates.library.biosample.life_stage',
                    });
                }
                if (!ageFilterExists) {
                    filters.push({
                        term: ageTerm,
                        remove: '',
                        field: 'replicates.library.biosample.age_display',
                    });
                }
            }
        });
    }

    // Get all "type=" in query string. We only display controls when URL has exactly one "type=".
    const typeFilters = filters.filter(filter => filter.field === 'type');
    if (typeFilters.length === 1) {
        // We'll get at least one `views` array element because /report/ is a view available to
        // every "type=" even if nothing has been registered for that type.
        let views;
        const viewInfo = ViewControlRegistry.lookup(typeFilters[0].term);
        if (viewInfo.typeFilter) {
            // Custom type filter defined, so call that to get the relevant views.
            views = viewInfo.typeFilter(viewInfo.types, results);
        } else {
            // No custom filter, so just get the default relevant views.
            views = viewInfo.types.filter(item => item !== results['@type'][0]);
        }
        if (activeFilters.length === 0) {
            results.filters = results.filters.filter(f3 => f3.remove !== '');
        }
        const queryString = getQueryFromFilters(results.filters);
        return (
            <div className="btn-attached">
                {views.map((view, viewIdx) => {
                    const buttonData = viewPathMap[view];
                    if (alternativeNames) {
                        return (
                            <a key={buttonData.path} href={`/${buttonData.path}/?${queryString}`} role="button" className="btn btn-info btn-sm" data-test={buttonData.path} aria-label={buttonData.label}>
                                {svgIcon(buttonData.icon)}
                                {alternativeNames[viewIdx]}
                            </a>
                        );
                    }
                    return (
                        <a key={buttonData.path} href={`/${buttonData.path}/?${queryString}`} role="button" className="btn btn-info btn-sm" data-test={buttonData.path} aria-label={buttonData.label}>
                            {svgIcon(buttonData.icon)}
                        </a>
                    );
                })}
            </div>
        );
    }
    return null;
};

ViewControls.propTypes = {
    /** Displayed search result object; @type[0] === 'Search', 'Report', etc */
    results: PropTypes.object.isRequired,
    /** Filter `type` to use in addition to `filters` property for missing "type" filter cases */
    filterTerm: PropTypes.string,
    activeFilters: PropTypes.array,
    alternativeNames: PropTypes.array,
};

ViewControls.defaultProps = {
    filterTerm: null,
    activeFilters: [],
    alternativeNames: null,
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
 */
export const BatchDownloadModal = ({ additionalContent, disabled, downloadClickHandler, closeModalHandler, modalText, canDownload }) => (
    <Modal focusId="batch-download-submit" closeModal={closeModalHandler} >
        <ModalHeader title="Using batch download" closeModal={closeModalHandler} />
        <ModalBody>
            {modalText}
            <div>{additionalContent}</div>
        </ModalBody>
        <ModalFooter
            closeModal={<button className="btn btn-default" onClick={closeModalHandler} >Close</button>}
            submitBtn={canDownload ?
                <button id="batch-download-submit" className="btn btn-info" disabled={disabled} onClick={downloadClickHandler}>Download</button>
                : null}
        />
    </Modal>
);

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

    const openModal = () => { setIsModalOpen(true); };
    const closeModal = () => { setIsModalOpen(false); };

    return (
        <React.Fragment>
            <button className="btn btn-info btn-sm" onClick={openModal} disabled={disabled} data-test="batch-download">{title}</button>
            {isModalOpen ?
                <BatchDownloadModal additionalContent={additionalContent} disabled={disabled} downloadClickHandler={handleDownloadClick} closeModalHandler={closeModal} modalText={modalText} canDownload={canDownload} />
            : null}
        </React.Fragment>
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
export class BatchDownloadControls extends React.Component {
    constructor(props) {
        super(props);
        this.handleDownloadClick = this.handleDownloadClick.bind(this);
    }

    handleDownloadClick() {
        const queryString = getQueryFromFilters(this.props.results.filters);
        this.context.navigate(`/batch_download/?${queryString}`);
    }

    render() {
        const { results, modalText, canDownload } = this.props;

        // No Download button if the search path is prohibited.
        const hasProhibitedPath = BATCH_DOWNLOAD_PROHIBITED_PATHS.some(path => results['@id'].startsWith(path));
        if (hasProhibitedPath) {
            return null;
        }

        // No download button if "type=" for an allowed type doesn't exist in query string.
        const hasDownloadDocType = results.filters.some(filter => filter.field === 'type' && BATCH_DOWNLOAD_DOC_TYPES.includes(filter.term));
        if (!hasDownloadDocType) {
            return null;
        }

        // No download button if no files.
        const hasFiles = results.facets.some(facet => facet.field === 'files.file_type' && facet.total > 0);
        if (!hasFiles) {
            return null;
        }

        return <BatchDownloadButton handleDownloadClick={this.handleDownloadClick} modalText={modalText} canDownload={canDownload} />;
    }
}

BatchDownloadControls.propTypes = {
    /** Search results object */
    results: PropTypes.object.isRequired,
    /** Message in modal body */
    modalText: PropTypes.element,
    /** Yes if download option is available, false otherwise */
    canDownload: PropTypes.bool,
};

BatchDownloadControls.contextTypes = {
    navigate: PropTypes.func,
};

BatchDownloadControls.defaultProps = {
    modalText: modalDefaultText,
    canDownload: true,
};
