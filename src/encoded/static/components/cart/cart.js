// Components for rendering the /carts/ page.
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import _ from 'underscore';
import Pager from '../../libs/bootstrap/pager';
import { Panel, PanelBody, PanelHeading } from '../../libs/bootstrap/panel';
import { contentViews, itemClass, encodedURIComponent } from '../globals';
import { requestObjects } from '../objectutils';
import { ResultTableList, BatchDownloadModal } from '../search';
import CartClear from './clear';
import CartMergeShared from './merge_shared';


/** Number of dataset items to display per page */
const PAGE_ITEM_COUNT = 25;


/**
 * Display a page of cart contents in the appearance of search results.
 */
class CartSearchResults extends React.Component {
    constructor() {
        super();
        this.state = {
            /** Carted items to display as search results; includes one page of search results */
            displayItems: [],
        };
        this.retrievePageItems = this.retrievePageItems.bind(this);
    }

    componentDidMount() {
        this.retrievePageItems();
    }

    componentDidUpdate(prevProps) {
        if (prevProps.currentPage !== this.props.currentPage || !_.isEqual(prevProps.items, this.props.items)) {
            this.retrievePageItems();
        }
    }

    /**
     * Given the whole cart items as a list of @ids as well as the currently displayed page of cart
     * contents, perform a search of a page of items.
     */
    retrievePageItems() {
        const pageStartIndex = this.props.currentPage * PAGE_ITEM_COUNT;
        const currentPageItems = this.props.items.slice(pageStartIndex, pageStartIndex + PAGE_ITEM_COUNT);
        const experimentTypeQuery = this.props.items.every(item => item.match(/^\/experiments\/.*?\/$/) !== null);
        const cartQueryString = `/search/?limit=all${experimentTypeQuery ? '&type=Experiment' : ''}`;
        requestObjects(currentPageItems, cartQueryString).then((searchResults) => {
            this.setState({ displayItems: searchResults });
        });
    }

    render() {
        return <ResultTableList results={this.state.displayItems} activeCart={this.props.activeCart} />;
    }
}

CartSearchResults.propTypes = {
    /** Array of cart item @ids */
    items: PropTypes.array,
    /** Page of results to display */
    currentPage: PropTypes.number,
    /** True if displaying an active cart */
    activeCart: PropTypes.bool,
};

CartSearchResults.defaultProps = {
    items: [],
    currentPage: 0,
    activeCart: false,
};


/**
 * Display one item of the File Format facet.
 */
class FileFormatItem extends React.Component {
    constructor() {
        super();
        this.handleFormatSelect = this.handleFormatSelect.bind(this);
    }

    /**
     * Called when a file format is selected from the facet.
     */
    handleFormatSelect() {
        this.props.formatSelectHandler(this.props.format);
    }

