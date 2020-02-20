/**
 * Components for rendering the /carts/ and /cart-view/ page.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import _ from 'underscore';
import { svgIcon } from '../../libs/svg-icons';
import * as encoding from '../../libs/query_encoding';
import Pager from '../../libs/ui/pager';
import { Panel, PanelBody, PanelHeading, TabPanel, TabPanelPane } from '../../libs/ui/panel';
import { tintColor, isLight } from '../datacolors';
import GenomeBrowser from '../genome_browser';
import { itemClass } from '../globals';
import { requestObjects, ItemAccessories, isFileVisualizable, computeAssemblyAnnotationValue, filterForVisualizableFiles } from '../objectutils';
import { ResultTableList } from '../search';
import CartBatchDownload from './batch_download';
import CartClearButton from './clear';
import { cartRetrieve } from './database';
import CartMergeShared from './merge_shared';

/**
 * This file uses some shorthand terms that need some explanation.
 * "Partial files" - File objects contained within dataset search results containing a subset of
 *                   properties from complete file objects. These get used to determine facet
 *                   contents, but we also retrieve complete file objects to pass to the genome
 *                   browser.
 * "Simplified facets" - Primary objects for displaying cart-view facets. We don't use the "facet"
 *                       properties from search results because we generate these facets from
 *                       *dataset* search results -- we don't do a file search on the cart-view
 *                       page to generate facets. We only do a file search for the current page of
 *                       genome-browser tracks.
 */


/** Number of dataset elements to display per page */
const PAGE_ELEMENT_COUNT = 25;
/** Number of genome-browser files to display per page */
const PAGE_FILE_COUNT = 20;


/**
 * Sort an array of assemblies for display in the facet according to system-wide criteria.
 * @param {array} assemblyList Assembly facet terms to sort
 *
 * @return {array} Same as `assemblyList` but sorted.
 */
const assemblySorter = (facetTerms, property) => (
    // Negate the sorting value to sort from highest to lowest.
    _(facetTerms).sortBy(facetTerm => -computeAssemblyAnnotationValue(facetTerm[property]))
);


/** File facet fields to display in order of display:
 *    field: facet field property
 *    title: Displayed facet title
 *    radio: True if radio-button facet; otherwise checkbox facet
 *    dataset: true to retrieve value from dataset instead of files
 *    sorter: function to sort terms within the facet
 */
const displayedFacetFields = [
    { field: 'assembly', title: 'Genome assembly', radio: true, sorter: assemblySorter },
    { field: 'output_type', title: 'Output type' },
    { field: 'file_type', title: 'File type' },
    { field: 'file_format', title: 'File format' },
    { field: 'assay_term_name', title: 'Assay term name' },
    { field: 'biosample_ontology.term_name', title: 'Biosample term name', dataset: true },
    { field: 'target.label', title: 'Target of assay', dataset: true },
    { field: 'lab.title', title: 'Lab' },
    { field: 'status', title: 'Status' },
];

/** Facet `field` values for properties from dataset instead of files */
const datasetFacets = displayedFacetFields.filter(facetField => facetField.dataset).map(facetField => facetField.field);

/** Facet `field` values for radio-button facets */
const radioFacetFields = displayedFacetFields.filter(facetFields => facetFields.radio).map(facetFields => facetFields.field);

