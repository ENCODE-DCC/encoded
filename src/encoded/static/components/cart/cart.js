/**
 * Components for rendering the /carts/ and /cart-view/ page.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import _ from 'underscore';
import Pager from '../../libs/bootstrap/pager';
import { Panel, PanelBody, PanelHeading } from '../../libs/bootstrap/panel';
import { contentViews, itemClass, encodedURIComponent, parseAndLogError } from '../globals';
import { requestObjects, DisplayAsJson } from '../objectutils';
import { ResultTableList } from '../search';
import CartBatchDownload from './batch_download';
import CartClear from './clear';
import CartMergeShared from './merge_shared';


/** Number of dataset elements to display per page */
const PAGE_ELEMENT_COUNT = 25;
/** File facet fields to display */
const displayedFacetFields = [
    'file_type',
];
/** File facet field to use to count the total file count */
const displayedFacetCountingField = 'file_type';


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
        if (prevProps.currentPage !== this.props.currentPage || !_.isEqual(prevProps.elements, this.props.elements) || (prevProps.loggedIn !== this.props.loggedIn)) {
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
        return <ResultTableList results={this.state.elementsForDisplay || []} activeCart={this.props.activeCart} />;
    }
}

CartSearchResults.propTypes = {
    /** Array of cart item @ids */
    elements: PropTypes.array,
    /** Page of results to display */
    currentPage: PropTypes.number,
    /** True if displaying an active cart */
    activeCart: PropTypes.bool,
    /** True if user has logged in */
    loggedIn: PropTypes.bool,
};

CartSearchResults.defaultProps = {
    elements: [],
    currentPage: 0,
    activeCart: false,
    loggedIn: false,
};


/**
 * Display one term of the File Format facet.
 */
class FacetTerm extends React.Component {
    constructor() {
        super();
        this.handleTermSelect = this.handleTermSelect.bind(this);
    }

    /**
     * Called when a file format is selected from the facet.
     */
    handleTermSelect() {
        this.props.termSelectHandler(this.props.term);
    }

    render() {
        const { term, termCount, totalTermCount, selected } = this.props;
        const barStyle = {
            width: `${Math.ceil((termCount / totalTermCount) * 100)}%`,
        };
        return (
            <li className={`facet-term${selected ? ' selected' : ''}`}>
                <button id={`facet-term-${term}`} onClick={this.handleTermSelect} aria-label={`${term} with count ${termCount}`}>
                    <div className="facet-term__item">
                        <div className="facet-term__text"><span>{term}</span></div>
                        <div className="facet-term__count">
                            {termCount}
                        </div>
                        <div className="facet-term__bar" style={barStyle} />
                    </div>
                </button>
            </li>
        );
    }
}

FacetTerm.propTypes = {
    /** Displayed facet item */
    term: PropTypes.string.isRequired,
    /** Displayed number of files for this item */
    termCount: PropTypes.number.isRequired,
    /** Total number of files in the item's facet */
    totalTermCount: PropTypes.number.isRequired,
    /** True if this term should appear selected */
    selected: PropTypes.bool,
    /** Callback for handling clicks in the item's button */
    termSelectHandler: PropTypes.func.isRequired,
};

FacetTerm.defaultProps = {
    selected: false,
};


/**
 * Request a search of files whose datasets match those in `items`. Uses search_elements endpoint
 * so we can send all the elements in the cart in the JSON payload of the request.
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
    const fieldQuery = displayedFacetFields.reduce((query, field) => `${query}&field=files.${field}`, '');
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
 * Adds facet term counts and totals from facets of a search result object to the corresponding
 * `accumulatedResults` facet objects. The facets processed have field names in `facetFields`.
 * This function works with multiple fields, but the currently implementation only has file_type.
 * The `displayedFacetFields` global controls which fields are used. `countingField` is controlled
 * by the `displayedFacetCountingField` global.
 * @param {object} accumulatedResults File search results being accumulated.
 * @param {object} currentResults Dataset search results whose file information is getting added
 *                                to the accumulating file results.
 * @param {array} facetFields Facet field values whose term counts are to be added to the
 *                            accumulating file results.
 * @param {string} countingField Field of facets to count to find total file count.
 * @return {object} Returns `accumulatingResults` with file information from `currentResults`
 *                  added. `accumulatingResults` does not get mutated -- this function returns a
 *                  new object each time.
 */
