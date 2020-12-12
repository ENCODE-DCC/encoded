/**
 * Displays the button at the top of search result pages that lets the user add all results to the
 * cart.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import url from 'url';
import QueryString from '../../libs/query_string';
import { atIdToType, truncateString } from '../globals';
import { requestSearch } from '../objectutils';
import { addMultipleToCartAndSave, cartOperationInProgress, triggerAlert } from './actions';
import CartLoggedOutWarning, { useLoggedOutWarning } from './loggedout_warning';
import CartMaxElementsWarning from './max_elements_warning';
import {
    cartGetAllowedTypes,
    cartGetAllowedObjectPathTypes,
    CART_MAX_ELEMENTS,
    mergeCarts,
} from './util';

/**
 * Button to add all qualifying elements to the user's cart.
 */
const CartAddAllSearchComponent = ({
    savedCartObj,
    searchResults,
    inProgress,
    addAllResults,
    setInProgress,
    loggedIn,
    showMaxElementsWarning,
}) => {
    /** Get hooks for the logged-out warning modal */
    const [loggedOutWarningStates, loggedOutWarningActions] = useLoggedOutWarning(false);

    /**
     * Handle a click in the Add All button by doing a search of elements allowed in carts to get
     * all their @ids that we can add to the cart.
     */
    const handleClick = () => {
        if (loggedIn) {
            // Don't use existing search results as they might only include 25 results and we need all
            // of them. Do the same search but with limit=all and field=@id.
            const parsedUrl = url.parse(searchResults['@id']);
            const query = new QueryString(parsedUrl.query);
            query.replaceKeyValue('limit', 'all').addKeyValue('field', '@id');
            const searchQuery = query.format();

            // With the updated query string, perform the search of all @ids matching the current
            // search.
            setInProgress(true);
            requestSearch(searchQuery).then((results) => {
                setInProgress(false);
                if (Object.keys(results).length > 0 && results['@graph'].length > 0) {
                    const allowedTypes = cartGetAllowedTypes();

                    // Get all elements from results that qualify to exist in carts.
                    const elementsForCart = results['@graph'].filter(result => allowedTypes.includes(result['@type'][0])).map(result => result['@id']);

                    // Check whether the final cart would have more elements than allowed by doing a
                    // trial merge. If the merged cart fits under the limit, add the new elements
                    // to the cart.
                    const mergedElements = mergeCarts(savedCartObj.elements, elementsForCart);
                    if (mergedElements.length > CART_MAX_ELEMENTS) {
                        showMaxElementsWarning();
                    } else if (elementsForCart.length > 0) {
                        addAllResults(elementsForCart);
                    }
                }
            });
        } else {
            // The user hasn't logged in, so show a modal that allows them to.
            loggedOutWarningActions.setIsWarningVisible(true);
        }
    };

    if (savedCartObj) {
        const cartName = Object.keys(savedCartObj).length > 0 ? savedCartObj.name : '';
        return (
            <div className="cart-add-all">
                {savedCartObj.name ? <div className="cart-toggle__name">{truncateString(savedCartObj.name, 22)}</div> : null}
                <button
                    disabled={inProgress || savedCartObj.locked}
                    className="btn btn-info btn-sm"
                    onClick={handleClick}
                    title={`Add all datasets in search results to cart${cartName ? `: ${cartName}` : ''}`}
                >
                    Add all items to cart
                </button>
                {loggedOutWarningStates.isWarningVisible ? <CartLoggedOutWarning closeModalHandler={loggedOutWarningActions.handleCloseWarning} /> : null}
            </div>
        );
    }
    return null;
};

CartAddAllSearchComponent.propTypes = {
    /** Current cart saved object */
    savedCartObj: PropTypes.object,
    /** Search result object of elements to add to cart */
    searchResults: PropTypes.object.isRequired,
    /** True if cart-updating operation is in progress */
    inProgress: PropTypes.bool,
    /** Function to call when Add All clicked */
    addAllResults: PropTypes.func.isRequired,
    /** Function to indicate cart operation in progress */
    setInProgress: PropTypes.func.isRequired,
    /** True if user has logged in */
    loggedIn: PropTypes.bool.isRequired,
    /** Call to show the max elements warning alert */
    showMaxElementsWarning: PropTypes.func.isRequired,
};

CartAddAllSearchComponent.defaultProps = {
    inProgress: false,
    savedCartObj: null,
};

