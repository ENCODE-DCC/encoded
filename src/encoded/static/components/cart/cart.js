/**
 * Components for rendering the /carts/ and /cart-view/ page.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import _ from 'underscore';
import { encodedURIComponent } from '../../libs/query_encoding';
import { svgIcon } from '../../libs/svg-icons';
import * as DropdownButton from '../../libs/ui/button';
import * as Pager from '../../libs/ui/pager';
import { Panel, PanelBody, PanelHeading, TabPanel, TabPanelPane } from '../../libs/ui/panel';
import { tintColor, isLight } from '../datacolors';
import GenomeBrowser, { annotationTypeMap } from '../genome_browser';
import { itemClass, atIdToType, keyCode } from '../globals';
import {
    ItemAccessories,
    isFileVisualizable,
    computeAssemblyAnnotationValue,
    filterForVisualizableFiles,
    filterForDefaultFiles,
    filterForDatasetFiles,
    Checkbox,
} from '../objectutils';
import { ResultTableList } from '../search';
import { compileDatasetAnalyses, sortDatasetAnalyses } from './analysis';
import CartBatchDownload from './batch_download';
import CartClearButton from './clear';
import CartLockTrigger from './lock';
import CartMergeShared from './merge_shared';
import Status from '../status';
import CartRemoveElements from './remove_multiple';
import { allowedDatasetTypes, defaultDatasetType } from './util';

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
 * Sorter function to sort an array of assemblies/annotations for display in the facet according to
 * system-wide criteria.
 * @param {array} facetTerms Assembly facet terms to sort
 *
 * @return {array} Same as `facetTerms` but sorted
 */
const assemblySorter = (facetTerms) => (
    // Negate the sorting value to sort from highest to lowest.
    _(facetTerms).sortBy((facetTerm) => -computeAssemblyAnnotationValue(facetTerm.term))
);


/**
 * Sorter function for analyses facet terms matches the order from the given analyses which have
 * already been sorted.
 * @param {array} facetTerms Analysis facet terms to sort
 *
 * @return {array} Same as `facetTerms`
 */
const analysisSorter = (facetTerms, analyses) => (
    _(facetTerms).sortBy((facetTerm) => (
        analyses.findIndex((analysis) => analysis.title === facetTerm.term)
    ))
);


/**
 * Field mapping transform for analyses. Generate a query string corresponding to all the selected
 * analyses with the given titles. More than one title can be selected, and more than one analysis
 * can correspond to a title, so all these get combined into one query string.
 * @param {array} analysisTitles Selected analysis titles from the facet.
 *
 * @return {string} Combined query string selecting file.analyses titles.
 */
const analysisFieldMap = (analysisTitles) => (
    analysisTitles.map((title) => `files.analyses.title=${encodedURIComponent(title)}`).join('&')
);


/**
 * Field `getValue` function to extract the top @type from the given dataset.
 * @param {object} dataset ...from which to extract its @type
 * @return {string} Top-level @type of given dataset
 */
const datasetTypeValue = (dataset) => dataset['@type'][0];


/**
 * Display a term of the Dataset Term facets mapped to the English-language equivalent from the
 * profile titles from <App> page load, e.g. "Functional Characterization Experiment" instead of
 * "FunctionalCharacterizationExperiment."
 */
const DatasetTypeTermDisplay = ({ term }, { profilesTitles }) => {
    if (profilesTitles && profilesTitles[term]) {
        return <div className="cart-facet-term__text">{profilesTitles[term]}</div>;
    }
    return <div className="cart-facet-term__text">{term}</div>;
};

DatasetTypeTermDisplay.propTypes = {
    /** Displayed facet term */
    term: PropTypes.string.isRequired,
};

DatasetTypeTermDisplay.contextTypes = {
    profilesTitles: PropTypes.object,
};


/**
 * File facet fields to display in order of display.
 * - field: `facet` field property
 * - title: Displayed facet title
 * - radio: True if radio-button facet; otherwise checkbox facet
 * - dataset: True to retrieve value from dataset instead of files
 * - sorter: Function to sort terms within the facet
 * - fieldMapper: Function to generate a batch download query string
 * - preferred: Facet appears when preferred_default selected
 * - calculated: True for facets displaying calculated (not requested) file/dataset props
 * - parent: Copy expanded state of this field; suppress this facet's expander title
 * - expanded: True to appear expanded by default
 * - nonCollapsable: True for the facet to always appear expanded; no expander trigger
 */
const displayedFileFacetFields = [
    {
        field: 'assembly',
        title: 'Analysis/Assembly',
        radio: true,
        sorter: assemblySorter,
        preferred: true,
        expanded: true,
    },
    {
        field: 'analyses',
        title: 'Analysis',
        dataset: true,
        sorter: analysisSorter,
        fieldMapper: analysisFieldMap,
        calculated: true,
        parent: 'assembly',
        css: 'cart-facet--analysis',
    },
    {
        field: 'annotation_type',
        title: 'Annotation type',
        dataset: true,
        preferred: true,
    },
    {
        field: 'output_type',
        title: 'Output type',
    },
    {
        field: 'file_type',
        title: 'File type',
    },
    {
        field: 'file_format',
        title: 'File format',
    },
    {
        field: 'lab.title',
        title: 'Lab',
        preferred: true,
    },
    {
        field: 'status',
        title: 'Status',
    },
];

/**
 * Dataset facet fields to display.
 */
// const requestedFacetFields = displayedFacetFields.filter((field) => !field.calculated).concat([
//     { field: '@id' },
//     { field: 'assembly' },
//     { field: 'assay_term_name' },
//     { field: 'file_format_type' },
//     { field: 'title' },
//     { field: 'genome_annotation' },
//     { field: 'href' },
//     { field: 'dataset' },
//     { field: 'biological_replicates' },
//     { field: 'analyses', dataset: true },
//     { field: 'preferred_default' },
//     { field: 'annotation_subtype', dataset: true },
//     { field: 'biochemical_inputs', dataset: true },
// ]);

// /** Facet `field` values for properties from dataset instead of files */
// const datasetFacets = displayedFacetFields.concat(requestedFacetFields).filter((facetField) => facetField.dataset).map((facetField) => facetField.field);

const displayedDatasetFacetFields = [
    {
        field: 'type',
        title: 'Dataset type',
        getValue: datasetTypeValue,
        termDisplay: DatasetTypeTermDisplay,
        nonCollapsable: true,
    },
    {
        field: 'assay_title',
        title: 'Assay title',
    },
    {
        field: 'biosample_ontology.term_name',
        title: 'Biosample',
    },
    {
        field: 'target.label',
        title: 'Target',
    },
    {
        field: 'replicates.library.biosample.organism.scientific_name',
        title: 'Organism',
    },
    {
        field: 'lab.title',
        title: 'Lab',
    },
    {
        field: 'status',
        title: 'Status',
    },
];

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
        { field: 'file_format_type' },
        { field: 'title' },
        { field: 'genome_annotation' },
        { field: 'href' },
        { field: 'dataset' },
        { field: 'biological_replicates' },
        { field: 'analysis_objects', dataset: true },
        { field: 'preferred_default' },
        { field: 'annotation_subtype', dataset: true },
        { field: 'biochemical_inputs', dataset: true },
        { field: 'award.project', dataset: true },
        { field: 'description', dataset: true },
    ]);

