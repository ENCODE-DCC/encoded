/**
 * Components for rendering the /carts/ and /cart-view/ page.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import _ from 'underscore';
import { svgIcon } from '../../libs/svg-icons';
import * as DropdownButton from '../../libs/ui/button';
import * as Pager from '../../libs/ui/pager';
import { Panel, PanelBody, PanelHeading, TabPanel, TabPanelPane } from '../../libs/ui/panel';
import GenomeBrowser, { annotationTypeMap } from '../genome_browser';
import { itemClass, atIdToType } from '../globals';
import {
    ItemAccessories,
    computeAssemblyAnnotationValue,
    filterForVisualizableFiles,
    filterForDefaultFiles,
    filterForDatasetFiles,
    filterForReleasedAnalyses,
} from '../objectutils';
import { ResultTableList } from '../search';
import { compileDatasetAnalyses, sortDatasetAnalyses } from './analysis';
import CartBatchDownload from './batch_download';
import CartClearButton from './clear';
import {
    assembleFileFacets,
    assembleDatasetFacets,
    datasetFieldFileFacets,
    displayedDatasetFacetFields,
    displayedFileFacetFields,
    CartFacets,
    resetDatasetFacets,
    resetFileFacets,
} from './facet';
import CartLockTrigger from './lock';
import CartMergeShared from './merge_shared';
import Status from '../status';
import CartRemoveElements from './remove_multiple';
import { allowedDatasetTypes } from './util';


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


/** Number of dataset elements to display per page */
const PAGE_ELEMENT_COUNT = 25;
/** Number of genome-browser tracks to display per page */
const PAGE_TRACK_COUNT = 20;
/** Number of files to display per page */
const PAGE_FILE_COUNT = 25;


/**
 * Facet fields to request from server -- superset of those displayed in facets, minus calculated
 * props.
 */
const requestedFacetFields = displayedFileFacetFields
    .concat(displayedDatasetFacetFields.map((facetField) => ({ ...facetField, dataset: true })))
    .filter((field) => !field.calculated).concat([
        { field: '@id' },
        { field: 'accession', dataset: true },
        { field: 'biosample_summary', dataset: true },
        { field: 'assembly' },
        { field: 'assay_term_name' },
        { field: 'annotation_subtype' },
        { field: 'annotation_type' },
        { field: 'file_format_type' },
        { field: 'title' },
        { field: 'genome_annotation' },
        { field: 'href' },
        { field: 'dataset' },
        { field: 'biological_replicates' },
        { field: 'analyses', dataset: true },
        { field: 'target', dataset: true },
        { field: 'targets', dataset: true },
        { field: 'preferred_default' },
        { field: 'annotation_subtype', dataset: true },
        { field: 'biochemical_inputs', dataset: true },
        { field: 'award.project', dataset: true },
        { field: 'description', dataset: true },
        { field: 'dbxrefs', dataset: true },
    ]);


/** Map of abbreviations for the allowed dataset types */
const datasetTabTitles = {
    Experiment: 'experiments',
    Annotation: 'annotations',
    FunctionalCharacterizationExperiment: 'FCEs',
};


/**
 * Display a page of cart contents within the cart display.
 */
const CartSearchResults = ({ elements, currentPage, cartControls, loading }) => {
    if (elements.length > 0) {
        const pageStartIndex = currentPage * PAGE_ELEMENT_COUNT;
        const currentPageElements = elements.slice(pageStartIndex, pageStartIndex + PAGE_ELEMENT_COUNT);
        return (
            <div className="cart-search-results">
                <ResultTableList results={currentPageElements} cartControls={cartControls} mode="cart-view" />
            </div>
        );
    }

    // No elements and the page isn't currently loading, so indicate no datasets to view.
    if (!loading) {
        return <div className="nav result-table cart__empty-message">No visible datasets on this page.</div>;
    }

    // Page is currently loading, so don't display anything for now.
    return <div className="nav result-table cart__empty-message">Page currently loading&hellip;</div>;
};

CartSearchResults.propTypes = {
    /** Array of cart items */
    elements: PropTypes.array,
    /** Page of results to display */
    currentPage: PropTypes.number,
    /** True if displaying an active cart */
    cartControls: PropTypes.bool,
    /** True if cart currently loading on page */
    loading: PropTypes.bool.isRequired,
};

