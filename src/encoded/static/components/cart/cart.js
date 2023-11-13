/**
 * Components for rendering the /carts/ and /cart-view/ page.
 */
// node_modules
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import _ from 'underscore';
import url from 'url';
// libs
import { svgIcon } from '../../libs/svg-icons';
// libs/ui
import * as DropdownButton from '../../libs/ui/button';
import * as Pager from '../../libs/ui/pager';
import { Panel, PanelBody, PanelHeading, TabPanel, TabPanelPane } from '../../libs/ui/panel';
// components
import GenomeBrowser, { annotationTypeMap } from '../genome_browser';
import { itemClass, atIdToType, hasType } from '../globals';
import { useMount } from '../hooks';
import {
    ItemAccessories,
    computeAssemblyAnnotationValue,
    filterForVisualizableFiles,
    filterForDefaultFiles,
    filterForDatasetFiles,
    filterForReleasedAnalyses,
    isFileVisualizable,
    requestObjects,
} from '../objectutils';
// local
import { compileDatasetAnalyses, sortDatasetAnalyses } from './analysis';
import CartBatchDownload, { CartStaticBatchDownload } from './batch_download';
import CartClearButton from './clear';
import * as constants from './constants';
import CartViewContext from './context';
import CartDescription from './description';
import {
    assembleFileFacets,
    assembleDatasetFacets,
    CartFacets,
    CartFacetsFileView,
    CartFacetsStandin,
    datasetFieldFileFacets,
    displayedDatasetFacetFields,
    displayedFileFacetFields,
    initSelectedTerms,
} from './facet';
import { CartFileViewToggle, CartFileViewOnlyToggle, FileViewControl } from './file_view';
import CartLockTrigger from './lock';
import CartMergeShared from './merge_shared';
import { CartSearchResults } from './search_results';
import Status from '../status';
import CartRemoveElements from './remove_multiple';
import { ManageSeriesModal, useSeriesManager } from './series';
import { CartListingAgentActuator, CartStatus } from './status';
import { allowedDatasetTypes, calcTotalPageCount, DEFAULT_FILE_VIEW_NAME, getReadOnlyState } from './util';


/**
 * This file uses some shorthand terms that need some explanation.
 * "Partial files" - File objects contained within dataset search results comprising only the
 *                   properties needed to generate the file facets and file list. These serve as a
 *                   source for retrieving complete file objects to pass to the genome browser.
 * "Simplified facets" - Primary objects for displaying cart-view facets. We don't use the "facet"
 *                       properties from search results because we generate simplified facets from
 *                       dataset search results. We only do a file search for the current page of
 *                       genome-browser tracks.
 */


/**
 * Get the value of the dataset `target` property. For series, return the empty string because its `target` is an array.
 * @param {object} dataset - Dataset object whose target we need
 * @returns {string} - The value of the `target` property
 */
const datasetTarget = (dataset) => (hasType(dataset, 'Series') ? '' : dataset.target);


/**
 * Requested dataset properties not displayed in facets.
 */
const hiddenDatasetFacetFields = [
    {
        field: 'default_analysis',
        title: 'Default analysis',
    },
];

/**
 * Facet fields to request from server -- superset of those displayed in facets, minus calculated
 * props.
 */
const requestedFacetFields = displayedFileFacetFields
    .concat(displayedDatasetFacetFields.map((facetField) => ({ ...facetField, dataset: true })))
    .concat(hiddenDatasetFacetFields.map((facetField) => ({ ...facetField, dataset: true })))
    .filter((field) => !field.calculated).concat([
        { field: '@id' },
        { field: 'related_datasets', dataset: true },
        { field: 'accession', dataset: true },
        { field: 'biosample_summary', dataset: true },
        { field: 'assembly' },
        { field: 'assay_term_name' },
        { field: 'annotation_subtype' },
        { field: 'default_analysis' },
        { field: 'annotation_type' },
        { field: 'file_format_type' },
        { field: 'output_category' },
        { field: 'processed' },
        { field: 'title' },
        { field: 'genome_annotation' },
        { field: 'href' },
        { field: 'dataset' },
        { field: 'biological_replicates' },
        { field: 'simple_biosample_summary' },
        { field: 'origin_batches' },
        { field: 'analyses', dataset: true },
        { field: 'target', dataset: true, getValue: datasetTarget },
        { field: 'targets', dataset: true },
        { field: 'preferred_default' },
        { field: 'annotation_subtype', dataset: true },
        { field: 'biochemical_inputs', dataset: true },
        { field: 'award.project', dataset: true },
        { field: 'award.name', dataset: true },
        { field: 'description', dataset: true },
        { field: 'dbxrefs', dataset: true },
    ]);


/** Map of abbreviations for the allowed dataset types */
const datasetTabTitles = {
    Experiment: 'experiments',
    Annotation: 'annotations',
    FunctionalCharacterizationExperiment: 'FCEs',
    SingleCellUnit: 'single-cell units',
    TransgenicEnhancerExperiment: 'TEEs',
};


/**
 * Display browser tracks for the selected page of files.
 */
const CartBrowser = ({ files, assemblies, pageNumber, loading }) => {
    if (loading) {
        return <div className="cart__empty-message">Page currently loading&hellip;</div>;
    }

    if (assemblies.length === 0) {
        return <div className="cart__empty-message">No files to visualize</div>;
    }

    if (assemblies.length !== 1) {
        return <div className="cart__empty-message">Select single assembly to view genome browser</div>;
    }

    // Extract the current page of file objects.
    const pageStartingIndex = pageNumber * constants.PAGE_TRACK_COUNT;
    const pageFiles = files.slice(pageStartingIndex, pageStartingIndex + constants.PAGE_TRACK_COUNT).map((file) => ({ ...file }));

    // Shorten long annotation_type values for the Valis track label; fine to mutate `pageFiles` as
    // it holds a copy of a segment of `files`.
    pageFiles.forEach((file) => {
        if (file.annotation_type) {
            const mappedAnnotationType = annotationTypeMap[file.annotation_type];
            if (mappedAnnotationType) {
                file.annotation_type = mappedAnnotationType;
            }
        }
    });

    const sortParam = ['Assay term name', 'Biosample term name', 'Output type'];
    return <GenomeBrowser files={pageFiles} label="cart" assembly={assemblies[0]} expanded sortParam={sortParam} />;
};

CartBrowser.propTypes = {
    /** Files of all visualizable tracks, not just on the displayed page */
    files: PropTypes.array.isRequired,
    /** Assembly to display; only one entry results in browser display */
    assemblies: PropTypes.array,
    /** Page of files to display */
    pageNumber: PropTypes.number.isRequired,
    /** True if the page is currently loading */
    loading: PropTypes.bool.isRequired,
};

CartBrowser.defaultProps = {
    assemblies: [],
};


/**
 * Display the list of files selected by the current cart facet selections.
 */
const CartFiles = ({
    cart,
    files,
    selectedFilesInFileView,
    isFileViewOnly,
    currentPage,
    defaultOnly,
    cartType,
    loading,
    options,
}) => {
    if (files.length > 0) {
        const pageStartIndex = currentPage * constants.PAGE_FILE_COUNT;
        const currentPageFiles = files.slice(pageStartIndex, pageStartIndex + constants.PAGE_ELEMENT_COUNT);
        const pseudoDefaultFiles = files.filter((file) => file.pseudo_default);
        const readOnlyState = getReadOnlyState(cart);
        return (
            <div className="cart-list cart-list--file">
                {defaultOnly && pseudoDefaultFiles.length > 0 && !options.suppressFileViewToggle
                    ? (
                        <div className="cart-list__no-dl">
                            Uncheck &ldquo;Show default data only&rdquo; to download gray files.
                        </div>
                    )
                    : null}
                {currentPageFiles.map((file) => {
                    let targets = file.target && file.target.label;
                    if (!targets) {
                        targets = file.targets && file.targets.map((target) => target.label).join(', ');
                    }
                    return (
                        <div key={file['@id']} className={`cart-list-item${defaultOnly && file.pseudo_default && !isFileViewOnly ? ' cart-list-item--no-dl' : ''}`}>
                            {!options.suppressFileViewToggle && selectedFilesInFileView && isFileVisualizable(file) ?
                                <CartFileViewToggle
                                    file={file}
                                    fileViewName={DEFAULT_FILE_VIEW_NAME}
                                    selected={selectedFilesInFileView.includes(file['@id'])}
                                    disabled={cartType !== 'ACTIVE' || readOnlyState.any}
                                />
                            : null}
                            <a href={file['@id']} className="cart-list-link">
                                <div className={`cart-list-link__file-type cart-list-item__file-type--${file.file_format}`}>
                                    <div className="cart-list-link__format">{file.file_format}</div>
                                    {defaultOnly && file.pseudo_default && !isFileViewOnly ?
                                        <div className="cart-list-link__no-dl">Not downloadable</div>
                                    : null}
                                </div>
                                <div className="cart-list-link__props">
                                    <div className="cart-list-link__details">
                                        <div className="cart-list-details__output-type">
                                            {file.output_type}
                                        </div>
                                        <div className="cart-list-details__type">
                                            <div className="cart-list-details__label">Type</div>
                                            <div className="cart-list-details__value">{file.file_type}</div>
                                        </div>
                                        <div className="cart-list-details__target">
                                            <div className="cart-list-details__label">Target</div>
                                            <div className="cart-list-details__value">{targets || 'None'}</div>
                                        </div>
                                        <div className="cart-list-details__assay">
                                            <div className="cart-list-details__label">Assay</div>
                                            <div className="cart-list-details__value">{file.assay_term_name}</div>
                                        </div>
                                        <div className="cart-list-details__biosample">
                                            <div className="cart-list-details__label">Biosample</div>
                                            <div className="cart-list-details__value">{file.biosample_ontology && file.biosample_ontology.term_name}</div>
                                        </div>
                                    </div>
                                    <div className="cart-list-link__identifier">
                                        <div className="cart-list-link__status">
                                            <Status item={file.status} badgeSize="small" />
                                        </div>
                                        <div className="cart-list-link__title">
                                            {file.title}
                                        </div>
                                    </div>
                                </div>
                                <div className="cart-list-link__hover" />
                            </a>
                        </div>
                    );
                })}
            </div>
        );
    }

    // Message for page loading.
    if (loading) {
        return <div className="cart__empty-message">Page currently loading&hellip;</div>;
    }

    // Page not loading and no elements.
    return <div className="cart__empty-message">No files to view in any dataset in the cart.</div>;
};