const addToAccumulatingFacets = (accumulatingResults, currentResults, facetFields, countingField) => {
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
        currentResults['@graph'].forEach((experiment) => {
            if (experiment.files && experiment.files.length > 0) {
                experiment.files.forEach((file) => {
                    if (!file.restricted) {
                        facetFields.forEach((field) => {
                            const facet = fileFacetsRefs[field];
                            const termIndex = facet.terms.findIndex(term => term.key === file[field]);
                            if (termIndex !== -1) {
                                // Facet already has an entry for this key, so just bump its counter.
                                facet.terms[termIndex] = { doc_count: facet.terms[termIndex].doc_count + 1, key: facet.terms[termIndex].key };
                            } else {
                                // Make a new entry for this key in the facet terms array.
                                facet.terms.push({ doc_count: 1, key: file[field] });
                            }
                            facet.total += 1;
                        });
                    }
                });
            }
        });

        // Update the entire facet count to be the same as the selected field, normally a required
        // field.
        fileResults.total = fileFacetsRefs[countingField].total;
    }
    return fileResults;
};


/**
 * Display a single file facet.
 */
class Facet extends React.Component {
    constructor() {
        super();
        this.handleFacetTermSelect = this.handleFacetTermSelect.bind(this);
    }

    /**
     * Handle a click in a facet term by calling a parent handler.
     */
    handleFacetTermSelect(term) {
        this.props.facetTermSelectHandler(this.props.facet.field, term);
    }

    render() {
        const { facet, selectedFacetTerms } = this.props;
        return (
            <div className="facet">
                <h5>{facet.title}</h5>
                <ul className="facet-list nav">
                    {facet.terms.map(term => (
                        <div key={term.key}>
                            {term.doc_count > 0 ?
                                <FacetTerm
                                    term={term.key}
                                    termCount={term.doc_count}
                                    totalTermCount={facet.total}
                                    selected={selectedFacetTerms.indexOf(term.key) > -1}
                                    termSelectHandler={this.handleFacetTermSelect}
                                />
                            : null}
                        </div>
                    ))}
                </ul>
            </div>
        );
    }
}

Facet.propTypes = {
    /** Facet object to display */
    facet: PropTypes.object.isRequired,
    /** Selected term keys */
    selectedFacetTerms: PropTypes.array,
    /** Function called when a facet term is clicked */
    facetTermSelectHandler: PropTypes.func.isRequired,
};

Facet.defaultProps = {
    selectedFacetTerms: [],
};


/**
 * Display the file facets. These display the number of files involved -- not the number of
 * experiments with files matching a criteria. As the primary input to this component is currently
 * an array of experiment IDs while this facet displays all the files involved with those
 * experiments, this component begins by retrieving information about all relevant files from the
 * DB. Each time an experiment is removed from the cart while viewing the cart page, this component
 * again retrieves all relevant files for the remaining experiments.
 */
class FileFacets extends React.Component {
    constructor() {
        super();
        this.state = {
            /** File search result facets to display */
            displayedFacets: null,
            /** Tracks facet loading progress */
            facetLoadProgress: 0,
        };
        this.retrieveFileFacets = this.retrieveFileFacets.bind(this);
    }

    componentDidMount() {
        this.retrieveFileFacets();
    }

    componentDidUpdate(prevProps) {
        if (prevProps.elements.length !== this.props.elements.length || prevProps.loggedIn !== this.props.loggedIn) {
            this.retrieveFileFacets();
        }
    }