CartSearchResults.defaultProps = {
    elements: [],
    currentPage: 0,
    cartControls: false,
};


/**
 * Display browser tracks for the selected page of files.
 */
const CartBrowser = ({ files, assembly, pageNumber, loading }) => {
    if (!loading) {
        // Extract the current page of file objects.
        const pageStartingIndex = pageNumber * PAGE_TRACK_COUNT;
        const pageFiles = files.slice(pageStartingIndex, pageStartingIndex + PAGE_TRACK_COUNT).map((file) => ({ ...file }));

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
        return <GenomeBrowser files={pageFiles} label="cart" assembly={assembly} expanded sortParam={sortParam} />;
    }

    // Message for page loading.
    if (loading) {
        return <div className="nav result-table cart__empty-message">Page currently loading&hellip;</div>;
    }

    return null;
};

CartBrowser.propTypes = {
    /** Files of all visualizable tracks, not just on the displayed page */
    files: PropTypes.array.isRequired,
    /** Assembly to display; can be empty before partial files loaded */
    assembly: PropTypes.string.isRequired,
    /** Page of files to display */
    pageNumber: PropTypes.number.isRequired,
    /** True if the page is currently loading */
    loading: PropTypes.bool.isRequired,
};


/**
 * Display the list of files selected by the current cart facet selections.
 */
const CartFiles = ({ files, currentPage, defaultOnly, loading }) => {
    if (files.length > 0) {
        const pageStartIndex = currentPage * PAGE_FILE_COUNT;
        const currentPageFiles = files.slice(pageStartIndex, pageStartIndex + PAGE_ELEMENT_COUNT);
        const pseudoDefaultFiles = files.filter((file) => file.pseudo_default);
        return (
            <div className="cart-list cart-list--file">
                {defaultOnly && pseudoDefaultFiles.length > 0
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
                        <a key={file['@id']} href={file['@id']} className={`cart-list-item${defaultOnly && file.pseudo_default ? ' cart-list-item--no-dl' : ''}`}>
                            <div className={`cart-list-item__file-type cart-list-item__file-type--${file.file_format}`}>
                                <div className="cart-list-item__format">{file.file_format}</div>
                                {defaultOnly && file.pseudo_default ? <div className="cart-list-item__no-dl">Not downloadable</div> : null}
                            </div>
                            <div className="cart-list-item__props">
                                <div className="cart-list-item__details">
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
                                <div className="cart-list-item__identifier">
                                    <div className="cart-list-item__status">
                                        <Status item={file.status} badgeSize="small" />
                                    </div>
                                    <div className="cart-list-item__title">
                                        {file.title}
                                    </div>
                                </div>
                            </div>
                            <div className="cart-list-item__hover" />
                        </a>
                    );
                })}
            </div>
        );
    }

    // Message for page loading.
    if (loading) {
        return <div className="nav result-table cart__empty-message">Page currently loading&hellip;</div>;
    }

    // Page not loading and no elements.
    return <div className="nav result-table cart__empty-message">No files to view in any dataset in the cart.</div>;
};

CartFiles.propTypes = {
    /** Array of files from datasets in the cart */
    files: PropTypes.array.isRequired,
    /** Page of results to display */
    currentPage: PropTypes.number.isRequired,
    /** True if only displaying default files */
    defaultOnly: PropTypes.bool,
    /** True if page currently loading */
    loading: PropTypes.bool.isRequired,
};

CartFiles.defaultProps = {
    defaultOnly: false,
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
        })
    ));
};


/**
 * Display a button that links to a report page showing the datasets in the currently displayed
 * cart.
 */
