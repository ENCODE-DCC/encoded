/**
 * Components for rendering the /carts/ and /cart-view/ page.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import _ from 'underscore';
import { encodedURIComponent } from '../../libs/query_encoding';
import { svgIcon } from '../../libs/svg-icons';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';
import Pager from '../../libs/ui/pager';
import { Panel, PanelBody, PanelHeading, TabPanel, TabPanelPane } from '../../libs/ui/panel';
import { tintColor, isLight } from '../datacolors';
import GenomeBrowser, { annotationTypeMap } from '../genome_browser';
import { itemClass, atIdToType } from '../globals';
import { requestObjects, ItemAccessories, isFileVisualizable, computeAssemblyAnnotationValue, filterForVisualizableFiles } from '../objectutils';
import { ResultTableList } from '../search';
import CartBatchDownload from './batch_download';
import CartClearButton from './clear';
import CartLockTrigger from './lock';
import CartMergeShared from './merge_shared';
import Status from '../status';
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
 * @return {array} Same as `facetTerms` but sorted.
 */
const assemblySorter = facetTerms => (
    // Negate the sorting value to sort from highest to lowest.
    _(facetTerms).sortBy(facetTerm => -computeAssemblyAnnotationValue(facetTerm.term))
);


/**
 * List of allowed dataset types. Generally maps from collection names (e.g. '/experiments/' to a
 * displayable title.
 */
const datasetTypes = {
    all: { title: 'All dataset types', type: '' }, // Default always first
    experiments: { title: 'Experiments', type: 'Experiment' },
    annotations: { title: 'Annotations', type: 'Annotation' },
    'functional-characterization-experiments': { title: 'Functional characterizations', type: 'FunctionalCharacterizationExperiment' },
};
const DEFAULT_DATASET_TYPE = Object.keys(datasetTypes)[0];


/**
 * File facet fields to display in order of display.
 * - field: `facet` field property
 * - title: Displayed facet title
 * - radio: True if radio-button facet; otherwise checkbox facet
 * - dataset: True to retrieve value from dataset instead of files
 * - sorter: Function to sort terms within the facet
 */
const displayedFacetFields = [
    { field: 'assembly', title: 'Genome assembly', radio: true, sorter: assemblySorter },
    { field: 'output_type', title: 'Output type' },
    { field: 'file_type', title: 'File type' },
    { field: 'file_format', title: 'File format' },
    { field: 'assay_term_name', title: 'Assay term name' },
    { field: 'biosample_ontology.term_name', title: 'Biosample term name', dataset: true },
    { field: 'target.label', title: 'Target of assay', dataset: true },
    { field: 'annotation_type', title: 'Annotation type', dataset: true },
    { field: 'lab.title', title: 'Lab' },
    { field: 'status', title: 'Status' },
];

/** Facet `field` values for properties from dataset instead of files */
const datasetFacets = displayedFacetFields.filter(facetField => facetField.dataset).map(facetField => facetField.field);

/** File facet fields to request from server -- superset of those displayed in facets */
const requestedFacetFields = displayedFacetFields.concat([
    { field: '@id' },
    { field: 'file_format_type' },
    { field: 'title' },
    { field: 'href' },
    { field: 'dataset' },
    { field: 'biological_replicates' },
]);


/**
 * Display a page of cart contents within the cart display.
 */
class CartSearchResults extends React.Component {
    constructor() {
        super();
        this.state = {
            /** Carted elements to display as search results; includes one page of search results */
            elementsForDisplay: null,
        };
        this.retrievePageElements = this.retrievePageElements.bind(this);
    }

    componentDidMount() {
        this.retrievePageElements();
    }

    componentDidUpdate(prevProps) {
        const { currentPage, elements, loggedIn } = this.props;
        if (prevProps.currentPage !== currentPage || !_.isEqual(prevProps.elements, elements) || (prevProps.loggedIn !== loggedIn)) {
            this.retrievePageElements();
        }
    }

    /**
     * Given the whole cart elements as a list of @ids as well as the currently displayed page
     * number, perform a search of a page of elements. If every element in the cart is an
     * experiment, add "?type=Experiment" to the search query. For now, this condition is always
     * true.
     */
    retrievePageElements() {
        const pageStartIndex = this.props.currentPage * PAGE_ELEMENT_COUNT;
        const currentPageElements = this.props.elements.slice(pageStartIndex, pageStartIndex + PAGE_ELEMENT_COUNT);
        const experimentTypeQuery = this.props.elements.every(element => element.match(/^\/experiments\/.*?\/$/) !== null);
        const cartQueryString = `/search/?limit=all${experimentTypeQuery ? '&type=Experiment' : ''}`;
        requestObjects(currentPageElements, cartQueryString).then((searchResults) => {
            this.setState({ elementsForDisplay: searchResults });
        });
    }

    render() {
        if (this.state.elementsForDisplay && this.state.elementsForDisplay.length === 0) {
            return <div className="nav result-table cart__empty-message">No visible datasets on this page.</div>;
        }
        return <ResultTableList results={this.state.elementsForDisplay || []} cartControls={this.props.cartControls} mode="cart-view" />;
    }
}

CartSearchResults.propTypes = {
    /** Array of cart item @ids */
    elements: PropTypes.array,
    /** Page of results to display */
    currentPage: PropTypes.number,
    /** True if displaying an active cart */
    cartControls: PropTypes.bool,
    /** True if user has logged in */
    loggedIn: PropTypes.bool,
};

CartSearchResults.defaultProps = {
    elements: [],
    currentPage: 0,
    cartControls: false,
    loggedIn: false,
};


/**
 * Display browser tracks for the selected page of files.
 */
const CartBrowser = ({ files, assembly, pageNumber }) => {
    // Extract the current page of file objects.
    const pageStartingIndex = pageNumber * PAGE_TRACK_COUNT;
    const pageFiles = files.slice(pageStartingIndex, pageStartingIndex + PAGE_TRACK_COUNT);

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
    return <GenomeBrowser files={pageFiles} label={'cart'} assembly={assembly} expanded sortParam={sortParam} />;
};