CartFiles.propTypes = {
    /** Cart object being displayed */
    cart: PropTypes.object.isRequired,
    /** Array of files from datasets in the cart */
    files: PropTypes.array.isRequired,
    /** Array of selected files in the file view; null to not display selection controls */
    selectedFilesInFileView: PropTypes.array,
    /** True if the user has selected to view only file view files */
    isFileViewOnly: PropTypes.bool,
    /** Page of results to display */
    currentPage: PropTypes.number.isRequired,
    /** True if only displaying default files */
    defaultOnly: PropTypes.bool,
    /** Type of cart displayed */
    cartType: PropTypes.string.isRequired,
    /** True if page currently loading */
    loading: PropTypes.bool.isRequired,
    /** Display options */
    options: PropTypes.exact({
        /** True to suppress file view toggle */
        suppressFileViewToggle: PropTypes.bool,
    }),
};

CartFiles.defaultProps = {
    selectedFilesInFileView: null,
    isFileViewOnly: false,
    defaultOnly: false,
    options: {},
};


/**
 * Search for datasets from the @ids in `elements`. Uses search_elements endpoint so we can send
 * all the elements in the cart in the JSON payload of the request.
 * @param {array} elements `@id`s of datasets to request
 * @param {func} fetch System fetch function
 * @param {object} session session object from <App> context
 *
 * @return {object} Promise with search result object
 */
const requestDatasets = (elements, fetch, session) => {
    // If <App> hasn't yet retrieved a CSRF token, retrieve one ourselves.
    let sessionPromise;
    if (!session || !session._csrft_) {
        // No session CSRF token, so do a GET of "/session" to retrieve it.
        sessionPromise = fetch('/session');
    } else {
        // We have a session CSRF token, so retrieve it immediately.
        sessionPromise = Promise.resolve(session._csrft_);
    }

    // We could have more dataset @ids than the /search/ endpoint can handle in the query string,
    // so pass the @ids in a POST request payload instead to the /search_elements/ endpoint.
    const fieldQuery = requestedFacetFields.reduce((query, facetField) => `${query}&field=${facetField.dataset ? '' : 'files.'}${facetField.field}`, '');
    return sessionPromise.then((csrfToken) => (
        fetch(`/search_elements/type=Dataset${fieldQuery}&field=files.restricted&limit=all&filterresponse=off`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken,
            },
            body: JSON.stringify({
                '@id': elements,
            }),
        }).then((response) => {
            if (response.ok) {
                return response.json();
            }
            throw new Error(response);
        }).then((response) => {
            // Patch all datasets' files with each dataset's award so that the genome browser can
            // accurately present the legend.
            if (response) {
                response['@graph'].forEach((dataset) => {
                    if (dataset.files?.length > 0) {
                        dataset.files.forEach((file) => {
                            file.award = dataset.award;
                        });
                    }
                });
            }
            return response;
        })
    ));
};


/**
 * Display a button that links to a report page showing the datasets in the currently displayed
 * cart.
 */
const CartDatasetReport = ({ cart, usedDatasetTypes }) => {
    // Only display the Dataset Report button if we have at least one experiment in the cart. This
    // button drops down a menu allowing the user to select the data type to view which links to
    // that report view.
    if (cart?.elements?.length > 0) {
        return (
            <DropdownButton.Immediate
                label={<>Dataset report {svgIcon('chevronDown')}</>}
                id="cart-dataset-report"
                css="cart-dataset-report"
            >
                {usedDatasetTypes.map((type) => (
                    <a key={type} href={`/cart-report/?type=${allowedDatasetTypes[type].type}&cart=${cart['@id']}`} className={`cart-dataset-option cart-dataset-option--${type}`}>
                        {allowedDatasetTypes[type].title}
                    </a>
                ))}
            </DropdownButton.Immediate>
        );
    }
    return null;
};

CartDatasetReport.propTypes = {
    /** Cart as it exists in the database */
    cart: PropTypes.object,
    /** Dataset types of objects that exist in cart */
    usedDatasetTypes: PropTypes.array.isRequired,
};

CartDatasetReport.defaultProps = {
    cart: null,
};


/**
 * Display header accessories specific for carts.
 */
const CartAccessories = ({ cart, viewableDatasets, cartType, inProgress }) => {
    const readOnlyStatus = getReadOnlyState(cart);
    return (
        <div className="cart-accessories">
            {cartType === 'OBJECT' ? <CartMergeShared sharedCartObj={cart} viewableDatasets={viewableDatasets} /> : null}
            {cartType === 'ACTIVE' ?
                <>
                    <CartLockTrigger cart={cart} inProgress={inProgress} />
                    <CartClearButton isCartReadOnly={readOnlyStatus.any} />
                    <CartListingAgentActuator cart={cart} inProgress={inProgress} disabled={readOnlyStatus.any} />
                </>
            : null}
        </div>
    );
};

CartAccessories.propTypes = {
    /** Cart as it exists in the database */
    cart: PropTypes.object,
    /** Viewable cart element @ids */
    viewableDatasets: PropTypes.array,
    /** Type of cart: ACTIVE, OBJECT */
    cartType: PropTypes.string.isRequired,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
};

CartAccessories.defaultProps = {
    cart: null,
    viewableDatasets: null,
};


/**
 * Display cart tool buttons. If `savedCartObj` is supplied, supply it for the metadata.tsv line
 * in the resulting files.txt.
 */
const CartTools = ({
    cart,
    elements,
    selectedFileTerms,
    selectedDatasetTerms,
    selectedDatasetType,
    facetFields,
    visualizable,
    isFileViewOnly,
}) => {
    // Make a list of all the allowed dataset types currently in the cart.
    const usedDatasetTypes = new Set(
        elements
            .map((element) => atIdToType(element['@id']))
            .filter((type) => allowedDatasetTypes[type])
    );

    return (
        <div className="cart-tools">
            {elements.length > 0 ?
                <CartBatchDownload
                    cart={cart}
                    selectedFileTerms={selectedFileTerms}
                    selectedDatasetTerms={selectedDatasetTerms}
                    selectedDatasetType={selectedDatasetType}
                    facetFields={facetFields}
                    visualizable={visualizable}
                    isFileViewOnly={isFileViewOnly}
                />
            : null}
            <CartDatasetReport
                cart={cart}
                usedDatasetTypes={[...usedDatasetTypes]}
            />
        </div>
    );
};

CartTools.propTypes = {
    cart: PropTypes.object,
    /** Cart elements */
    elements: PropTypes.array,
    /** Selected file facet terms */
    selectedFileTerms: PropTypes.object,
    /** Selected dataset facet terms */
    selectedDatasetTerms: PropTypes.object,
    /** Currently selected dataset type */
    selectedDatasetType: PropTypes.string.isRequired,
    /** Currently used facet field definitions */
    facetFields: PropTypes.array.isRequired,
    /** True if only visualizable files should be downloaded */
    visualizable: PropTypes.bool,
    /** True if user has "File view" checked */
    isFileViewOnly: PropTypes.bool.isRequired,
};

CartTools.defaultProps = {
    cart: null,
    elements: [],
    selectedFileTerms: null,
    selectedDatasetTerms: null,
    visualizable: false,
};


/**
 * Display the pager control area.
 */
const CartPager = ({ currentPage, totalPageCount, updateCurrentPage }) => (
    <>
        {totalPageCount > 1 ?
            <div className="cart-pager-area">
                <Pager.Simple total={totalPageCount} current={currentPage} updateCurrentPage={updateCurrentPage} />
            </div>
        : null}
    </>
);

CartPager.propTypes = {
    /** Zero-based current page to display */
    currentPage: PropTypes.number.isRequired,
    /** Total number of pages */
    totalPageCount: PropTypes.number.isRequired,
    /** Called when user clicks pager controls */
    updateCurrentPage: PropTypes.func.isRequired,
};


/**
 * Displays controls at the top of search results within the tab content areas.
 */
const CartSearchResultsControls = ({
    cart,
    currentTab,
    elements,
    currentPage,
    totalPageCount,
    updateCurrentPage,
    fileViewOptions,
    cartType,
    loading,
}) => {
    const {
        filesToAddToFileView,
        fileViewName,
        fileViewControlsEnabled,
        isFileViewOnly,
    } = fileViewOptions;
    const readOnlyStatus = getReadOnlyState(cart);
    const pager = totalPageCount > 1 && (
        <CartPager
            currentPage={currentPage}
            totalPageCount={totalPageCount}
            updateCurrentPage={updateCurrentPage}
        />
    );
    const controls = currentTab === 'datasets' && cartType === 'ACTIVE'
        ? <CartRemoveElements elements={elements} loading={loading} />
        : currentTab === 'processeddata' && filesToAddToFileView?.length > 0 &&
            <FileViewControl
                files={filesToAddToFileView}
                fileViewName={fileViewName}
                fileViewControlsEnabled={fileViewControlsEnabled}
                isFileViewOnly={isFileViewOnly}
                disabled={cartType !== 'ACTIVE' || readOnlyStatus.any}
            />;

    return (controls || pager) && (
        <div className="cart-search-results-controls">
            {controls}
            {pager}
        </div>
    );
};

