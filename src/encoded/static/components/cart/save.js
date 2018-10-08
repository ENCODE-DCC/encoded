import { parseAndLogError } from '../globals';


/**
 * Update the current user's cart object in the DB. You must provide `cartAtId` because `cart`
 * cannot have non-writeable properties in it, and @id is one of several non-writeable properites.
 * @param {object} cart Cart object to update; must be writeable version
 * @param {string} cartAtId @id of the cart object to update
 * @param {func} fetch System-wide fetch operation
 * @return {object} Promise containing updated cart object for logged-in user
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
        if (response.ok) {
            return response.json();
        }
        throw new Error(response);
    }).then(result => (
        result['@graph'][0]
    )).catch((err) => {
        parseAndLogError.bind('Updating cart object in DB', err);
    })
);


/**
 * Get a writeable version of the cart object specified by `cartAtId` from the DB. You can mutate
 * the resulting cart object.
 * @param {string} cartAtId @id of the cart object to retrieve
 * @param {func} fetch System-wide fetch operation
 * @return {object} Promise with the retrieved cart object
 */
const getWriteableCartObject = (cartAtId, fetch) => (
    fetch(`${cartAtId}?frame=edit`, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
        },
    }).then((response) => {
        if (response.ok) {
            return response.json();
        }
        throw new Error(response);
    }).catch((err) => {
        parseAndLogError('Retrieving writeable cart object', err);
    })
);


/**
 * Create a new object in the DB for the given cart object and user.
 * @param {object} cart Current cart object to be saved
 * @param {object} user Current logged-in user's object
 * @param {func} fetch System-wide fetch operation
 * @return {object} Promise with new cart object just created
 */
const createCartObject = (cart, user, fetch) => {
    const writeableCart = {
        name: `${user.title} cart`,
        elements: cart,
        submitted_by: user['@id'],
        status: 'current',
    };
    return fetch('/carts/', {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(writeableCart),
    }).then((response) => {
        if (response.ok) {
            return response.json();
        }
        throw new Error(response);
    }).then(result => (
        result['@graph'][0]
    )).catch((err) => {
        parseAndLogError('Error creating cart object in DB', err);
    });
};


/**
 * Save the in-memory cart to the database. The user object has the @id of the user's cart, but not
 * the cart object itself which must be provided in `savedCartObj`.
 * @param {array} cart Array of @ids contained in the in-memory cart to be saved
 * @param {object} savedCartObj User's saved cart object
 * @param {user} user User object normally retrieved from session_properties
 * @param {func} fetch System-wide fetch operation
 * @return {object} Promise with new or updated cart object
 */
const cartSave = (cart, savedCartObj, user, fetch) => {
    const cartAtId = savedCartObj && savedCartObj['@id'];
    if (cartAtId) {
        return getWriteableCartObject(cartAtId, fetch).then((writeableCart) => {
            // Copy the in-memory cart to the writeable cart object and then update it in the DB.
            writeableCart.elements = cart;
            return updateCartObject(writeableCart, cartAtId, fetch);
        });
    }

    // No user cart. Make one from scratch and save it.
    return createCartObject(cart, user, fetch);
};

export default cartSave;