/** File facet fields to request from server -- superset of those displayed in facets */
const requestedFacetFields = displayedFacetFields.concat([
    { field: '@id' },
    { field: 'file_format_type' },
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

        return (
            <div className="cart__facet-progress-overlay">
                <progress value={facetLoadProgress} max="100" />
            </div>
        );
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
 * @param {string} queryString Query string to add to URI being fetched; '' for no additions
 * @param {object} session session object from <App> context
 *
 * @return {object} Promise with search result object
 */
const requestDatasets = (elements, fetch, queryString, session) => {
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
        fetch(`/search_elements/type=Experiment${fieldQuery}&field=files.restricted&limit=all&filterresponse=off${queryString || ''}`, {
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
        const { facets, selectedTerms, selectedFileCount, termClickHandler, visualizableOnly, visualizableOnlyChangeHandler, facetLoadProgress } = this.props;

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
};

FileFacets.defaultProps = {
    facets: [],
    selectedTerms: null,
    selectedFileCount: 0,
    visualizableOnly: false,
    facetLoadProgress: null,
};


/**
 * Display cart tool buttons. If `savedCartObj` is supplied, supply it for the metadata.tsv line
 * in the resulting files.txt.
 */
const CartTools = ({ elements, selectedTerms, savedCartObj, viewableElements, fileCount, cartType, sharedCart, visualizable }) => (
    <div className="cart__tools">
        {elements.length > 0 ?
            <CartBatchDownload
                elements={elements}
                selectedTerms={selectedTerms}
                datasetFacets={datasetFacets}
                cartType={cartType}
                savedCartObj={savedCartObj}
                sharedCart={sharedCart}
                fileCount={fileCount}
                visualizable={visualizable}
            />
        : null}
        {cartType === 'OBJECT' ? <CartMergeShared sharedCartObj={sharedCart} viewableElements={viewableElements} /> : null}
        {cartType === 'ACTIVE' || cartType === 'MEMORY' ? <CartClearButton /> : null}
    </div>
);

CartTools.propTypes = {
    /** Cart elements */
    elements: PropTypes.array,
    /** Selected facet terms */
    selectedTerms: PropTypes.object,
    /** Cart as it exists in the database; use JSON payload method if none */
    savedCartObj: PropTypes.object,
    /** Viewable cart element @ids */
    viewableElements: PropTypes.array,
    /** Type of cart: ACTIVE, OBJECT, MEMORY */
    cartType: PropTypes.string.isRequired,
    /** Elements in the shared cart, if that's being displayed */
    sharedCart: PropTypes.object,
    /** Number of files batch download will cause to be downloaded */
    fileCount: PropTypes.number,
    /** True if only visualizable files should be downloaded */
    visualizable: PropTypes.bool,
};

CartTools.defaultProps = {
    elements: [],
    selectedTerms: null,
    savedCartObj: null,
    viewableElements: null,
    sharedCart: null,
    fileCount: 0,
    visualizable: false,
};


/**
 * Display the total number of cart elements.
 */
const ElementCountArea = ({ count, viewableElementCount, typeName, typeNamePlural }) => {
    if (count > 0) {
        const countFormatted = count.toLocaleString ? count.toLocaleString() : count.toString();
        return (
            <div className="cart__element-count">
                <span>{countFormatted}&nbsp;{count === 1 ? typeName : typeNamePlural} in cart</span>
                {viewableElementCount >= 0 && viewableElementCount !== count ? <span> ({viewableElementCount} visible)</span> : null}
            </div>
        );
    }
    return null;
};

ElementCountArea.propTypes = {
    /** Number of elements in cart display */
    count: PropTypes.number.isRequired,
    /** Count of viewable cart elements at user's access level */
    viewableElementCount: PropTypes.number,
    /** Singular type name of elements being displayed */
    typeName: PropTypes.string.isRequired,
    /** Plural type name of elements being displayed */
    typeNamePlural: PropTypes.string.isRequired,
};

ElementCountArea.defaultProps = {
    viewableElementCount: 0,
};


/**
 * Display the pager control area.
 */
const PagerArea = ({ currentPage, totalPageCount, updateCurrentPage }) => (
    <React.Fragment>
        {totalPageCount > 1 ?
            <Pager total={totalPageCount} current={currentPage} updateCurrentPage={updateCurrentPage} />
        : null}
    </React.Fragment>
);

PagerArea.propTypes = {
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
 * @param {object} filesPartial Partial file objects being collected
 * @param {object} currentResults Dataset search results containing partial file objects
 *
 * @return {object} Returns `filesPartial` with file information from `currentResults` added.
 */
const addToAccumulatingFilesPartial = (filesPartial, currentResults) => {
    if (currentResults['@graph'] && currentResults['@graph'].length > 0) {
        const currentFilesPartial = [];

        // Go through each experiment result to collect files suitable for the cart-view page.
        currentResults['@graph'].forEach((dataset) => {
            if (dataset.files && dataset.files.length > 0) {
                dataset.files.forEach((file) => {
                    if (!file.restricted) {
                        // Mutate the files to include faceted properties from the dataset
                        // object before adding it to the accumulating list of files.
                        displayedFacetFields.forEach((facetField) => {
                            if (facetField.dataset) {
                                const [experimentProp] = facetField.field.split('.');
                                file[experimentProp] = dataset[experimentProp];
                            }
                        });
                        currentFilesPartial.push(file);
                    }
                });
            }
        });

        // Return a new array combining the existing partial files with the additional files.
        return filesPartial.concat(currentFilesPartial);
    }

    // No search results; just return unchanged list of partial files.
    return filesPartial;
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
 * cart, generate the facets and corresponding counts object used to render the cart file facets.
 *
 * @param {object} selectedTerms Currently selected terms within each facet
 * @param {array} files Files to consider when building these facets.
 *
 * @return {object}
 *     {array} facets - Array of simplified facet objects including fields and terms; empty array
 *                      if none
 *     {number} selectedFileCount - Number of files selected by current facet selections
 */
const assembleFacets = (selectedTerms, files) => {
    const facets = [];
    let selectedFileCount = 0;
    if (files.length > 0) {
        const selectedFacetKeys = Object.keys(selectedTerms).filter(term => selectedTerms[term].length > 0);
        files.forEach((file) => {
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
            // counts. Files that don't pass go through a second test to see if they should
            // appear unselected within a facet. Files that fail both tests get ignored for
            // facets.
            if (match) {
                // The file passed the first test, so it appears selected in its facet. Add all
                // its properties to the relevant facet terms.
                Object.keys(selectedTerms).forEach((facetField) => {
                    addFileTermToFacet(facets, facetField, file);
                });
                selectedFileCount += 1;
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
                        addFileTermToFacet(facets, selectedFacetField, file);
                    }
                });
            }
        });

        // We need to include selected terms that happen to have a zero count, so add all
        // selected facet terms not yet included in `facets`.
        Object.keys(selectedTerms).forEach((field) => {
            const matchingFacet = facets.find(facet => facet.field === field);
            if (matchingFacet) {
                // Find selected terms NOT in facets and add them with a zero count.
                const matchingFacetTerms = matchingFacet.terms.map(facetTerm => facetTerm.term);
                const missingTerms = selectedTerms[field].filter(term => matchingFacetTerms.indexOf(term) === -1);
                if (missingTerms.length > 0) {
                    missingTerms.forEach((term) => {
                        matchingFacet.terms.push({ term, cont: 0 });
                    });
                }
            }
        });

        // Sort each facet's terms either alphabetically or by some criteria specific to a
        // facet. `facets` and `displayedFacetFields` have the same order, but `facets` might
        // not have all possible facets -- just currently relevant ones.
        facets.forEach((facet) => {
            // We know a corresponding `displayedFacetFields` entry exists because `facets` gets
            // built from it, so no not-found condition needs checking.
            const facetDisplay = displayedFacetFields.find(displayedFacetField => displayedFacetField.field === facet.field);
            facet.title = facetDisplay.title;
            facet.terms = facetDisplay.sorter ?
                facetDisplay.sorter(facet.terms, 'term')
            :
                _(facet.terms).sortBy(facetTerm => facetTerm.term.toLowerCase());
        });
    }

    return { facets: facets.length > 0 ? facets : [], selectedFileCount };
};


/**
 * For any radio-button facets, select the first term if no items within them have been selected.
 * @param {array} facets Simplified facet object
 * @param {object} selectedTerms Selected terms within the facets
 *
 * @return {object} Same as `selectedTerms` but with radio-button facet terms selected
 */
const initSelectedFacets = (facets, selectedTerms) => {
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
    return initSelectedFacets(facets, emptySelectedTerms);
};


/**
 * Sets the initial React state for the cart page.
 */
const createInitialCartState = () => {
    const selectedTerms = {};
    displayedFacetFields.forEach((facetField) => {
        selectedTerms[facetField.field] = [];
    });
    const newState = {
        /** Array of currently displayed facets and the terms each contains */
        facets: [],
        /** Files formats selected to be included in results; all formats if empty array */
        selectedTerms,
        /** Count of elements viewable at user's access level; only for shared carts */
        viewableElementCount: -1,
        /** Array of viewable element @ids */
        viewableElements: null,
        /** Currently displayed page of dataset search results */
        currentDatasetResultsPage: 0,
        /** Currently displayed page of files for the genome browser */
        currentGenomeBrowserPage: 0,
        /** Currently displayed tab key; match key of first TabPanelPane */
        currentDisplay: 'datasets',
        /** Full file objects to display in current genome browser page */
        visualizableFiles: [],
        /** Total number of pages of visualizable files in the genome browser */
        totalGenomeBrowserPages: 0,
        /** Cart context after update */
        updatedContext: null,
        /** Number of files selected for download */
        selectedFileCount: 0,
        /** Tracks facet-loading for loading progress bar */
        facetLoadProgress: null,
        /** True if only facet terms for visualizable files displayed */
        visualizableOnly: false,
    };
    return newState;
};


/**
 * Renders the cart search results page. Display either:
 * 1. OBJECT (/carts/<uuid>)
 *    * context contains items to display.
 * 2. ACTIVE (/cart-view/) containing the current cart's contents
 *    * savedCartObj contains items to display
 * 3. MEMORY (/cart-view/) containing nothing
 *    * this.props.cart contains items to display
 * All files in all cart experiments are kept in an array of "partial file objects" which contain
 * only the file object properties requested in `requestedFacetFields`. When visualizing a subset
 * of these files, complete file objects get retrieved.
 */
class CartComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = createInitialCartState();

        // All files involved in the current cart as partial file objects. Not affected by
        // currently selected facets.
        this.allFilesPartial = [];
        // Same as `allFilesPartial` but only including visualizable files.
        this.visualizableFilesPartial = [];
        /** All elements in the current cart regardless of the cart type */
        this.cartElements = [];

        this.getConsideredFiles = this.getConsideredFiles.bind(this);
        this.retrieveFileFacets = this.retrieveFileFacets.bind(this);
        this.handleTermClick = this.handleTermClick.bind(this);
        this.computePageInfo = this.computePageInfo.bind(this);
        this.updateCurrentPage = this.updateCurrentPage.bind(this);
        this.loadPageFiles = this.loadPageFiles.bind(this);
        this.handleTabClick = this.handleTabClick.bind(this);
        this.handleVisualizableOnlyChange = this.handleVisualizableOnlyChange.bind(this);
    }

    componentDidMount() {
        const { cartElements } = this.computePageInfo();
        this.cartElements = cartElements;
        this.retrieveFileFacets();
    }

    componentDidUpdate(prevProps, prevState) {
        const { cartType, cartElements, totalDatasetPages } = this.computePageInfo();

        // Update facets if visualizable-only changes state.
        if (prevState.visualizableOnly !== this.state.visualizableOnly) {
            const newSelectedTerms = initSelectedFacets(this.state.facets, this.state.selectedTerms);
            this.setState({ selectedTerms: newSelectedTerms });
            const { facets, selectedFileCount } = assembleFacets(newSelectedTerms, this.getConsideredFiles());
            this.setState({ facets, selectedFileCount });
        }

        if (this.cartElements.length !== cartElements.length || prevProps.elements.length !== this.props.elements.length || prevProps.loggedIn !== this.props.loggedIn) {
            this.cartElements = cartElements;
            this.retrieveFileFacets();
        }

        // If enough datasets got removed that we lost a page of search results, go back to the
        // first page.
        if (totalDatasetPages > 0 && totalDatasetPages <= this.state.currentDatasetResultsPage) {
            this.setState({ currentDatasetResultsPage: 0 });
        }

        // If the user has logged in, retrieve relevant data and redraw the page.
        if (prevProps.loggedIn !== this.props.loggedIn) {
            const newState = createInitialCartState();
            this.setState({
                selectedTerms: newState.selectedTerms,
                viewableElementCount: newState.viewableElementCount,
                currentDatasetResultsPage: newState.currentDatasetResultsPage,
            });
        }

        // Redraw an OBJECT page if the underlying data changed.
        if (cartType === 'OBJECT' && !this.props.inProgress && prevProps.inProgress) {
            cartRetrieve(this.props.context['@id'], this.props.fetch).then((response) => {
                this.setState({ updatedContext: response });
            });
        }
    }

    /**
     * Get the list of experiment files to use depending on the setting of the `visualizableOnly`
     * state.
     *
     * @return {array} Array of all or visualizable partial files
     */
    getConsideredFiles() {
        return this.state.visualizableOnly ? this.visualizableFilesPartial : this.allFilesPartial;
    }

    /**
     * Perform a special search to get just the facet information for files associated with cart
     * elements. The cart elements are passed in the JSON body of the POST. No search results get
     * returned but we do get file facet information.
     */
    retrieveFileFacets() {
        // Break incoming array of dataset @ids into manageable chunks of arrays, each with
        // CHUNK_SIZE elements. Each chunk gets used in a search of relevant files, and all the
        // results get combined into one facet object.
        const CHUNK_SIZE = 2000;
        const chunks = [];
        for (let elementIndex = 0; elementIndex < this.cartElements.length; elementIndex += CHUNK_SIZE) {
            chunks.push(this.cartElements.slice(elementIndex, elementIndex + CHUNK_SIZE));
        }

        // Assemble the query string from the selected facets. Useful when the user removes a
        // dataset or logs in while facets are selected.
        let queryString = '';
        displayedFacetFields.forEach((facetField) => {
            if (this.state.selectedTerms[facetField.field].length > 0) {
                const termQuery = this.state.selectedTerms[facetField.field].map(term => (
                    `${facetField.dataset ? '' : 'files.'}${facetField.field}=${encoding.encodedURIComponentOLD(term)}`
                )).join('&');
                queryString += `&${termQuery}`;
            }
        });

        // Using the arrays of dataset @id arrays, do a sequence of searches of CHUNK_SIZE datasets
        // adding to extract information to display the facets, search results, and visualization.
        this.setState({ facetLoadProgress: null });
        chunks.reduce((promiseChain, currentChunk, currentChunkIndex) => (
            // As each experiment search-result promise resolves, add its results to the array of
            // partial files and facets in `accumulatingResults`.
            promiseChain.then(accumulatingResults => (
                // Request one chunk of datasets. `currentResults` contains the request search
                // results including the partial file objects we need.
                requestDatasets(currentChunk, this.context.fetch, queryString, this.context.session).then((currentResults) => {
                    this.setState({ facetLoadProgress: Math.round(((currentChunkIndex + 1) / chunks.length) * 100) });

                    // Add the chunk's worth of results to the array of partial files and facets
                    // we're accumulating.
                    return {
                        filesPartial: addToAccumulatingFilesPartial(accumulatingResults.filesPartial, currentResults),
                        viewableElements: accumulatingResults.viewableElements.concat(currentResults['@graph'].map(experiment => experiment['@id'])),
                        viewableElementsCount: accumulatingResults.viewableElementsCount + currentResults.total,
                    };
                })
            ))
        ), Promise.resolve({ filesPartial: [], viewableElements: [], viewableElementsCount: 0 })).then((accumulatedResults) => {
            // All cart datasets in all chunks have been retrieved and their files extracted, and
            // the file facet results accumulated. Save this list of partial file objects as well
            // as a map of facet field name to corresponding title.
            this.allFilesPartial = accumulatedResults.filesPartial;
            this.visualizableFilesPartial = filterForVisualizableFiles(this.allFilesPartial);
            this.setState({
                viewableElements: accumulatedResults.viewableElements,
                viewableElementCount: accumulatedResults.viewableElementsCount,
                facetLoadProgress: -1,
            });

            // Chicken and egg: We can't assemble facets until we have selected the first term of
            // radio-button facets, but we don't know any facet terms until we have assembled the
            // facets. If no facets contain selections, then build an inital set of facets based on
            // no selections, then select the first of any radio-button facets, then after we'll
            // rebuild the facets based on that.
            let currentSelectedFacets = {};
            const consideredFiles = this.getConsideredFiles();
            const hasSelectedTerms = radioFacetFields.some(field => this.state.selectedTerms[field].length > 1);
            if (!hasSelectedTerms) {
                // At least one radio-button facet has no selected terms (a good sign none of them
                // do). Rebuild the facets from scratch and get the initial facet selections.
                currentSelectedFacets = resetFacets(consideredFiles);
            } else {
                // Radio-button facets contain selections, so just continue with the current facet
                // term selections.
                currentSelectedFacets = this.state.selectedTerms;
            }

            // Use the file information to build the facet objects for rendering.
            const { facets, selectedFileCount } = assembleFacets(currentSelectedFacets, consideredFiles);
            const newSelectedTerms = initSelectedFacets(facets, currentSelectedFacets);
            this.loadPageFiles(newSelectedTerms);
            this.setState({ facets, selectedFileCount, selectedTerms: newSelectedTerms });
        });
    }

    /**
     * Compute information about the currently displayed page of cart contents including:
     * cartType: Type of cart being displayed:
     *           'ACTIVE': Viewing the current cart
     *           'OBJECT': Viewing the cart specified in the URL
     *           'MEMORY': Viewing carts in browser memory (non-logged-in user)
     * cartName: Name of cart
     * cartElements: Array of cart element @ids
     * totalDatasetPages: Total number of pages of cart elements to display
     */
    computePageInfo(props) {
        const { context, savedCartObj, elements } = props || this.props;
        const cartContext = this.state.updatedContext || context;
        let cartType = '';
        let cartElements = [];
        let cartName = '';
        if (cartContext['@type'][0] === 'cart-view') {
            // Viewing a current active or memory cart on the /cart-view/ page.
            if (savedCartObj && Object.keys(savedCartObj).length > 0) {
                cartType = 'ACTIVE';
                cartName = savedCartObj.name;
                cartElements = savedCartObj.elements;
            } else {
                cartType = 'MEMORY';
                cartName = 'Cart';
                cartElements = elements;
            }
        } else {
            // Viewing a saved cart at its unique path.
            cartType = 'OBJECT';
            cartName = cartContext.name;
            cartElements = cartContext.elements;
        }
        return {
            cartType,
            cartName,
            cartElements,
            totalDatasetPages: Math.floor(cartElements.length / PAGE_ELEMENT_COUNT) + (cartElements.length % PAGE_ELEMENT_COUNT !== 0 ? 1 : 0),
        };
    }

    /**
     * Called when the given facet term was selected or deselected.
     * @param {string} clickedField `field` value of the facet whose term was clicked
     * @param {string} clickedTerm `term` value that was clicked
     */
    handleTermClick(clickedField, clickedTerm) {
        this.setState((prevState) => {
            const newSelectedTerms = {};
            const matchingFacetField = displayedFacetFields.find(facetField => facetField.field === clickedField);
            if (matchingFacetField && matchingFacetField.radio) {
                // The user clicked a radio-button facet.
                displayedFacetFields.forEach((facetField) => {
                    // Set new term for the clicked radio button, or copy the array for other
                    // terms within this as well as other facets.
                    newSelectedTerms[facetField.field] = facetField.field === clickedField ? [clickedTerm] : prevState.selectedTerms[facetField.field].slice(0);
                });
            } else {
                // The user clicked a checkbox facet. Determine whether we need to add or subtract
                // a term from the facet selections.
                const addTerm = this.state.selectedTerms[clickedField].indexOf(clickedTerm) === -1;

                // prevState is immutable, so make a copy with the newly clicked term to set the
                // new state.
                if (addTerm) {
                    // Adding a selected term. Copy the previous selectedFacetTerms, adding the newly
                    // selected term in its facet in sorted position.
                    displayedFacetFields.forEach((facetField) => {
                        if (clickedField === facetField.field) {
                            // Clicked term belongs to this field's facet. Insert it into its
                            // sorted position in a copy of the selectedTerms array.
                            const sortedIndex = _(prevState.selectedTerms[facetField.field]).sortedIndex(clickedTerm);
                            newSelectedTerms[facetField.field] = [...prevState.selectedTerms[facetField.field].slice(0, sortedIndex), clickedTerm, ...prevState.selectedTerms[facetField.field].slice(sortedIndex)];
                        } else {
                            // Clicked term doesn't belong to this field's facet. Just copy the
                            // `selectedTerms` array unchanged.
                            newSelectedTerms[facetField.field] = prevState.selectedTerms[facetField.field].slice(0);
                        }
                    });
                } else {
                    // Removing a selected term. Copy the previous selectedFacetTerms, filtering out
                    // the unselected term in its facet.
                    displayedFacetFields.forEach((facetField) => {
                        newSelectedTerms[facetField.field] = prevState.selectedTerms[facetField.field].filter(term => term !== clickedTerm);
                    });
                }
            }

            // Rebuild the facets with the new selected terms.
            const { facets, selectedFileCount } = assembleFacets(newSelectedTerms, this.getConsideredFiles());

            return { selectedTerms: newSelectedTerms, facets, selectedFileCount, currentGenomeBrowserPage: 0 };
        }, () => {
            this.loadPageFiles(this.state.selectedTerms);
        });
    }

    /**
     * Called when the user selects a new page of datasets or genome-browser files to view.
     * @param {number} newCurrent New current page to view; zero based
     */
    updateCurrentPage(newCurrent) {
        if (this.state.currentDisplay === 'datasets') {
            this.setState({ currentDatasetResultsPage: newCurrent });
        } else {
            this.setState({ currentGenomeBrowserPage: newCurrent }, () => {
                this.loadPageFiles(this.state.selectedTerms);
            });
        }
    }

    /**
     * Load complete file objects for the current genome browser page and place it in state so the
     * genome browser rerenders with this list.
     */
    loadPageFiles(selectedTerms) {
        // Given the limited amount we know about the files in the cart so far, determine whether
        // any are visualizable.
        const selectedVisualizableFilesPartial = this.visualizableFilesPartial.filter(file => (
            Object.keys(selectedTerms).every(term => (
                selectedTerms[term].length > 0 ? selectedTerms[term].includes(getObjectFieldValue(file, term)) : true
            ))
        ));

        if (selectedVisualizableFilesPartial.length > 0) {
            const totalGenomeBrowserPages = Math.floor(selectedVisualizableFilesPartial.length / PAGE_FILE_COUNT) + (selectedVisualizableFilesPartial.length % PAGE_FILE_COUNT !== 0 ? 1 : 0);

            // Extract the list of partial files for the currently displayed page of genome
            // browser files.
            const pageStartingIndex = this.state.currentGenomeBrowserPage * PAGE_FILE_COUNT;
            const currentPageFilesPartial = selectedVisualizableFilesPartial.slice(pageStartingIndex, pageStartingIndex + PAGE_FILE_COUNT);
            const visualizableFileIds = currentPageFilesPartial.map(file => file['@id']);

            // We have a list of all visualizable files as partial file objects. Using the @ids of
            // all of them, fetch complete file objects. Save an original copy of the visualizable
            // files as well as in state, so that when the user selects facets we can use the
            // original copy to help calculate a new list of visualizable files in state.
            requestObjects(visualizableFileIds, '/search/?type=File').then((visualizableFiles) => {
                this.setState({ visualizableFiles, totalGenomeBrowserPages });
            });
        } else {
            this.setState({ visualizableFiles: [] });
        }
    }

    /**
     * Called when the user clicks either of the Dataset/Genome browser tabs.
     * @param {string} tab ID of the clicked tab
     */
    handleTabClick(tab) {
        this.setState({ currentDisplay: tab });
    }

    /**
     * Called when the user clicks the vizualizable-only checkbox.
     */
    handleVisualizableOnlyChange() {
        this.setState((state) => {
            const initialSelectedTerms = resetFacets(this.getConsideredFiles());
            return { visualizableOnly: !state.visualizableOnly, selectedTerms: initialSelectedTerms };
        });
    }

    render() {
        const { context, savedCartObj, loggedIn } = this.props;
        const { cartType, cartElements, cartName, totalDatasetPages } = this.computePageInfo();
        const cartContext = this.state.updatedContext || context;

        // Generate pager component for the currently selected tab.
        let currentPager;
        if (this.state.currentDisplay === 'datasets') {
            currentPager = <PagerArea
                currentPage={this.state.currentDatasetResultsPage}
                totalPageCount={totalDatasetPages}
                updateCurrentPage={this.updateCurrentPage}
            />;
        } else {
            currentPager = <PagerArea
                currentPage={this.state.currentGenomeBrowserPage}
                totalPageCount={this.state.totalGenomeBrowserPages}
                updateCurrentPage={this.updateCurrentPage}
            />;
        }

        return (
            <div className={itemClass(cartContext, 'view-item')}>
                <header>
                    <h2>{cartName}</h2>
                    {cartType === 'OBJECT' ? <ItemAccessories item={context} /> : null}
                </header>
                <Panel addClasses="cart__result-table">
                    {cartElements.length > 0 ?
                        <PanelHeading addClasses="cart__header">
                            <CartTools
                                elements={cartElements}
                                savedCartObj={savedCartObj}
                                selectedTerms={this.state.selectedTerms}
                                viewableElements={this.state.viewableElements}
                                cartType={cartType}
                                sharedCart={cartContext}
                                fileCount={this.state.selectedFileCount}
                                visualizable={this.state.visualizableOnly}
                            />
                        </PanelHeading>
                    : null}
                    <ElementCountArea
                        count={cartElements.length}
                        viewableElementCount={cartType === 'OBJECT' ? this.state.viewableElementCount : -1}
                        typeName="dataset"
                        typeNamePlural="datasets"
                    />
                    <PanelBody>
                        {cartElements.length > 0 ?
                            <div className="cart__display">
                                <FileFacets
                                    facets={this.state.facets}
                                    elements={cartElements}
                                    selectedTerms={this.state.selectedTerms}
                                    termClickHandler={this.handleTermClick}
                                    selectedFileCount={this.state.selectedFileCount}
                                    visualizableOnly={this.state.visualizableOnly}
                                    visualizableOnlyChangeHandler={this.handleVisualizableOnlyChange}
                                    loggedIn={loggedIn}
                                    facetLoadProgress={this.state.facetLoadProgress}
                                />
                                <TabPanel
                                    tabPanelCss="cart__display-content"
                                    tabs={{ datasets: 'Datasets', browser: 'Genome browser' }}
                                    decoration={currentPager}
                                    decorationClasses="cart__tab-tools"
                                    handleTabClick={this.handleTabClick}
                                >
                                    <TabPanelPane key="datasets">
                                        <CartSearchResults
                                            elements={cartElements}
                                            currentPage={this.state.currentDatasetResultsPage}
                                            cartControls={cartType !== 'OBJECT'}
                                            loggedIn={loggedIn}
                                        />
                                    </TabPanelPane>
                                    <TabPanelPane key="browser">
                                        <GenomeBrowser files={this.state.visualizableFiles} assembly={this.state.selectedTerms.assembly[0]} expanded />
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
    }
}

CartComponent.propTypes = {
    /** Cart object to display */
    context: PropTypes.object.isRequired,
    /** In-memory cart contents */
    elements: PropTypes.array.isRequired,
    /** Cart as it exists in the database */
    savedCartObj: PropTypes.object,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
    /** True if user has logged in */
    loggedIn: PropTypes.bool,
    /** System fetch function */
    fetch: PropTypes.func.isRequired,
};

CartComponent.defaultProps = {
    savedCartObj: null,
    loggedIn: false,
};

CartComponent.contextTypes = {
    fetch: PropTypes.func,
    session: PropTypes.object,
};


const mapStateToProps = (state, ownProps) => ({
    elements: state.elements,
    savedCartObj: state.savedCartObj,
    inProgress: state.inProgress,
    context: ownProps.context,
    loggedIn: ownProps.loggedIn,
    fetch: ownProps.fetch,
});

const CartInternal = connect(mapStateToProps)(CartComponent);


/**
 * Wrapper to receive React <App> context and pass it to CartInternal as regular props.
 */
const Cart = (props, reactContext) => {
    const loggedIn = !!(reactContext.session && reactContext.session['auth.userid']);
    return <CartInternal context={props.context} fetch={reactContext.fetch} loggedIn={loggedIn} />;
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