CartAddAllSearchComponent.mapStateToProps = (state, ownProps) => ({
    elements: state.elements,
    savedCartObj: state.savedCartObj,
    inProgress: state.inProgress,
    searchResults: ownProps.searchResults,
    loggedIn: ownProps.loggedIn,
});
CartAddAllSearchComponent.mapDispatchToProps = (dispatch, ownProps) => ({
    addAllResults: elementsForCart => dispatch(addMultipleToCartAndSave(elementsForCart, ownProps.fetch)),
    setInProgress: enable => dispatch(cartOperationInProgress(enable)),
    showMaxElementsWarning: () => dispatch(triggerAlert(<CartMaxElementsWarning />)),
});

const CartAddAllSearchInternal = connect(CartAddAllSearchComponent.mapStateToProps, CartAddAllSearchComponent.mapDispatchToProps)(CartAddAllSearchComponent);

export const CartAddAllSearch = (props, reactContext) => (
    <CartAddAllSearchInternal searchResults={props.searchResults} fetch={reactContext.fetch} loggedIn={!!(reactContext.session && reactContext.session['auth.userid'])} />
);

CartAddAllSearch.propTypes = {
    /** Search result object of elements to add to cart */
    searchResults: PropTypes.object.isRequired,
};

CartAddAllSearch.contextTypes = {
    fetch: PropTypes.func,
    session: PropTypes.object,
};


/**
 * Renders a button to add all elements from an array of dataset objects to the current cart.
 */
const CartAddAllElementsComponent = ({
    savedCartObj,
    elements,
    inProgress,
    addAllResults,
    loggedIn,
    showMaxElementsWarning,
}) => {
    /** Get hooks for the logged-out warning modal */
    const [loggedOutWarningStates, loggedOutWarningActions] = useLoggedOutWarning(false);

    /**
     * Handle a click in the button to add all datasets from a list to the current cart.
     */
    const handleClick = () => {
        if (loggedIn) {
            // Filter the added elements to those allowed in carts.
            const allowedPathTypes = cartGetAllowedObjectPathTypes();
            const allowedElements = elements.filter(element => (
                allowedPathTypes.includes(atIdToType(element))
            ));

            // Add the allowed elements to the cart.
            if (allowedElements.length > 0) {
                // Check whether the final cart would have more elements than allowed by doing a
                // trial merge. If the merged cart fits under the limit, add the new elements to
                // the cart.
                const mergedElements = mergeCarts(savedCartObj.elements, allowedElements);
                if (mergedElements.length > CART_MAX_ELEMENTS) {
                    showMaxElementsWarning();
                } else {
                    addAllResults(allowedElements);
                }
            }
        } else {
            // The user hasn't logged in, so show a modal that allows them to.
            loggedOutWarningActions.setIsWarningVisible(true);
        }
    };

    const cartName = (savedCartObj && Object.keys(savedCartObj).length > 0 ? savedCartObj.name : '');
    return (
        <div className="cart-add-all">
            {savedCartObj && savedCartObj.name ? <div className="cart-toggle__name">{truncateString(savedCartObj.name, 22)}</div> : null}
            <button
                disabled={inProgress || (savedCartObj && savedCartObj.locked)}
                className="btn btn-info btn-sm"
                onClick={handleClick}
                title={`Add all related experiments to cart${cartName ? `: ${cartName}` : ''}`}
            >
                Add all items to cart
            </button>
            {loggedOutWarningStates.isWarningVisible ? <CartLoggedOutWarning closeModalHandler={loggedOutWarningActions.handleCloseWarning} /> : null}
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
    /** True if user has logged in */
    loggedIn: PropTypes.bool.isRequired,
    /** Call to show the max elements warning alert */
    showMaxElementsWarning: PropTypes.func.isRequired,
};

CartAddAllElementsComponent.defaultProps = {
    savedCartObj: null,
};

CartAddAllElementsComponent.mapStateToProps = (state, ownProps) => ({
    savedCartObj: state.savedCartObj,
    elements: ownProps.elements,
    inProgress: state.inProgress,
    loggedIn: ownProps.loggedIn,
});

CartAddAllElementsComponent.mapDispatchToProps = (dispatch, ownProps) => ({
    addAllResults: elements => dispatch(addMultipleToCartAndSave(elements, ownProps.fetch)),
    showMaxElementsWarning: () => dispatch(triggerAlert(<CartMaxElementsWarning />)),
});

const CartAddAllElementsInternal = connect(CartAddAllElementsComponent.mapStateToProps, CartAddAllElementsComponent.mapDispatchToProps)(CartAddAllElementsComponent);


// Public component used to bind to context properties.
export const CartAddAllElements = ({ elements }, reactContext) => (
    <CartAddAllElementsInternal elements={elements} fetch={reactContext.fetch} loggedIn={!!(reactContext.session && reactContext.session['auth.userid'])} />
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
