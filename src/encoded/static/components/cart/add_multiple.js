/**
 * Displays the button at the top of search result pages that lets the user add all results to the
 * cart.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { addMultipleToCartAndSave, cartOperationInProgress } from './actions';
import { encodedURIComponent } from '../globals';
import { requestSearch } from '../objectutils';
import { MaximumElementsLoggedoutModal, CART_MAXIMUM_ELEMENTS_LOGGEDOUT, getAllowedCartTypes, mergeCarts } from './util';

/**
 * Button to add all qualifying elements to the user's cart.
 */
class CartAddAllSearchComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            /** True if search results total more than maximum # of elements while not logged in */
            overMaximumError: false,
        };
        this.handleClick = this.handleClick.bind(this);
        this.handleErrorModalClose = this.handleErrorModalClose.bind(this);
    }

    /**
     * Handle a click in the Add All button by doing a search of elements allowed in carts to get
     * all their @ids that we can add to the cart.
     */
    handleClick() {
        // Get the array of object types in the cart and remove any types found in the filter
        // array of the current search results. Also make a copy of the current search results
        // including only the properties we need to avoid mutating a prop.
        const allowedTypes = getAllowedCartTypes();
        const queryFilters = [];
        this.props.searchResults.filters.forEach((filter) => {
            // Copy all filter fields and terms to our array of filters used for the query, except
            // any 'type=something' terms for types not allowed in carts.
            if (filter.field !== 'type' || allowedTypes.indexOf(filter.term) !== -1) {
                queryFilters.push({ field: filter.field, term: filter.term });
            }

            // If the filter is for a type allowed in the cart, remove it from the allowedTypes
            // list as we don't need to add it later.
            if (filter.field === 'type') {
                const index = allowedTypes.indexOf(filter.term);
                if (index !== -1) {
                    allowedTypes.splice(index, 1);
                }
            }
        });

        // Add a partial filter entry for any types not included in the current search result
        // filters.
        allowedTypes.forEach((type) => {
            queryFilters.push({ field: 'type', term: type });
        });

        // Use the existing query plus any cartable object types to search for all @ids to add to
        // the cart.
        const searchQuery = `${queryFilters.map(element => (
            `${element.field}=${encodedURIComponent(element.term)}`
        )).join('&')}&limit=all&field=%40id`;
        this.props.setInProgress(true);
        requestSearch(searchQuery).then((results) => {
            this.props.setInProgress(false);
            if (Object.keys(results).length > 0 && results['@graph'].length > 0) {
                const loggedIn = !!(this.props.session && this.props.session['auth.userid']);
                const elementsForCart = results['@graph'].map(result => result['@id']);
                if (!loggedIn) {
                    // Not logged in, so test whether the merged new and existing carts would have
                    // more elements than allowed in a logged-out cart. Display an error modal if
                    // that happens.
                    const margedCarts = mergeCarts(this.props.elements, elementsForCart);
                    if (margedCarts.length > CART_MAXIMUM_ELEMENTS_LOGGEDOUT) {
                        this.setState({ overMaximumError: true });
                        return;
                    }
                }
                this.props.addAllResults(elementsForCart);
            }
        });
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
            <span>
                <button
                    disabled={inProgress}
                    className="btn btn-info btn-sm"
                    onClick={this.handleClick}
                    title={`Add all patients in search results to cohort${cartName ? `: ${cartName}` : ''}`}
                >
                    Add all items to cohort
                </button>
                {this.state.overMaximumError ?
                    <MaximumElementsLoggedoutModal closeClickHandler={this.handleErrorModalClose} />
                : null}
            </span>
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
class CartAddAllElementsComponent extends React.Component {
    constructor() {
        super();
        this.handleClick = this.handleClick.bind(this);
    }

    /**
     * Handle a click in the button to add all datasets from a list to the current cart.
     */
    handleClick() {
        const elementAtIds = this.props.elements.map(element => element['@id']);
        this.props.addAllResults(elementAtIds);
    }

    render() {
        const { savedCartObj, inProgress } = this.props;
        const cartName = (savedCartObj && Object.keys(savedCartObj).length > 0 ? savedCartObj.name : '');
        return (
            <div className="cart__add-all-element-control">
                <button
                    disabled={inProgress}
                    className="btn btn-info btn-sm"
                    onClick={this.handleClick}
                    title={`Add all related patients to cohort${cartName ? `: ${cartName}` : ''}`}
                >
                    Add all items to cohort
                </button>
            </div>
        );
    }
}

CartAddAllElementsComponent.propTypes = {
    /** Current cart saved object */
    savedCartObj: PropTypes.object,
    /** New elements to add to cart as array of dataset objects */
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
    /** New elements to add to cart as array of dataset objects */
    elements: PropTypes.array,
};

CartAddAllElements.defaultProps = {
    elements: [],
};

CartAddAllElements.contextTypes = {
    session: PropTypes.object,
    fetch: PropTypes.func,
};