    render() {
        const { format, termCount, totalTermCount, selected } = this.props;
        const barStyle = {
            width: `${Math.ceil((termCount / totalTermCount) * 100)}%`,
        };
        return (
            <li className={`facet-term${selected ? ' selected' : ''}`}>
                <button onClick={this.handleFormatSelect} aria-label={`${format} with count ${termCount}`}>
                    <div className="facet-term__item">
                        <div className="facet-term__text"><span>{format}</span></div>
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

FileFormatItem.propTypes = {
    /** File format this button displays */
    format: PropTypes.string.isRequired,
    /** Number of files matching this item's format */
    termCount: PropTypes.number.isRequired,
    /** Total number of files in the item's facet */
    totalTermCount: PropTypes.number.isRequired,
    /** True if this term should appear selected */
    selected: PropTypes.bool,
    /** Callback for handling clicks in a file format button */
    formatSelectHandler: PropTypes.func.isRequired,
};

FileFormatItem.defaultProps = {
    selected: false,
};


/**
 * Request a search of files whose datasets match those in `items`.
 * @param {array} items `@id`s of file datasets to request for a facet
 * @param {func} fetch System fetch function
 * @return {object} Promise with search result object
 */
const requestFacet = (items, fetch) => (
    fetch('/search_items/type=File&restricted!=true&limit=0&filterresponse=off', {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            dataset: items,
        }),
    }).then(response => (
        response.ok ? response.json() : null
    ))
);


/**
 * Adds facet term counts and totals from one facet of a search result object to the corresponding
 * `accumulatedResults` facet.
 * @param {object} accumulatedResults Mutated search results object that gets its facet term counts
 *                                    updated.
 * @param {object} currentResults Search results object to add to `accumulatedResults`.
 * @param {string} facetField Facet field value whose term counts are to be added to
 *                            `accumulatedResults`.
 * @param {object} cachedAccumulatedFacet Saved facet object within accumulatedResults. Pass in the
 *                                        value returned by this function. Saves time so calls
 *                                        after the first don't need to search for the same object
 *                                        over and over.
 */
const addToAccumulatedFacets = (accumulatedResults, currentResults, facetField, cachedAccumulatedFacet) => {
    const accumulatedFacet = cachedAccumulatedFacet || accumulatedResults.facets.find(facet => facet.field === facetField);
    const currentFacet = currentResults.facets.find(facet => facet.field === facetField);
    accumulatedFacet.total += currentFacet.total;
    currentFacet.terms.forEach((currentTerm) => {
        const matchingAccumulatedTerm = accumulatedFacet.terms.find(accumulatedTerm => accumulatedTerm.key === currentTerm.key);
        if (matchingAccumulatedTerm) {
            matchingAccumulatedTerm.doc_count += currentTerm.doc_count;
        } else {
            accumulatedFacet.terms.push(currentTerm);
        }
    });
    return accumulatedFacet;
};


/**
 * Display the file format facet.
 */
class FileFormatFacet extends React.Component {
    constructor() {
        super();
        this.state = {
            /** file_format facet from search results */
            fileFormatFacet: null,
            /** Tracks facet loading progress */
            facetLoadProgress: -1,
        };
        this.retrieveFileFacets = this.retrieveFileFacets.bind(this);
    }

    componentDidMount() {
        this.retrieveFileFacets();
    }

    componentDidUpdate(prevProps) {
        if (prevProps.items.length !== this.props.items.length || !_.isEqual(prevProps.items, this.props.items)) {
            this.retrieveFileFacets();
        }
    }

    /**
     * Perform a special search to get just the facet information for files associated with cart
     * items. The cart items are passed in the JSON body of the POST. No search results get
     * returned but we do get file facet information.
     */
    retrieveFileFacets() {
        // Break incoming array of experiment @ids into manageable chunks of arrays, each with
        // CHUNK_SIZE items. Each chunk gets used in a search of files, and all the results get
        // combined into one facet object.
        const CHUNK_SIZE = 500;
        const chunks = [];
        for (let itemIndex = 0; itemIndex < this.props.items.length; itemIndex += CHUNK_SIZE) {
            chunks.push(this.props.items.slice(itemIndex, itemIndex + CHUNK_SIZE));
        }

        // Using the arrays of dataset @id arrays, do a sequence of searches of CHUNK_SIZE datasets
        // adding the totals together to form the final facet.
        chunks.reduce((promiseChain, currentChunk, currentChunkIndex) => (
            promiseChain.then(accumulatedResults => (
                requestFacet(currentChunk, this.context.fetch).then((currentResults) => {
                    this.setState({ facetLoadProgress: Math.round((currentChunkIndex / chunks.length) * 100) });
                    if (accumulatedResults) {
                        accumulatedResults.total += currentResults.total;
                        addToAccumulatedFacets(accumulatedResults, currentResults, 'file_format');
                        return accumulatedResults;
                    }
                    return currentResults;
                })
            ))
        ), Promise.resolve(null)).then((results) => {
            // `results` holds the accumulated results of completing all facet requests.
            const fileFormatFacet = results.facets.find(facet => facet.field === 'file_format');
            fileFormatFacet.terms = fileFormatFacet.terms.sort((a, b) => b.doc_count - a.doc_count);
            this.setState({ fileFormatFacet, facetLoadProgress: -1 });
        });
    }