CartSearchResultsControls.propTypes = {
    /** Object for the current cart */
    cart: PropTypes.object.isRequired,
    /** Key of the currently selected tab */
    currentTab: PropTypes.string.isRequired,
    /** Array of currently displayed cart items */
    elements: PropTypes.array,
    /** Zero-based current page to display */
    currentPage: PropTypes.number.isRequired,
    /** Total number of pages */
    totalPageCount: PropTypes.number.isRequired,
    /** Called when user clicks pager controls */
    updateCurrentPage: PropTypes.func.isRequired,
    /** Options when displaying file view controls */
    fileViewOptions: PropTypes.exact({
        /** Files to add to file view, including those that can't */
        filesToAddToFileView: PropTypes.array,
        /** File view name */
        fileViewName: PropTypes.string,
        /** True to enable the file view buttons */
        fileViewControlsEnabled: PropTypes.bool,
        /** True if "File view" switch selected */
        isFileViewOnly: PropTypes.bool,
    }),
    /** Current cart type, e.g. ACTIVE, SHARED... */
    cartType: PropTypes.string.isRequired,
    /** True if cart still loading on page */
    loading: PropTypes.bool.isRequired,
};

CartSearchResultsControls.defaultProps = {
    elements: [],
    fileViewOptions: {},
};

/**
 * Add the datasets search results to the given array of datasets, only including individual
 * datasets -- not series objects.
 * @param {array} datasets Add new search result individual datasets to this array
 * @param {object} currentResults Dataset search results
 * @return {array} `datasets` with search-result datasets added
 */
const addToAccumulatingDatasets = (datasets, currentResults) => {
    if (currentResults['@graph'] && currentResults['@graph'].length > 0) {
        // Filter out series datasets; only consider individual datasets.
        const individualDatasets = currentResults['@graph'].filter((dataset) => !hasType(dataset, 'Series'));
        individualDatasets.forEach((dataset) => {
            // Mutate the datasets for those properties that need their values altered from how
            // they appear in search results.
            requestedFacetFields.forEach((facetField) => {
                if (facetField.getValue) {
                    dataset[facetField.field] = facetField.getValue(dataset);
                }
            });
        });

        // Return a new array combining the existing individual datasets with the datasets from
        // the given search results.
        return datasets.concat(individualDatasets);
    }

    // No search results; just return unchanged list of datasets.
    return datasets;
};


/**
 * Add the series search results to the given array of series.
 * @param {array} series Add new search results to this array
 * @param {object} currentResults Dataset search results
 * @return {array} `series` with search-result series added
 */
const addToAccumulatingSeries = (series, currentResults) => {
    if (currentResults['@graph']?.length > 0) {
        const seriesDatasets = currentResults['@graph'].filter((dataset) => hasType(dataset, 'Series'));

        // Return a new array combining the existing partial files with the additional files.
        return series.concat(seriesDatasets);
    }

    // No search results; just return unchanged list of datasets.
    return series;
};


/**
 * Adds partial file objects from a dataset search-result object to an existing array of partial
 * file objects. Mutate the file objects to include faceted properties from the relevant datasets.
 * @param {object} files Partial file objects being collected
 * @param {object} currentResults Dataset search results containing partial file objects to collect
 *
 * @return {object} Returns `files` copy with file information from `currentResults` added.
 */
const addToAccumulatingFiles = (files, currentResults) => {
    if (currentResults['@graph'] && currentResults['@graph'].length > 0) {
        const currentFilesPartial = [];
        currentResults['@graph'].forEach((dataset) => {
            if (dataset.files && dataset.files.length > 0) {
                dataset.files.forEach((file) => {
                    if (!file.restricted) {
                        // Mutate the files to include faceted properties from the dataset
                        // object before adding it to the accumulating list of files.
                        datasetFieldFileFacets.forEach((datasetFacet) => {
                            const [experimentProp] = datasetFacet.split('.');
                            file[experimentProp] = dataset[experimentProp];
                        });
                        currentFilesPartial.push(file);

                        // Mutate the files for any properties whose values need altering through
                        // their `getValue` properties from the facet definitions.
                        displayedFileFacetFields.forEach((facetField) => {
                            if (facetField.getValue) {
                                const [fileProp] = facetField.field.split('.');
                                file[fileProp] = facetField.getValue(file);
                            }
                        });

                        // Special case: mutate the files to copy the target/targets of the parent
                        // dataset.
                        if (dataset.target) {
                            file.target = dataset.target;
                        } else if (dataset.targets && dataset.targets.length > 0) {
                            file.targets = dataset.targets;
                        }
                    }
                });
            }
        });

        // Return a new array combining the existing partial files with the additional files.
        return files.concat(currentFilesPartial);
    }

    // No search results; just return unchanged list of partial files.
    return files;
};


/**
 * Content of the tabs with counters.
 */
const CounterTab = ({ title, count, icon, voice }) => (
    <div className="cart-tab" aria-label={`${count} ${voice}`}>
        {icon ? svgIcon(icon) : null}
        {title} <div className="cart-tab__count">{count}</div>
    </div>
);

CounterTab.propTypes = {
    /** Text title for the tab */
    title: PropTypes.string.isRequired,
    /** Counter value to display next to the tab */
    count: PropTypes.number.isRequired,
    /** ID of icon to display, if any */
    icon: PropTypes.string,
    /** Screen reader text */
    voice: PropTypes.string,
};

CounterTab.defaultProps = {
    icon: '',
    voice: 'items',
};


/**
 * Get information about the cart contents including:
 * cartType: Type of cart being displayed:
 *           'ACTIVE': Viewing the current cart
 *           'OBJECT': Viewing the cart specified in the URL
 * During page load, this function can get called for /cart-view/ but with `savedCartObj` not yet
 * filled in. Check the returned `cartType` for the empty string to detect this.
 * @param {object} context Cart search results object; often empty depending on cart type
 * @param {object} savedCartObj Cart object in Redux store for active logged-in carts
 *
 * @return {object} -
 * {
 *      {object} cart - Cart object from Redux for active carts or from context for object carts
 *      {string} cartType - Cart type: OBJECT, ACTIVE; '' if undetermined
 *      {string} cartName - Name of cart
 *      {array} cartDatasets - @ids of all datasets in cart
 * }
 */
const getCartInfo = (context, savedCartObj) => {
    let cart = null;
    let cartType = '';
    let cartName = '';
    let cartDatasets = [];
    if (context['@type'][0] === 'cart-view' && savedCartObj && Object.keys(savedCartObj).length > 0) {
        cart = savedCartObj;
        cartType = 'ACTIVE';
        cartName = savedCartObj.name;
        cartDatasets = savedCartObj.elements;
    } else if (context['@type'][0] === 'Cart') {
        // Viewing a saved cart at its unique path.
        cart = context;
        cartType = 'OBJECT';
        cartName = context.name;
        cartDatasets = context.elements;
    }
    return { cart, cartType, cartName, cartDatasets };
};


/**
 * Given search results containing datasets, add their compiled analyses to the array of compiled
 * analyses. A new array of compiled analyses gets generated every time.
 * @param {array} analyses Compiled analyses being accumulated
 * @param {object} currentResults Search results containing datasets
 *
 * @return {array} Compiled analyses after adding the ones from `currentResults`
 */
const addToAccumulatingAnalyses = (analyses, currentResults) => {
    // Generate a new batch of compiled analyses from the given search results.
    const currentAnalyses = compileDatasetAnalyses(currentResults['@graph']);

    // Add the files of any of the new batch that matches any of the given compiled analyses. Any
    // of the new batch that don't match a given one get added to the array of analyses.
    const nonMatchingAnalyses = currentAnalyses.reduce((accumulatedAnalyses, currentAnalysis) => {
        const matchingAnalysisIndex = analyses.findIndex((analysis) => analysis.title === currentAnalysis.title);
        if (matchingAnalysisIndex === -1) {
            // None of the given analyses matches one of the new batch, so add that one to the end
            // of the list of new non-matching compiled analyses.
            return accumulatedAnalyses.concat(currentAnalysis);
        }

        // One of the given analyses matches a new compiled analysis, so add the new ones' files to
        // the file list of the given analysis that matches. Then return the accumulating non-
        // matching analyses unchanged.
        analyses[matchingAnalysisIndex].files.push(...currentAnalysis.files);
        return accumulatedAnalyses;
    }, []);
    return analyses.concat(nonMatchingAnalyses);
};


/**
 * Replace the files' analyses property with the titles of the compiled analyses that refer
 * to them. Mutates the files in `files`.
 * @param {array} files Partial file objects to alter
 * @param {array} analyses Compiled analysis objects for all datasets in cart
 */
const processFilesAnalyses = (files, analyses) => {
    files.forEach((file) => {
        const matchingAnalysis = analyses.find((analysis) => analysis.files.includes(file['@id']));
        if (matchingAnalysis) {
            file.analysis = matchingAnalysis.title;
        }
    });
};


/**
 * After retrieving the dataset objects, they get passed to this function to extract the Annotation
 * `targets` property or other datasets' `target` property, and then mutate each dataset to contain
 * the calculated `targetList` array property so it can generate a facet.
 * @param {array} datasets Datasets to process for `targetList` property; each dataset mutated
 */
const processDatasetTargetList = (datasets) => {
    datasets.forEach((dataset) => {
        let targetList = [];
        if (dataset['@type'][0] === 'Annotation' && dataset.targets.length > 0) {
            targetList = dataset.targets.map((target) => target.label);
        } else if (dataset.target) {
            targetList = [dataset.target.label];
        }
        dataset.targetList = targetList;
    });
};


/**
 * Fill in a `_relatedSeries` property of each of the given `datasets` objects with an array of the
 * @ids of the given `series` objects that include each dataset. That allows you to see what series
 * objects include a given dataset, if any.
 * @param {object} series Array of series objects in cart to apply to their related datasets
 * @param {object} datasets Array of dataset objects in cart to apply their related series
 */
