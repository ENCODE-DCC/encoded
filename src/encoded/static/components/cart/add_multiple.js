/**
 * Displays the button at the top of search result pages that lets the user add all results to the
 * cart.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import url from 'url';
import QueryString from '../../libs/query_string';
import { addMultipleToCartAndSave, cartOperationInProgress } from './actions';
import { atIdToType } from '../globals';
import { requestSearch, Spinner } from '../objectutils';
import {
    MaximumElementsLoggedoutModal,
    CART_MAXIMUM_ELEMENTS_LOGGEDOUT,
    cartGetAllowedTypes,
    cartGetAllowedObjectPathTypes,
    mergeCarts,
} from './util';

/**
 * Button to add all qualifying elements to the user's cart.
 */
class CartAddAllSearchComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            /** True if search results total more than maximum # of elements while not logged in */
            overMaximumError: false,
            /** True to show spinner, false to hide it */
            showSpinner: false,
        };
        this.handleClick = this.handleClick.bind(this);
        this.handleErrorModalClose = this.handleErrorModalClose.bind(this);
    }

    /**
     * Handle a click in the Add All button by doing a search of elements allowed in carts to get
     * all their @ids that we can add to the cart.
     */
    handleClick() {
        // Don't use existing search results as they might only include 25 results and we need all
        // of them. Do the same search but with limit=all and field=@id.
        const parsedUrl = url.parse(this.props.searchResults['@id']);
        const query = new QueryString(parsedUrl.query);
        query.replaceKeyValue('limit', 'all').addKeyValue('field', '@id');
        const searchQuery = query.format();
        this.setState({ showSpinner: true });

        // With the updated query string, perform the search of all @ids matching the current
        // search.
        this.props.setInProgress(true);
        requestSearch(searchQuery).then((results) => {
            this.props.setInProgress(false);
            if (Object.keys(results).length > 0 && results['@graph'].length > 0) {
                const loggedIn = !!(this.props.session && this.props.session['auth.userid']);
                const allowedTypes = cartGetAllowedTypes();

                // Get all elements from results that qualify to exist in carts.
                const elementsForCart = results['@graph'].filter(result => allowedTypes.includes(result['@type'][0])).map(result => result['@id']);
                if (elementsForCart.length > 0) {
                    // We should always have elements qualified to exist in a cart because we
                    // wouldn't have shown the "Add all items to cart" button if we didn't know we
                    // had qualfied elements in the search results, but just in case.
                    if (!loggedIn) {
                        // Not logged in, so test whether the merged new and existing carts would have
                        // more elements than allowed in a logged-out cart. Display an error modal if
                        // that happens.
                        const mergedCarts = mergeCarts(this.props.elements, elementsForCart);
                        if (mergedCarts.length > CART_MAXIMUM_ELEMENTS_LOGGEDOUT) {
                            this.setState({ overMaximumError: true });
                            return;
                        }
                    }
                    this.props.addAllResults(elementsForCart);
                }
            }
        }).finally(() => { this.setState({ showSpinner: false }); });
    }

    /**
     * Called when user clicks the close button on the error modal.
     */
    handleErrorModalClose() {
        this.setState({ overMaximumError: false });
    }

    render() {
        const { savedCartObj, inProgress } = this.props;
        const cartName = (savedCartObj && Object.keys(savedCartObj).length > 0 ? savedCartObj.name : '');
        return (
            <React.Fragment>
                <Spinner isActive={this.state.showSpinner} />
                <button
                    disabled={inProgress || savedCartObj.locked}
                    className="btn btn-info btn-sm"
                    onClick={this.handleClick}
                    title={`Add all experiments in search results to cart${cartName ? `: ${cartName}` : ''}`}
                >
                    Add all items to cart
                </button>
                {this.state.overMaximumError ?
                    <MaximumElementsLoggedoutModal closeClickHandler={this.handleErrorModalClose} />
                : null}
            </React.Fragment>
        );
    }
}

CartAddAllSearchComponent.propTypes = {
    /** Existing cart contents before adding new items */
    elements: PropTypes.array.isRequired,
    /** Current cart saved object */
    savedCartObj: PropTypes.object,
    /** Search result object of elements to add to cart */
    searchResults: PropTypes.object.isRequired,
    /** True if cart updating operation is in progress */
    inProgress: PropTypes.bool,
    /** Function to call when Add All clicked */
    addAllResults: PropTypes.func.isRequired,
    /** Function to indicate cart operation in progress */
    setInProgress: PropTypes.func.isRequired,
    /** Logged-in user information */
    session: PropTypes.object,
};