/** Facet `field` values for properties from dataset instead of files */
const datasetFieldFileFacets = displayedFileFacetFields.concat(requestedFacetFields).filter((facetField) => facetField.dataset).map((facetField) => facetField.field);

/** Map of abbreviations for the allowed dataset types */
const datasetTabTitles = {
    Experiment: 'experiments',
    Annotation: 'annotations',
    FunctionalCharacterizationExperiment: 'FCEs',
};


/**
 * Display a page of cart contents within the cart display.
 */
const CartSearchResults = ({ elements, currentPage, cartControls }) => {
    if (elements.length > 0) {
        const pageStartIndex = currentPage * PAGE_ELEMENT_COUNT;
        const currentPageElements = elements.slice(pageStartIndex, pageStartIndex + PAGE_ELEMENT_COUNT);
        return (
            <div className="cart-search-results">
                <ResultTableList results={currentPageElements} cartControls={cartControls} mode="cart-view" />
            </div>
        );
    }
    return <div className="nav result-table cart__empty-message">No visible datasets on this page.</div>;
};

CartSearchResults.propTypes = {
    /** Array of cart items */
    elements: PropTypes.array,
    /** Page of results to display */
    currentPage: PropTypes.number,
    /** True if displaying an active cart */
    cartControls: PropTypes.bool,
};

CartSearchResults.defaultProps = {
    elements: [],
    currentPage: 0,
    cartControls: false,
};


/**
 * Display browser tracks for the selected page of files.
 */
const CartBrowser = ({ files, assembly, pageNumber }) => {
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
};

CartBrowser.propTypes = {
    /** Files of all visualizable tracks, not just on the displayed page */
    files: PropTypes.array.isRequired,
    /** Assembly to display; can be empty before partial files loaded */
    assembly: PropTypes.string.isRequired,
    /** Page of files to display */
    pageNumber: PropTypes.number.isRequired,
};


/**
 * Display the list of files selected by the current cart facet selections.
 */
const CartFiles = ({ files, currentPage, defaultOnly }) => {
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
                {currentPageFiles.map((file) => (
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
                                    <div className="cart-list-details__value">{(file.target && file.target.label) || 'None'}</div>
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
                ))}
            </div>
        );
    }
    return <div className="nav result-table cart__empty-message">No files to view in any dataset in the cart.</div>;
};

CartFiles.propTypes = {
    /** Array of files from datasets in the cart */
    files: PropTypes.array.isRequired,
    /** Page of results to display */
    currentPage: PropTypes.number.isRequired,
    /** True if only displaying default files */
    defaultOnly: PropTypes.bool,
};

CartFiles.defaultProps = {
    defaultOnly: false,
};


/**
 * Display a count of the total number of elements selected in the facet, given the current facet term
 * selections. Shows the facet-loading progress bar if needed.
 */
const FacetCount = ({ count, element, facetLoadProgress }) => {
    const [triggerEnabled, setTriggerEnabled] = React.useState(false);

    /**
     * Called when CSS animation ends. Removes the <div> that shows the yellow highlight when the
     * count changes.
     */
    const handleAnimationEnd = () => {
        setTriggerEnabled(false);
    };

    React.useEffect(() => {
        // Inserts the <div> to show the yellow highlight when the file count changes.
        setTriggerEnabled(true);
    }, [count]);

    if (facetLoadProgress === -1) {
        const fileCountFormatted = count.toLocaleString ? count.toLocaleString() : count.toString();
        return (
            <div className="cart__facet-count">
                {triggerEnabled ? <div className="cart__facet-count-changer" onAnimationEnd={handleAnimationEnd} /> : null}
                {count > 0 ?
                    <>{svgIcon(element)} {fileCountFormatted} {element}{count !== 1 ? 's' : ''} selected</>
                :
                    <>No files selected for download</>
                }
            </div>
        );
    }

    return <progress value={facetLoadProgress} max="100" />;
};

FacetCount.propTypes = {
    /** Number of files selected for download */
    count: PropTypes.number,
    /** What sort of element to document in the display, e.g. "dataset" */
    element: PropTypes.string.isRequired,
    /** Value for the progress bar; -1 to not show it */
    facetLoadProgress: PropTypes.number,
};

FacetCount.defaultProps = {
    count: 0,
    facetLoadProgress: 0,
};


/**
 * Display the selection checkbox for a single cart file facet term.
 */
const FacetTermCheck = ({ checked }) => (
    <div className={`cart-facet-term__check${checked ? ' cart-facet-term__check--checked' : ''}`}>
        {checked ?
            <i className="icon icon-check" />
        : null}
    </div>
);

FacetTermCheck.propTypes = {
    /** True if facet term checkbox checked */
    checked: PropTypes.bool,
};

FacetTermCheck.defaultProps = {
    checked: false,
};


/**
 * Display the selection radio button for a single cart file facet term.
 */
const FacetTermRadio = ({ checked }) => (
    <div className={`cart-facet-term__radio${checked ? ' cart-facet-term__radio--checked' : ''}`}>
        {checked ?
            <i className="icon icon-circle" />
        : null}
    </div>
);

FacetTermRadio.propTypes = {
    /** True if facet term radio button checked */
    checked: PropTypes.bool,
};

FacetTermRadio.defaultProps = {
    checked: false,
};


/**
 * Render the text contents of a facet term, using custom displays from the `termDisplay` property
 * of a facet definition if provided.
 */
const FacetTermContent = ({ term, displayedFacetField }) => {
    if (displayedFacetField.termDisplay) {
        return <displayedFacetField.termDisplay term={term} displayedFacetField={displayedFacetField} />;
    }
    return <div className="cart-facet-term__text">{term}</div>;
};

FacetTermContent.propTypes = {
    /** Displayed facet term */
    term: PropTypes.string.isRequired,
    /** Field definition representing the facet being displayed */
    displayedFacetField: PropTypes.object.isRequired,
};


/**
 * Display the cart file facet term count that shows the magnitude of a facet term through its
 * color tint. The maximum value for the facet gets the full base color, and lesser values get
 * lighter tints.
 */
const FacetTermMagnitude = ({ termCount, maxTermCount }) => {
    const MAGNITUDE_BASE_COLOR = '#656BFF';
    const magnitudeColor = tintColor(MAGNITUDE_BASE_COLOR, 1 - (termCount / maxTermCount));
    const textColor = isLight(magnitudeColor) ? '#000' : '#fff';
    return (
        <div className="cart-facet-term__magnitude" style={{ backgroundColor: magnitudeColor }}>
            <span style={{ color: textColor }}>{termCount}</span>
        </div>
    );
};

FacetTermMagnitude.propTypes = {
    /** Number of items this facet term indicates */
    termCount: PropTypes.number.isRequired,
    /** Maximum count value among all terms in this facet */
    maxTermCount: PropTypes.number.isRequired,
};


/**
 * Display one term of a facet.
 */