const processSeriesDatasets = (series, datasets) => {
    if (series && series.length > 0) {
        series.forEach((singleSeries) => {
            if (singleSeries.related_datasets && singleSeries.related_datasets.length > 0) {
                singleSeries.related_datasets.forEach((relatedDataset) => {
                    const matchingRelatedDataset = datasets.find((dataset) => relatedDataset['@id'] === dataset['@id']);
                    if (matchingRelatedDataset) {
                        if (matchingRelatedDataset._relatedSeries) {
                            matchingRelatedDataset._relatedSeries.push(singleSeries['@id']);
                        } else {
                            matchingRelatedDataset._relatedSeries = [singleSeries['@id']];
                        }
                    }
                });
            }
        });
    }
};


/**
 * Use the following order when sorting files by status for evaluating pseudo-default files.
 */
const pseudoDefaultFileStatusOrder = ['released', 'archived', 'in progress'];


/**
 * Sort an array of files by their statuses according to their order in
 * pseudoDefaultFileStatusOrder. Anything not in pseudoDefaultFileStatusOrder gets sorted randomly
 * at the end.
 * @param {array} files Files to sort
 * @return {array} Files sorted by the three following statuses
 */
const sortPseudoDefaultFilesByStatus = (files) => (
    _(files).sortBy((file) => {
        const foundIndex = pseudoDefaultFileStatusOrder.indexOf(file.status);
        return foundIndex !== -1 ? foundIndex : pseudoDefaultFileStatusOrder.length;
    })
);


/**
 * Sort an array of assemblies, newer assemblies first. Carts don’t track genome_annotation, so those
 * don't enter into this sorting.
 * @param {array} assemblies Assemblies to sort
 * @return {array} Files sorted by assembly.
 */
const sortAssemblies = (assemblies) => (
    _(assemblies).sortBy((assembly) => (
        -computeAssemblyAnnotationValue(assembly)
    ))
);


/**
 * Mutate the files of the given datasets that have no files with preferred_default set so that
 * they appear as though they had preferred_default set. Once wranglers have patched all
 * appropriate files' preferred_default properties, this function serves no purpose. A number of
 * criteria determine how and whether any files within a dataset get this modification. Exported
 * for Jest test.
 * @param {array} datasets Datasets containing files to mutate with preferred_default
 */
export const processPseudoDefaultFiles = (datasets = []) => {
    datasets.forEach((dataset) => {
        // Consider only the visualizable files of datasets that contain no default files.
        if (dataset.files && dataset.files.length > 0 && filterForDefaultFiles(dataset.files).length === 0) {
            const visualizableFiles = sortPseudoDefaultFilesByStatus(filterForVisualizableFiles(dataset.files));
            if (visualizableFiles.length > 0) {
                let pseudoDefaultFiles = [];
                const mixedBioRepFiles = visualizableFiles.filter((file) => file.biological_replicates.length > 1);
                if (mixedBioRepFiles.length > 0) {
                    // Process files with multiple biological replicates. Don't modify any of the
                    // other files.
                    pseudoDefaultFiles = mixedBioRepFiles;
                } else {
                    // No files have multiple biological replicates. Get all the output_type values
                    // from all visualizable files.
                    const outputTypes = visualizableFiles.reduce((accOutputTypes, file) => accOutputTypes.add(file.output_type), new Set());
                    if (outputTypes.size > 1) {
                        // Multiple output types among the files. Group first by sorted assembly,
                        // then replicate, and then by output_type.
                        const assemblyFiles = _(visualizableFiles).groupBy((file) => file.assembly);
                        const sortedAssemblies = sortAssemblies(Object.keys(assemblyFiles));
                        sortedAssemblies.forEach((assembly) => {
                            const replicateFiles = _(assemblyFiles[assembly]).groupBy((file) => file.biological_replicates[0]);
                            Object.keys(replicateFiles).forEach((replicate) => {
                                const outputTypeFiles = _(replicateFiles[replicate]).groupBy((file) => file.output_type);
                                Object.keys(outputTypeFiles).forEach((outputType) => {
                                    // Select the first bigWig and first bigBed within each
                                    // output_type within each replicate.
                                    const firstBigWig = outputTypeFiles[outputType].find((file) => file.file_format === 'bigWig');
                                    const firstBigBed = outputTypeFiles[outputType].find((file) => file.file_format === 'bigBed');
                                    pseudoDefaultFiles.push(..._.compact([firstBigWig, firstBigBed]));
                                });
                            });
                        });
                    } else {
                        // Single output type among all the files. Get all files with a single
                        // biological replicate value of 1 and select the first bigWig and bigBed
                        // of those.
                        const bioRep1Files = visualizableFiles.filter((file) => file.biological_replicates && file.biological_replicates[0] === 1);
                        if (bioRep1Files.length > 0) {
                            const firstBigWig = bioRep1Files.find((file) => file.file_format === 'bigWig');
                            const firstBigBed = bioRep1Files.find((file) => file.file_format === 'bigBed');
                            pseudoDefaultFiles = _.compact([firstBigWig, firstBigBed]);
                        }
                    }
                }

                // Mutate the selected pseudo default files to have the preferred_default property.
                pseudoDefaultFiles.forEach((file) => {
                    file.pseudo_default = true;
                });
            }
        }
    });
};


/**
 * Retrieve partial file objects for all given datasets, as well as a list of datasets viewable at
 * the user's access level -- needed for shared carts.
 * @param {array} datasetsIds Array of dataset @ids to retrieve
 * @param {func} facetLoadHandler Called with progress in loading chunks of datasets1
 * @param {func} fetch System fetch
 * @param {object} session System session
 *
 * @return {promise}:
 * {
 *      datasetFiles - Array of all partial file objects in all datasets
 *      datasets - Array of all datasets viewable at user's access level; subset of `datasetsIds`
 * }
 */
const retrieveDatasetsFiles = (datasetsIds, facetProgressHandler, fetch, session) => {
    // Break incoming array of dataset @ids into manageable chunks of arrays, each with
    // CHUNK_SIZE elements. Search results from all these chunks get consolidated before returning
    // a promise.
    const CHUNK_SIZE = 100;
    const chunks = [];
    for (let datasetIndex = 0; datasetIndex < datasetsIds.length; datasetIndex += CHUNK_SIZE) {
        chunks.push(datasetsIds.slice(datasetIndex, datasetIndex + CHUNK_SIZE));
    }

    // Using the arrays of dataset @id arrays, do a sequence of searches of CHUNK_SIZE datasets
    // adding to extract information to display the facets, search results, and visualization.
    facetProgressHandler(null);
    return chunks.reduce((promiseChain, currentChunk, currentChunkIndex) => (
        // As each experiment search-result promise resolves, add its results to the array of
        // partial files and facets in `accumulatingResults`.
        promiseChain.then((accumulatingResults) => (
            // Request one chunk of datasets. `currentResults` contains the request search
            // results including the partial file objects we need.
            requestDatasets(currentChunk, fetch, session).then((currentResults) => {
                // Update progress on each chunk.
                facetProgressHandler(Math.round(((currentChunkIndex + 1) / chunks.length) * 100));

                // * Temporary code until all experiments have preferred_default files set: Mutate
                // * the files in each returned dataset to include a preferred_default property
                // * if they meet certain criteria.
                processPseudoDefaultFiles(currentResults['@graph']);

                // Add the chunk's worth of results to the array of partial files and facets
                // we're accumulating.
                return {
                    datasetFiles: addToAccumulatingFiles(accumulatingResults.datasetFiles, currentResults),
                    datasets: addToAccumulatingDatasets(accumulatingResults.datasets, currentResults),
                    series: addToAccumulatingSeries(accumulatingResults.series, currentResults),
                    datasetAnalyses: addToAccumulatingAnalyses(accumulatingResults.datasetAnalyses, currentResults),
                };
            })
        ))
    ), Promise.resolve({ datasetFiles: [], datasets: [], series: [], datasetAnalyses: [] })).then(({ datasetFiles, datasets, series, datasetAnalyses }) => {
        facetProgressHandler(-1);

        // Mutate the files or datasets for their calculated properties.
        processFilesAnalyses(datasetFiles, datasetAnalyses);
        processDatasetTargetList(datasets);
        processSeriesDatasets(series, datasets);
        return { datasetFiles, datasets, series, datasetAnalyses: sortDatasetAnalyses(datasetAnalyses) };
    });
};


/**
 * Filter an array of files to ones included in the current file view.
 * @param {array} fileList Files to filter
 * @param {array} fileViewPaths @ids of files in file view
 * @returns {array} Filtered `fileList`
 */
export const filterForFileView = (fileList, fileViewPaths) => {
    if (fileList.length > 0 && fileViewPaths.length > 0) {
        return fileList.filter((file) => fileViewPaths.includes(file['@id']));
    }
    return [];
};


/**
 * Reducer function for setting the pager page numbers for each of the cart tabs.
 * @param {object} state Contains pager page numbers; do not mutate
 * @param {object} action Contains page number and tab to update
 *
 * @return {object} Copy of `state` updated with new page numbers for a tab key
 */
const reducerTabPanePageNumber = (state, action) => {
    // action.tab is the key of the tab needing its value updated.
    const newPages = { ...state };
    newPages[action.tab] = action.pageNumber;
    return newPages;
};


/**
 * Reducer function for setting the pager total page counts for each of the cart tabs.
 * @param {object} state Contains the pager total page counts; do not mutate
 * @param {object} action Contains total page count and tab to update
 *
 * @return {object} Copy of `state` updated with new values for a tab key
 */
const reducerTabPaneTotalPageCount = (state, action) => {
    // action.tab is the key of the tab needing its value updated.
    const newPageCounts = { ...state };
    newPageCounts[action.tab] = action.totalPageCount;
    return newPageCounts;
};