    render() {
        const { selectedFormats, formatSelectHandler } = this.props;
        const { fileFormatFacet } = this.state;
        return (
            <div className="box facets">
                {fileFormatFacet ?
                    <div className="facet">
                        <h5>{fileFormatFacet.title}</h5>
                        <ul className="facet-list nav">
                            {fileFormatFacet.terms.map(term => (
                                <div key={term.key}>
                                    {term.doc_count > 0 ?
                                        <FileFormatItem
                                            format={term.key}
                                            termCount={term.doc_count}
                                            totalTermCount={fileFormatFacet.total}
                                            selected={selectedFormats.indexOf(term.key) > -1}
                                            formatSelectHandler={formatSelectHandler}
                                        />
                                    : null}
                                </div>
                            ))}
                        </ul>
                    </div>
                :
                    <progress value={this.state.facetLoadProgress} max="100" />
                }
            </div>
        );
    }
}

FileFormatFacet.propTypes = {
    /** Array of @ids of all items in the cart */
    items: PropTypes.array,
    /** Array of file formats to include in rendered lists, or [] to render all */
    selectedFormats: PropTypes.array,
    /** Callback when the user clicks on a file format facet item */
    formatSelectHandler: PropTypes.func.isRequired,
};

FileFormatFacet.defaultProps = {
    items: [],
    selectedFormats: [],
};

FileFormatFacet.contextTypes = {
    fetch: PropTypes.func,
};


/**
 * Display cart tool buttons.
 */
class CartTools extends React.Component {
    constructor() {
        super();
        this.batchDownload = this.batchDownload.bind(this);
    }

    batchDownload() {
        let contentDisposition;

        // Form query string from currently selected file formats.
        const fileFormatQuery = this.props.selectedFormats.map(format => `files.file_type=${encodedURIComponent(format)}`).join('&');

        // Initiate a batch download as a POST, passing it all dataset @ids in the payload.
        this.context.fetch(`/batch_download/type=Experiment${fileFormatQuery ? `&${fileFormatQuery}` : ''}`, {
            method: 'POST',
            headers: {
                Accept: 'text/plain',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                items: this.props.items,
            }),
        }).then((response) => {
            if (response.ok) {
                contentDisposition = response.headers.get('content-disposition');
                return response.blob();
            }
            return Promise.reject(new Error(response.statusText));
        }).then((blob) => {
            // Extract filename from batch_download response content disposition tag.
            const matchResults = contentDisposition.match(/filename="(.*?)"/);
            const filename = matchResults ? matchResults[1] : 'files.txt';

            // Make a temporary link in the DOM with the URL from the response blob and then
            // click the link to automatically download the file. Many references to the technique
            // including https://blog.jayway.com/2017/07/13/open-pdf-downloaded-api-javascript/
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }).catch((err) => {
            console.warn('batchDownload error %s:%s', err.name, err.message);
        });
    }

    render() {
        const { items, activeCart, sharedCart } = this.props;

        return (
            <div className="cart__tools">
                {items.length > 0 ? <BatchDownloadModal handleDownloadClick={this.batchDownload} /> : null}
                <CartMergeShared sharedCartObj={sharedCart} />
                {activeCart ? <CartClear /> : null}
            </div>
        );
    }
}

CartTools.propTypes = {
    /** Cart items */
    items: PropTypes.array,
    /** Selected file formats */
    selectedFormats: PropTypes.array,
    /** True if cart is active, False if cart is shared */
    activeCart: PropTypes.bool,
    /** Items in the shared cart, if that's being displayed */
    sharedCart: PropTypes.object,
};

CartTools.defaultProps = {
    items: [],
    selectedFormats: [],
    activeCart: true,
    sharedCart: null,
};

CartTools.contextTypes = {
    fetch: PropTypes.func,
};


/**
 * Display the total number of cart items.
 */
const ItemCountArea = ({ itemCount, itemName, itemNamePlural }) => {
    if (itemCount > 0) {
        return (
            <div className="cart__item-count">
                {itemCount}&nbsp;{itemCount === 1 ? itemName : itemNamePlural}
            </div>
        );
    }
    return null;
};

ItemCountArea.propTypes = {
    itemCount: PropTypes.number.isRequired, // Number of items in cart display
    itemName: PropTypes.string.isRequired, // Singular name of item being displayed
    itemNamePlural: PropTypes.string.isRequired, // Plural name of item being displayed
};


/**
 * Display the pager control area.
 */