    /**
     * Need to see how file facets look so we can gradually accumulate one, so retrieve an empty
     * file search result. Return a promise with this facet template.
     */
    retrieveFileFacetTemplate() {
        return this.context.fetch(
            '/search/?type=File&limit=0',
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
                const termQuery = this.props.selectedTerms[field].map(term => `files.${field}=${encodedURIComponent(term)}`).join('&');
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
                    viewableElements.push(...currentResults['@graph'].map(experiment => experiment['@id']));
                    return addToAccumulatingFacets(accumulatingResults, currentResults, displayedFacetFields, displayedFacetCountingField);
                })
            )).catch((response) => {
                parseAndLogError('Error reading file facets', response);
            })
        ), this.retrieveFileFacetTemplate()).then((accumulatedResults) => {
            // All datasets in all chunks have been retrieved for their file information, and the
            // file facet results accumulated. Now reformat the accumulated results into normal
            // facet objects, then update the `displayedFacets` state to render the facets. This
            // mechanism handles more than one facet, but at this time we have only one.
            const displayedFacets = {};
            displayedFacetFields.forEach((field) => {
                const displayedFacet = accumulatedResults.facets.find(facet => facet.field === field);
                if (displayedFacet) {
                    displayedFacet.terms.sort((a, b) => b.doc_count - a.doc_count);
                }
                displayedFacets[field] = displayedFacet;
            });
            this.setState({ displayedFacets, facetLoadProgress: -1 });
            this.props.searchResultHandler(accumulatedResults, viewableElementCount, viewableElements);
        });
    }

    render() {
        const { selectedTerms, fileCount, termSelectHandler } = this.props;
        const { displayedFacets } = this.state;
        const fileCountFormatted = fileCount.toLocaleString ? fileCount.toLocaleString() : fileCount.toString();

        // Detect if we have empty facets.
        let emptyFacets = false;
        if (displayedFacets) {
            emptyFacets = !Object.keys(displayedFacets).some(field => displayedFacets[field].terms && displayedFacets[field].terms.length > 0);
        }

        return (
            <div className="box facets">
                {this.state.facetLoadProgress >= 0 ?
                    <div className="cart__facet-progress-overlay">
                        <progress value={this.state.facetLoadProgress} max="100" />
                    </div>
                : null}
                {fileCount > 0 ? <div className="cart__facet-file-count">{fileCountFormatted} files selected for download</div> : null}
                {displayedFacets ?
                    <div>
                        {emptyFacets ?
                            <div className="cart__empty-message">No files available</div>
                        :
                            <div>
                                {displayedFacetFields.map(field => (
                                    <div key={field}>
                                        {displayedFacets[field] ?
                                            <Facet key={field} facet={displayedFacets[field]} selectedFacetTerms={selectedTerms[field]} facetTermSelectHandler={termSelectHandler} />
                                        : null}
                                    </div>
                                ))}
                            </div>
                        }
                    </div>
                : null}
            </div>
        );
    }
}

FileFacets.propTypes = {
    /** Array of @ids of all elements in the cart */
    elements: PropTypes.array,
    /** Selected facet fields */
    selectedTerms: PropTypes.object,
    /** Number of files batch download will cause to be downloaded */
    fileCount: PropTypes.number,
    /** Callback when the user clicks on a file format facet item */
    termSelectHandler: PropTypes.func.isRequired,
    /** Callback that receives accumulated search results */
    searchResultHandler: PropTypes.func.isRequired,
    /** True if user has logged in */
    loggedIn: PropTypes.bool,
};