/**
 * Renders the cart search results page. Display either:
 * 1. OBJECT (/carts/<uuid>)
 *    * context contains items to display (shared cart).
 * 2. ACTIVE (/cart-view/) containing the current cart's contents
 *    * savedCartObj contains items to display (your own logged-in cart)
 * All files in all cart experiments are kept in an array of partial file objects which contain
 * only the file object properties requested in `requestedFacetFields`. When visualizing a subset
 * of these files, complete file objects get retrieved.
 */
const CartComponent = ({ context, savedCartObj, inProgress, fetch, session, locationHref }) => {
    // Keeps track of currently selected dataset facet terms keyed by facet fields.
    const [selectedDatasetTerms, setSelectedDatasetTerms] = React.useState({});
    // Keeps track of currently selected file facet terms keyed by facet fields.
    const [selectedFileTerms, setSelectedFileTerms] = React.useState({});
    // Array of datasets the user has access to view; subset of `cartDatasets`.
    const [viewableDatasets, setViewableDatasets] = React.useState([]);
    // Array of series objects in the cart.
    const [allSeries, setAllSeries] = React.useState([]);
    // True if the user has selected viewing only file view files
    const [isFileViewOnly, setIsFileViewOnly] = React.useState(false);
    // Compiled analyses applicable to the current datasets.
    const [analyses, setAnalyses] = React.useState([]);
    // Currently displayed page number for each tab panes; for pagers.
    const [pageNumbers, dispatchPageNumbers] = React.useReducer(reducerTabPanePageNumber, { series: 0, datasets: 0, browser: 0, processeddata: 0, rawdata: 0 });
    // Total number of displayed pages for each tab pane; for pagers.
    const [totalPageCount, dispatchTotalPageCounts] = React.useReducer(reducerTabPaneTotalPageCount, { series: 0, datasets: 0, browser: 0, processeddata: 0, rawdata: 0 });
    // Currently displayed tab; match key of first TabPanelPane initially.
    const [displayedTab, setDisplayedTab] = React.useState('datasets');
    // Facet-loading progress bar value; null=indeterminate; -1=disable
    const [facetProgress, setFacetProgress] = React.useState(null);
    // True if only facet terms for visualizable files displayed.
    const [visualizableOnly, setVisualizableOnly] = React.useState(false);
    // True if only preferred_default files displayed.
    const [defaultOnly, setDefaultOnly] = React.useState(true);
    // All partial file objects in the cart datasets. Not affected by currently selected facets.
    const [allFiles, setAllFiles] = React.useState([]);
    // Tracks previous contents of `cartDatasets` to know if the cart contents have changed.
    const cartDatasetsRef = React.useRef([]);
    // Series manager states and actions.
    const seriesManager = useSeriesManager();

    // Retrieve current unfiltered cart information regardless of its source (object or active).
    // Determine if the cart contents have changed.
    const { cart, cartType, cartName, cartDatasets } = getCartInfo(context, savedCartObj);
    const isCartDatasetsChanged = !_.isEqual(cartDatasetsRef.current, cartDatasets);
    if (isCartDatasetsChanged) {
        cartDatasetsRef.current = cartDatasets;
    }
    const readOnlyState = getReadOnlyState(cart);

    // Filter out conditional facets.
    const usedFileFacetFields = React.useMemo(() => {
        // Only the assembly facet is active when "File view" checked.
        if (isFileViewOnly) {
            return [displayedFileFacetFields.find((facetField) => facetField.field === 'assembly')];
        }

        // Get a subset of available facets when "Show default data only" checked.
        if (defaultOnly) {
            return displayedFileFacetFields.filter((facetField) => facetField.preferred);
        }

        // Otherwise, all facets available.
        return displayedFileFacetFields;
    }, [defaultOnly, isFileViewOnly]);

    // Get the files selected in the current file view.
    const selectedView = savedCartObj && savedCartObj.file_views
        ? savedCartObj.file_views.find((view) => view.title === DEFAULT_FILE_VIEW_NAME)
        : [];
    const selectedFilesInFileView = selectedView && selectedView.files ? selectedView.files : [];

    // Build the dataset facets based on the currently selected facet terms.
    const { datasetFacets, selectedDatasets } = React.useMemo(() => {
        if (!isFileViewOnly) {
            return assembleDatasetFacets(selectedDatasetTerms, viewableDatasets, displayedDatasetFacetFields);
        }
        return { datasetFacets: null, selectedDatasets: viewableDatasets };
    }, [selectedDatasetTerms, viewableDatasets, isFileViewOnly, isCartDatasetsChanged]);

    // Build the file facets based on the currently selected facet terms.
    const selectedDatasetFiles = React.useMemo(() => filterForDatasetFiles(allFiles, selectedDatasets), [allFiles, selectedDatasets]);
    const { fileFacets, selectedFiles, selectedVisualizableFiles } = React.useMemo(() => {
        // If "File view" selected, filter out files not in the selected view. Build a single
        // assembly facet, ignoring all others.
        if (isFileViewOnly) {
            const files = filterForFileView(allFiles.filter((file) => file.assembly), selectedFilesInFileView);
            const { fileFacets: facets, selectedFiles: allSelectedFiles } = assembleFileFacets(selectedFileTerms, files, [], usedFileFacetFields);
            const visualizableSelectedFiles = filterForVisualizableFiles(allSelectedFiles);
            return { fileFacets: facets, selectedFiles: files, selectedVisualizableFiles: visualizableSelectedFiles };
        }

        let files = defaultOnly ? filterForDefaultFiles(selectedDatasetFiles) : selectedDatasetFiles;
        files = visualizableOnly ? filterForVisualizableFiles(files) : files;

        // While "Show default data only" selected, further restrict displayed files to those in
        // released analyses.
        if (defaultOnly) {
            const analysisFilteredFiles = filterForReleasedAnalyses(files, analyses);
            if (analysisFilteredFiles.length > 0) {
                files = analysisFilteredFiles;
            }
        }

        const { fileFacets: facets, selectedFiles: allSelectedFiles } = assembleFileFacets(selectedFileTerms, files, analyses, usedFileFacetFields);
        const visualizableSelectedFiles = filterForVisualizableFiles(allSelectedFiles);
        return { fileFacets: facets, selectedFiles: allSelectedFiles, selectedVisualizableFiles: visualizableSelectedFiles };
    }, [
        selectedFileTerms,
        selectedDatasets,
        selectedFilesInFileView.length,
        isFileViewOnly,
        visualizableOnly,
        defaultOnly,
        selectedDatasetFiles,
        analyses,
        allFiles,
        usedFileFacetFields,
    ]);

    // Construct the file lists for the genome browser and raw file tabs.
    const rawdataFiles = React.useMemo(() => selectedDatasetFiles.filter((files) => files.output_category === 'raw data'), [selectedDatasetFiles]);
    const selectedProcessedFiles = React.useMemo(() => selectedFiles.filter((files) => files.processed), [selectedFiles]);

    // Called when the user selects a new page of items to view using the pager.
    const updateDisplayedPage = (newDisplayedPage) => {
        // Set the new page number for the currently-displayed tab pane.
        dispatchPageNumbers({ tab: displayedTab, pageNumber: newDisplayedPage });
    };

    // Get the currently selected dataset type if the user selected exactly one.
    const selectedDatasetType = selectedDatasetTerms.type && selectedDatasetTerms.type.length === 1
        ? selectedDatasetTerms.type[0]
        : '';

    // Called when the user clicks any term in any facet.
    const handleDatasetTermClick = (clickedField, clickedTerm) => {
        // The user clicked a checkbox facet. Determine whether we need to add or subtract
        // a term from the facet selections.
        const newSelectedTerms = {};
        const addTerm = selectedDatasetTerms[clickedField].indexOf(clickedTerm) === -1;
        if (addTerm) {
            // Adding a selected term. Copy the previous selectedDatasetTerms, adding the newly
            // selected term in its facet in sorted position.
            displayedDatasetFacetFields.forEach((facetField) => {
                if (clickedField === facetField.field) {
                    // Clicked term belongs to this field's facet. Insert it into its
                    // sorted position in a copy of the selectedDatasetTerms array.
                    const sortedIndex = _(selectedDatasetTerms[facetField.field]).sortedIndex(clickedTerm);
                    newSelectedTerms[facetField.field] = [...selectedDatasetTerms[facetField.field].slice(0, sortedIndex), clickedTerm, ...selectedDatasetTerms[facetField.field].slice(sortedIndex)];
                } else {
                    // Clicked term doesn't belong to this field's facet. Just copy the
                    // `selectedDatasetTerms` array unchanged.
                    newSelectedTerms[facetField.field] = selectedDatasetTerms[facetField.field].slice(0);
                }
            });
        } else {
            // Removing a selected term. Copy the previous selectedDatasetTerms, filtering out
            // the unselected term in its facet.
            displayedDatasetFacetFields.forEach((facetField) => {
                newSelectedTerms[facetField.field] = selectedDatasetTerms[facetField.field].filter((term) => term !== clickedTerm);
            });
        }

        setSelectedDatasetTerms(newSelectedTerms);
    };

    // Called when the user clicks any term in any facet.
    const handleFileTermClick = (clickedField, clickedTerm) => {
        // The user clicked a checkbox facet. Determine whether we need to add or subtract
        // a term from the facet selections.
        const newSelectedTerms = {};
        const addTerm = selectedFileTerms[clickedField].indexOf(clickedTerm) === -1;
        if (addTerm) {
            // Adding a selected term. Copy the previous selectedFacetTerms, adding the newly
            // selected term in its facet in sorted position.
            displayedFileFacetFields.forEach((facetField) => {
                if (clickedField === facetField.field) {
                    // Clicked term belongs to this field's facet. Insert it into its
                    // sorted position in a copy of the selectedTerms array.
                    const sortedIndex = _(selectedFileTerms[facetField.field]).sortedIndex(clickedTerm);
                    newSelectedTerms[facetField.field] = [...selectedFileTerms[facetField.field].slice(0, sortedIndex), clickedTerm, ...selectedFileTerms[facetField.field].slice(sortedIndex)];
                } else {
                    // Clicked term doesn't belong to this field's facet. Just copy the
                    // `selectedTerms` array unchanged.
                    newSelectedTerms[facetField.field] = selectedFileTerms[facetField.field].slice(0);
                }
            });
        } else {
            // Removing a selected term. Copy the previous selectedFacetTerms, filtering out
            // the unselected term in its facet.
            displayedFileFacetFields.forEach((facetField) => {
                newSelectedTerms[facetField.field] = selectedFileTerms[facetField.field].filter((term) => term !== clickedTerm);
            });
        }

        setSelectedFileTerms(newSelectedTerms);
    };

    // Called when the user clicks the Show Visualizable Only checkbox.
    const handleVisualizableOnlyChange = React.useCallback(() => {
        setVisualizableOnly((oldVisualizableOnly) => !oldVisualizableOnly);
    }, []);

    // Called when the user clicks the Show Default Data Only checkbox.
    const handlePreferredOnlyChange = React.useCallback(() => {
        setDefaultOnly((prevPreferredOnly) => !prevPreferredOnly);
        setVisualizableOnly(false);
    }, []);

    // Called when the user clicks a tab.
    const handleTabClick = (newTab) => {
        setDisplayedTab(newTab);
    };

    // Clear all selected dataset terms within the facet specified by the given field.
    const clearDatasetFacetSelections = (field) => {
        const newSelectedDatasetTerms = { ...selectedDatasetTerms };
        newSelectedDatasetTerms[field] = [];
        setSelectedDatasetTerms(newSelectedDatasetTerms);
    };

    // Clear all selected file terms within the facet specified by the given field.
    const clearFileFacetSelections = (field) => {
        const newSelectedFileTerms = { ...selectedFileTerms };
        newSelectedFileTerms[field] = [];
        setSelectedFileTerms(newSelectedFileTerms);
    };

    // Handle a click on the "File view" checkbox.
    const handleFileViewOnlyClick = () => {
        setIsFileViewOnly((prevFileViewOnly) => !prevFileViewOnly);
    };

    // Turn off "Set file view" checkbox if no files are in the current file view.
    React.useEffect(() => {
        if (selectedFilesInFileView.length === 0) {
            setIsFileViewOnly(false);
        }
    }, [selectedFilesInFileView.length]);

    React.useEffect(() => {
        // Reset the currently selected tab if the user selects `isFileViewOnly`.
        if (isFileViewOnly && displayedTab !== 'browser' && displayedTab !== 'processeddata') {
            setDisplayedTab('processeddata');
        }
    }, [isFileViewOnly]);

    // Enable the "Set file view" checkbox if the hashtag in the URL matches the current file view.
    React.useEffect(() => {
        const parsedUrl = url.parse(locationHref);
        if (parsedUrl.hash === `#${DEFAULT_FILE_VIEW_NAME}`) {
            setIsFileViewOnly(true);
            setDisplayedTab('processeddata');
        }
    }, [locationHref]);

    // Use the file information to build the facets and its initial selections. Resetting the
    // facets to their initial states should only happen with a change to files.
    React.useEffect(() => {
        // Reset file terms.
        const newSelectedFileTerms = initSelectedTerms(displayedFileFacetFields);
        setSelectedFileTerms(newSelectedFileTerms);

        // Reset dataset terms.
        const newSelectedDatasetTerms = initSelectedTerms(displayedDatasetFacetFields);
        setSelectedDatasetTerms(newSelectedDatasetTerms);
    }, [allFiles]);

    // After mount, we can fetch all datasets in the cart that are viewable at the user's
    // permission level and from them extract all their files.
    React.useEffect(() => {
        if (isCartDatasetsChanged) {
            retrieveDatasetsFiles(cartDatasets, setFacetProgress, fetch, session).then(({ datasetFiles, datasets, series, datasetAnalyses }) => {
                // Mutate files for special cases.
                datasetFiles.forEach((file) => {
                    // De-embed any embedded datasets.files.dataset.
                    if (typeof file.dataset === 'object') {
                        file.dataset = file.dataset['@id'];
                    }
                });

                setAllFiles(datasetFiles);
                setViewableDatasets(datasets);
                setAllSeries(series);
                setAnalyses(datasetAnalyses);
            });
        }
    }, [isCartDatasetsChanged]);

    // Data changes or initial load need a total-page-count calculation.
    React.useEffect(() => {
        const seriesPageCount = calcTotalPageCount(allSeries.length, constants.PAGE_ELEMENT_COUNT);
        const datasetPageCount = calcTotalPageCount(selectedDatasets.length, constants.PAGE_ELEMENT_COUNT);
        const browserPageCount = calcTotalPageCount(selectedVisualizableFiles.length, constants.PAGE_TRACK_COUNT);
        const processedDataPageCount = calcTotalPageCount(selectedProcessedFiles.length, constants.PAGE_FILE_COUNT);
        const rawdataPageCount = calcTotalPageCount(rawdataFiles.length, constants.PAGE_FILE_COUNT);
        dispatchTotalPageCounts({ tab: 'series', totalPageCount: seriesPageCount });
        dispatchTotalPageCounts({ tab: 'datasets', totalPageCount: datasetPageCount });
        dispatchTotalPageCounts({ tab: 'browser', totalPageCount: browserPageCount });
        dispatchTotalPageCounts({ tab: 'processeddata', totalPageCount: processedDataPageCount });
        dispatchTotalPageCounts({ tab: 'rawdata', totalPageCount: rawdataPageCount });

        // Go to first page if current page number goes out of range of new page count.
        if (pageNumbers.series >= seriesPageCount) {
            dispatchPageNumbers({ tab: 'series', pageNumber: 0 });
        }
        if (pageNumbers.datasets >= datasetPageCount) {
            dispatchPageNumbers({ tab: 'datasets', pageNumber: 0 });
        }
        if (pageNumbers.browser >= browserPageCount) {
            dispatchPageNumbers({ tab: 'browser', pageNumber: 0 });
        }
        if (pageNumbers.processeddata >= processedDataPageCount) {
            dispatchPageNumbers({ tab: 'processeddata', pageNumber: 0 });
        }
        if (pageNumbers.rawdata >= rawdataPageCount) {
            dispatchPageNumbers({ tab: 'rawdata', pageNumber: 0 });
        }
    }, [selectedDatasets, selectedVisualizableFiles, selectedProcessedFiles, rawdataFiles, pageNumbers.datasets, pageNumbers.browser, pageNumbers.processeddata, pageNumbers.rawdata]);

    return (
        <CartViewContext.Provider
            value={{
                allSeriesInCart: allSeries,
                allDatasetsInCart: viewableDatasets,
                setManagedSeries: seriesManager.setManagedSeries,
            }}
        >
            <div className={itemClass(context, 'view-item')}>
                <header>
                    <h1>{cartName}</h1>
                    <CartStatus cart={cart} />
                    {(cartDatasets.length > 0 || allSeries.length > 0) &&
                        <>
                            <CartDescription cart={cart} cartType={cartType} isCartReadOnly={readOnlyState.any} />
                            <CartAccessories
                                cart={cart}
                                viewableDatasets={viewableDatasets.map((dataset) => dataset['@id'])}
                                inProgress={inProgress}
                                cartType={cartType}
                            />
                            {cartType === 'OBJECT' ? <ItemAccessories item={context} /> : null}
                        </>
                    }
                </header>
                <Panel addClasses="cart__result-table">
                    {selectedDatasets.length > 0 ?
                        <PanelHeading addClasses="cart__header">
                            <CartTools
                                cart={cart}
                                elements={viewableDatasets}
                                selectedFileTerms={selectedFileTerms}
                                selectedDatasetTerms={selectedDatasetTerms}
                                selectedDatasetType={selectedDatasetType}
                                facetFields={displayedFileFacetFields.concat(displayedDatasetFacetFields)}
                                savedCartObj={savedCartObj}
                                cartType={cartType}
                                sharedCart={context}
                                visualizable={visualizableOnly}
                                isFileViewOnly={isFileViewOnly}
                            />
                            <CartFileViewOnlyToggle
                                isFileViewOnly={isFileViewOnly}
                                updateFileViewOnly={handleFileViewOnlyClick}
                                selectedFilesInFileView={selectedFilesInFileView}
                            />
                        </PanelHeading>
                    : null}
                    <PanelBody>
                        {cartDatasets.length > 0 || allSeries.length > 0 ?
                            <div className="cart__display">
                                {!isFileViewOnly
                                    ?
                                        <CartFacets
                                            datasetProps={{
                                                facets: datasetFacets,
                                                selectedTerms: selectedDatasetTerms,
                                                termClickHandler: handleDatasetTermClick,
                                                clearFacetSelections: clearDatasetFacetSelections,
                                            }}
                                            fileProps={{
                                                facets: fileFacets,
                                                selectedTerms: selectedFileTerms,
                                                termClickHandler: handleFileTermClick,
                                                clearFacetSelections: clearFileFacetSelections,
                                                usedFacetFields: usedFileFacetFields,
                                            }}
                                            options={{
                                                visualizableOnly,
                                                visualizableOnlyChangeHandler: handleVisualizableOnlyChange,
                                                preferredOnly: defaultOnly,
                                                preferredOnlyChangeHandler: handlePreferredOnlyChange,
                                                disabled: displayedTab === 'series',
                                            }}
                                            datasets={selectedDatasets}
                                            files={selectedFiles}
                                            facetProgress={facetProgress}
                                        />
                                    : (
                                        displayedTab === 'browser'
                                            ?
                                                <CartFacetsFileView
                                                    files={selectedVisualizableFiles}
                                                    facetProgress={facetProgress}
                                                    fileProps={{
                                                        facets: fileFacets,
                                                        selectedTerms: selectedFileTerms,
                                                        termClickHandler: handleFileTermClick,
                                                    }}
                                                />
                                            : <CartFacetsStandin files={displayedTab === 'processeddata' ? selectedProcessedFiles : []} facetProgress={facetProgress} />
                                    )
                                }
                                <TabPanel
                                    tabPanelCss="cart__display-content"
                                    tabs={!isFileViewOnly
                                        ? {
                                            series: 'Series',
                                            datasets: 'All datasets',
                                            browser: 'Genome browser',
                                            processeddata: 'Processed',
                                            rawdata: 'Raw',
                                        } : {
                                            browser: 'Genome browser',
                                            processeddata: 'Processed',
                                        }
                                    }
                                    tabDisplay={!isFileViewOnly
                                        ? {
                                            series: <CounterTab title="Series" count={allSeries.length} icon="dataset" voice="series" />,
                                            datasets: (
                                                <CounterTab
                                                    title={`Selected ${selectedDatasetType && datasetTabTitles[selectedDatasetType] ? datasetTabTitles[selectedDatasetType] : 'datasets'}`}
                                                    count={selectedDatasets.length}
                                                    icon="dataset"
                                                    voice="selected datasets"
                                                />
                                            ),
                                            browser: (
                                                <CounterTab
                                                    title="Genome browser"
                                                    count={selectedFileTerms.assembly?.length === 1 ? selectedVisualizableFiles.length : 0}
                                                    icon="file"
                                                    voice="visualizable tracks"
                                                />
                                            ),
                                            processeddata: <CounterTab title="Processed" count={selectedProcessedFiles.length} icon="file" voice="processed data files" />,
                                            rawdata: <CounterTab title="Raw" count={rawdataFiles.length} icon="file" voice="raw data files" />,
                                        } : {
                                            browser: <CounterTab title="Genome browser" count={selectedFileTerms.assembly?.length === 1 ? selectedVisualizableFiles.length : 0} icon="file" voice="visualizable tracks" />,
                                            processeddata: <CounterTab title="Processed" count={selectedProcessedFiles.length} icon="file" voice="processed data files" />,
                                        }
                                    }
                                    selectedTab={displayedTab}
                                    handleTabClick={handleTabClick}
                                >
                                    {!isFileViewOnly ?
                                        <TabPanelPane key="series">
                                            <CartSearchResults
                                                elements={allSeries}
                                                currentPage={pageNumbers.series}
                                                cartControls={cartType !== 'OBJECT'}
                                                isReadOnly={readOnlyState.any}
                                                loading={facetProgress !== -1}
                                            />
                                        </TabPanelPane>
                                    : null}
                                    {!isFileViewOnly ?
                                        <TabPanelPane key="datasets">
                                            <CartSearchResultsControls
                                                cart={cart}
                                                currentTab={displayedTab}
                                                elements={selectedDatasets}
                                                currentPage={pageNumbers.datasets}
                                                totalPageCount={totalPageCount.datasets}
                                                updateCurrentPage={updateDisplayedPage}
                                                cartType={cartType}
                                                loading={facetProgress !== -1}
                                            />
                                            <CartSearchResults
                                                elements={selectedDatasets}
                                                currentPage={pageNumbers.datasets}
                                                cartControls={cartType !== 'OBJECT'}
                                                isReadOnly={readOnlyState.any}
                                                loading={facetProgress !== -1}
                                            />
                                        </TabPanelPane>
                                    : null}
                                    <TabPanelPane key="browser">
                                        <CartSearchResultsControls
                                            cart={cart}
                                            currentTab={displayedTab}
                                            elements={selectedDatasets}
                                            currentPage={pageNumbers.browser}
                                            totalPageCount={totalPageCount.browser}
                                            updateCurrentPage={updateDisplayedPage}
                                            cartType={cartType}
                                            loading={facetProgress !== -1}
                                        />
                                        <CartBrowser files={selectedVisualizableFiles} assemblies={selectedFileTerms.assembly || []} pageNumber={pageNumbers.browser} loading={facetProgress !== -1} />
                                    </TabPanelPane>
                                    <TabPanelPane key="processeddata">
                                        <CartSearchResultsControls
                                            cart={cart}
                                            currentTab={displayedTab}
                                            elements={selectedDatasets}
                                            currentPage={pageNumbers.processeddata}
                                            totalPageCount={totalPageCount.processeddata}
                                            updateCurrentPage={updateDisplayedPage}
                                            fileViewOptions={{
                                                filesToAddToFileView: filterForVisualizableFiles(selectedProcessedFiles),
                                                fileViewName: DEFAULT_FILE_VIEW_NAME,
                                                fileViewControlsEnabled: true,
                                                isFileViewOnly,
                                            }}
                                            cartType={cartType}
                                            loading={facetProgress !== -1}
                                        />
                                        <CartFiles
                                            cart={cart}
                                            files={selectedProcessedFiles}
                                            isFileViewOnly={isFileViewOnly}
                                            selectedFilesInFileView={selectedFilesInFileView}
                                            currentPage={pageNumbers.processeddata}
                                            defaultOnly={defaultOnly}
                                            cartType={cartType}
                                            loading={facetProgress !== -1}
                                        />
                                    </TabPanelPane>
                                    {!isFileViewOnly ?
                                        <TabPanelPane key="rawdata">
                                            <CartSearchResultsControls
                                                cart={cart}
                                                currentTab={displayedTab}
                                                elements={selectedDatasets}
                                                currentPage={pageNumbers.rawdata}
                                                totalPageCount={totalPageCount.rawdata}
                                                updateCurrentPage={updateDisplayedPage}
                                                cartType={cartType}
                                                loading={facetProgress !== -1}
                                            />
                                            <CartFiles
                                                cart={cart}
                                                files={rawdataFiles}
                                                currentPage={pageNumbers.rawdata}
                                                cartType={cartType}
                                                loading={facetProgress !== -1}
                                            />
                                        </TabPanelPane>
                                    : null}
                                </TabPanel>
                            </div>
                        :
                            <p className="cart__empty-message">Empty cart</p>
                        }
                    </PanelBody>
                </Panel>
                {seriesManager.isSeriesManagerOpen && (
                    <ManageSeriesModal
                        series={seriesManager.managedSeries}
                        cartControls={seriesManager.cartControls}
                        onCloseModalClick={() => seriesManager.setManagedSeries(null)}
                    />
                )}
            </div>
        </CartViewContext.Provider>
    );
};