const FacetTerm = ({
    term,
    displayedFacetField,
    termCount,
    maxTermCount,
    selected,
    visualizable,
    termClickHandler,
    FacetTermSelectRenderer,
}) => {
    /**
     * Called when user clicks a term within a facet.
     */
    const handleTermClick = () => {
        termClickHandler(term);
    };

    return (
        <li className="cart-facet-term">
            <button
                className="cart-facet-term__item"
                type="button"
                id={`cart-facet-term-${term}`}
                onClick={handleTermClick}
                aria-pressed={selected}
                aria-label={`${termCount} ${term} file${termCount === 1 ? '' : 's'}${visualizable ? ' visualizable' : ''}`}
            >
                <FacetTermSelectRenderer checked={selected} />
                <FacetTermContent term={term} displayedFacetField={displayedFacetField} />
                <FacetTermMagnitude termCount={termCount} maxTermCount={maxTermCount} />
                <div className="cart-facet-term__visualizable">
                    {visualizable ?
                        <div title="Selects visualizable files">{svgIcon('genomeBrowser')}</div>
                    : null}
                </div>
            </button>
        </li>
    );
};

FacetTerm.propTypes = {
    /** Displayed facet term */
    term: PropTypes.string.isRequired,
    /** Field definition representing the facet being displayed */
    displayedFacetField: PropTypes.object.isRequired,
    /** Displayed number of files for this term */
    termCount: PropTypes.number.isRequired,
    /** Maximum number of files for all terms in the facet */
    maxTermCount: PropTypes.number.isRequired,
    /** True if this term should appear selected */
    selected: PropTypes.bool,
    /** True if term selection results in visualizable files */
    visualizable: PropTypes.bool,
    /** Callback for handling clicks in the term */
    termClickHandler: PropTypes.func.isRequired,
    /** Facet term checkbox/radio renderer */
    FacetTermSelectRenderer: PropTypes.elementType.isRequired,
};

