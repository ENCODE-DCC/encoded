import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { parseAndLogError } from '../globals';
import cartCacheSaved from './cache_saved';
import cartSetOperationInProgress from './in_progress';


/**
 * Update the cart object in the DB. You must provide `cartAtId` because `cart` cannot have non-
 * writeable properties in it, and @id is one of several non-writeable properites. You normally
 * get an object with no non-writeable properties by doing a GET request on that object with
 * "frame=edit" in the query string.
 *
 * @param {object} cart - cart object to update; must be editable version (no @id etc)
 * @param {string} cartAtId - @id of the cart object to update
 * @param {func} fetch - system-wide fetch operation
 * @return {object} - Promise containing array of carts for logged-in user
 */
const updateCartObject = (cart, cartAtId, fetch) => (
    fetch(cartAtId, {
        method: 'PUT',
        body: JSON.stringify(cart),
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        },
    }).then((response) => {
        if (!response.ok) {
            throw response;
        }
        return response.json();
    }).then(result => (
        result['@graph'][0]
    )).catch(parseAndLogError.bind('Update cart', 'putRequest'))
);


/**
 * Get a writeable version of the cart object specified by `cartAtId`.
 *
 * @param {string} cartAtId - @id of the cart object to retrieve
 * @param {func} fetch - system-wide fetch operation
 * @return {object} - Promise containing the retrieved cart object, or an error response
 */
const getWriteableCartObject = (cartAtId, fetch) => (
    fetch(`${cartAtId}?frame=edit`, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
        },
    }).then((response) => {
        if (!response.ok) {
            throw response;
        }
        return response.json();
    }).catch(parseAndLogError.bind('Get writeable cart', 'getRequest'))
);


/**
 * Create a new object in the DB for the given cart object and user.
 *
 * @param {object} cart - current cart object to be saved
 * @param {object} user - current logged-in user's object
 * @param {func} fetch - system-wide fetch operation
 */
const createCartObject = (cart, user, fetch) => {
    const writeableCart = {
        name: `${user.title} cart`,
        items: cart,
        submitted_by: user['@id'],
        status: 'current',
    };
    return fetch('/carts/', {
        method: 'POST',
        body: JSON.stringify(writeableCart),
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        },
    }).then((response) => {
        if (!response.ok) {
            throw response;
        }
        return response.json();
    }).then(result => result['@graph'][0]);
};


/**
 * Save the in-memory cart to the database. The user object has the @id of the user's cart, but not
 * the cart object itself which must be provided in `savedCartObj`.
 *
 * @param {array} cart Array of @ids contained with the in-memory cart to be saved
 * @param {object} savedCartObj User's saved cart object
 * @param {user} user User object normally retrieved from session_properties
 * @param {func} fetch System fetch function; usually from <App> context
 * @return {object} Promise for creating or updating the cart object
 */
export const cartSave = (cart, savedCartObj, user, fetch) => {
    const cartAtId = savedCartObj && savedCartObj['@id'];
    if (cartAtId) {
        return getWriteableCartObject(cartAtId, fetch).then((writeableCart) => {
            // Copy the in-memory cart to the writeable cart object and then update it in the DB.
            writeableCart.items = cart;
            return updateCartObject(writeableCart, cartAtId, fetch);
        });
    }

    // No user cart. Make one from scratch and save it.
    return createCartObject(cart, user, fetch);
};


// Renders and reacts to the button to save a cart to the DB.
class CartSaveComponent extends React.Component {
    constructor() {
        super();
        this.saveCartClick = this.saveCartClick.bind(this);
    }

    saveCartClick() {
        this.props.onSaveCartClick(this.props.cart, this.props.savedCartObj, this.props.user, this.props.fetch);
    }

    render() {
        if (this.props.user) {
            return <button className="btn btn-info btn-sm cart__save-button" onClick={this.saveCartClick}>Save cart</button>;
        }
        return null;
    }
}

CartSaveComponent.propTypes = {
    cart: PropTypes.array.isRequired, // In-memory cart from redux store
    savedCartObj: PropTypes.object, // Cached saved cart items
    user: PropTypes.object, // Logged-in user object
    onSaveCartClick: PropTypes.func.isRequired, // Function to call when "Save cart" clicked
    fetch: PropTypes.func.isRequired, // fetch function from App context
};

CartSaveComponent.defaultProps = {
    savedCartObj: null,
    user: null,
};

const mapStateToProps = (state, ownProps) => ({
    cart: state.cart,
    savedCartObj: state.savedCartObj,
    user: ownProps.sessionProperties.user,
    fetch: ownProps.fetch,
    fetchSessionProperties: ownProps.fetchSessionProperties,
});
const mapDispatchToProps = dispatch => (
    {
        onSaveCartClick: (cart, savedCartObj, user, fetch) => {
            cartSetOperationInProgress(true);
            return cartSave(cart, savedCartObj, user, fetch).then((updatedSavedCartObj) => {
                cartCacheSaved(updatedSavedCartObj, dispatch);
                // cartSetOperationInProgress(false);
            });
        },
    }
);

const CartSaveInternal = connect(mapStateToProps, mapDispatchToProps)(CartSaveComponent);


const CartSave = (props, reactContext) => (
    <CartSaveInternal sessionProperties={reactContext.session_properties} fetch={reactContext.fetch} />
);

CartSave.contextTypes = {
    session_properties: PropTypes.object.isRequired,
    fetch: PropTypes.func.isRequired,
};

export default CartSave;