CartComponent.propTypes = {
    /** Cart object to display */
    context: PropTypes.object.isRequired,
    /** Cart as it exists in the database */
    savedCartObj: PropTypes.object,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool,
    /** System fetch function */
    fetch: PropTypes.func.isRequired,
    /** System session information */
    session: PropTypes.object,
    /** URL in the URL bar including hash */
    locationHref: PropTypes.string.isRequired,
};

CartComponent.defaultProps = {
    savedCartObj: null,
    inProgress: false,
    session: null,
};

CartComponent.contextTypes = {
    session: PropTypes.object,
};


const mapStateToProps = (state, ownProps) => ({
    savedCartObj: state.savedCartObj,
    context: ownProps.context,
    inProgress: state.inProgress,
    fetch: ownProps.fetch,
    session: ownProps.session,
});

const CartInternal = connect(mapStateToProps)(CartComponent);


/**
 * Wrapper to receive React <App> context and pass it to CartInternal as regular props.
 */
const Cart = (props, reactContext) => (
    <CartInternal context={props.context} fetch={reactContext.fetch} session={reactContext.session} locationHref={reactContext.location_href} />
);

Cart.propTypes = {
    /** Cart object from server, either for shared cart or 'cart-view' */
    context: PropTypes.object.isRequired,
};

