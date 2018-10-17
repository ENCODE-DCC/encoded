/**
 * Displays the button displayed at the top of search result pages that lets the user add all
 * results to the cart.
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
class CartAddAllComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            /** True if search results total more than maximum number of elements while not logged in */
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
                const adminUser = !!(this.props.sessionProperties && this.props.sessionProperties.admin);
                const elementsForCart = results['@graph'].map(result => result['@id']);
                if (!adminUser) {
                    // Not logged in, so test whether the merged new and existing carts would have
                    // more elements than allowed in a logged-out cart. Display an error modal if
                    // that happens.
                    const margedCarts = mergeCarts(this.props.cart, elementsForCart);
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
        const { inProgress } = this.props;
        return (
            <span>
                <button
                    disabled={inProgress}
                    className="btn btn-info btn-sm"
                    onClick={this.handleClick}
                    title="Add all experiments in search results to cart"
                >
                    Add all items to cart
                </button>
                {this.state.overMaximumError ?
                    <MaximumElementsLoggedoutModal closeClickHandler={this.handleErrorModalClose} />
                : null}
            </span>
        );
    }
}

CartAddAllComponent.propTypes = {
    /** Existing cart contents before adding new items */
    cart: PropTypes.array.isRequired,
    /** Search result object of elements to add to cart */
    searchResults: PropTypes.object.isRequired,
    /** True if cart updating operation is in progress */
    inProgress: PropTypes.bool,
    /** Function to call when Add All clicked */
    addAllResults: PropTypes.func.isRequired,
    /** Function to indicate cart operation in progress */
    setInProgress: PropTypes.func.isRequired,
    /** Logged-in user information */
    sessionProperties: PropTypes.object,
};

CartAddAllComponent.defaultProps = {
    inProgress: false,
    sessionProperties: null,
};

const mapStateToProps = (state, ownProps) => ({ cart: state.cart, inProgress: state.inProgress, searchResults: ownProps.searchResults, sessionProperties: ownProps.sessionProperties });
const mapDispatchToProps = (dispatch, ownProps) => ({
    addAllResults: elementsForCart => dispatch(addMultipleToCartAndSave(elementsForCart, ownProps.sessionProperties.user, ownProps.sessionProperties.admin, ownProps.fetch)),
    setInProgress: enable => dispatch(cartOperationInProgress(enable)),
});

const CartAddAllInternal = connect(mapStateToProps, mapDispatchToProps)(CartAddAllComponent);

const CartAddAll = (props, reactContext) => (
    <CartAddAllInternal searchResults={props.searchResults} sessionProperties={reactContext.session_properties} fetch={reactContext.fetch} />
);

CartAddAll.propTypes = {
    /** Search result object of elements to add to cart */
    searchResults: PropTypes.object.isRequired,
};

CartAddAll.contextTypes = {
    session_properties: PropTypes.object,
    fetch: PropTypes.func,
};

export default CartAddAll;