const CartDatasetReport = ({ savedCartObj, sharedCartObj, usedDatasetTypes, cartType }) => {
    /** Cart that this button links to for search results */
    const linkedCart = React.useRef(null);

    // Get the object for the cart to link to search results.
    if (cartType === 'ACTIVE') {
        linkedCart.current = savedCartObj;
    } else if (cartType === 'OBJECT') {
        linkedCart.current = sharedCartObj;
    } else {
        // Shouldn't happen but just in case.
        return null;
    }

    // Only display the Dataset Report button if we have at least one experiment in the cart. This
    // button drops down a menu allowing the user to select the data type to view which links to
    // that report view.
    if (linkedCart.current && linkedCart.current.elements && linkedCart.current.elements.length > 0) {
        return (
            <DropdownButton.Immediate
                label={<>Dataset report {svgIcon('chevronDown')}</>}
                id="cart-dataset-report"
                css="cart-dataset-report"
            >
                {usedDatasetTypes.map((type) => (
                    <a key={type} href={`/cart-report/?type=${allowedDatasetTypes[type].type}&cart=${linkedCart.current['@id']}`} className={`cart-dataset-option cart-dataset-option--${type}`}>
                        {allowedDatasetTypes[type].title}
                    </a>
                ))}
            </DropdownButton.Immediate>
        );
    }
    return null;
};

CartDatasetReport.propTypes = {
    /** Active cart */
    savedCartObj: PropTypes.object.isRequired,
    /** Shared cart */
    sharedCartObj: PropTypes.object.isRequired,
    /** Dataset types of objects that exist in cart */
    usedDatasetTypes: PropTypes.array.isRequired,
    /** Type of cart to link to the button */
    cartType: PropTypes.string.isRequired,
};


/**
 * Display header accessories specific for carts.
 */
const CartAccessories = ({ savedCartObj, viewableDatasets, sharedCart, cartType, inProgress }) => (
    <div className="cart-accessories">
        {cartType === 'OBJECT' ? <CartMergeShared sharedCartObj={sharedCart} viewableDatasets={viewableDatasets} /> : null}
        {cartType === 'ACTIVE' ?
            <>
                <CartLockTrigger savedCartObj={savedCartObj} inProgress={inProgress} />
                <CartClearButton />
            </>
        : null}
    </div>
);

CartAccessories.propTypes = {
    /** Cart as it exists in the database */
    savedCartObj: PropTypes.object,
    /** Viewable cart element @ids */
    viewableDatasets: PropTypes.array,
    /** Elements in the shared cart, if that's being displayed */
    sharedCart: PropTypes.object,
    /** Type of cart: ACTIVE, OBJECT */
    cartType: PropTypes.string.isRequired,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
};

CartAccessories.defaultProps = {
    savedCartObj: null,
    viewableDatasets: null,
    sharedCart: null,
};


/**
 * Display cart tool buttons. If `savedCartObj` is supplied, supply it for the metadata.tsv line
 * in the resulting files.txt.
 */
const CartTools = ({
    elements,
    selectedFileTerms,
    selectedDatasetTerms,
    selectedDatasetType,
    facetFields,
    savedCartObj,
    cartType,
    sharedCart,
    visualizable,
}) => {
    // Make a list of all the dataset types currently in the cart.
    const usedDatasetTypes = elements.reduce((types, elementAtId) => {
        const type = atIdToType(elementAtId);
        return types.includes(type) ? types : types.concat(type);
    }, []);

    return (
        <div className="cart-tools">
            {elements.length > 0 ?
                <CartBatchDownload
                    cartType={cartType}
                    selectedFileTerms={selectedFileTerms}
                    selectedDatasetTerms={selectedDatasetTerms}
                    selectedDatasetType={selectedDatasetType}
                    facetFields={facetFields}
                    savedCartObj={savedCartObj}
                    sharedCart={sharedCart}
                    visualizable={visualizable}
                />
            : null}
            <CartDatasetReport
                savedCartObj={savedCartObj}
                sharedCartObj={sharedCart}
                cartType={cartType}
                usedDatasetTypes={usedDatasetTypes}
            />
        </div>
    );
};

CartTools.propTypes = {
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
    /** Cart as it exists in the database; use JSON payload method if none */
    savedCartObj: PropTypes.object,
    /** Type of cart: ACTIVE, OBJECT */
    cartType: PropTypes.string.isRequired,
    /** Elements in the shared cart, if that's being displayed */
    sharedCart: PropTypes.object,
    /** True if only visualizable files should be downloaded */
    visualizable: PropTypes.bool,
};