Cart.contextTypes = {
    session: PropTypes.object,
    fetch: PropTypes.func,
    location_href: PropTypes.string,
};

export default Cart;


/**
 * Allows the user to select a single assembly for the genome browser.
 */
const CartAssemblySelector = ({ selectedAssembly, assemblies, onChangeAssembly }) => (
    <>
        <select value={selectedAssembly} onChange={(e) => onChangeAssembly(e.target.value)}>
            {assemblies.map((assembly) => (
                <option key={assembly} value={assembly}>{assembly}</option>
            ))}
        </select>
    </>
);

CartAssemblySelector.propTypes = {
    /** Currently selected assembly */
    selectedAssembly: PropTypes.string.isRequired,
    /** List of available assemblies */
    assemblies: PropTypes.arrayOf(PropTypes.string).isRequired,
    /** Called when the user selects an assembly */
    onChangeAssembly: PropTypes.func.isRequired,
};


/**
 * Display controls used for the static cart display.
 */
const CartStaticControls = ({
    selectedAssembly,
    batchDownloadProps: {
        cart,
        datasetTypes,
        isFileViewActive,
    },
    assemblyProps: {
        assemblies,
        onChangeAssembly,
    },
}) => (
    <div className="cart-static-controls">
        {selectedAssembly &&
            <CartAssemblySelector
                assemblies={assemblies}
                selectedAssembly={selectedAssembly}
                onChangeAssembly={onChangeAssembly}
            />
        }
        <CartStaticBatchDownload
            cart={cart}
            assembly={selectedAssembly}
            datasetTypes={datasetTypes}
            isFileViewActive={isFileViewActive}
        />
    </div>
);

CartStaticControls.propTypes = {
    selectedAssembly: PropTypes.string,
    batchDownloadProps: PropTypes.exact({
        cart: PropTypes.object.isRequired,
        datasetTypes: PropTypes.arrayOf(PropTypes.string).isRequired,
        isFileViewActive: PropTypes.bool.isRequired,
    }).isRequired,
    assemblyProps: PropTypes.exact({
        assemblies: PropTypes.arrayOf(PropTypes.string).isRequired,
        onChangeAssembly: PropTypes.func.isRequired,
    }).isRequired,
};