FacetTerm.defaultProps = {
    selected: false,
    visualizable: false,
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
 * Extract the value of an object property based on a dotted-notation field,
 * e.g. { a: 1, b: { c: 5 }} you could retrieve the 5 by passing 'b.c' in `field`.
 * Based on https://stackoverflow.com/questions/6393943/convert-javascript-string-in-dot-notation-into-an-object-reference#answer-6394168
 * @param {object} object Object containing the value you want to extract.
 * @param {string} field  Dotted notation for the property to extract.
 *
 * @return {value} Whatever value the dotted notation specifies, or undefined.
 */
const getObjectFieldValue = (object, field) => {
    const parts = field.split('.');
    if (parts.length === 1) {
        return object[field];
    }
    return parts.reduce((partObject, part) => partObject && partObject[part], object);
};


/**
 * Display the title inside the facet expander.
 */
const FacetTitle = ({ title }) => (
    <div className="cart-facet__expander-title">
        {title}
    </div>
);

FacetTitle.propTypes = {
    /** Text title to display */
    title: PropTypes.string.isRequired,
};


/**
 * Display a button that shows an indicator when the user has selected at least one term in the
 * facet, and allows the user to click the indicator to clear all selections within that facet.
 */
const FacetSelectionControl = ({ selectionCount, name, clearSelectionHandler }) => {
    /**
     * Called when the user types a key while the control holds the current selection.
     */
    const handleKeyPress = (e) => {
        if (e.keyCode === keyCode.RETURN || e.keyCode === keyCode.SPACE) {
            e.preventDefault();
            clearSelectionHandler(e);
        }
    };

    if (selectionCount > 0) {
        return (
            <div role="button" tabIndex="0" id={`cart-facet-clear-${name}`} className="cart-facet-clear" onKeyDown={handleKeyPress} onClick={clearSelectionHandler}>
                <div className="cart-facet-clear__control cart-facet-clear__control--has-selections">{svgIcon('circle')}</div>
                <div className="cart-facet-clear__control cart-facet-clear__control--clear-selections">{svgIcon('multiplication')}</div>
                <span className="sr-only">
                    Clear {selectionCount} {selectionCount === 1 ? 'selection' : 'selections'}
                </span>
            </div>
        );
    }
    return null;
};

FacetSelectionControl.propTypes = {
    /** Number of selected terms in the facet */
    selectionCount: PropTypes.number.isRequired,
    /** Used as part of the ID to uniquely identify the button on the page */
    name: PropTypes.string.isRequired,
    /** Function to call when someone clicks the control */
    clearSelectionHandler: PropTypes.func.isRequired,
};


/**
 * Display the facet title and expansion icon, and react to clicks in the button to tell the parent
 * component that a facet needs to be expanded or collapsed.
 */
const FacetExpander = ({ title, field, labelId, expanded, selectionCount, expanderEventHandler, clearFacetSelections }) => {
    /**
     * Called when the user clicks the control to clear all selected terms in the facet.
     */
    const controlClickHandler = (e) => {
        e.stopPropagation();
        clearFacetSelections(field);
    };

    // Use an expander button if the caller provides an event handler to expand or collapse
    // the facet.
    if (expanderEventHandler) {
        return (
            <button
                type="button"
                id={labelId}
                className="cart-facet__expander"
                aria-controls={field}
                aria-expanded={expanded}
                onClick={expanderEventHandler}
            >
                <FacetTitle title={title} />
                {clearFacetSelections ? <FacetSelectionControl name={field} selectionCount={selectionCount} clearSelectionHandler={controlClickHandler} /> : null}
                <i className={`icon icon-chevron-${expanded ? 'up' : 'down'}`} />
            </button>
        );
    }

    // Just display the title without an expander button if no event handler given.
    return (
        <div className="cart-facet__expander cart-facet__expander--non-collapsable">
            <FacetTitle title={title} />
            <FacetSelectionControl name={field} selectionCount={selectionCount} clearSelectionHandler={controlClickHandler} />
        </div>
    );
};

FacetExpander.propTypes = {
    /** Displayed title of the facet */
    title: PropTypes.string.isRequired,
    /** File facet field representing this facet */
    field: PropTypes.string.isRequired,
    /** Used as an id for this button corresponding to expanded component label */
    labelId: PropTypes.string.isRequired,
    /** True if facet is currently expanded */
    expanded: PropTypes.bool.isRequired,
    /** Number of selected terms */
    selectionCount: PropTypes.number.isRequired,
    /** Called when the user clicks the expander button; null for always-open */
    expanderEventHandler: PropTypes.func,
    /** Called when the user clears all selections in a facet */
    clearFacetSelections: PropTypes.func,
};

FacetExpander.defaultProps = {
    expanderEventHandler: null,
    clearFacetSelections: null,
};


/**
 * Display a single file facet.
 */
class Facet extends React.Component {
    constructor() {
        super();
        this.handleFacetTermClick = this.handleFacetTermClick.bind(this);
        this.handleExpanderEvent = this.handleExpanderEvent.bind(this);
    }

    /**
     * Handle a click in a facet term by calling a parent handler.
     * @param {string} term Clicked facet term
     */
    handleFacetTermClick(term) {
        this.props.facetTermClickHandler(this.props.displayedFacetField.field, term);
    }

    /**
     * Handle a click in the facet expander by calling a parent handler.
     * @param {object} e React synthetic event
     */
    handleExpanderEvent(e) {
        this.props.expanderClickHandler(this.props.displayedFacetField.field, e.altKey);
    }

    render() {
        const { facet, displayedFacetField, expanded, selectedFacetTerms, clearFacetSelections, options } = this.props;
        const maxTermCount = Math.max(...facet.terms.map((term) => term.count));
        const labelId = `${displayedFacetField.field}-label`;
        const FacetTermSelectRenderer = displayedFacetField.radio ? FacetTermRadio : FacetTermCheck;
        return (
            <div className="facet">
                {!options.supressTitle
                    ? (
                        <FacetExpander
                            title={facet.title}
                            field={displayedFacetField.field}
                            labelId={labelId}
                            expanded={expanded}
                            expanderEventHandler={displayedFacetField.nonCollapsable ? null : this.handleExpanderEvent}
                            selectionCount={selectedFacetTerms.length}
                            clearFacetSelections={displayedFacetField.radio ? null : clearFacetSelections}
                        />
                    )
                : null}
                {expanded || displayedFacetField.nonCollapsable ?
                    <ul className={`cart-facet${displayedFacetField.css ? ` ${displayedFacetField.css}` : ''}`} role="region" id={displayedFacetField.field} aria-labelledby={labelId}>
                        {facet.terms.map((facetTerm) => (
                            <FacetTerm
                                key={facetTerm.term}
                                displayedFacetField={displayedFacetField}
                                term={facetTerm.term}
                                termCount={facetTerm.count}
                                visualizable={options.suppressVisualizable ? false : facetTerm.visualizable}
                                maxTermCount={maxTermCount}
                                selected={selectedFacetTerms.indexOf(facetTerm.term) > -1}
                                termClickHandler={this.handleFacetTermClick}
                                FacetTermSelectRenderer={FacetTermSelectRenderer}
                            />
                        ))}
                    </ul>
                : null}
            </div>
        );
    }
}

Facet.propTypes = {
    /** Facet object to display */
    facet: PropTypes.object.isRequired,
    /** Field definition representing the facet being displayed */
    displayedFacetField: PropTypes.object.isRequired,
    /** True if facet should appear expanded */
    expanded: PropTypes.bool.isRequired,
    /** Called when the expander button is clicked */
    expanderClickHandler: PropTypes.func.isRequired,
    /** Selected term keys */
    selectedFacetTerms: PropTypes.array,
    /** Called when a facet term is clicked */
    facetTermClickHandler: PropTypes.func.isRequired,
    /** Called when the user clears all selections in a facet */
    clearFacetSelections: PropTypes.func.isRequired,
    /** Facet-specific options */
    options: PropTypes.shape({
        /** Suppress display of facet title */
        supressTitle: PropTypes.bool,
        /** Suppress display of visualizable icons */
        suppressVisualizable: PropTypes.bool,
    }),
};

Facet.defaultProps = {
    selectedFacetTerms: [],
    options: {},
};


/**
 * Manage the expanded states of collapsable facets in a facet list.
 * @param {object} facetFields Definitions for facet list
 * @return {array} expanded states of each facet; callback when user clicks an expander
 */
const useExpanders = (facetFields) => {
    /** Expanded facet fields; `displayedFileFacetFields` array creates an entry for each field */
    const [expandedStates, setExpandedStates] = React.useState(() => (
        facetFields.reduce((accExpanded, facetField) => (
            ({ ...accExpanded, [facetField.field]: !!facetField.expanded })
        ), {})
    ));

    /**
     * Called when the user clicks a facet expander button. Updates the expander states so the
     * facets re-render to the new expanded states.
     * @param {string} field Field name for clicked facet expander
     * @param {boolean} altKey True if alt/option key down at time of click
     */
    const handleExpanderClick = (field, altKey) => {
        setExpandedStates((prevExpandedStates) => {
            if (altKey) {
                // Alt key held down, so expand or collapse *all* facets.
                const allExpandedState = !prevExpandedStates[field];
                const nextExpandedStates = {};
                Object.keys(prevExpandedStates).forEach((facetField) => {
                    nextExpandedStates[facetField] = allExpandedState;
                });
                return nextExpandedStates;
            }

            // Alt key not held down, so just expand or collapse the clicked facet.
            const nextExpandedStates = { ...prevExpandedStates };
            nextExpandedStates[field] = !prevExpandedStates[field];
            return nextExpandedStates;
        });
    };

    return [expandedStates, handleExpanderClick];
};


/**
 * Display the file facets. These display the number of files involved -- not the number of
 * experiments with files matching a criteria. As the primary input to this component is currently
 * an array of experiment IDs while these facets displays all the files involved with those
 * experiments, this component begins by retrieving information about all relevant files from the
 * DB. Each time an experiment is removed from the cart while viewing the cart page, this component
 * again retrieves all relevant files for the remaining experiments.
 */
const FileFacets = ({
    facets,
    usedFacetFields,
    selectedTerms,
    selectedFileCount,
    termClickHandler,
    visualizableOnly,
    visualizableOnlyChangeHandler,
    preferredOnly,
    preferredOnlyChangeHandler,
    facetLoadProgress,
    disabled,
    clearFacetSelections,
}) => {
    const [expandedStates, handleExpanderClick] = useExpanders(displayedFileFacetFields);

    return (
        <div className="cart__display-facets">
            <FacetCount count={selectedFileCount} element="file" facetLoadProgress={facetLoadProgress} />
            {facetLoadProgress === -1 ?
                <>
                    <Checkbox label="Show default data only" id="default-data-toggle" checked={preferredOnly} css="cart-checkbox" clickHandler={preferredOnlyChangeHandler} />
                    {!preferredOnly ? <Checkbox label="Show visualizable data only" id="visualizable-data-toggle" checked={visualizableOnly} css="cart-checkbox" clickHandler={visualizableOnlyChangeHandler} /> : null}
                </>
            : null}
            {facets && facets.length > 0 ?
                <>
                    {usedFacetFields.map((facetField) => {
                        const facetContent = facets.find((facet) => facet.field === facetField.field);
                        if (facetContent) {
                            const expanded = facetField.parent ? expandedStates[facetField.parent] : expandedStates[facetField.field];
                            return (
                                <Facet
                                    key={facetField.field}
                                    facet={facetContent}
                                    displayedFacetField={facetField}
                                    selectedFacetTerms={selectedTerms[facetField.field]}
                                    facetTermClickHandler={termClickHandler}
                                    expanded={expanded}
                                    expanderClickHandler={handleExpanderClick}
                                    options={{ supressTitle: !!facetField.parent, suppressVisualizable: preferredOnly }}
                                    clearFacetSelections={clearFacetSelections}
                                />
                            );
                        }
                        return null;
                    })}
                </>
            :
                <>
                    {facetLoadProgress === -1 ?
                        <div className="cart__empty-message">No files available</div>
                    : null}
                </>
            }
            {disabled || facetLoadProgress !== -1 ?
                <div className="cart__facet-disabled-overlay" />
            : null}
        </div>
    );
};

FileFacets.propTypes = {
    /** Array of objects for each displayed facet */
    facets: PropTypes.array,
    /** Currently displayed facet fields */
    usedFacetFields: PropTypes.array,
    /** Selected facet fields */
    selectedTerms: PropTypes.object,
    /** Count of the files selected by current selected facet terms */
    selectedFileCount: PropTypes.number,
    /** Callback when the user clicks on a file format facet item */
    termClickHandler: PropTypes.func.isRequired,
    /** True to check the Show Visualizable Data Only checkbox */
    visualizableOnly: PropTypes.bool,
    /** Call to handle clicks in the Visualize Only checkbox */
    visualizableOnlyChangeHandler: PropTypes.func.isRequired,
    /** True to check the Show Preferred Data Only checkbox */
    preferredOnly: PropTypes.bool,
    /** Call to handle clicks in the Preferred Only checkbox */
    preferredOnlyChangeHandler: PropTypes.func.isRequired,
    /** Facet-loading progress for progress bar, or null if not displayed */
    facetLoadProgress: PropTypes.number,
    /** True to disable the facets; grayed out and non-clickable */
    disabled: PropTypes.bool,
    /** Called when the user clears all selections in a facet */
    clearFacetSelections: PropTypes.func.isRequired,
};

FileFacets.defaultProps = {
    facets: [],
    usedFacetFields: [],
    selectedTerms: null,
    selectedFileCount: 0,
    visualizableOnly: false,
    preferredOnly: false,
    facetLoadProgress: null,
    disabled: false,
};


/**
 * Display the dataset facets relevant to the currently selected facet terms and datasets in the
 * cart.
 */
const DatasetFacets = ({
    facets,
    selectedTerms,
    selectedDatasetCount,
    termClickHandler,
    facetLoadProgress,
    clearFacetSelections,
}) => {
    const [expandedStates, handleExpanderClick] = useExpanders(displayedDatasetFacetFields);

    return (
        <div className="cart__display-facets">
            <FacetCount count={selectedDatasetCount} element="dataset" facetLoadProgress={facetLoadProgress} />
            {displayedDatasetFacetFields.map((facetField) => {
                const facetContent = facets.find((facet) => facet.field === facetField.field);
                if (facetContent) {
                    const expanded = facetField.parent ? expandedStates[facetField.parent] : expandedStates[facetField.field];
                    return (
                        <Facet
                            key={facetField.field}
                            facet={facetContent}
                            displayedFacetField={facetField}
                            selectedFacetTerms={selectedTerms[facetField.field]}
                            facetTermClickHandler={termClickHandler}
                            expanded={expanded}
                            expanderClickHandler={handleExpanderClick}
                            clearFacetSelections={clearFacetSelections}
                        />
                    );
                }
                return null;
            })}
        </div>
    );
};

DatasetFacets.propTypes = {
    /** Array of objects for each displayed facet */
    facets: PropTypes.array,
    /** Selected facet fields */
    selectedTerms: PropTypes.object,
    /** Number of datasets currently selected */
    selectedDatasetCount: PropTypes.number,
    /** Callback when the user clicks on a file format facet item */
    termClickHandler: PropTypes.func.isRequired,
    /** Facet-loading progress for progress bar, or null if not displayed */
    facetLoadProgress: PropTypes.number,
    /** Callback for clearing a single facet's selections */
    clearFacetSelections: PropTypes.func.isRequired,
};

DatasetFacets.defaultProps = {
    facets: [],
    selectedTerms: null,
    selectedDatasetCount: 0,
    facetLoadProgress: null,
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
 * Selector menu to choose between dataset types to view and download.
 */
const CartTypeSelector = ({ selectedDatasetType, usedDatasetTypes, typeChangeHandler }) => {
    // Add the "All datasets" option to the used dataset types.
    const displayedDatasets = Object.assign(defaultDatasetType, allowedDatasetTypes);

    return (
        <select value={selectedDatasetType} onChange={typeChangeHandler} className="cart-dataset-selector">
            {usedDatasetTypes.map((type) => <option key={type} value={type} className={`cart-dataset-option cart-dataset-option--${type}`}>{displayedDatasets[type].title}</option>)}
        </select>
    );
};

CartTypeSelector.propTypes = {
    /** Currently selected dataset type */
    selectedDatasetType: PropTypes.string.isRequired,
    /** Types of datasets in `elements` as collection names e.g. "experiments" */
    usedDatasetTypes: PropTypes.array.isRequired,
    /** Called when the user selects a new dataset type from the dropdown */
    typeChangeHandler: PropTypes.func.isRequired,
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
    analyses,
    selectedFileTerms,
    selectedDatasetTerms,
    selectedDatasetType,
    facetFields,
    savedCartObj,
    fileCounts,
    cartType,
    sharedCart,
    visualizable,
    preferredDefault,
}) => {
    // Disable the download button and show `disabledMessage` if the selected dataset matches "All
    // datasets."
    const disabledMessage = selectedDatasetType ? '' : 'Select single dataset type to download';

    // Make a list of all the dataset types currently in the cart.
    const usedDatasetTypes = elements.reduce((types, elementAtId) => {
        const type = atIdToType(elementAtId);
        return types.includes(type) ? types : types.concat(type);
    }, []);

    return (
        <div className="cart-tools">
            {elements.length > 0 ?
                <CartBatchDownload
                    elements={elements}
                    analyses={analyses}
                    selectedFileTerms={selectedFileTerms}
                    selectedDatasetTerms={selectedDatasetTerms}
                    selectedType={selectedDatasetType}
                    facetFields={facetFields}
                    cartType={cartType}
                    savedCartObj={savedCartObj}
                    sharedCart={sharedCart}
                    fileCounts={fileCounts}
                    visualizable={visualizable}
                    preferredDefault={preferredDefault}
                    disabledMessage={disabledMessage}
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
    /** All compiled analyses for the cart */
    analyses: PropTypes.array,
    /** Selected file facet terms */
    selectedFileTerms: PropTypes.object,
    /** Selected file facet terms */
    selectedDatasetTerms: PropTypes.object,
    /** Selected dataset type */
    selectedDatasetType: PropTypes.string.isRequired,
    /** Currently used facet field definitions */
    facetFields: PropTypes.array.isRequired,
    /** Cart as it exists in the database; use JSON payload method if none */
    savedCartObj: PropTypes.object,
    /** Type of cart: ACTIVE, OBJECT */
    cartType: PropTypes.string.isRequired,
    /** Elements in the shared cart, if that's being displayed */
    sharedCart: PropTypes.object,
    /** Number of files batch download will download for each download type */
    fileCounts: PropTypes.object,
    /** True if only visualizable files should be downloaded */
    visualizable: PropTypes.bool,
    /** True to download only preferred_default files */
    preferredDefault: PropTypes.bool,
};

CartTools.defaultProps = {
    elements: [],
    analyses: [],
    selectedFileTerms: null,
    selectedDatasetTerms: null,
    savedCartObj: null,
    sharedCart: null,
    fileCounts: {},
    visualizable: false,
    preferredDefault: false,
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
const CartSearchResultsControls = ({ currentTab, elements, currentPage, totalPageCount, updateCurrentPage }) => {
    if (currentTab === 'datasets' || totalPageCount > 1) {
        return (
            <div className="cart-search-results-controls">
                {currentTab === 'datasets'
                    ? <CartRemoveElements elements={elements.map((element) => element['@id'])} />
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
                            const [fileProp] = facetField.field.split('.');
                            if (facetField.getValue) {
                                file[fileProp] = facetField.getValue(file);
                            }
                        });
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
 * Update the `facets` array by incrementing the count of the term within it selected by the
 * `field` within the given `dataset`.
 * @param {array} facets Facet array to update - mutated!
 * @param {string} field Field key within the facet to update
 * @param {object} dataset Contains the term to add to the facet
 */
const addDatasetTermToFacet = (facets, field, dataset) => {
    const facetTerm = getObjectFieldValue(dataset, field);
    if (facetTerm !== undefined) {
        const matchingFacet = facets.find((facet) => facet.field === field);
        if (matchingFacet) {
            // The facet has been seen in this loop before, so add to or initialize
            // the relevant term within this facet.
            const matchingTerm = matchingFacet.terms.find((matchingFacetTerm) => matchingFacetTerm.term === facetTerm);
            if (matchingTerm) {
                // Facet term has been counted before, so add to its count. Mark the term as
                // visualizable if any file contributing to this term is visualizable.
                matchingTerm.count += 1;
            } else {
                // Facet term has not been counted before, so initialize a new facet term entry.
                matchingFacet.terms.push({ term: facetTerm, count: 1 });
            }
        } else {
            // The facet has not been seen in this loop before, so initialize it as
            // well as the value of the relevant term within the facet.
            facets.push({ field, terms: [{ term: facetTerm, count: 1 }] });
        }
    }
};


/**
 * Update the `facets` array by incrementing the count of the term within it selected by the
 * `field` within the given `file`.
 * @param {array} facets Facet array to update - mutated!
 * @param {string} field Field key within the facet to update
 * @param {object} file File containing the term to add to the facet
 */
const addFileTermToFacet = (facets, field, file) => {
    const facetTerm = getObjectFieldValue(file, field);
    const visualizable = isFileVisualizable(file);
    if (facetTerm !== undefined) {
        const matchingFacet = facets.find((facet) => facet.field === field);
        if (matchingFacet) {
            // The facet has been seen in this loop before, so add to or initialize
            // the relevant term within this facet.
            const matchingTerm = matchingFacet.terms.find((matchingFacetTerm) => matchingFacetTerm.term === facetTerm);
            if (matchingTerm) {
                // Facet term has been counted before, so add to its count. Mark the term as
                // visualizable if any file contributing to this term is visualizable.
                matchingTerm.count += 1;
                if (visualizable) {
                    matchingTerm.visualizable = visualizable;
                }
            } else {
                // Facet term has not been counted before, so initialize a new facet term entry.
                matchingFacet.terms.push({ term: facetTerm, count: 1, visualizable });
            }
        } else {
            // The facet has not been seen in this loop before, so initialize it as
            // well as the value of the relevant term within the facet.
            facets.push({ field, terms: [{ term: facetTerm, count: 1, visualizable }] });
        }
    }
};


/**
 * Extract the file @ids of the analyses selected by the given analysis titles.
 * @param {array} availableAnalyses Compiled analysis objects.
 * @param {array} analysisTitles Titles of analyses from which to extract file @ids.
 *
 * @return {array} Combined @ids of selected analysis files.
 */
const getAnalysesFileIds = (availableAnalyses, analysisTitles = []) => {
    const selectedFileIds = availableAnalyses.reduce((fileIds, analysis) => {
        if (analysisTitles.length === 0 || analysisTitles.includes(analysis.title)) {
            return fileIds.concat(analysis.files);
        }
        return fileIds;
    }, []);
    return _.uniq(selectedFileIds);
};


/**
 * Based on the currently selected facet terms and the current set of datasets in the cart,
 * generate the simplified facets and the subset of datasets these facets select.
 * @param {object} selectedTerms Currently selected terms within each facet
 * @param {array} datasets Datasets to consider when building these facets.
 * @param {array} usedFacetFields Facet fields to consider when assembling.
 *
 * @return {object}
 *     {array} facets - Array of simplified facet objects including fields and terms;
 *                               empty array if none
 *     {array} selectedFiles - Array of datasets selected by currently selected facets
 */
const assembleDatasetFacets = (selectedTerms, datasets, usedFacetFields) => {
    const assembledFacets = [];
    const selectedDatasets = [];

    if (datasets.length > 0) {
        const selectedFacetKeys = Object.keys(selectedTerms).filter((term) => selectedTerms[term].length > 0);
        datasets.forEach((dataset) => {
            // Determine whether the dataset passes the currently selected facet terms. Properties
            // within the dataset have to match any of the terms within a facet, and across all
            // facets that include selected terms. This is the "first test" I refer to later.
            let match = selectedFacetKeys.every((selectedFacetKey) => {
                // `selectedFacetKey` is one facet field, e.g. "assay_title".
                // `propValue` is the dataset's value for that field.
                const propValue = getObjectFieldValue(dataset, selectedFacetKey);

                // Determine if the dataset's `selectedFacetKey` prop has been selected by at
                // least one facet term.
                return selectedTerms[selectedFacetKey].indexOf(propValue) !== -1;
            });

            // Datasets that pass the first test add their properties to the relevant facet term
            // counts. Datasets that don't pass go through a second test to see if their properties
            // should appear unselected within a facet. Datasets that fail both tests get ignored
            // for facets.
            if (match) {
                // The dataset passed the first test, so its terms appear selected in their facets.
                // Add all its properties to the relevant facet terms.
                Object.keys(selectedTerms).forEach((facetField) => {
                    addDatasetTermToFacet(assembledFacets, facetField, dataset);
                });
                selectedDatasets.push(dataset);
            } else {
                // The dataset didn't pass the first test, so run the same test repeatedly but
                // with one facet removed from the test each time. For each easier test the
                // dataset passes, add to the corresponding term count for the removed facet,
                // allowing the user to select it to extend the set of selected datasets.
                selectedFacetKeys.forEach((selectedFacetField) => {
                    // Remove one facet containing a selection from the test.
                    const filteredSelectedFacetKeys = selectedFacetKeys.filter((key) => key !== selectedFacetField);
                    match = filteredSelectedFacetKeys.every((filteredSelectedFacetKey) => {
                        const datasetPropValue = getObjectFieldValue(dataset, filteredSelectedFacetKey);
                        return selectedTerms[filteredSelectedFacetKey].indexOf(datasetPropValue) !== -1;
                    });

                    // A match means to add to the count of the current facet field dataset term
                    // only.
                    if (match) {
                        addDatasetTermToFacet(assembledFacets, selectedFacetField, dataset);
                    }
                });
            }
        });

        // We need to include selected terms that happen to have a zero count, so add all
        // selected facet terms not yet included in `facets`.
        Object.keys(selectedTerms).forEach((field) => {
            const matchingFacet = assembledFacets.find((facet) => facet.field === field);
            if (matchingFacet) {
                // Find selected terms NOT in facets and add them with a zero count.
                const matchingFacetTerms = matchingFacet.terms.map((facetTerm) => facetTerm.term);
                const missingTerms = selectedTerms[field].filter((term) => matchingFacetTerms.indexOf(term) === -1);
                if (missingTerms.length > 0) {
                    missingTerms.forEach((term) => {
                        matchingFacet.terms.push({ term, count: 0, visualizable: false });
                    });
                }
            }
        });

        // Sort each facet's terms either alphabetically or by some criteria specific to a
        // facet. `facets` and `usedFacetFields` have the same order, but `facets` might
        // not have all possible facets -- just currently relevant ones.
        assembledFacets.forEach((facet) => {
            // We know a corresponding `usedFacetFields` entry exists because `facets` gets
            // built from it, so no not-found condition needs checking.
            const facetDisplay = usedFacetFields.find((facetField) => facetField.field === facet.field);
            facet.title = facetDisplay.title;
            facet.terms = _(facet.terms).sortBy((facetTerm) => facetTerm.term.toLowerCase());
        });
    }

    return { datasetFacets: assembledFacets.length > 0 ? assembledFacets : [], selectedDatasets };
};


/**
 * Based on the currently selected facet terms and the files collected from the datasets in the
 * cart, generate the simplified facets and the subset of files these facets select. `analyses` not
 * needed when `assembleFileFacets` called simply to reset the facets.
 * @param {object} selectedTerms Currently selected terms within each facet
 * @param {array} files Partial files to consider when building these facets.
 * @param {array} analyses Compiled analysis objects from experiments in cart.
 * @param {array} usedFacetFields Facet fields to consider when assembling.
 *
 * @return {object}
 *     {array} facets - Array of simplified facet objects including fields and terms;
 *                               empty array if none
 *     {array} selectedFiles - Array of partial files selected by currently selected facets
 */
const assembleFileFacets = (selectedTerms, files, analyses, usedFacetFields) => {
    const assembledFacets = [];
    const selectedFiles = [];
    const usedSelectedTerms = {};
    const usedFieldValues = usedFacetFields.map((facetField) => facetField.field);
    Object.keys(selectedTerms).forEach((term) => {
        if (usedFieldValues.includes(term)) {
            usedSelectedTerms[term] = selectedTerms[term];
        }
    });

    // Get complete list of files to consider -- processed files, and those associated with all
    // available analyses if any selected.
    let consideredFiles;
    consideredFiles = files.filter((file) => file.assembly);
    if (usedSelectedTerms.analysis && usedSelectedTerms.analysis.length > 0) {
        // Consider all files the selected analyses corresponds to.
        const fileIds = getAnalysesFileIds(analyses);
        consideredFiles = _.compact(fileIds.map((id) => files.find((file) => id === file['@id'])));
    }
    if (consideredFiles.length > 0) {
        const selectedFacetKeys = Object.keys(usedSelectedTerms).filter((term) => usedSelectedTerms[term].length > 0);
        consideredFiles.forEach((file) => {
            // Determine whether the file passes the currently selected facet terms. Properties
            // within the file have to match any of the terms within a facet, and across all
            // facets that include selected terms. This is the "first test" I refer to later.
            let match = selectedFacetKeys.every((selectedFacetKey) => {
                // `selectedFacetKey` is one facet field, e.g. "output_type".
                // `filePropValue` is the file's value for that field.
                const filePropValue = getObjectFieldValue(file, selectedFacetKey);

                // Determine if the file's `selectedFacetKey` prop has been selected by at
                // least one facet term.
                return usedSelectedTerms[selectedFacetKey].indexOf(filePropValue) !== -1;
            });

            // Files that pass the first test add their properties to the relevant facet term
            // counts. Files that don't pass go through a second test to see if their properties
            // should appear unselected within a facet. Files that fail both tests get ignored for
            // facets.
            if (match) {
                // The file passed the first test, so its terms appear selected in their facets.
                // Add all its properties to the relevant facet terms.
                Object.keys(usedSelectedTerms).forEach((facetField) => {
                    addFileTermToFacet(assembledFacets, facetField, file);
                });
                selectedFiles.push(file);
            } else {
                // The file didn't pass the first test, so run the same test repeatedly but
                // with one facet removed from the test each time. For each easier test the
                // file passes, add to the corresponding term count for the removed facet,
                // allowing the user to select it to extend the set of selected files.
                selectedFacetKeys.forEach((selectedFacetField) => {
                    // Remove one facet containing a selection from the test.
                    const filteredSelectedFacetKeys = selectedFacetKeys.filter((key) => key !== selectedFacetField);
                    match = filteredSelectedFacetKeys.every((filteredSelectedFacetKey) => {
                        const filePropValue = getObjectFieldValue(file, filteredSelectedFacetKey);
                        return selectedTerms[filteredSelectedFacetKey].indexOf(filePropValue) !== -1;
                    });

                    // A match means to add to the count of the current facet field file term
                    // only.
                    if (match) {
                        addFileTermToFacet(assembledFacets, selectedFacetField, file);
                    }
                });
            }
        });

        // We need to include selected terms that happen to have a zero count, so add all
        // selected facet terms not yet included in `facets`.
        Object.keys(usedSelectedTerms).forEach((field) => {
            const matchingFacet = assembledFacets.find((facet) => facet.field === field);
            if (matchingFacet) {
                // Find selected terms NOT in facets and add them with a zero count.
                const matchingFacetTerms = matchingFacet.terms.map((facetTerm) => facetTerm.term);
                const missingTerms = selectedTerms[field].filter((term) => matchingFacetTerms.indexOf(term) === -1);
                if (missingTerms.length > 0) {
                    missingTerms.forEach((term) => {
                        matchingFacet.terms.push({ term, count: 0, visualizable: false });
                    });
                }
            }
        });

        // Sort each facet's terms either alphabetically or by some criteria specific to a
        // facet. `facets` and `usedFacetFields` have the same order, but `facets` might
        // not have all possible facets -- just currently relevant ones.
        assembledFacets.forEach((facet) => {
            // We know a corresponding `usedFacetFields` entry exists because `facets` gets
            // built from it, so no not-found condition needs checking.
            const facetDisplay = usedFacetFields.find((facetField) => facetField.field === facet.field);
            facet.title = facetDisplay.title;
            facet.terms = facetDisplay.sorter ? facetDisplay.sorter(facet.terms, analyses) : _(facet.terms).sortBy((facetTerm) => facetTerm.term.toLowerCase());
        });
    }

    return { fileFacets: assembledFacets.length > 0 ? assembledFacets : [], selectedFiles, defaultFiles: filterForDefaultFiles(selectedFiles) };
};


/**
 * For any radio-button facets, select the first term if no items within them have been selected.
 * @param {array} facets Simplified facet object
 * @param {object} selectedTerms Selected terms within the facets
 *
 * @return {object} Same as `selectedTerms` but with radio-button facet terms selected
 */
const initRadioFacets = (facets, selectedTerms, usedFacetFields) => {
    const newSelectedTerms = {};
    usedFacetFields.forEach((facetField) => {
        if (facetField.radio && selectedTerms[facetField.field].length === 0) {
            // Assign the first term of the radio-button facet as the sole selection. In the
            // unusual case that no facet terms for this radio-button facet have been collected,
            // just copy the existing selection for the facet.
            const matchingFacet = facets.find((facet) => facet.field === facetField.field);
            newSelectedTerms[facetField.field] = (
                matchingFacet ? [matchingFacet.terms[0].term] : selectedTerms[facetField.field].slice(0)
            );
        } else {
            // Not a radio-button facet, or radio-button facet has selected terms; copy existing
            // selected terms.
            newSelectedTerms[facetField.field] = selectedTerms[facetField.field].slice(0);
        }
    });
    return newSelectedTerms;
};


/**
 * Make a selected-terms object showing no selections based on the given facet properties.
 * @param {array} usedFacetFields Currently used subset of `displayedFileFacetFields`.
 *
 * @return {object} Selected facet showing no selections; used with `assembleFileFacets`
 */
const initSelectedTerms = (usedFacetFields) => {
    const emptySelectedTerms = {};
    usedFacetFields.forEach((facetField) => {
        emptySelectedTerms[facetField.field] = [];
    });
    return emptySelectedTerms;
};


/**
 * Reset the facets to no selections as if the page has just been loaded.
 * @param {array} files Files to consider when building facets.
 * @param {array} usedFacetFields Facet fields to consider
 *
 * @return {object} Initial facet-term selections
 */
const resetDatasetFacets = (datasets, usedFacetFields) => {
    // Make an empty selected-terms object so `assembleDatasetFacets` can generate fresh simplified
    // facets.
    const emptySelectedTerms = initSelectedTerms(usedFacetFields);

    // Build the facets based on no selections, then select the first term of any radio-button
    // facets.
    const { datasetFacets } = assembleDatasetFacets(emptySelectedTerms, datasets, usedFacetFields);
    return initRadioFacets(datasetFacets, emptySelectedTerms, usedFacetFields);
};


/**
 * Reset the facets to no selections, and select the first term of radio-button facets, all as if
 * the page has just been loaded.
 * @param {array} files Files to consider when building facets.
 * @param {array} usedFacetFields Facet fields to consider
 *
 * @return {object} Initial facet-term selections
 */
const resetFileFacets = (files, analyses, usedFacetFields) => {
    // Make an empty selected-terms object so `assembleFileFacets` can generate fresh simplified
    // facets.
    const emptySelectedTerms = initSelectedTerms(usedFacetFields);

    // Build the facets based on no selections, then select the first term of any radio-button
    // facets.
    const { fileFacets } = assembleFileFacets(emptySelectedTerms, files, analyses, usedFacetFields);
    return initRadioFacets(fileFacets, emptySelectedTerms, usedFacetFields);
};


/**
 * Filter visualizable files to ones included in the selected facet terms.
 * @param {array} visualizableFiles Files in cart datasets that are visualizable
 * @param {object} selectedTerms Selected facet terms
 *
 * @return {array} `visualizableFiles` filtered by facet term selections
 */
const getSelectedVisualizableFiles = (visualizableFiles, selectedTerms) => (
    visualizableFiles.filter((file) => (
        Object.keys(selectedTerms).every((term) => (
            selectedTerms[term].length > 0 ? selectedTerms[term].includes(getObjectFieldValue(file, term)) : true
        ))
    ))
);


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
    const CHUNK_SIZE = 500;
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

        // Mutate the files to refer to their relevant analyses.
        processFilesAnalyses(datasetFiles, datasetAnalyses);
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

    // Build the facets based on the currently selected facet terms.
    const { datasetFacets, selectedDatasets } = React.useMemo(() => (
        assembleDatasetFacets(selectedDatasetTerms, viewableDatasets, displayedDatasetFacetFields)
    ), [selectedDatasetTerms, viewableDatasets]);

    // Build the facets based on the currently selected facet terms.
    const selectedDatasetFiles = React.useMemo(() => filterForDatasetFiles(allFiles, selectedDatasets), [allFiles, selectedDatasets]);
    const { fileFacets, selectedFiles } = React.useMemo(() => {
        let files = defaultOnly ? filterForDefaultFiles(selectedDatasetFiles) : selectedDatasetFiles;
        files = visualizableOnly ? filterForVisualizableFiles(files) : files;
        return assembleFileFacets(selectedFileTerms, files, analyses, usedFileFacetFields);
    }, [selectedFileTerms, selectedDatasets, visualizableOnly, defaultOnly, selectedDatasetFiles, analyses, usedFileFacetFields]);

    // Construct the file lists for the genome browser and raw file tabs.
    const rawdataFiles = React.useMemo(() => selectedDatasetFiles.filter((files) => !files.assembly), [selectedDatasetFiles]);
    const selectedVisualizableFiles = React.useMemo(() => {
        const files = defaultOnly ? filterForDefaultFiles(selectedDatasetFiles) : selectedDatasetFiles;
        return getSelectedVisualizableFiles(filterForVisualizableFiles(files), selectedFileTerms);
    }, [selectedDatasetFiles, selectedFileTerms]);

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
                            savedCartObj={savedCartObj}
                            selectedFileTerms={selectedFileTerms}
                            selectedDatasetTerms={selectedDatasetTerms}
                            selectedDatasetType={selectedDatasetType}
                            facetFields={requestedFacetFields}
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
                            {displayedTab === 'datasets'
                                ? (
                                    <DatasetFacets
                                        facets={datasetFacets}
                                        selectedTerms={selectedDatasetTerms}
                                        selectedDatasetCount={selectedDatasets.length}
                                        facetLoadProgress={facetProgress}
                                        termClickHandler={handleDatasetTermClick}
                                        clearFacetSelections={clearDatasetFacetSelections}
                                    />
                                ) : (
                                    <FileFacets
                                        facets={fileFacets}
                                        usedFacetFields={usedFileFacetFields}
                                        elements={selectedDatasets}
                                        selectedTerms={selectedFileTerms}
                                        termClickHandler={handleFileTermClick}
                                        selectedFileCount={selectedFiles.length}
                                        visualizableOnly={visualizableOnly}
                                        visualizableOnlyChangeHandler={handleVisualizableOnlyChange}
                                        preferredOnly={defaultOnly}
                                        preferredOnlyChangeHandler={handlePreferredOnlyChange}
                                        facetLoadProgress={facetProgress}
                                        disabled={displayedTab === 'rawdata'}
                                        clearFacetSelections={clearFileFacetSelections}
                                    />
                                )
                            }
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
                                    />
                                    <CartSearchResults
                                        elements={selectedDatasets}
                                        currentPage={pageNumbers.datasets}
                                        cartControls={cartType !== 'OBJECT'}
                                    />
                                </TabPanelPane>
                                <TabPanelPane key="browser">
                                    <CartSearchResultsControls
                                        currentTab={displayedTab}
                                        elements={selectedDatasets}
                                        currentPage={pageNumbers.browser}
                                        totalPageCount={totalPageCount.browser}
                                        updateCurrentPage={updateDisplayedPage}
                                    />
                                    {selectedFileTerms.assembly && selectedFileTerms.assembly.length > 0
                                        ? <CartBrowser files={selectedVisualizableFiles} assembly={selectedFileTerms.assembly[0]} pageNumber={pageNumbers.browser} />
                                        : null}
                                </TabPanelPane>
                                <TabPanelPane key="processeddata">
                                    <CartSearchResultsControls
                                        currentTab={displayedTab}
                                        elements={selectedDatasets}
                                        currentPage={pageNumbers.processeddata}
                                        totalPageCount={totalPageCount.processeddata}
                                        updateCurrentPage={updateDisplayedPage}
                                    />
                                    <CartFiles files={selectedFiles} currentPage={pageNumbers.processeddata} defaultOnly={defaultOnly} />
                                </TabPanelPane>
                                <TabPanelPane key="rawdata">
                                    <CartSearchResultsControls
                                        currentTab={displayedTab}
                                        elements={selectedDatasets}
                                        currentPage={pageNumbers.rawdata}
                                        totalPageCount={totalPageCount.rawdata}
                                        updateCurrentPage={updateDisplayedPage}
                                    />
                                    <CartFiles files={rawdataFiles} currentPage={pageNumbers.rawdata} />
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