FileFacets.defaultProps = {
    elements: [],
    selectedTerms: null,
    fileCount: 0,
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
const CartTools = ({ elements, selectedTerms, savedCartObj, viewableElements, fileCount, activeCart, sharedCart }) => (
    <div className="cart__tools">
        {elements.length > 0 ?
            <CartBatchDownload
                elements={elements}
                selectedTerms={selectedTerms}
                activeCart={activeCart}
                savedCartObj={savedCartObj}
                sharedCart={sharedCart}
                fileCount={fileCount}
            />
        : null}
        {activeCart ? null : <CartMergeShared sharedCartObj={sharedCart} viewableElements={viewableElements} />}
        {activeCart ? <CartClear /> : null}
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
    /** True if cart is active, False if cart is shared */
    activeCart: PropTypes.bool,
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
    activeCart: true,
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
    <div className="cart__pager">
        {totalPageCount > 1 ?
            <Pager total={totalPageCount} current={currentPage} updateCurrentPage={updateCurrentPage} />
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
    };
    displayedFacetFields.forEach((field) => {
        newState.selectedTerms[field] = [];
        newState.fileFacets[field] = [];
    });
    return newState;
};


/**
 * Renders the cart search results page. Display either:
 * 1. Shared cart (/carts/<uuid>) containing a user's saved elements
 * 2. Active cart (/cart-view/) containing saved and in-memory elements
 */
class CartComponent extends React.Component {
    constructor() {
        super();
        this.state = createInitialCartState();
        this.handleTermSelect = this.handleTermSelect.bind(this);
        this.handleFileSearchResults = this.handleFileSearchResults.bind(this);
        this.computePageInfo = this.computePageInfo.bind(this);
        this.updateDatasetCurrentPage = this.updateDatasetCurrentPage.bind(this);
    }

    componentDidUpdate(prevProps) {
        const { totalDatasetPages } = this.computePageInfo();

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
    }

    /**
     * Compute information about the currently displayed page of cart contents including:
     * activeCart: True if cart is active, false if cart coming from database cart object
     * cartElements: Array of cart element @ids
     * totalDatasetPages: Total number of pages of cart elements to display
     */
    computePageInfo() {
        const { context, cart } = this.props;
        const activeCart = context['@type'][0] === 'cart-view';
        const cartElements = activeCart ? cart : context.elements;
        return {
            activeCart,
            cartElements,
            totalDatasetPages: Math.floor(cartElements.length / PAGE_ELEMENT_COUNT) + (cartElements.length % PAGE_ELEMENT_COUNT !== 0 ? 1 : 0),
        };
    }

    /**
     * Called when the given file format was selected or deselected in the facet.
     * @param {string} clickedField `field` value of the facet whose term was clicked
     * @param {string} clickedTerm `term` value that was clicked
     */
    handleTermSelect(clickedField, clickedTerm) {
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

    render() {
        const { context, savedCartObj, loggedIn } = this.props;
        const { activeCart, cartElements, totalDatasetPages } = this.computePageInfo();

        // Calculate nubmer of files facet has selected, or all if none selected.
        let fileCount = 0;
        if (this.state.fileFacets[displayedFacetCountingField]) {
            const hasSelectedTerms = this.state.selectedTerms[displayedFacetCountingField].length > 0;
            fileCount = this.state.fileFacets[displayedFacetCountingField].reduce((accumulator, term) => (
                (!hasSelectedTerms || this.state.selectedTerms[displayedFacetCountingField].indexOf(term.key) !== -1) ? accumulator + term.doc_count : accumulator
            ), 0);
        }

        return (
            <div className={itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{activeCart ? <span>Cart</span> : <span>{context.name}</span>}</h2>
                        {activeCart ? null : <DisplayAsJson />}
                    </div>
                </header>
                <Panel addClasses="cart__result-table">
                    {cartElements.length ?
                        <PanelHeading addClasses="cart__header">
                            <PagerArea currentPage={this.state.currentDatasetResultsPage} totalPageCount={totalDatasetPages} updateCurrentPage={this.updateDatasetCurrentPage} />
                            <CartTools elements={cartElements} savedCartObj={savedCartObj} selectedTerms={this.state.selectedTerms} viewableElements={this.state.viewableElements} activeCart={activeCart} sharedCart={context} fileCount={fileCount} />
                        </PanelHeading>
                    : null}
                    <ElementCountArea count={cartElements.length} viewableElementCount={activeCart ? -1 : this.state.viewableElementCount} typeName="dataset" typeNamePlural="datasets" />
                    <PanelBody>
                        {cartElements.length > 0 ?
                            <div className="cart__display">
                                <FileFacets
                                    elements={cartElements}
                                    selectedTerms={this.state.selectedTerms}
                                    fileCount={fileCount}
                                    termSelectHandler={this.handleTermSelect}
                                    searchResultHandler={this.handleFileSearchResults}
                                    loggedIn={loggedIn}
                                />
                                <CartSearchResults elements={cartElements} currentPage={this.state.currentDatasetResultsPage} activeCart={activeCart} loggedIn={loggedIn} />
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
    cart: PropTypes.array.isRequired,
    /** Cart as it exists in the database */
    savedCartObj: PropTypes.object,
    /** True if user has logged in */
    loggedIn: PropTypes.bool,
};

CartComponent.defaultProps = {
    savedCartObj: null,
    loggedIn: false,
};

const mapStateToProps = (state, ownProps) => ({
    cart: state.cart,
    savedCartObj: state.savedCartObj,
    context: ownProps.context,
    loggedIn: ownProps.loggedIn,
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

contentViews.register(Cart, 'cart-view'); // /cart-view/ URI
contentViews.register(Cart, 'Cart'); // /carts/<uuid> URI