CartStaticControls.defaultProps = {
    selectedAssembly: '',
};


/**
 * Displays the static cart status line.
 */
const CartStaticStatus = ({ isFileViewActive }) => (
    <div className="cart-static-status">
        <>Displaying </>
        {isFileViewActive ? <>file view</> : <>default files</>}
    </div>
);

CartStaticStatus.propTypes = {
    /** True if a file view is active */
    isFileViewActive: PropTypes.bool.isRequired,
};


/**
 * Displays a single static cart.
 */
const CartStaticDisplay = ({ cart }, reactContext) => {
    /** Dataset loading progres; -1=done */
    const [facetProgress, setFacetProgress] = React.useState(null);
    /** File objects from datasets in cart */
    const [processedFiles, setProcessedFiles] = React.useState([]);
    /** Compiled analyses applicable to the current datasets */
    const [analyses, setAnalyses] = React.useState([]);
    /** All types from cart datasets, for downloads */
    const [datasetTypes, setDatasetTypes] = React.useState([]);
    /** Current tab's ID */
    const [displayedTab, setDisplayedTab] = React.useState('browser');
    /** Currently selected assembly */
    const [selectedAssembly, setSelectedAssembly] = React.useState('');
    /** Currently displayed page number for each tab pane; for pagers. */
    const [pageNumbers, dispatchPageNumbers] = React.useReducer(reducerTabPanePageNumber, { browser: 0, processeddata: 0 });
    /** Total number of displayed pages for each tab pane; for pagers. */
    const [totalPageCount, dispatchTotalPageCounts] = React.useReducer(reducerTabPaneTotalPageCount, { browser: 0, processeddata: 0 });

    // Find the selected file view, if any.
    const selectedFileView = cart.file_views?.find((view) => view.title === DEFAULT_FILE_VIEW_NAME);
    const isFileViewActive = selectedFileView?.files.length > 0;

    // Collect files, filtered for default files and file-view files, but including files from all
    // assemblies.
    const allAssemblyFiles = React.useMemo(() => {
        if (isFileViewActive) {
            // Non-empty file view in the cart, so use the files from the view.
            return filterForFileView(processedFiles, selectedFileView.files);
        }

        // No file view in the cart, so use the default files.
        const defaultFiles = filterForDefaultFiles(processedFiles);
        const analysisFilteredFiles = filterForReleasedAnalyses(defaultFiles, analyses);
        return analysisFilteredFiles.length > 0 ? analysisFilteredFiles : defaultFiles;
    }, [processedFiles, analyses, cart.file_views]);

    // Collect all assemblies in all filtered files.
    const assemblies = React.useMemo(() => {
        const assembliesSet = [...allAssemblyFiles.reduce((accumulatedAssemblies, file) => (
            file.assembly ? accumulatedAssemblies.add(file.assembly) : accumulatedAssemblies
        ), new Set())];
        return sortAssemblies([...assembliesSet]);
    }, [allAssemblyFiles]);

    // Filter files by the selected assembly.
    const selectedFiles = React.useMemo(() => (
        selectedAssembly ? allAssemblyFiles.filter((file) => file.assembly === selectedAssembly) : allAssemblyFiles
    ), [allAssemblyFiles, selectedAssembly]);

    // Filter files from the selected assembly to the visualizable ones.
    const selectedVisualizableFiles = React.useMemo(() => (
        filterForVisualizableFiles(selectedFiles)
    ), [selectedFiles]);

    /**
     * Called when the user clicks a tab to make its panel visible.
     * @param {string} newTab ID of clicked tab
     */
    const handleTabClick = (newTab) => {
        setDisplayedTab(newTab);
    };

    // Called when the user selects a new page of items to view using the pager.
    const updateDisplayedPage = (newDisplayedPage) => {
        // Set the new page number for the currently-displayed tab pane.
        dispatchPageNumbers({ tab: displayedTab, pageNumber: newDisplayedPage });
    };

    // Set the selected assembly to the first one in the sorted list if no assembly has been
    // selected yet.
    React.useEffect(() => {
        setSelectedAssembly(assemblies[0]);
    }, [assemblies]);

    // Data changes or initial load need a total-page-count calculation.
    React.useEffect(() => {
        const browserPageCount = calcTotalPageCount(selectedVisualizableFiles.length, constants.PAGE_TRACK_COUNT);
        const processedDataPageCount = calcTotalPageCount(selectedFiles.length, constants.PAGE_FILE_COUNT);
        dispatchTotalPageCounts({ tab: 'browser', totalPageCount: browserPageCount });
        dispatchTotalPageCounts({ tab: 'processeddata', totalPageCount: processedDataPageCount });

        // Go to first page if current page number goes out of range of new page count.
        if (pageNumbers.browser >= browserPageCount) {
            dispatchPageNumbers({ tab: 'browser', pageNumber: 0 });
        }
        if (pageNumbers.processeddata >= processedDataPageCount) {
            dispatchPageNumbers({ tab: 'processeddata', pageNumber: 0 });
        }
    }, [selectedVisualizableFiles, selectedFiles]);

    useMount(() => {
        // Load the files associated with the cart's datasets.
        retrieveDatasetsFiles(cart.elements, setFacetProgress, reactContext.fetch, reactContext.session).then(({ datasets, datasetFiles, datasetAnalyses }) => {
            // Only track processed files with static carts.
            const processedDatasetFiles = datasetFiles.filter((file) => file.processed);

            // De-embed any embedded datasets.files.dataset to reduce memory usage.
            processedDatasetFiles.forEach((file) => {
                // De-embed any embedded datasets.files.dataset.
                if (typeof file.dataset === 'object') {
                    file.dataset = file.dataset['@id'];
                }
            });

            // Collect all types of all datasets. Don't count series because we already have their
            // related datasets here too.
            const types = new Set(datasets.map((dataset) => dataset['@type'][0]));

            setProcessedFiles(processedDatasetFiles);
            setAnalyses(datasetAnalyses);
            setDatasetTypes([...types]);
        });
    });

    return (
        <Panel addClasses="cart-static-display">
            <PanelHeading>
                <h4>{cart.name}</h4>
            </PanelHeading>
            <CartStaticStatus isFileViewActive={isFileViewActive} />
            {facetProgress === -1
                ?
                    <div className="cart__display">
                        <TabPanel
                            tabPanelCss="cart__display-content cart__display-content--static"
                            tabs={{
                                browser: 'Genome browser',
                                processeddata: 'Processed',
                            }}
                            tabDisplay={{
                                browser: <CounterTab title="Genome browser" count={selectedVisualizableFiles.length} icon="file" voice="visualizable tracks" />,
                                processeddata: <CounterTab title="Processed" count={selectedFiles.length} icon="file" voice="processed data files" />,
                            }}
                            decoration={
                                <CartStaticControls
                                    selectedAssembly={selectedAssembly}
                                    batchDownloadProps={{
                                        cart,
                                        datasetTypes,
                                        isFileViewActive,
                                    }}
                                    assemblyProps={{
                                        assemblies,
                                        onChangeAssembly: setSelectedAssembly,
                                    }}
                                />
                            }
                            decorationClasses="cart-assembly-selector"
                            selectedTab={displayedTab}
                            handleTabClick={handleTabClick}
                        >
                            <TabPanelPane key="browser">
                                <CartSearchResultsControls
                                    cart={cart}
                                    currentTab={displayedTab}
                                    currentPage={pageNumbers.browser}
                                    totalPageCount={totalPageCount.browser}
                                    updateCurrentPage={updateDisplayedPage}
                                    cartType="OBJECT"
                                    loading={facetProgress !== -1}
                                />
                                <CartBrowser files={selectedVisualizableFiles} assemblies={selectedAssembly ? [selectedAssembly] : []} pageNumber={pageNumbers.browser} loading={facetProgress !== -1} />
                            </TabPanelPane>
                            <TabPanelPane key="processeddata">
                                <CartSearchResultsControls
                                    cart={cart}
                                    currentTab={displayedTab}
                                    currentPage={pageNumbers.processeddata}
                                    totalPageCount={totalPageCount.processeddata}
                                    updateCurrentPage={updateDisplayedPage}
                                    cartType="OBJECT"
                                    loading={facetProgress !== -1}
                                />
                                <CartFiles
                                    cart={cart}
                                    files={selectedFiles}
                                    isFileViewOnly={false}
                                    selectedFilesInFileView={selectedFiles}
                                    currentPage={pageNumbers.processeddata}
                                    defaultOnly={!isFileViewActive}
                                    cartType="OBJECT"
                                    loading={facetProgress !== -1}
                                    options={{ suppressFileViewToggle: true }}
                                />
                            </TabPanelPane>
                        </TabPanel>
                    </div>
                :
                    <p className="cart__empty-message">Loading&hellip;</p>
            }
        </Panel>
    );
};

CartStaticDisplay.propTypes = {
    /** Cart object to display */
    cart: PropTypes.object.isRequired,
};

CartStaticDisplay.contextTypes = {
    session: PropTypes.object,
    fetch: PropTypes.func,
};


/**
 * Display a list of static carts that have few controls and no facets. Intended for embedding on
 * other pages.
 */
export const CartStaticDisplayList = ({ cartPaths }) => {
    const [carts, setCarts] = React.useState([]);

    useMount(() => {
        // When the static cart mounts, request the publication's cart objects from the server.
        if (cartPaths.length > 0) {
            requestObjects(cartPaths, '/search/?type=Cart&limit=all&status!=deleted').then((publicationCarts) => {
                setCarts(publicationCarts);
            });
        }
    });

    return (
        <div className="cart-display">
            {carts.length > 0 &&
                carts.map((cart) => <CartStaticDisplay key={cart['@id']} cart={cart} />)
            }
        </div>
    );
};

CartStaticDisplayList.propTypes = {
    /** Carts to display */
    cartPaths: PropTypes.arrayOf(PropTypes.string).isRequired,
};
