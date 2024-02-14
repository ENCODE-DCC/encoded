/**
 * Functions to handle the saving and updating of cart objects.
 */
import { parseAndLogError } from '../globals';


/**
 * Update the current user's cart object in the DB. You must provide `cartAtId` because `cart`
 * cannot have non-writeable properties in it, and @id is one of several non-writeable properties.
 * Pass false in `expectUpdatedObj` if permissions could limit you from viewing the updated object,
 * such as when you delete a cart.
 * @param {object} cart Cart object to update; must be writeable version
 * @param {string} cartAtId @id of the cart object to update
 * @param {func} fetch System-wide fetch operation
 * @param {bool} expectUpdatedObj True (default) to get the updated object as the promise result
 * @return {object} Promise containing updated cart object, or cart object @id if expectUpdatedObj
 *                  is false.
 */
const updateCartObject = (cart, cartAtId, fetch, expectUpdatedObj = true) => (
    fetch(`${cartAtId}${!expectUpdatedObj ? '?render=false' : ''}`, {
        method: 'PUT',
        body: JSON.stringify(cart),
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        },
    }).then((response) => {
        if (response.ok) {
            return Promise.resolve(response.json());
        }
        return Promise.reject(response.status);
    }).then((result) => (
        result['@graph'][0]
    ))
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
 * Save the in-memory cart to the database. The user object has the @id of the user's cart, but not
 * the cart object itself which must be provided in `savedCartObj`.
 * @param {array} elements Array of @ids contained in the in-memory cart to be saved
 * @param {array} fileViews Array of file views to save; falsy to not save
 * @param {object} savedCartObj User's saved cart object
 * @param {func} fetch System-wide fetch operation
 * @return {object} Promise with new or updated cart object
 */
const cartSave = (elements, fileViews, savedCartObj, fetch) => {
    const cartAtId = savedCartObj && savedCartObj['@id'];
    if (cartAtId) {
        return getWriteableCartObject(cartAtId, fetch).then((writeableCart) => {
            // Copy the in-memory cart to the writeable cart object and then update it in the DB.
            writeableCart.elements = elements;
            if (fileViews) {
                writeableCart.file_views = fileViews;
            }
            return updateCartObject(writeableCart, cartAtId, fetch);
        });
    }
    return Promise.resolve(null);
};

export default cartSave;


/**
 * Create a new cart in the DB for the current user.
 * @param {string} {name Name for the new cart
 * @param {string} {identifier Identifier for the new cart (optional)
 * @param {string} {status} Status for the new cart (optional)
 * @param {func} fetch System-wide fetch operation
 * @return {Promise} Resolves to newly created cart object, or reject with error code.
 */
export const cartCreate = ({ name, identifier, status }, fetch) => {
    const body = {
        name,
        locked: false,
        file_views: [],
    };
    if (identifier) {
        body.identifier = identifier;
    }
    if (status) {
        body.status = status;
    }
    return fetch('/carts/@@put-cart', {
        method: 'PUT',
        body: JSON.stringify(body),
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        },
    }).then((response) => {
        if (response.ok) {
            return Promise.resolve(response.json());
        }
        return Promise.reject(response.status);
    }).then((result) => (
        result['@graph'][0]
    ));
};


/**
 * Create a new auto-save cart in the DB for the current user.
 * @param {func} fetch System-wide fetch function
 * @return {Promise} Resolves to newly created cart object, or reject with error code.
 */
export const cartCreateAutosave = (fetch) => (
    cartCreate({ name: 'Auto Save', status: 'disabled' }, fetch)
);


/**
 * Retrieve a cart or related object and return its data in a promise.
 * @param {string} URI of cart-related object to retrieve
 * @param {func} fetch System XHR fetch function
 * @return {Promise} Resolves to contents of retrieved cart
 */
export const cartRetrieve = (cartUri, fetch) => (
    fetch(cartUri, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
        },
    }).then((response) => {
        if (response.ok) {
            return response.json();
        }
        throw new Error(response);
    })
);


/**
 * Update a cart object with new, updated, or removed properties.
 * @param {string} cartAtId @id of the cart object to update
 * @param {object} properties Object containing the properties within the cart object to set
 * @param {array} propertiesForRemoval Names of properties to remove from the object
 * @param {func} fetch System fetch function
 * @param {bool} expectUpdatedObject True to expect updated object in promise; false to ignore.
 *                                   Set to false when setting status to "deleted" to avoid
 *                                   permission error (submitter can't get updated object that
 *                                   they deleted)
 * @return {object} Promise containing the updated object
 */
export const cartUpdate = (cartAtId, properties, propertiesForRemoval, fetch, expectUpdatedObject = true) => (
    getWriteableCartObject(cartAtId, fetch).then((writeableCart) => {
        // Remove requested properties from the cart object.
        if (propertiesForRemoval && propertiesForRemoval.length > 0) {
            propertiesForRemoval.forEach((property) => {
                delete writeableCart[property];
            });
        }

        // Copy the in-memory cart to the writeable cart object and then update it in the DB.
        const updatedCart = { ...writeableCart, ...properties };
        return updateCartObject(updatedCart, cartAtId, fetch, expectUpdatedObject);
    })
);
