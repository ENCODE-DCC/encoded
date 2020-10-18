/**
 * Components for rendering the /carts/ and /cart-view/ page.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import _ from 'underscore';
import Pager from '../../libs/bootstrap/pager';
import { Panel, PanelBody, PanelHeading } from '../../libs/bootstrap/panel';
import { tintColor } from '../datacolors';
import { itemClass, encodedURIComponent, parseAndLogError } from '../globals';
import { requestObjects, DisplayAsJson } from '../objectutils';
import { ResultTableList } from '../search';
import CartBatchDownload from './batch_download';
import CartClearButton from './clear';
import { cartRetrieve } from './database';
import CartMergeShared from './merge_shared';


/** Number of dataset elements to display per page */
const PAGE_ELEMENT_COUNT = 25;
/** File facet fields to display in order of display */
const displayedFacetFields = [
    'sample_type',
    'tissue_derivatives',
    'tissue_type',
    'anatomic_site',
    'status',
];


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
        const experimentTypeQuery = this.props.elements.every(element => element.match(/^\/patients\/.*?\/$/) !== null);
        const cartQueryString = `/search/?limit=all${experimentTypeQuery ? '&type=Patient' : ''}`;
        requestObjects(currentPageElements, cartQueryString).then((searchResults) => {
            this.setState({ elementsForDisplay: searchResults });
        });
    }

    render() {
        if (this.state.elementsForDisplay && this.state.elementsForDisplay.length === 0) {
            return <div className="nav result-table cart__empty-message">No visible datasets on this page.</div>;
        }
        return <ResultTableList results={this.state.elementsForDisplay || []} cartControls={this.props.cartControls} />;
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
                        <span>{fileCountFormatted} {fileCount === 1 ? 'biospecimen or file' : 'biospecimens or files'} selected</span>
                    :
                        <span>No biospecimen or files selected for download</span>
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
 * Display the cart file facet term icon that shows the magnitude of a facet term through its color
 * tint. The maximum value for the facet gets the full base color, and lesser values get lighter
 * tints.
 */
const FacetTermMagnitude = ({ termCount, maxTermCount }) => {
    const MAGNITUDE_BASE_COLOR = '#656BFF';
    const magnitudeColor = tintColor(MAGNITUDE_BASE_COLOR, 1 - (termCount / maxTermCount));
    return (
        <div className="cart-facet-term__magnitude">
            <i className="icon icon-circle" style={{ color: magnitudeColor }} />
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
        const { term, termCount, maxTermCount, selected } = this.props;
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
                    aria-label={`${termCount} ${term} files`}
                >
                    <FacetTermCheck checked={selected} />
                    <div className="cart-facet-term__text">{term}</div>
                    <div className="cart-facet-term__count">{termCount}</div>
                    <FacetTermMagnitude termCount={termCount} maxTermCount={maxTermCount} />
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
    /** Callback for handling clicks in the term */
    termClickHandler: PropTypes.func.isRequired,
};

FacetTerm.defaultProps = {
    selected: false,
};


/**
 * Request a search of files whose datasets match those in `elements`. Uses search_elements
 * endpoint so we can send all the elements in the cart in the JSON payload of the request.
 * @param {array} elements `@id`s of datasets to request for a file facet
 * @param {func} fetch System fetch function
 * @param {string} queryString Query string to add to URI being fetched; '' for no additions
 * @param {object} session session object from <App> context
 * @return {object} Promise with search result object
 */
const requestFacet = (elements, fetch, queryString, session) => {
    // If <App> hasn't yet retrieved a CSRF token, retrieve one ourselves.
    let sessionPromise;
    if (!session || !session._csrft_) {
        // No session CSRF token, so do a GET of "/session" to retrieve it.
        sessionPromise = fetch('/session');
    } else {
        // We have a session CSRF token, so retrieve it immediately.
        sessionPromise = Promise.resolve(session._csrft);
    }

    // We could have more experiment @ids than the /search/ endpoint can handle in the query
    // string, so pass the @ids in a POST request payload instead to the /search_elements/
    // endpoint instead.
    const fieldQuery = displayedFacetFields.reduce((query, field) => `${query}&field=biospecimen.${field}`, '');
    return sessionPromise.then(csrfToken => (
        fetch(`/search_elements/type=Patient${fieldQuery}&limit=all&filterresponse=off${queryString || ''}`, {
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
    return parts.reduce((partObject, part) => partObject[part], object);
};


/**
 * Adds facet term counts and totals from facets of a search result object to the corresponding
 * `accumulatingResults` facet objects. The facets processed have field names in `facetFields`.
 * The `displayedFacetFields` global controls which fields are used.
 * @param {object} accumulatingResults File search results being accumulated.
 * @param {object} currentResults Dataset search results whose file information is getting added
 *                                to the accumulating file results.
 * @param {array}  facetFields Facet field values whose term counts are to be added to the
 *                             accumulating file results.
 *
 * @return {object} Returns `accumulatingResults` with file information from `currentResults`
 *                  added. `accumulatingResults` does not get mutated -- this function returns a
 *                  new object each time.
 */
const addToAccumulatingFacets = (accumulatingResults, currentResults, facetFields) => {
    let fileResults = accumulatingResults;
    if (currentResults['@graph'] && currentResults['@graph'].length > 0) {
        // Copy the incoming accumulating file results object to avoid mutating it, and then make
        // the `fileFacetsRefs` object to make finding each field's entry in the copy easy.
        fileResults = Object.assign({}, accumulatingResults);
        fileResults.facets = accumulatingResults.facets.slice(0);
        const fileFacetsRefs = {};
        facetFields.forEach((field) => {
            const matchingFacetIndex = fileResults.facets.findIndex(facet => facet.field === field);
            fileResults.facets[matchingFacetIndex] = Object.assign({}, fileResults.facets[matchingFacetIndex]);
            fileResults.facets[matchingFacetIndex].terms = fileResults.facets[matchingFacetIndex].terms.slice(0);
            fileFacetsRefs[field] = fileResults.facets[matchingFacetIndex];
        });

        // Go through each experiment result to collect file information in the faked file results
        // object.
        currentResults['@graph'].forEach((patient) => {
            if (patient.biospecimen && patient.biospecimen.length > 0) {
                patient.biospecimen.forEach((file) => {
                    if (file) {
                        // For each field we're collecting file information for, add its file facet
                        // count to the fake file facet we're putting together.
                        facetFields.forEach((field) => {
                            const fileFieldValue = getObjectFieldValue(file, field);
                            if (fileFieldValue) {
                                const facet = fileFacetsRefs[field];
                                const termIndex = facet.terms.findIndex(term => term.key === fileFieldValue);
                                if (termIndex !== -1) {
                                    // Facet already has an entry for this key, so just bump its counter.
                                    facet.terms[termIndex] = { doc_count: facet.terms[termIndex].doc_count + 1, key: facet.terms[termIndex].key };
                                } else {
                                    // Make a new entry for this key in the facet terms array.
                                    facet.terms.push({ doc_count: 1, key: fileFieldValue });
                                }
                                facet.total += 1;
                            }
                        });
                    }
                });

                // Collect files in the @graph of the fake file search results object.
                fileResults['@graph'] = fileResults['@graph'].concat(patient.biospecimen.filter(biospecimen => biospecimen));
            }
        });
    }
    return fileResults;
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
        this.props.facetTermClickHandler(this.props.field, term);
    }

    /**
     * Handle a click in the facet expander by calling a parent handler.
     * @param {object} e React synthetic event
     */
    handleExpanderEvent(e) {
        this.props.expanderClickHandler(this.props.field, e.altKey);
    }

    render() {
        const { facet, field, title, expanded, selectedFacetTerms } = this.props;
        const maxTermCount = Math.max(...Object.keys(facet).map(term => facet[term]));
        const sortedTerms = Object.keys(facet).sort();
        const labelId = `${field}-label`;
        return (
            <div className="facet">
                <FacetExpander title={title} field={field} labelId={labelId} expanded={expanded} expanderEventHandler={this.handleExpanderEvent} />
                {expanded ?
                    <ul className="cart-facet" role="region" id={field} aria-labelledby={labelId}>
                        {sortedTerms.map(term => (
                            <FacetTerm
                                key={term}
                                term={term}
                                termCount={facet[term]}
                                maxTermCount={maxTermCount}
                                selected={selectedFacetTerms.indexOf(term) > -1}
                                termClickHandler={this.handleFacetTermClick}
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
    field: PropTypes.string.isRequired,
    /** Human-readable title for the facet being displayed */
    title: PropTypes.string.isRequired,
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
 * Display the file facets. These display the number of files involved -- not the number of
 * experiments with files matching a criteria. As the primary input to this component is currently
 * an array of experiment IDs while these facets displays all the files involved with those
 * experiments, this component begins by retrieving information about all relevant files from the
 * DB. Each time an experiment is removed from the cart while viewing the cart page, this component
 * again retrieves all relevant files for the remaining experiments.
 */
class FileFacets extends React.Component {
    /**
     * Update the `facets` object by incrementing the count of the term within it selected by the
     * `field` within the given `file`. This utility function only avoids duplicating code in the
     * `assembleFacets` method.
     * @param {object} facets Facet object to update - mutated!
     * @param {string} field Field key within the facet to update
     * @param {object} file File containing the term to add to the facet
     */
    static addFileTermToFacet(facets, field, file) {
        const term = getObjectFieldValue(file, field);
        if (term !== undefined) {
            if (facets[field]) {
                // The facet has been seen in this loop before, so add to or initialize
                // the relevant term within this facet.
                if (facets[field][term]) {
                    facets[field][term] += 1;
                } else {
                    facets[field][term] = 1;
                }
            } else {
                // The facet has not been seen in this loop before, so initialize it as
                // well as the value of the relevant term within the facet.
                facets[field] = {};
                facets[field][term] = 1;
            }
        }
    }

    constructor() {
        super();
        this.state = {
            /** Tracks facet loading progress */
            facetLoadProgress: null,
        };

        // Initialize the expanded state of every facet; only the first one is expanded by default.
        const expandedStates = {};
        displayedFacetFields.forEach((field, index) => {
            expandedStates[field] = index === 0;
        });
        this.state.expanded = expandedStates;

        this.files = [];
        this.fileCount = 0;
        this.titleMap = {};

        this.retrieveFileFacets = this.retrieveFileFacets.bind(this);
        this.assembleFacets = this.assembleFacets.bind(this);
        this.handleExpanderClick = this.handleExpanderClick.bind(this);
    }

    componentDidMount() {
        this.retrieveFileFacets();
    }

    componentDidUpdate(prevProps) {
        if (prevProps.elements.length !== this.props.elements.length || prevProps.loggedIn !== this.props.loggedIn) {
            this.retrieveFileFacets();
        }
        this.props.selectedFileCountHandler(this.selectedFileCount);
    }

    /**
     * Need to see how file facets look so we can gradually accumulate one, so retrieve an empty
     * file search result. Return a promise with this facet template.
     */
    retrieveFileFacetTemplate() {
        return this.context.fetch(
            '/search/?type=Biospecimen&limit=0',
            {
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json',
                },
            }
        ).then((response) => {
            if (response.ok) {
                return response.json();
            }
            throw new Error(response);
        }).then((response) => {
            // Extract only the facets defined in displayedFacetFields.
            const facets = [];
            displayedFacetFields.forEach((field) => {
                const displayedFacet = response.facets.find(facet => facet.field === field);
                if (displayedFacet) {
                    facets.push(Object.assign({}, displayedFacet, { terms: [], total: 0 }));
                }
            });
            response.facets = facets;
            response.total = 0;
            return response;
        }).catch((response) => {
            parseAndLogError('getWriteableCartObject', response);
        });
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
        for (let elementIndex = 0; elementIndex < this.props.elements.length; elementIndex += CHUNK_SIZE) {
            chunks.push(this.props.elements.slice(elementIndex, elementIndex + CHUNK_SIZE));
        }

        // Assemble the query string from the selected facets.
        let queryString = '';
        displayedFacetFields.forEach((field) => {
            if (this.props.selectedTerms[field].length > 0) {
                const termQuery = this.props.selectedTerms[field].map(term => `biospecimen.${field}=${encodedURIComponent(term)}`).join('&');
                queryString += `&${termQuery}`;
            }
        });

        // Using the arrays of dataset @id arrays, do a sequence of searches of CHUNK_SIZE datasets
        // adding the totals from their files together to form the final file facet. Also count the
        // total number of viewable cart elements for logged-out users viewing shared carts. The
        // initial promise comes from retrieving the file-facet template, and then we accumulate
        // file data from the chunked dataset searches.
        let viewableElementCount = 0;
        const viewableElements = [];
        chunks.reduce((promiseChain, currentChunk, currentChunkIndex) => (
            promiseChain.then(accumulatingResults => (
                requestFacet(currentChunk, this.context.fetch, queryString, this.context.session).then((currentResults) => {
                    this.setState({ facetLoadProgress: Math.round(((currentChunkIndex + 1) / chunks.length) * 100) });
                    viewableElementCount += currentResults.total;
                    viewableElements.push(...currentResults['@graph'].map(patient => patient['@id']));
                    return addToAccumulatingFacets(accumulatingResults, currentResults, displayedFacetFields);
                })
            )).catch((response) => {
                parseAndLogError('Error reading biospecimen facets', response);
            })
        ), this.retrieveFileFacetTemplate()).then((accumulatedResults) => {
            // All cart datasets in all chunks have been retrieved and their files extracted, and
            // the file facet results accumulated. Save the list of files as well as a map of facet
            // field name to corresponding title.
            this.files = accumulatedResults['@graph'];
            this.titleMap = {};
            accumulatedResults.facets.forEach((facet) => {
                this.titleMap[facet.field] = facet.title;
            });

            // Indicate that file facet loading is done.
            this.setState({ facetLoadProgress: -1 });
            this.props.searchResultHandler(accumulatedResults, viewableElementCount, viewableElements);
        });
    }

    /**
     * Based on the currently selected facet terms and the files collected from the carted
     * experiments, generate a list of facets and corresponding counts. The length of the files
     * array could be in the hundreds of thousands, so this data has to be extracted by going
     * through this array only once per render.
     */
    assembleFacets() {
        const facets = {};
        let selectedFileCount = 0;
        if (this.files.length > 0) {
            const { selectedTerms } = this.props;
            const selectedFacetKeys = Object.keys(selectedTerms).filter(term => selectedTerms[term].length > 0);
            this.files.forEach((file) => {
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
                        FileFacets.addFileTermToFacet(facets, facetField, file);
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
                            FileFacets.addFileTermToFacet(facets, selectedFacetField, file);
                        }
                    });
                }
            });

            // We need to include selected terms that happen to have a zero count, so add all
            // selected facet terms not yet included in `facets`.
            Object.keys(selectedTerms).forEach((field) => {
                if (field in facets) {
                    // Find selected terms NOT in facets and add them with a zero count.
                    const missingTerms = selectedTerms[field].filter(term => Object.keys(facets[field]).indexOf(term) === -1);
                    if (missingTerms.length > 0) {
                        missingTerms.forEach((term) => {
                            facets[field][term] = 0;
                        });
                    }
                }
            });
        }

        return { facets: Object.keys(facets).length > 0 ? facets : null, selectedFileCount };
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
                    expandedStates[facetField] = nextExpandedState;
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
        const { selectedTerms, termClickHandler } = this.props;

        // Based on carted files and currently selected facet terms, generate a facet object for
        // rendering.
        const { facets, selectedFileCount } = this.assembleFacets();
        this.selectedFileCount = selectedFileCount;

        return (
            <div className="box facets">
                <FileCount fileCount={selectedFileCount} facetLoadProgress={this.state.facetLoadProgress} />
                <div>
                    {facets ?
                        <div>
                            {displayedFacetFields.map(field => (
                                <div key={field}>
                                    {facets[field] ?
                                        <Facet
                                            key={field}
                                            field={field}
                                            title={this.titleMap[field]}
                                            facet={facets[field]}
                                            selectedFacetTerms={selectedTerms[field]}
                                            facetTermClickHandler={termClickHandler}
                                            expanded={this.state.expanded[field]}
                                            expanderClickHandler={this.handleExpanderClick}
                                        />
                                    : null}
                                </div>
                            ))}
                        </div>
                    :
                        <div className="cart__empty-message">No biospecimens or files available</div>
                    }
                </div>
            </div>
        );
    }
}

FileFacets.propTypes = {
    /** Array of @ids of all elements in the cart */
    elements: PropTypes.array,
    /** Selected facet fields */
    selectedTerms: PropTypes.object,
    /** Callback when the user clicks on a file format facet item */
    termClickHandler: PropTypes.func.isRequired,
    /** Callback that receives accumulated search results */
    searchResultHandler: PropTypes.func.isRequired,
    /** Called when count of selected files determined */
    selectedFileCountHandler: PropTypes.func.isRequired,
    /** True if user has logged in */
    loggedIn: PropTypes.bool,
};

FileFacets.defaultProps = {
    elements: [],
    selectedTerms: null,
    loggedIn: false,
};

FileFacets.contextTypes = {
    fetch: PropTypes.func,
    session: PropTypes.object,
};


/**
 * Display cart tool buttons. If `savedCartObj` is supplied, supply it for the metadata.tsv line
 * in the resulting files.txt.
 */
const CartTools = ({ elements, selectedTerms, savedCartObj, viewableElements, fileCount, cartType, sharedCart }) => (
    <div className="cart__tools">
        {elements.length > 0 ?
            <CartBatchDownload
                elements={elements}
                selectedTerms={selectedTerms}
                cartType={cartType}
                savedCartObj={savedCartObj}
                sharedCart={sharedCart}
                fileCount={fileCount}
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
};

CartTools.defaultProps = {
    elements: [],
    selectedTerms: null,
    savedCartObj: null,
    viewableElements: null,
    sharedCart: null,
    fileCount: 0,
};


/**
 * Display the total number of cart elements.
 */
const ElementCountArea = ({ count, viewableElementCount, typeName, typeNamePlural }) => {
    if (count > 0) {
        const countFormatted = count.toLocaleString ? count.toLocaleString() : count.toString();
        return (
            <div className="cart__element-count">
                <span>{countFormatted}&nbsp;{count === 1 ? typeName : typeNamePlural} in cohort</span>
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
    <div className="cart__pager">
        {totalPageCount > 1 ?
            <div>
                <Pager total={totalPageCount} current={currentPage} updateCurrentPage={updateCurrentPage} />
                <div className="cart__pager-note">pages of datasets</div>
            </div>
        : null}
    </div>
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
 * Sets the initial React state for the cart page.
 */
const createInitialCartState = () => {
    const newState = {
        /** Files formats selected to be included in results; all formats if empty array */
        selectedTerms: {},
        /** Search result facets */
        fileFacets: {},
        /** Count of elements viewable at user's access level; only for shared carts */
        viewableElementCount: -1,
        /** Array of viewable element @ids */
        viewableElements: null,
        /** Currently displayed page of dataset search results */
        currentDatasetResultsPage: 0,
        /** Cart context after update */
        updatedContext: null,
        /** Number of files selected for download */
        selectedFileCount: 0,
    };
    displayedFacetFields.forEach((field) => {
        newState.selectedTerms[field] = [];
        newState.fileFacets[field] = [];
    });
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
 */
class CartComponent extends React.Component {
    constructor() {
        super();
        this.state = createInitialCartState();
        this.files = [];
        this.handleTermClick = this.handleTermClick.bind(this);
        this.handleFileSearchResults = this.handleFileSearchResults.bind(this);
        this.computePageInfo = this.computePageInfo.bind(this);
        this.updateDatasetCurrentPage = this.updateDatasetCurrentPage.bind(this);
        this.handleSelectedFileCount = this.handleSelectedFileCount.bind(this);
    }

    componentDidUpdate(prevProps) {
        const { cartType, totalDatasetPages } = this.computePageInfo();

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
                fileFacets: newState.fileFacets,
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
     * Compute information about the currently displayed page of cart contents including:
     * cartType: Type of cart being displayed:
     *           'ACTIVE': Viewing the current cart
     *           'OBJECT': Viewing the cart specified in the URL
     *           'MEMORY': Viewing carts in browser memory (non-logged-in user)
     * cartName: Name of cart
     * cartElements: Array of cart element @ids
     * totalDatasetPages: Total number of pages of cart elements to display
     */
    computePageInfo() {
        const { context, savedCartObj, elements } = this.props;
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
                cartName = 'Cohort';
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
            // Determine whether we need to add or subtract a term from the facet selections.
            const addTerm = this.state.selectedTerms[clickedField].indexOf(clickedTerm) === -1;

            // prevState is immutable, so make a copy with the newly clicked term to set the
            // new state.
            const newSelectedTerms = {};
            if (addTerm) {
                // Adding a selected term. Copy the previous selectedFacetTerms, adding the newly
                // selected term in its facet in sorted position.
                displayedFacetFields.forEach((field) => {
                    if (clickedField === field) {
                        // Clicked term belongs to this field's facet. Insert it into its sorted
                        // position in a copy of the selectedTerms array.
                        const sortedIndex = _(prevState.selectedTerms[field]).sortedIndex(clickedTerm);
                        newSelectedTerms[field] = [...prevState.selectedTerms[field].slice(0, sortedIndex), clickedTerm, ...prevState.selectedTerms[field].slice(sortedIndex)];
                    } else {
                        // Clicked term doesn't belong to this field's facet. Just copy the
                        // `selectedTerms` array unchanged.
                        newSelectedTerms[field] = prevState.selectedTerms[field].slice(0);
                    }
                });
            } else {
                // Removing a selected term. Copy the previous selectedFacetTerms, filtering out
                // the unselected term in its facet.
                displayedFacetFields.forEach((field) => {
                    newSelectedTerms[field] = prevState.selectedTerms[field].filter(term => term !== clickedTerm);
                });
            }
            return { selectedTerms: newSelectedTerms };
        });
    }

    /**
     * Handle incoming file facet search results. If any previously unseen facet fields have come
     * in, add them to the list of facets fields with a copy of the field’s term array.
     * @param {object} results File search results from server
     * @param {number} viewableElementCount Number of elements viewable to logged-out users
     * @param {array} viewableElements Datasets viewable to logged-out users
     */
    handleFileSearchResults(results, viewableElementCount, viewableElements) {
        const newFacets = Object.assign({}, this.state.fileFacets);
        results.facets.forEach((facet) => {
            if (displayedFacetFields.indexOf(facet.field) !== -1) {
                newFacets[facet.field] = facet.terms.slice(0);
            }
        });
        this.setState({ fileFacets: newFacets, viewableElementCount, viewableElements });
    }

    /**
     * Called when the user selects a new page of cart elements to view.
     * @param {number} newCurrent New current page to view; zero based
     */
    updateDatasetCurrentPage(newCurrent) {
        this.setState({ currentDatasetResultsPage: newCurrent });
    }

    /**
     * Called when the number of files selected for download has been determined.
     * @param {number} selectedFileCount Number of files selected for downlaod
     */
    handleSelectedFileCount(selectedFileCount) {
        if (selectedFileCount !== this.state.selectedFileCount) {
            this.setState({ selectedFileCount });
        }
    }

    render() {
        const { context, savedCartObj, loggedIn } = this.props;
        const { cartType, cartElements, cartName, totalDatasetPages } = this.computePageInfo();
        const cartContext = this.state.updatedContext || context;

        return (
            <div className={itemClass(cartContext, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{cartName}</h2>
                        {cartType === 'OBJECT' ? <DisplayAsJson /> : null}
                    </div>
                </header>
                <Panel addClasses="cart__result-table">
                    {cartElements.length ?
                        <PanelHeading addClasses="cart__header">
                            <PagerArea currentPage={this.state.currentDatasetResultsPage} totalPageCount={totalDatasetPages} updateCurrentPage={this.updateDatasetCurrentPage} />
                            <CartTools
                                elements={cartElements}
                                savedCartObj={savedCartObj}
                                selectedTerms={this.state.selectedTerms}
                                viewableElements={this.state.viewableElements}
                                cartType={cartType}
                                sharedCart={cartContext}
                                fileCount={this.state.selectedFileCount}
                            />
                        </PanelHeading>
                    : null}
                    <ElementCountArea
                        count={cartElements.length}
                        viewableElementCount={cartType === 'OBJECT' ? this.state.viewableElementCount : -1}
                        typeName="patient"
                        typeNamePlural="patients"
                    />
                    <PanelBody>
                        {cartElements.length > 0 ?
                            <div className="cart__display">
                                <FileFacets
                                    elements={cartElements}
                                    selectedTerms={this.state.selectedTerms}
                                    termClickHandler={this.handleTermClick}
                                    searchResultHandler={this.handleFileSearchResults}
                                    selectedFileCountHandler={this.handleSelectedFileCount}
                                    loggedIn={loggedIn}
                                />
                                <CartSearchResults
                                    elements={cartElements}
                                    currentPage={this.state.currentDatasetResultsPage}
                                    cartControls={cartType !== 'OBJECT'}
                                    loggedIn={loggedIn}
                                />
                            </div>
                        :
                            <p className="cart__empty-message">Empty cohort</p>
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
