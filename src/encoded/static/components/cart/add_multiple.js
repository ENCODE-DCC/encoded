import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { addMultipleToCartAndSave, cartOperationInProgress } from './actions';
import { encodedURIComponent } from '../globals';
import { requestSearch } from '../objectutils';
import { MaximumElementsLoggedoutModal, CART_MAXIMUM_ELEMENTS_LOGGEDOUT } from './util';

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
     * Handle a click in the Add All button by doing a search of qualifying elements to get all
     * their @ids that we can add to the cart.
     */
    handleClick() {
        const loggedIn = this.props.session && this.props.session['auth.userid'];
        if (!loggedIn && this.props.searchResults.total > CART_MAXIMUM_ELEMENTS_LOGGEDOUT) {
            // User is logged out and requested more than the maximum allowed elements in the cart,
            // so how an error alert.
            this.setState({ overMaximumError: true });
        } else {
            const searchQuery = `${this.props.searchResults.filters.map(element => (
                `${element.field}=${encodedURIComponent(element.term)}`
            )).join('&')}&limit=all&field=%40id`;
            this.props.setInProgress(true);
            requestSearch(searchQuery).then((results) => {
                this.props.setInProgress(false);
                if (Object.keys(results).length > 0 && results['@graph'].length > 0) {
                    const elementsForCart = results['@graph'].map(result => result['@id']);
                    this.props.addAllResults(elementsForCart);
                }
            });
        }
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
                <button disabled={inProgress} className="btn btn-info btn-sm" onClick={this.handleClick}>Add all items to cart</button>
                {this.state.overMaximumError ?
                    <MaximumElementsLoggedoutModal closeClickHandler={this.handleErrorModalClose} />
                : null}
            </span>
        );
    }
}

CartAddAllComponent.propTypes = {
    /** Search result object of elements to add to cart */
    searchResults: PropTypes.object.isRequired,
    /** True if cart updating operation is in progress */
    inProgress: PropTypes.bool,
    /** Function to call when Add All clicked */
    addAllResults: PropTypes.func.isRequired,
    /** Function to indicate cart operation in progress */
    setInProgress: PropTypes.func.isRequired,
    /** Login session information */
    session: PropTypes.object,
};

CartAddAllComponent.defaultProps = {
    inProgress: false,
    session: null,
};

const mapStateToProps = (state, ownProps) => ({ cart: state.cart, inProgress: state.inProgress, searchResults: ownProps.searchResults, session: ownProps.session });
const mapDispatchToProps = (dispatch, ownProps) => ({
    addAllResults: elementsForCart => dispatch(addMultipleToCartAndSave(elementsForCart, ownProps.sessionProperties.user, ownProps.fetch)),
    setInProgress: enable => dispatch(cartOperationInProgress(enable)),
});

const CartAddAllInternal = connect(mapStateToProps, mapDispatchToProps)(CartAddAllComponent);

const CartAddAll = (props, reactContext) => (
    <CartAddAllInternal searchResults={props.searchResults} session={reactContext.session} sessionProperties={reactContext.session_properties} fetch={reactContext.fetch} />
);

CartAddAll.propTypes = {
    /** Search result object of elements to add to cart */
    searchResults: PropTypes.object.isRequired,
};

CartAddAll.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
    fetch: PropTypes.func,
};

export default CartAddAll;