CartAddAllSearchComponent.defaultProps = {
    inProgress: false,
    savedCartObj: null,
    session: null,
};

CartAddAllSearchComponent.mapStateToProps = (state, ownProps) => ({
    elements: state.elements,
    savedCartObj: state.savedCartObj,
    inProgress: state.inProgress,
    searchResults: ownProps.searchResults,
    session: ownProps.session,
});
CartAddAllSearchComponent.mapDispatchToProps = (dispatch, ownProps) => ({
    addAllResults: elementsForCart => dispatch(addMultipleToCartAndSave(elementsForCart, !!(ownProps.session && ownProps.session['auth.userid']), ownProps.fetch)),
    setInProgress: enable => dispatch(cartOperationInProgress(enable)),
});

const CartAddAllSearchInternal = connect(CartAddAllSearchComponent.mapStateToProps, CartAddAllSearchComponent.mapDispatchToProps)(CartAddAllSearchComponent);

export const CartAddAllSearch = (props, reactContext) => (
    <CartAddAllSearchInternal searchResults={props.searchResults} session={reactContext.session} fetch={reactContext.fetch} />
);

CartAddAllSearch.propTypes = {
    /** Search result object of elements to add to cart */
    searchResults: PropTypes.object.isRequired,
};

CartAddAllSearch.contextTypes = {
    session: PropTypes.object,
    fetch: PropTypes.func,
};


/**
 * Renders a button to add all elements from an array of dataset objects to the current cart.
 */
const CartAddAllElementsComponent = ({ savedCartObj, elements, inProgress, addAllResults }) => {
    /**
     * Handle a click in the button to add all datasets from a list to the current cart.
     */
    const handleClick = () => {
        // Filter the added elements to those allowed in carts.
        const allowedPathTypes = cartGetAllowedObjectPathTypes();
        const allowedElements = elements.filter(element => (
            allowedPathTypes.includes(atIdToType(element))
        ));

        // Add the allowed elements to the cart.
        if (allowedElements.length > 0) {
            addAllResults(allowedElements);
        }
    };

    const cartName = (savedCartObj && Object.keys(savedCartObj).length > 0 ? savedCartObj.name : '');
    return (
        <div className="cart__add-all-element-control">
            <button
                disabled={inProgress || savedCartObj.locked}
                className="btn btn-info btn-sm"
                onClick={handleClick}
                title={`Add all related experiments to cart${cartName ? `: ${cartName}` : ''}`}
            >
                Add all items to cart
            </button>
        </div>
    );
};

CartAddAllElementsComponent.propTypes = {
    /** Current cart saved object */
    savedCartObj: PropTypes.object,
    /** New elements to add to cart as array of @ids */
    elements: PropTypes.array.isRequired,
    /** True if cart updating operation is in progress */
    inProgress: PropTypes.bool.isRequired,
    /** Function to call when Add All clicked */
    addAllResults: PropTypes.func.isRequired,
};

CartAddAllElementsComponent.defaultProps = {
    savedCartObj: null,
};

CartAddAllElementsComponent.mapStateToProps = (state, ownProps) => ({
    savedCartObj: state.savedCartObj,
    elements: ownProps.elements,
    inProgress: state.inProgress,
});

CartAddAllElementsComponent.mapDispatchToProps = (dispatch, ownProps) => ({
    addAllResults: elements => dispatch(addMultipleToCartAndSave(elements, !!(ownProps.session && ownProps.session['auth.userid']), ownProps.fetch)),
});

const CartAddAllElementsInternal = connect(CartAddAllElementsComponent.mapStateToProps, CartAddAllElementsComponent.mapDispatchToProps)(CartAddAllElementsComponent);


// Public component used to bind to context properties.
export const CartAddAllElements = ({ elements }, reactContext) => (
    <CartAddAllElementsInternal elements={elements} session={reactContext.session} fetch={reactContext.fetch} />
);

CartAddAllElements.propTypes = {
    /** New elements to add to cart as array of @ids */
    elements: PropTypes.array,
};

CartAddAllElements.defaultProps = {
    elements: [],
};

CartAddAllElements.contextTypes = {
    session: PropTypes.object,
    fetch: PropTypes.func,
};