CartTools.defaultProps = {
    elements: [],
    selectedFileTerms: null,
    selectedDatasetTerms: null,
    savedCartObj: null,
    sharedCart: null,
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
const CartSearchResultsControls = ({ currentTab, elements, currentPage, totalPageCount, updateCurrentPage, cartType, loading }) => {
    if (currentTab === 'datasets' || totalPageCount > 1) {
        return (
            <div className="cart-search-results-controls">
                {currentTab === 'datasets' && cartType === 'ACTIVE'
                    ? <CartRemoveElements elements={elements.map((element) => element['@id'])} loading={loading} />
                    : <div />}
                {totalPageCount > 1
                    ? <CartPager currentPage={currentPage} totalPageCount={totalPageCount} updateCurrentPage={updateCurrentPage} />
                    : null}
            </div>
        );
    }
    return null;
};

CartSearchResultsControls.propTypes = {
    /** Key of the currently selected tab */
    currentTab: PropTypes.string.isRequired,
    /** Array of currently displayed cart items */
    elements: PropTypes.array.isRequired,
    /** Zero-based current page to display */
    currentPage: PropTypes.number.isRequired,
    /** Total number of pages */
    totalPageCount: PropTypes.number.isRequired,
    /** Called when user clicks pager controls */
    updateCurrentPage: PropTypes.func.isRequired,
    /** Current cart type, e.g. ACTIVE, SHARED... */
    cartType: PropTypes.string.isRequired,
    /** True if cart still loading on page */
    loading: PropTypes.bool.isRequired,
};


/**
 * Add the datasets search results to the given array of datasets.
 * @param {array} datasets Add new search results to this array
 * @param {object} currentResults Dataset search results
 * @return {array} `datasets` with search-result datasets added
 */
const addToAccumulatingDatasets = (datasets, currentResults) => {
    if (currentResults['@graph'] && currentResults['@graph'].length > 0) {
        currentResults['@graph'].forEach((dataset) => {
            // Mutate the datasets for those properties that need their values altered from how
            // they appear in search results.
            displayedDatasetFacetFields.forEach((facetField) => {
                if (facetField.getValue) {
                    dataset[facetField.field] = facetField.getValue(dataset);
                }
            });
        });

        // Return a new array combining the existing partial files with the additional files.
        return datasets.concat(currentResults['@graph']);
    }

    // No search results; just return unchanged list of datasets.
    return datasets;
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
 *      {string} cartType - Cart type: OBJECT, ACTIVE; '' if undetermined
 *      {string} cartName - Name of cart
 *      {array} cartDatasets - @ids of all datasets in cart
 * }
 */
const getCartInfo = (context, savedCartObj) => {
    let cartType = '';
    let cartName = '';
    let cartDatasets = [];
    if (context['@type'][0] === 'cart-view' && savedCartObj && Object.keys(savedCartObj).length > 0) {
        cartType = 'ACTIVE';
        cartName = savedCartObj.name;
        cartDatasets = savedCartObj.elements;
    } else if (context['@type'][0] === 'Cart') {
        // Viewing a saved cart at its unique path.
        cartType = 'OBJECT';
        cartName = context.name;
        cartDatasets = context.elements;
    }
    return { cartType, cartName, cartDatasets };
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
        analyses[matchingAnalysisIndex].files.push(currentAnalysis.files);
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
                    datasetAnalyses: addToAccumulatingAnalyses(accumulatingResults.datasetAnalyses, currentResults),
                };
            })
        ))
    ), Promise.resolve({ datasetFiles: [], datasets: [], datasetAnalyses: [] })).then(({ datasetFiles, datasets, datasetAnalyses }) => {
        facetProgressHandler(-1);

        // Mutate the files or datasets for their calculated properties.
        processFilesAnalyses(datasetFiles, datasetAnalyses);
        processDatasetTargetList(datasets);
        return { datasetFiles, datasets, datasetAnalyses: sortDatasetAnalyses(datasetAnalyses) };
    });
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
 * Calculate the total number of pages needed to display all items in any of the tab panes
 * (datasets, files, etc.).
 * @param {number} itemCount Total number of items being displayed on pages
 * @param {number} maxCount Maximum number of items per page
 *
 * @return {number} Number of pages to contain all items
 */