CartBrowser.propTypes = {
    /** Files of all visualizable tracks, not just on the displayed page */
    files: PropTypes.array.isRequired,
    /** Assembly to display; can be empty before partial files loaded */
    assembly: PropTypes.string,
    /** Page of files to display */
    pageNumber: PropTypes.number.isRequired,
};

CartBrowser.defaultProps = {
    assembly: '',
};


/**
 * Display the list of files selected by the current cart facet selections.
 */
const CartFiles = ({ files, currentPage }) => {
    if (files.length > 0) {
        const pageStartIndex = currentPage * PAGE_FILE_COUNT;
        const currentPageFiles = files.slice(pageStartIndex, pageStartIndex + PAGE_ELEMENT_COUNT);
        return (
            <div className="cart-list cart-list--file">
                {currentPageFiles.map(file =>
                    <a key={file['@id']} href={file['@id']} className="cart-list-item">
                        <div className={`cart-list-item__file-type cart-list-item__file-type--${file.file_format}`}>
                            <div className="cart-list-item__format">{file.file_format}</div>
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
                )}
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
};


/**
 * Display a count of the total number of files selected for download given the current facet term
 * selections. Shows the facet-loading progress bar if needed.
 */
class FileCount extends React.Component {
    constructor() {
        super();
        this.state = {
            triggerEnabled: false,
        };
        this.handleAnimationEnd = this.handleAnimationEnd.bind(this);
    }

    /**
     * Inserts the <div> to show the yellow highlight when the file count changes.
     */
    componentDidUpdate(prevProps) {
        if (prevProps.fileCount !== this.props.fileCount) {
            this.setState({ triggerEnabled: true });
        }
    }

    /**
     * Called when CSS animation ends. Removes the <div> that shows the yellow highlight when the
     * count changes.
     */
    handleAnimationEnd() {
        this.setState({ triggerEnabled: false });
    }

    render() {
        const { fileCount, facetLoadProgress } = this.props;
        const fileCountFormatted = fileCount.toLocaleString ? fileCount.toLocaleString() : fileCount.toString();

        if (facetLoadProgress === -1) {
            return (
                <div className="cart__facet-file-count">
                    {this.state.triggerEnabled ? <div className="cart__facet-file-count-changer" onAnimationEnd={this.handleAnimationEnd} /> : null}
                    {fileCount > 0 ?
                        <span>{fileCountFormatted} {fileCount === 1 ? 'file' : 'files'} selected</span>
                    :
                        <span>No files selected for download</span>
                    }
                </div>
            );
        }

        return <progress value={facetLoadProgress} max="100" />;
    }
}

FileCount.propTypes = {
    /** Number of files selected for download */
    fileCount: PropTypes.number,
    /** Value for the progress bar; -1 to not show it */
    facetLoadProgress: PropTypes.number,
};

FileCount.defaultProps = {
    fileCount: 0,
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
class FacetTerm extends React.Component {
    constructor() {
        super();
        this.handleTermClick = this.handleTermClick.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);
    }

    /**
     * Called when user clicks a term within a facet.
     */
    handleTermClick() {
        this.props.termClickHandler(this.props.term);
    }

    /**
     * Called when user types a key while focused on a facet term. If the user types a space or
     * return we call the term click handler -- needed for a11y because we have a <div> acting as a
     * button instead of an actual <button>.
     * @param {object} e React synthetic event
     */
    handleKeyDown(e) {
        if (e.keyCode === 13 || e.keyCode === 32) {
            e.preventDefault();
            this.props.termClickHandler(this.props.term);
        }
    }

    render() {
        const { term, termCount, maxTermCount, selected, visualizable, FacetTermSelectRenderer } = this.props;
        return (
            <li className="cart-facet-term">
                <div
                    className="cart-facet-term__item"
                    role="button"
                    tabIndex="0"
                    id={`cart-facet-term-${term}`}
                    onKeyDown={this.handleKeyDown}
                    onClick={this.handleTermClick}
                    aria-pressed={selected}
                    aria-label={`${termCount} ${term} file${termCount === 1 ? '' : 's'}${visualizable ? ' visualizable' : ''}`}
                >
                    <FacetTermSelectRenderer checked={selected} />
                    <div className="cart-facet-term__text">{term}</div>
                    <FacetTermMagnitude termCount={termCount} maxTermCount={maxTermCount} />
                    <div className="cart-facet-term__visualizable">
                        {visualizable ?
                            <div title="Selects visualizable files">{svgIcon('genomeBrowser')}</div>
                        : null}
                    </div>
                </div>
            </li>
        );
    }
}

FacetTerm.propTypes = {
    /** Displayed facet term */
    term: PropTypes.string.isRequired,
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
        sessionPromise = Promise.resolve(session._csrft);
    }

    // We could have more dataset @ids than the /search/ endpoint can handle in the query string,
    // so pass the @ids in a POST request payload instead to the /search_elements/ endpoint.
    const fieldQuery = requestedFacetFields.reduce((query, facetField) => `${query}&field=${facetField.dataset ? '' : 'files.'}${facetField.field}`, '');
    return sessionPromise.then(csrfToken => (
        fetch(`/search_elements/type=Dataset${fieldQuery}&field=files.restricted&limit=all&filterresponse=off`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
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
 * Display the facet title and expansion icon, and react to clicks in the button to tell the parent
 * component that a facet needs to be expanded or collapsed.
 */
class FacetExpander extends React.Component {
    constructor() {
        super();
        this.handleKeyDown = this.handleKeyDown.bind(this);
    }

    /**
     * Called when the user types a key while a facet title expansion button has focus. If the user
     * typed Return or Space, call the parent component to handle the expand/collapse of the facet.
     * @param {object} e React synthetic event
     */
    handleKeyDown(e) {
        if (e.keyCode === 13 || e.keyCode === 32) {
            e.preventDefault();
            this.props.expanderEventHandler(e);
        }
    }

    render() {
        const { title, field, labelId, expanded, expanderEventHandler } = this.props;
        return (
            <div
                role="button"
                tabIndex="0"
                id={labelId}
                className="cart-facet__expander"
                aria-controls={field}
                aria-expanded={expanded}
                onKeyDown={this.handleKeyDown}
                onClick={expanderEventHandler}
            >
                <div className="cart-facet__expander-title">
                    {title}
                </div>
                <i className={`icon icon-chevron-${expanded ? 'up' : 'down'}`} />
            </div>
        );
    }
}

FacetExpander.propTypes = {
    /** Displayed title of the facet */
    title: PropTypes.string.isRequired,
    /** File facet field representing this facet */
    field: PropTypes.string.isRequired,
    /** Used as an id for this button corresponding to expanded component label */
    labelId: PropTypes.string.isRequired,
    /** True if facet is currently expanded */
    expanded: PropTypes.bool.isRequired,
    /** Called when the user clicks the expander button */
    expanderEventHandler: PropTypes.func.isRequired,
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
        const { facet, displayedFacetField, expanded, selectedFacetTerms } = this.props;
        const maxTermCount = Math.max(...facet.terms.map(term => term.count));
        const labelId = `${displayedFacetField.field}-label`;
        const FacetTermSelectRenderer = displayedFacetField.radio ? FacetTermRadio : FacetTermCheck;
        return (
            <div className="facet">
                <FacetExpander title={facet.title} field={displayedFacetField.field} labelId={labelId} expanded={expanded} expanderEventHandler={this.handleExpanderEvent} />
                {expanded ?
                    <ul className="cart-facet" role="region" id={displayedFacetField.field} aria-labelledby={labelId}>
                        {facet.terms.map(facetTerm => (
                            <FacetTerm
                                key={facetTerm.term}
                                term={facetTerm.term}
                                termCount={facetTerm.count}
                                visualizable={facetTerm.visualizable}
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
    /** Field name representing the facet being displayed */
    displayedFacetField: PropTypes.object.isRequired,
    /** True if facet should appear expanded */
    expanded: PropTypes.bool.isRequired,
    /** Called when the expander button is clicked */
    expanderClickHandler: PropTypes.func.isRequired,
    /** Selected term keys */
    selectedFacetTerms: PropTypes.array,
    /** Called when a facet term is clicked */
    facetTermClickHandler: PropTypes.func.isRequired,
};

Facet.defaultProps = {
    selectedFacetTerms: [],
};


/**
 * Display a checkbox and label to allow users to filter out facet terms not included in any
 * visualizable files.
 */
const VisualizableTermsToggle = ({ visualizableOnly, handleClick }) => (
    <div className="cart-viz-toggle">
        <button id="viz-terms-toggle" role="checkbox" aria-checked={visualizableOnly} onClick={handleClick}>
            <div className={`cart-viz-toggle__check${visualizableOnly ? ' cart-viz-toggle__check--checked' : ''}`}>
                {visualizableOnly ? <i className="icon icon-check" /> : null}
            </div>
            <label htmlFor="viz-terms-toggle">
                <div className="cart-viz-toggle__label-text">Show visualizable data only</div>
                <div className="cart-viz-toggle__icon">{svgIcon('genomeBrowser')}</div>
            </label>
        </button>
    </div>
);

VisualizableTermsToggle.propTypes = {
    /** True to display checkbox as checked */
    visualizableOnly: PropTypes.bool,
    /** Callback when button is clicked */
    handleClick: PropTypes.func.isRequired,
};

VisualizableTermsToggle.defaultProps = {
    visualizableOnly: false,
};


/**
 * Display the file facets. These display the number of files involved -- not the number of
 * experiments with files matching a criteria. As the primary input to this component is currently
 * an array of experiment IDs while these facets displays all the files involved with those
 * experiments, this component begins by retrieving information about all relevant files from the
 * DB. Each time an experiment is removed from the cart while viewing the cart page, this component
 * again retrieves all relevant files for the remaining experiments.
 */
class FileFacets extends React.Component {
    constructor() {
        super();

        // Initialize the expanded state of every facet; only the first one is expanded by default.
        const expandedStates = {};
        displayedFacetFields.forEach((facetField, index) => {
            expandedStates[facetField.field] = index === 0;
        });
        this.state = {
            /** Tracks expanded/nonexpanded states of every facet */
            expanded: expandedStates,
        };

        this.files = [];
        this.fileCount = 0;

        this.handleExpanderClick = this.handleExpanderClick.bind(this);
    }

    /**
     * Called when the user clicks a facet expander button. Updates the expander states so the
     * facets re-render to the new expanded states.
     * @param {string} field Field name for clicked facet expander
     * @param {bool}   altKey True if alt/option key down at time of click
     */
    handleExpanderClick(field, altKey) {
        this.setState((state) => {
            if (altKey) {
                // Alt key held down, so expand or collapse *all* facets.
                const nextExpandedState = !state.expanded[field];
                const expandedStates = {};
                displayedFacetFields.forEach((facetField) => {
                    expandedStates[facetField.field] = nextExpandedState;
                });
                return { expanded: expandedStates };
            }

            // Alt key not held down, so just expand or collapse the clicked facet.
            const nextExpandedStates = Object.assign({}, state.expanded);
            nextExpandedStates[field] = !nextExpandedStates[field];
            return { expanded: nextExpandedStates };
        });
    }

    render() {
        const {
            facets,
            selectedTerms,
            selectedFileCount,
            termClickHandler,
            visualizableOnly,
            visualizableOnlyChangeHandler,
            facetLoadProgress,
            disabled,
        } = this.props;

        return (
            <div className="cart__display-facets">
                <FileCount fileCount={selectedFileCount} facetLoadProgress={facetLoadProgress} />
                {facetLoadProgress === -1 ?
                    <VisualizableTermsToggle visualizableOnly={visualizableOnly} handleClick={visualizableOnlyChangeHandler} />
                : null}
                <div>
                    {facets && facets.length > 0 ?
                        <div>
                            {displayedFacetFields.map((displayedFacetField) => {
                                const facetContent = facets.find(facet => facet.field === displayedFacetField.field);
                                if (facetContent) {
                                    return (
                                        <div key={displayedFacetField.field}>
                                            <Facet
                                                key={displayedFacetField.field}
                                                displayedFacetField={displayedFacetField}
                                                facet={facetContent}
                                                selectedFacetTerms={selectedTerms[displayedFacetField.field]}
                                                facetTermClickHandler={termClickHandler}
                                                expanded={this.state.expanded[displayedFacetField.field]}
                                                expanderClickHandler={this.handleExpanderClick}
                                            />
                                        </div>
                                    );
                                }
                                return null;
                            })}
                        </div>
                    :
                        <React.Fragment>
                            {facetLoadProgress === -1 ?
                                <div className="cart__empty-message">No files available</div>
                            : null}
                        </React.Fragment>
                    }
                </div>
                {disabled || facetLoadProgress !== -1 ?
                    <div className="cart__facet-disabled-overlay" />
                : null}
            </div>
        );
    }
}

FileFacets.propTypes = {
    /** Array of objects for each displayed facet */
    facets: PropTypes.array,
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
    /** Facet-loading progress for progress bar, or null if not displayed */
    facetLoadProgress: PropTypes.number,
    /** True to disable the facets; grayed out and non-clickable */
    disabled: PropTypes.bool,
};

FileFacets.defaultProps = {
    facets: [],
    selectedTerms: null,
    selectedFileCount: 0,
    visualizableOnly: false,
    facetLoadProgress: null,
    disabled: false,
};


/**
 * Display a button that links to experiment search results. This *only* works for Experiments, not
 * FCCs for now.
 */
const MAX_SEARCHABLE_DATASETS = 125; // Maximum number of datasets for search-results links.
const CartDatasetSearch = ({ elements, usedDatasetTypes }, reactContext) => {
    const [isWarningVisible, setIsWarningVisible] = React.useState(false);

    // Filter to the actual dataset types; not including 'all'.
    const actualDatasetTypes = usedDatasetTypes.filter(type => type !== 'all');

    // Called when the user clicks the Dataset Search button.
    const handleButtonClick = () => {
        if (elements.length > MAX_SEARCHABLE_DATASETS) {
            setIsWarningVisible(true);
        } else {
            // Build type= query based on the types of datasets in `elements`.
            const typeQuery = actualDatasetTypes.map(type => `type=${datasetTypes[type].type}`).join('&');
            const datasetsQuery = elements.map(element => `@id=${encodedURIComponent(element)}`).join('&');
            const query = `/search/?${typeQuery}&${datasetsQuery}`;
            reactContext.navigate(query);
        }
    };

    // Called when the user closes the warning modal.
    const handleCloseClick = () => {
        setIsWarningVisible(false);
    };

    // Only display the Dataset Search button if we have at least one experiment in the cart.
    if (elements.length > 0) {
        return (
            <React.Fragment>
                <button onClick={handleButtonClick} className="btn btn-sm btn-info btn-inline cart-dataset-search">Dataset search</button>
                {isWarningVisible ?
                    <Modal closeModal={handleCloseClick}>
                        <ModalHeader title={<h4>Cart dataset search results</h4>} closeModal={handleCloseClick} />
                        <ModalBody>
                            Viewing cart dataset search results requires {MAX_SEARCHABLE_DATASETS} datasets
                            or fewer. This cart contains {elements.length} datasets.
                        </ModalBody>
                        <ModalFooter
                            closeModal={handleCloseClick}
                        />
                    </Modal>
                : null}
            </React.Fragment>
        );
    }
    return null;
};

CartDatasetSearch.propTypes = {
    /** Dataset @ids in the cart */
    elements: PropTypes.array.isRequired,
    /** Types of datasets in `elements` as collection names e.g. "experiments" */
    usedDatasetTypes: PropTypes.array.isRequired,
};

CartDatasetSearch.contextTypes = {
    navigate: PropTypes.func,
};


/**
 * Selector menu to choose between dataset types to view and download.
 */
const CartTypeSelector = ({ selectedDatasetType, usedDatasetTypes, typeChangeHandler }) => {
    // Add the "All datasets" option to the used dataset types.
    const displayedDatasets = Object.assign(defaultDatasetType, allowedDatasetTypes);

    return (
        <select value={selectedDatasetType} onChange={typeChangeHandler} className="cart-dataset-selector">
            {usedDatasetTypes.map(type => <option key={type} value={type} className={`cart-dataset-option cart-dataset-option--${type}`}>{displayedDatasets[type].title}</option>)}
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
 * Display cart tool buttons. If `savedCartObj` is supplied, supply it for the metadata.tsv line
 * in the resulting files.txt.
 */
const CartTools = ({ elements, selectedTerms, selectedDatasetType, typeChangeHandler, savedCartObj, viewableDatasets, fileCounts, cartType, sharedCart, visualizable, inProgress }) => {
    // Disable the download button and show `disabledMessage` if the selected dataset matches "All
    // datasets."
    const disabledMessage = selectedDatasetType === DEFAULT_DATASET_TYPE ? 'Select dataset type to download' : '';
    const selectedType = datasetTypes[selectedDatasetType].type;

    // Make a list of all the dataset types currently in the cart.
    const usedDatasetTypes = [Object.keys(defaultDatasetType)[0]].concat(elements.reduce((types, elementAtId) => {
        const type = atIdToType(elementAtId);
        return types.includes(type) ? types : types.concat(type);
    }, []));

    return (
        <div className="cart-tools">
            <CartTypeSelector selectedDatasetType={selectedDatasetType} usedDatasetTypes={usedDatasetTypes} typeChangeHandler={typeChangeHandler} />
            {elements.length > 0 ?
                <CartBatchDownload
                    elements={elements}
                    selectedTerms={selectedTerms}
                    selectedType={selectedType}
                    datasetFacets={datasetFacets}
                    cartType={cartType}
                    savedCartObj={savedCartObj}
                    sharedCart={sharedCart}
                    fileCounts={fileCounts}
                    visualizable={visualizable}
                    disabledMessage={disabledMessage}
                />
            : null}
            {cartType === 'OBJECT' ? <CartMergeShared sharedCartObj={sharedCart} viewableDatasets={viewableDatasets} /> : null}
            {cartType === 'ACTIVE' || cartType === 'MEMORY' ?
                <div className="cart-tools-extras">
                    {cartType !== 'MEMORY' ? <CartLockTrigger savedCartObj={savedCartObj} inProgress={inProgress} /> : null}
                    <CartClearButton />
                </div>
            : null}
            <CartDatasetSearch elements={elements} usedDatasetTypes={usedDatasetTypes} />
        </div>
    );
};

CartTools.propTypes = {
    /** Cart elements */
    elements: PropTypes.array,
    /** Selected facet terms */
    selectedTerms: PropTypes.object,
    /** Selected dataset type */
    selectedDatasetType: PropTypes.string.isRequired,
    /** Called when the user selects a new dataset type */
    typeChangeHandler: PropTypes.func.isRequired,
    /** Cart as it exists in the database; use JSON payload method if none */
    savedCartObj: PropTypes.object,
    /** Viewable cart element @ids */
    viewableDatasets: PropTypes.array,
    /** Type of cart: ACTIVE, OBJECT, MEMORY */
    cartType: PropTypes.string.isRequired,
    /** Elements in the shared cart, if that's being displayed */
    sharedCart: PropTypes.object,
    /** Number of files batch download will download for each download type */
    fileCounts: PropTypes.object,
    /** True if only visualizable files should be downloaded */
    visualizable: PropTypes.bool,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
};

CartTools.defaultProps = {
    elements: [],
    selectedTerms: null,
    savedCartObj: null,
    viewableDatasets: null,
    sharedCart: null,
    fileCounts: {},
    visualizable: false,
};


/**
 * Display the pager control area.
 */
const CartPager = ({ currentPage, totalPageCount, updateCurrentPage }) => (
    <React.Fragment>
        {totalPageCount > 1 ?
            <div className="cart-pager-area">
                <Pager total={totalPageCount} current={currentPage} updateCurrentPage={updateCurrentPage} />
            </div>
        : null}
    </React.Fragment>
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
                        datasetFacets.forEach((datasetFacet) => {
                            const [experimentProp] = datasetFacet.split('.');
                            file[experimentProp] = dataset[experimentProp];
                        });
                        currentFilesPartial.push(file);
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
 * `field` within the given `file`.
 * @param {array} facets Facet array to update - mutated!
 * @param {string} field Field key within the facet to update
 * @param {object} file File containing the term to add to the facet
 */
const addFileTermToFacet = (facets, field, file) => {
    const facetTerm = getObjectFieldValue(file, field);
    const visualizable = isFileVisualizable(file);
    if (facetTerm !== undefined) {
        const matchingFacet = facets.find(facet => facet.field === field);
        if (matchingFacet) {
            // The facet has been seen in this loop before, so add to or initialize
            // the relevant term within this facet.
            const matchingTerm = matchingFacet.terms.find(matchingFacetTerm => matchingFacetTerm.term === facetTerm);
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
 * Based on the currently selected facet terms and the files collected from the datasets in the
 * cart, generate the simplified facets and the subset of files these facets select.
 * @param {object} selectedTerms Currently selected terms within each facet
 * @param {array} files Partial files to consider when building these facets.
 *
 * @return {object}
 *     {array} facets - Array of simplified facet objects including fields and terms;
 *                               empty array if none
 *     {array} selectedFiles - Array of partial files selected by currently selected facets
 */
const assembleFacets = (selectedTerms, files) => {
    const assembledFacets = [];
    const selectedFiles = [];
    const processedFiles = files.filter(file => file.assembly);
    if (processedFiles.length > 0) {
        const selectedFacetKeys = Object.keys(selectedTerms).filter(term => selectedTerms[term].length > 0);
        processedFiles.forEach((file) => {
            // Determine whether the file passes the currently selected facet terms. Properties
            // within the file have to match any of the terms within a facet, and across all
            // facets that include selected terms. This is the "first test" I refer to later.
            let match = selectedFacetKeys.every((selectedFacetKey) => {
                // `selectedFacetKey` is one facet field, e.g. "output_type".
                // `filePropValue` is the file's value for that field.
                const filePropValue = getObjectFieldValue(file, selectedFacetKey);

                // Determine if the file's `selectedFacetKey` prop has been selected by at
                // least one facet term.
                return selectedTerms[selectedFacetKey].indexOf(filePropValue) !== -1;
            });

            // Files that pass the first test add their properties to the relevant facet term
            // counts. Files that don't pass go through a second test to see if their properties
            // should appear unselected within a facet. Files that fail both tests get ignored for
            // facets.
            if (match) {
                // The file passed the first test, so its terms appear selected in their facets.
                // Add all its properties to the relevant facet terms.
                Object.keys(selectedTerms).forEach((facetField) => {
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
                    const filteredSelectedFacetKeys = selectedFacetKeys.filter(key => key !== selectedFacetField);
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
        Object.keys(selectedTerms).forEach((field) => {
            const matchingFacet = assembledFacets.find(facet => facet.field === field);
            if (matchingFacet) {
                // Find selected terms NOT in facets and add them with a zero count.
                const matchingFacetTerms = matchingFacet.terms.map(facetTerm => facetTerm.term);
                const missingTerms = selectedTerms[field].filter(term => matchingFacetTerms.indexOf(term) === -1);
                if (missingTerms.length > 0) {
                    missingTerms.forEach((term) => {
                        matchingFacet.terms.push({ term, count: 0, visualizable: false });
                    });
                }
            }
        });

        // Sort each facet's terms either alphabetically or by some criteria specific to a
        // facet. `facets` and `displayedFacetFields` have the same order, but `facets` might
        // not have all possible facets -- just currently relevant ones.
        assembledFacets.forEach((facet) => {
            // We know a corresponding `displayedFacetFields` entry exists because `facets` gets
            // built from it, so no not-found condition needs checking.
            const facetDisplay = displayedFacetFields.find(displayedFacetField => displayedFacetField.field === facet.field);
            facet.title = facetDisplay.title;
            facet.terms = facetDisplay.sorter ?
                facetDisplay.sorter(facet.terms)
            :
                _(facet.terms).sortBy(facetTerm => facetTerm.term.toLowerCase());
        });
    }

    return { facets: assembledFacets.length > 0 ? assembledFacets : [], selectedFiles };
};


/**
 * For any radio-button facets, select the first term if no items within them have been selected.
 * @param {array} facets Simplified facet object
 * @param {object} selectedTerms Selected terms within the facets
 *
 * @return {object} Same as `selectedTerms` but with radio-button facet terms selected
 */
const initRadioFacets = (facets, selectedTerms) => {
    const newSelectedTerms = {};
    displayedFacetFields.forEach((displayedFacetField) => {
        if (displayedFacetField.radio && selectedTerms[displayedFacetField.field].length === 0) {
            // Assign the first term of the radio-button facet as the sole selection. In the
            // unusual case that no facet terms for this radio-button facet have been collected,
            // just copy the existing selection for the facet.
            const matchingFacet = facets.find(facet => facet.field === displayedFacetField.field);
            newSelectedTerms[displayedFacetField.field] = (
                matchingFacet ? [matchingFacet.terms[0].term] : selectedTerms[displayedFacetField.field].slice(0)
            );
        } else {
            // Not a radio-button facet, or radio-button facet has selected terms; copy existing
            // selected terms.
            newSelectedTerms[displayedFacetField.field] = selectedTerms[displayedFacetField.field].slice(0);
        }
    });
    return newSelectedTerms;
};


/**
 * Reset the facets to no selections, and select the first term of radio-button facets, all as if
 * the page has just been loaded.
 * @param {array} files Files to consider when building facets.
 *
 * @return {object} Initial facet-term selections
 */
const resetFacets = (files) => {
    // Make an empty selected-terms object so `assembleFacets` can generate fresh simplified
    // facets.
    const emptySelectedTerms = {};
    displayedFacetFields.forEach((facetField) => {
        emptySelectedTerms[facetField.field] = [];
    });

    // Build the facets based on no selections, then select the first term of any radio-button
    // facets.
    const { facets } = assembleFacets(emptySelectedTerms, files);
    return initRadioFacets(facets, emptySelectedTerms);
};


/**
 * Filter visualizable files to ones included in the selected facet terms.
 * @param {array} visualizableFiles Files in cart datasets that are visualizable
 * @param {object} selectedTerms Selected facet terms
 *
 * @return {array} `visualizableFiles` filtered by facet term selections
 */
const getSelectedVisualizableFiles = (visualizableFiles, selectedTerms) => (
    visualizableFiles.filter(file => (
        Object.keys(selectedTerms).every(term => (
            selectedTerms[term].length > 0 ? selectedTerms[term].includes(getObjectFieldValue(file, term)) : true
        ))
    ))
);


/**
 * Content of the tabs with counters.
 */
const CounterTab = ({ title, count, voice }) => (
    <div className="cart-tab" aria-label={`${count} ${voice}`}>
        {title} <div className="cart-tab__count">{count}</div>
    </div>
);

CounterTab.propTypes = {
    /** Text title for the tab */
    title: PropTypes.string.isRequired,
    /** Counter value to display next to the tab */
    count: PropTypes.number.isRequired,
    /** Screen reader text */
    voice: PropTypes.string,
};

CounterTab.defaultProps = {
    voice: 'items',
};


/**
 * Get information about the cart contents including:
 * cartType: Type of cart being displayed:
 *           'ACTIVE': Viewing the current cart
 *           'OBJECT': Viewing the cart specified in the URL
 *           'MEMORY': Viewing carts in browser memory (non-logged-in user)
 * @param {object} context Cart search results object; often empty depending on cart type
 * @param {object} savedCartObj Cart object in Redux store for active logged-in carts
 * @param {object} elements Elements of the in-memory cart
 *
 * @return {object} -
 * {
 *      {string} cartType - Cart type: OBJECT, MEMORY, ACTIVE
 *      {string} cartName - Name of cart
 *      {array} cartDatasets - @ids of all datasets in cart
 * }
 */
const getCartInfo = (context, savedCartObj, elements) => {
    let cartType;
    let cartName;
    let cartDatasets;
    if (context['@type'][0] === 'cart-view') {
        // Viewing a current active or memory cart on the /cart-view/ page.
        if (savedCartObj && Object.keys(savedCartObj).length > 0) {
            cartType = 'ACTIVE';
            cartName = savedCartObj.name;
            cartDatasets = savedCartObj.elements;
        } else {
            cartType = 'MEMORY';
            cartName = 'Cart';
            cartDatasets = elements;
        }
    } else {
        // Viewing a saved cart at its unique path.
        cartType = 'OBJECT';
        cartName = context.name;
        cartDatasets = context.elements;
    }
    return { cartType, cartName, cartDatasets };
};


/**
 * Generate a template for selected facet terms with all possible facets but void of any selections
 * -- this is just to establish an initial selectedTerms object to build on.
 *
 * @return {object} Facet terms keyed by displayed facet fields.
 */
const generateFacetTermsTemplate = () => {
    const termTemplate = {};
    displayedFacetFields.forEach((facetField) => {
        termTemplate[facetField.field] = [];
    });
    return termTemplate;
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
 *      datasetFiles - Array of all parital file objects in all datasets
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
        promiseChain.then(accumulatingResults => (
            // Request one chunk of datasets. `currentResults` contains the request search
            // results including the partial file objects we need.
            requestDatasets(currentChunk, fetch, session).then((currentResults) => {
                // Update progress on each chunk.
                facetProgressHandler(Math.round(((currentChunkIndex + 1) / chunks.length) * 100));

                // Add the chunk's worth of results to the array of partial files and facets
                // we're accumulating.
                return {
                    datasetFiles: addToAccumulatingFiles(accumulatingResults.datasetFiles, currentResults),
                    datasets: accumulatingResults.datasets.concat(currentResults['@graph'].map(experiment => experiment['@id'])),
                };
            })
        ))
    ), Promise.resolve({ datasetFiles: [], datasets: [] })).then(({ datasetFiles, datasets }) => {
        facetProgressHandler(-1);
        return { datasetFiles, datasets };
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
    const newPages = Object.assign({}, state);
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
    const newPageCounts = Object.assign({}, state);
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
 * 3. MEMORY (/cart-view/) containing nothing
 *    * this.props.cart contains items to display (logged-out in-memory cart)
 * All files in all cart experiments are kept in an array of partial file objects which contain
 * only the file object properties requested in `requestedFacetFields`. When visualizing a subset
 * of these files, complete file objects get retrieved.
 */
const CartComponent = ({ context, elements, savedCartObj, loggedIn, inProgress, fetch, session }) => {
    // Keeps track of currently selected facet terms keyed by facet fields.
    const [selectedTerms, setSelectedTerms] = React.useState(() => generateFacetTermsTemplate());
    // Currently selected dataset type.
    const [selectedDatasetType, setSelectedDatasetType] = React.useState(DEFAULT_DATASET_TYPE);
    // Array of dataset @ids the user has access to view; subset of `cartDatasets`.
    const [viewableDatasets, setViewableDatasets] = React.useState(null);
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
    // All partial file objects in the cart datasets. Not affected by currently selected facets.
    const [allFiles, setAllFiles] = React.useState([]);

    // Retrieve current unfiltered cart information regardless of its source (memory, object,
    // active).
    const { cartType, cartName, cartDatasets } = React.useMemo(() => (
        getCartInfo(context, savedCartObj, elements)
    ), [context, savedCartObj, elements]);

    // Get the cart datasets subject to the dataset-type dropdown.
    const cartDatasetsForType = React.useMemo(() => (
        selectedDatasetType === 'all' ? cartDatasets : cartDatasets.filter(datasetAtId => atIdToType(datasetAtId) === selectedDatasetType)
    ), [selectedDatasetType, cartDatasets]);

    // Build the facets based on the currently selected facet terms.
    const { facets, selectedFiles } = React.useMemo(() => (
        assembleFacets(selectedTerms, visualizableOnly ? filterForVisualizableFiles(allFiles) : allFiles)
    ), [selectedTerms, visualizableOnly, allFiles]);
    const rawdataFiles = React.useMemo(() => allFiles.filter(files => !files.assembly), [allFiles]);
    const selectedVisualizableFiles = React.useMemo(() => (
        getSelectedVisualizableFiles(filterForVisualizableFiles(allFiles), selectedTerms)
    ), [allFiles, selectedTerms]);

    // Called when the user selects a new page of items to view using the pager.
    const updateDisplayedPage = (newDisplayedPage) => {
        // Set the new page number for the currently-displayed tab pane.
        dispatchPageNumbers({ tab: displayedTab, pageNumber: newDisplayedPage });
    };

    // Called when the user clicks any term in any facet.
    const handleTermClick = (clickedField, clickedTerm) => {
        const newSelectedTerms = {};
        const matchingFacetField = displayedFacetFields.find(facetField => facetField.field === clickedField);
        if (matchingFacetField && matchingFacetField.radio) {
            // The user clicked a radio-button facet.
            displayedFacetFields.forEach((facetField) => {
                // Set new term for the clicked radio button, or copy the array for other
                // terms within this as well as other facets.
                newSelectedTerms[facetField.field] = facetField.field === clickedField ? [clickedTerm] : selectedTerms[facetField.field].slice(0);
            });
        } else {
            // The user clicked a checkbox facet. Determine whether we need to add or subtract
            // a term from the facet selections.
            const addTerm = selectedTerms[clickedField].indexOf(clickedTerm) === -1;
            if (addTerm) {
                // Adding a selected term. Copy the previous selectedFacetTerms, adding the newly
                // selected term in its facet in sorted position.
                displayedFacetFields.forEach((facetField) => {
                    if (clickedField === facetField.field) {
                        // Clicked term belongs to this field's facet. Insert it into its
                        // sorted position in a copy of the selectedTerms array.
                        const sortedIndex = _(selectedTerms[facetField.field]).sortedIndex(clickedTerm);
                        newSelectedTerms[facetField.field] = [...selectedTerms[facetField.field].slice(0, sortedIndex), clickedTerm, ...selectedTerms[facetField.field].slice(sortedIndex)];
                    } else {
                        // Clicked term doesn't belong to this field's facet. Just copy the
                        // `selectedTerms` array unchanged.
                        newSelectedTerms[facetField.field] = selectedTerms[facetField.field].slice(0);
                    }
                });
            } else {
                // Removing a selected term. Copy the previous selectedFacetTerms, filtering out
                // the unselected term in its facet.
                displayedFacetFields.forEach((facetField) => {
                    newSelectedTerms[facetField.field] = selectedTerms[facetField.field].filter(term => term !== clickedTerm);
                });
            }
        }

        setSelectedTerms(newSelectedTerms);
    };

    // Called when the user clicks the Show Visualizable Only checkbox.
    const handleVisualizableOnlyChange = () => {
        setVisualizableOnly(!visualizableOnly);
    };

    // Called when the user clicks a tab.
    const handleTabClick = (newTab) => {
        setDisplayedTab(newTab);
    };

    // Called when the user changes the currently selected dataset type.
    const handleTypeChange = (e) => {
        setSelectedDatasetType(e.target.value);
    };

    // After mount, we can fetch all datasets in the cart that are viewable at the user's
    // permission level and from them extract all their files.
    React.useEffect(() => {
        if (cartDatasetsForType.length > 0) {
            retrieveDatasetsFiles(cartDatasetsForType, setFacetProgress, fetch, session).then(({ datasetFiles, datasets }) => {
                // Mutate files for special cases.
                datasetFiles.forEach((file) => {
                    // De-embed any embedded datasets.files.dataset.
                    if (typeof file.dataset === 'object') {
                        file.dataset = file.dataset['@id'];
                    }
                });

                setAllFiles(datasetFiles);
                setViewableDatasets(datasets);
            });
        }
    }, [cartDatasetsForType, fetch, session]);

    // Use the file information to build the facets and its initial selections.
    React.useEffect(() => {
        const allVisualizableFiles = filterForVisualizableFiles(allFiles);
        const consideredFiles = visualizableOnly ? allVisualizableFiles : allFiles;
        const newSelectedTerms = resetFacets(consideredFiles);
        setSelectedTerms(newSelectedTerms);
    }, [visualizableOnly, allFiles]);

    // Data changes or initial load need a total-page-count calculation.
    React.useEffect(() => {
        const datasetPageCount = calcTotalPageCount(cartDatasetsForType.length, PAGE_ELEMENT_COUNT);
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
    }, [cartDatasetsForType, selectedVisualizableFiles, selectedFiles, rawdataFiles, pageNumbers.datasets, pageNumbers.browser, pageNumbers.processeddata, pageNumbers.rawdata]);

    return (
        <div className={itemClass(context, 'view-item')}>
            <header>
                <h1>{cartName}</h1>
                {cartType === 'OBJECT' ? <ItemAccessories item={context} /> : null}
            </header>
            <Panel addClasses="cart__result-table">
                {cartDatasetsForType.length > 0 ?
                    <PanelHeading addClasses="cart__header">
                        <CartTools
                            elements={cartDatasets}
                            savedCartObj={savedCartObj}
                            selectedTerms={selectedTerms}
                            selectedDatasetType={selectedDatasetType}
                            typeChangeHandler={handleTypeChange}
                            viewableDatasets={viewableDatasets}
                            cartType={cartType}
                            sharedCart={context}
                            fileCounts={{ processed: selectedFiles.length, raw: rawdataFiles.length, all: allFiles.length }}
                            visualizable={visualizableOnly}
                            inProgress={inProgress}
                        />
                        {selectedTerms.assembly[0] ? <div className="cart-assembly-indicator">{selectedTerms.assembly[0]}</div> : null}
                    </PanelHeading>
                : null}
                <PanelBody>
                    {cartDatasetsForType.length > 0 ?
                        <div className="cart__display">
                            <FileFacets
                                facets={facets}
                                elements={cartDatasetsForType}
                                selectedTerms={selectedTerms}
                                termClickHandler={handleTermClick}
                                selectedFileCount={selectedFiles.length}
                                visualizableOnly={visualizableOnly}
                                visualizableOnlyChangeHandler={handleVisualizableOnlyChange}
                                loggedIn={loggedIn}
                                facetLoadProgress={facetProgress}
                                disabled={displayedTab === 'rawdata'}
                            />
                            <TabPanel
                                tabPanelCss="cart__display-content"
                                tabs={{ datasets: 'All datasets', browser: 'Genome browser', processeddata: 'Processed data', rawdata: 'Raw data' }}
                                tabDisplay={{
                                    datasets: <CounterTab title={datasetTypes[selectedDatasetType].title} count={cartDatasetsForType.length} voice="datasets" />,
                                    browser: <CounterTab title="Genome browser" count={selectedVisualizableFiles.length} voice="visualizable tracks" />,
                                    processeddata: <CounterTab title="Processed data" count={selectedFiles.length} voice="processed data files" />,
                                    rawdata: <CounterTab title="Raw data" count={rawdataFiles.length} voice="raw data files" />,
                                }}
                                handleTabClick={handleTabClick}
                            >
                                <TabPanelPane key="datasets">
                                    <CartPager
                                        currentPage={pageNumbers.datasets}
                                        totalPageCount={totalPageCount.datasets}
                                        updateCurrentPage={updateDisplayedPage}
                                    />
                                    <CartSearchResults
                                        elements={cartDatasetsForType}
                                        currentPage={pageNumbers.datasets}
                                        cartControls={cartType !== 'OBJECT'}
                                        loggedIn={loggedIn}
                                    />
                                </TabPanelPane>
                                <TabPanelPane key="browser">
                                    <CartPager
                                        currentPage={pageNumbers.browser}
                                        totalPageCount={totalPageCount.browser}
                                        updateCurrentPage={updateDisplayedPage}
                                    />
                                    <CartBrowser files={selectedVisualizableFiles} assembly={selectedTerms.assembly[0]} pageNumber={pageNumbers.browser} />
                                </TabPanelPane>
                                <TabPanelPane key="processeddata">
                                    <CartPager
                                        currentPage={pageNumbers.processeddata}
                                        totalPageCount={totalPageCount.processeddata}
                                        updateCurrentPage={updateDisplayedPage}
                                    />
                                    <CartFiles files={selectedFiles} currentPage={pageNumbers.processeddata} />
                                </TabPanelPane>
                                <TabPanelPane key="rawdata">
                                    <CartPager
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
    /** In-memory cart contents */
    elements: PropTypes.array.isRequired,
    /** Cart as it exists in the database */
    savedCartObj: PropTypes.object,
    /** True if user has logged in */
    loggedIn: PropTypes.bool,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool,
    /** System fetch function */
    fetch: PropTypes.func.isRequired,
    /** System session information */
    session: PropTypes.object,
};

CartComponent.defaultProps = {
    savedCartObj: null,
    loggedIn: false,
    inProgress: false,
    session: null,
};

CartComponent.contextTypes = {
    session: PropTypes.object,
};


const mapStateToProps = (state, ownProps) => ({
    elements: state.elements,
    savedCartObj: state.savedCartObj,
    context: ownProps.context,
    loggedIn: ownProps.loggedIn,
    inProgress: state.inProgress,
    fetch: ownProps.fetch,
    session: ownProps.session,
});

const CartInternal = connect(mapStateToProps)(CartComponent);


/**
 * Wrapper to receive React <App> context and pass it to CartInternal as regular props.
 */
const Cart = (props, reactContext) => {
    const loggedIn = !!(reactContext.session && reactContext.session['auth.userid']);
    return <CartInternal context={props.context} fetch={reactContext.fetch} loggedIn={loggedIn} session={reactContext.session} />;
};

Cart.propTypes = {
    /** Cart object from server, either for shared cart or 'cart-view' */
    context: PropTypes.object.isRequired,
};

Cart.contextTypes = {
    session: PropTypes.object,
    fetch: PropTypes.func,
};

export default Cart;