const PagerArea = ({ currentPage, totalPageCount, updateCurrentPage }) => {
    if (totalPageCount > 1) {
        return (
            <div className="cart__pager">
                <Pager total={totalPageCount} current={currentPage} updateCurrentPage={updateCurrentPage} />
            </div>
        );
    }
    return null;
};

PagerArea.propTypes = {
    /** Zero-based current page to display */
    currentPage: PropTypes.number.isRequired,
    /** Total number of pages */
    totalPageCount: PropTypes.number.isRequired,
    /** Called when user clicks pager controls */
    updateCurrentPage: PropTypes.func.isRequired,
};


/**
 * Renders the cart search results page. Display either:
 * 1. Shared cart (/carts/<uuid>) containing a user's saved items
 * 2. Active cart (/cart-view/) containing saved and in-memory items
 */
class CartComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            /** Files formats selected to be included in results; all formats if empty array */
            selectedFormats: [],
            /** Currently displayed page of dataset search results */
            currentDatasetResultsPage: 0,
        };
        this.handleFormatSelect = this.handleFormatSelect.bind(this);
        this.updateDatasetCurrentPage = this.updateDatasetCurrentPage.bind(this);
    }

    /**
     * Called when the given file format was selected or deselected in the facet.
     * @param {string} format File format facet item that was clicked
     */
    handleFormatSelect(format) {
        const matchingIndex = this.state.selectedFormats.indexOf(format);
        if (matchingIndex === -1) {
            // Selected file format not in the list of included formats, so add it.
            this.setState(prevState => ({
                selectedFormats: prevState.selectedFormats.concat([format]),
                currentFileResultsPage: 0,
            }));
        } else {
            // Selected file format is in the list of included formats, so remove it.
            this.setState(prevState => ({
                selectedFormats: prevState.selectedFormats.filter(includedFormat => includedFormat !== format),
                currentFileResultsPage: 0,
            }));
        }
    }

    /**
     * Called when the user selects a new page of cart items to view.
     * @param {number} newCurrent New current page to view; zero based
     */
    updateDatasetCurrentPage(newCurrent) {
        this.setState({ currentDatasetResultsPage: newCurrent });
    }

    render() {
        const { context, cart } = this.props;

        // Active and shared carts displayed slightly differently. Active carts' contents come from
        // the in-memory Redux store while shared carts' contents come from the cart object `items`
        // property.
        const activeCart = context['@type'][0] === 'cart-view';
        const cartItems = activeCart ? cart : context.items;
        const totalDatasetPages = Math.floor(cartItems.length / PAGE_ITEM_COUNT) + (cartItems.length % PAGE_ITEM_COUNT !== 0 ? 1 : 0);

        return (
            <div className={itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>Cart</h2>
                    </div>
                </header>
                <Panel addClasses="cart__result-table">
                    <PanelHeading addClasses="cart__header">
                        <PagerArea currentPage={this.state.currentDatasetResultsPage} totalPageCount={totalDatasetPages} updateCurrentPage={this.updateDatasetCurrentPage} />
                        <CartTools items={cartItems} selectedFormats={this.state.selectedFormats} activeCart={activeCart} sharedCart={context} />
                    </PanelHeading>
                    <ItemCountArea itemCount={cartItems.length} itemName="dataset" itemNamePlural="datasets" />
                    <PanelBody>
                        {cartItems.length > 0 ?
                            <div className="cart__display">
                                <FileFormatFacet items={cartItems} selectedFormats={this.state.selectedFormats} formatSelectHandler={this.handleFormatSelect} />
                                <CartSearchResults items={cartItems} currentPage={this.state.currentDatasetResultsPage} activeCart={activeCart} />
                            </div>
                        :
                            <p className="cart__empty-message">
                                Empty cart
                            </p>
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
    /** System fetch function */
};

const mapStateToProps = (state, ownProps) => ({
    cart: state.cart,
    context: ownProps.context,
});

const CartInternal = connect(mapStateToProps)(CartComponent);


const Cart = (props, reactContext) => (
    <CartInternal context={props.context} fetch={reactContext.fetch} />
);

Cart.propTypes = {
    context: PropTypes.object.isRequired,
};

contentViews.register(Cart, 'cart-view'); // /cart-view/ URI
contentViews.register(Cart, 'Cart'); // /carts/<uuid> URI