const calcTotalPageCount = (itemCount, maxCount) => Math.floor(itemCount / maxCount) + (itemCount % maxCount !== 0 ? 1 : 0);


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
const CartComponent = ({ context, savedCartObj, inProgress, fetch, session }) => {
    // Keeps track of currently selected dataset facet terms keyed by facet fields.
    const [selectedDatasetTerms, setSelectedDatasetTerms] = React.useState({});
    // Keeps track of currently selected file facet terms keyed by facet fields.
    const [selectedFileTerms, setSelectedFileTerms] = React.useState({});
    // Array of datasets the user has access to view; subset of `cartDatasets`.
    const [viewableDatasets, setViewableDatasets] = React.useState([]);
    // Compiled analyses applicable to the current datasets.
    const [analyses, setAnalyses] = React.useState([]);
    // Currently displayed page number for each tab panes; for pagers.
    const [pageNumbers, dispatchPageNumbers] = React.useReducer(reducerTabPanePageNumber, { datasets: 0, browser: 0, processeddata: 0, rawdata: 0 });
    // Total number of displayed pages for each tab pane; for pagers.
    const [totalPageCount, dispatchTotalPageCounts] = React.useReducer(reducerTabPaneTotalPageCount, { datasets: 0, browser: 0, processeddata: 0, rawdata: 0 });
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

    // Retrieve current unfiltered cart information regardless of its source (object or active).
    // Determine if the cart contents have changed.
    const { cartType, cartName, cartDatasets } = getCartInfo(context, savedCartObj);
    const isCartDatasetsChanged = !_.isEqual(cartDatasetsRef.current, cartDatasets);
    if (isCartDatasetsChanged) {
        cartDatasetsRef.current = cartDatasets;
    }

    // Filter out conditional facets.
    const usedFileFacetFields = React.useMemo(() => (
        defaultOnly
            ? displayedFileFacetFields.filter((facetField) => facetField.preferred)
            : displayedFileFacetFields
    ), [defaultOnly]);

    // Build the dataset facets based on the currently selected facet terms.
    const { datasetFacets, selectedDatasets } = React.useMemo(() => (
        assembleDatasetFacets(selectedDatasetTerms, viewableDatasets, displayedDatasetFacetFields)
    ), [selectedDatasetTerms, viewableDatasets]);

    // Build the file facets based on the currently selected facet terms.
    const selectedDatasetFiles = React.useMemo(() => filterForDatasetFiles(allFiles, selectedDatasets), [allFiles, selectedDatasets]);
    const { fileFacets, selectedFiles, selectedVisualizableFiles } = React.useMemo(() => {
        let files = defaultOnly ? filterForDefaultFiles(selectedDatasetFiles) : selectedDatasetFiles;
        files = visualizableOnly ? filterForVisualizableFiles(files) : files;

        // While "Show default data only" selected, futher restrict displayed files to those in
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
    }, [selectedFileTerms, selectedDatasets, visualizableOnly, defaultOnly, selectedDatasetFiles, analyses, usedFileFacetFields]);

    // Construct the file lists for the genome browser and raw file tabs.
    const rawdataFiles = React.useMemo(() => selectedDatasetFiles.filter((files) => !files.assembly), [selectedDatasetFiles]);

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
        const newSelectedTerms = {};
        const matchingFacetField = displayedDatasetFacetFields.find((facetField) => facetField.field === clickedField);
        if (matchingFacetField && matchingFacetField.radio) {
            // The user clicked a radio-button facet.
            displayedDatasetFacetFields.usedFileFacetFields.forEach((facetField) => {
                // Set new term for the clicked radio button, or copy the array for other
                // terms within this as well as other facets.
                newSelectedTerms[facetField.field] = facetField.field === clickedField ? [clickedTerm] : selectedDatasetTerms[facetField.field].slice(0);
            });
        } else {
            // The user clicked a checkbox facet. Determine whether we need to add or subtract
            // a term from the facet selections.
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
        }

        setSelectedDatasetTerms(newSelectedTerms);
    };

    // Called when the user clicks any term in any facet.
    const handleFileTermClick = (clickedField, clickedTerm) => {
        const newSelectedTerms = {};
        const matchingFacetField = displayedFileFacetFields.find((facetField) => facetField.field === clickedField);
        if (matchingFacetField && matchingFacetField.radio) {
            // The user clicked a radio-button facet.
            displayedFileFacetFields.forEach((facetField) => {
                // Set new term for the clicked radio button, or copy the array for other
                // terms within this as well as other facets.
                newSelectedTerms[facetField.field] = facetField.field === clickedField ? [clickedTerm] : selectedFileTerms[facetField.field].slice(0);
            });
        } else {
            // The user clicked a checkbox facet. Determine whether we need to add or subtract
            // a term from the facet selections.
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

    // Use the file information to build the facets and its initial selections. Resetting the
    // facets to their initial states should only happen with a change to files.
    React.useEffect(() => {
        // Reset file terms.
        const files = defaultOnly ? filterForDefaultFiles(allFiles) : allFiles;
        const allVisualizableFiles = filterForVisualizableFiles(files);
        const consideredFiles = visualizableOnly ? allVisualizableFiles : files;
        const newSelectedFileTerms = resetFileFacets(consideredFiles, analyses, displayedFileFacetFields);
        setSelectedFileTerms(newSelectedFileTerms);

        // Reset dataset terms.
        const newSelectedDatasetTerms = resetDatasetFacets(viewableDatasets, displayedDatasetFacetFields);
        setSelectedDatasetTerms(newSelectedDatasetTerms);
    }, [allFiles]);

    // After mount, we can fetch all datasets in the cart that are viewable at the user's
    // permission level and from them extract all their files.
    React.useEffect(() => {
        if (isCartDatasetsChanged) {
            retrieveDatasetsFiles(cartDatasets, setFacetProgress, fetch, session).then(({ datasetFiles, datasets, datasetAnalyses }) => {
                // Mutate files for special cases.
                datasetFiles.forEach((file) => {
                    // De-embed any embedded datasets.files.dataset.
                    if (typeof file.dataset === 'object') {
                        file.dataset = file.dataset['@id'];
                    }
                });

                setAllFiles(datasetFiles);
                setViewableDatasets(datasets);
                setAnalyses(datasetAnalyses);
            });
        }
    }, [isCartDatasetsChanged]);

    // Data changes or initial load need a total-page-count calculation.
    React.useEffect(() => {
        const datasetPageCount = calcTotalPageCount(selectedDatasets.length, PAGE_ELEMENT_COUNT);
        const browserPageCount = calcTotalPageCount(selectedVisualizableFiles.length, PAGE_TRACK_COUNT);
        const processedDataPageCount = calcTotalPageCount(selectedFiles.length, PAGE_FILE_COUNT);
        const rawdataPageCount = calcTotalPageCount(rawdataFiles.length, PAGE_FILE_COUNT);
        dispatchTotalPageCounts({ tab: 'datasets', totalPageCount: datasetPageCount });
        dispatchTotalPageCounts({ tab: 'browser', totalPageCount: browserPageCount });
        dispatchTotalPageCounts({ tab: 'processeddata', totalPageCount: processedDataPageCount });
        dispatchTotalPageCounts({ tab: 'rawdata', totalPageCount: rawdataPageCount });

        // Go to first page if current page number goes out of range of new page count.
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
    }, [selectedDatasets, selectedVisualizableFiles, selectedFiles, rawdataFiles, pageNumbers.datasets, pageNumbers.browser, pageNumbers.processeddata, pageNumbers.rawdata]);

    return (
        <div className={itemClass(context, 'view-item')}>
            <header>
                <h1>{cartName}</h1>
                <CartAccessories
                    savedCartObj={savedCartObj}
                    viewableDatasets={viewableDatasets}
                    sharedCart={context}
                    cartType={cartType}
                    inProgress={inProgress}
                />
                {cartType === 'OBJECT' ? <ItemAccessories item={context} /> : null}
            </header>
            <Panel addClasses="cart__result-table">
                {selectedDatasets.length > 0 ?
                    <PanelHeading addClasses="cart__header">
                        <CartTools
                            elements={cartDatasets}
                            analyses={analyses}
                            selectedDatasetType={selectedDatasetType}
                            savedCartObj={savedCartObj}
                            selectedFileTerms={selectedFileTerms}
                            selectedDatasetTerms={selectedDatasetTerms}
                            facetFields={displayedFileFacetFields.concat(displayedDatasetFacetFields)}
                            viewableDatasets={viewableDatasets}
                            cartType={cartType}
                            sharedCart={context}
                            fileCounts={{ processed: selectedFiles.length, raw: rawdataFiles.length, all: allFiles.length }}
                            visualizable={visualizableOnly}
                            preferredDefault={defaultOnly}
                        />
                        {selectedFileTerms.assembly && selectedFileTerms.assembly[0] ? <div className="cart-assembly-indicator">{selectedFileTerms.assembly[0]}</div> : null}
                    </PanelHeading>
                : null}
                <PanelBody>
                    {cartDatasets.length > 0 ?
                        <div className="cart__display">
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
                                }}
                                datasets={selectedDatasets}
                                files={selectedFiles}
                                facetProgress={facetProgress}
                            />
                            <TabPanel
                                tabPanelCss="cart__display-content"
                                tabs={{ datasets: 'All datasets', browser: 'Genome browser', processeddata: 'Processed data', rawdata: 'Raw data' }}
                                tabDisplay={{
                                    datasets: <CounterTab title={`Selected ${selectedDatasetType ? datasetTabTitles[selectedDatasetType] : 'datasets'}`} count={selectedDatasets.length} icon="dataset" voice="selected datasets" />,
                                    browser: <CounterTab title="Genome browser" count={selectedVisualizableFiles.length} icon="file" voice="visualizable tracks" />,
                                    processeddata: <CounterTab title="Processed data" count={selectedFiles.length} icon="file" voice="processed data files" />,
                                    rawdata: <CounterTab title="Raw data" count={rawdataFiles.length} icon="file" voice="raw data files" />,
                                }}
                                handleTabClick={handleTabClick}
                            >
                                <TabPanelPane key="datasets">
                                    <CartSearchResultsControls
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
                                        loading={facetProgress !== -1}
                                    />
                                </TabPanelPane>
                                <TabPanelPane key="browser">
                                    <CartSearchResultsControls
                                        currentTab={displayedTab}
                                        elements={selectedDatasets}
                                        currentPage={pageNumbers.browser}
                                        totalPageCount={totalPageCount.browser}
                                        updateCurrentPage={updateDisplayedPage}
                                        cartType={cartType}
                                        loading={facetProgress !== -1}
                                    />
                                    {selectedFileTerms.assembly && selectedFileTerms.assembly.length > 0
                                        ? <CartBrowser files={selectedVisualizableFiles} assembly={selectedFileTerms.assembly[0]} pageNumber={pageNumbers.browser} loading={facetProgress !== -1} />
                                        : null}
                                </TabPanelPane>
                                <TabPanelPane key="processeddata">
                                    <CartSearchResultsControls
                                        currentTab={displayedTab}
                                        elements={selectedDatasets}
                                        currentPage={pageNumbers.processeddata}
                                        totalPageCount={totalPageCount.processeddata}
                                        updateCurrentPage={updateDisplayedPage}
                                        cartType={cartType}
                                        loading={facetProgress !== -1}
                                    />
                                    <CartFiles files={selectedFiles} currentPage={pageNumbers.processeddata} defaultOnly={defaultOnly} loading={facetProgress !== -1} />
                                </TabPanelPane>
                                <TabPanelPane key="rawdata">
                                    <CartSearchResultsControls
                                        currentTab={displayedTab}
                                        elements={selectedDatasets}
                                        currentPage={pageNumbers.rawdata}
                                        totalPageCount={totalPageCount.rawdata}
                                        updateCurrentPage={updateDisplayedPage}
                                        cartType={cartType}
                                        loading={facetProgress !== -1}
                                    />
                                    <CartFiles files={rawdataFiles} currentPage={pageNumbers.rawdata} loading={facetProgress !== -1} />
                                </TabPanelPane>
                            </TabPanel>
                        </div>
                    :
                        <p className="cart__empty-message">Empty cart</p>
                    }
                </PanelBody>
            </Panel>
        </div>
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
    <CartInternal context={props.context} fetch={reactContext.fetch} session={reactContext.session} />
);

Cart.propTypes = {
    /** Cart object from server, either for shared cart or 'cart-view' */
    context: PropTypes.object.isRequired,
};

Cart.contextTypes = {
    session: PropTypes.object,
    fetch: PropTypes.func,
};

export default Cart;
