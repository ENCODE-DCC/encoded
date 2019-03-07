/**
 * Redux and thunk functions to interact with the cart in the Redux store.
 */
import cartCacheSaved from './cache_saved';
import cartSave, { cartPatch } from './database';
import cartSetOperationInProgress from './in_progress';
import { cartGetSettings, cartSetSettingsCurrent } from './settings';


// Actions to use with Redux store.dispatch().
export const ADD_TO_CART = 'ADD_TO_CART';
export const ADD_MULTIPLE_TO_CART = 'ADD_MULTIPLE_TO_CART';
export const REMOVE_FROM_CART = 'REMOVE_FROM_CART';
export const REMOVE_MULTIPLE_FROM_CART = 'REMOVE_MULTIPLE_FROM_CART';
export const REPLACE_CART = 'REPLACE_CART';
export const CACHE_SAVED_CART = 'CACHE_SAVED_CART';
export const CART_OPERATION_IN_PROGRESS = 'CART_OPERATION_IN_PROGRESS';
export const SET_CURRENT = 'SET_CURRENT';
export const SET_NAME = 'SET_NAME';
export const SET_IDENTIFIER = 'SET_IDENTIFIER';
export const SET_STATUS = 'SET_STATUS';
export const NO_ACTION = 'NO_ACTION';


/**
 * Redux action creator to add an element to the cart.
 * @param {string} elementAtId `@id` of element being added to cart
 * @return {object} Redux action object
 */
export const addToCart = elementAtId => (
    { type: ADD_TO_CART, elementAtId }
);


/**
 * Redux thunk action creator to add an element to the cart and save this change to the logged-in
 * user's cart object in the database.
 * @param {string} elementAtId `@id` of element being added to cart
 * @param {bool} loggedIn True if user is logged in.
 * @param {function} fetch fetch function from <App> context
 * @return {object} Promise from saving the cart; null if not logged in
 */
export const addToCartAndSave = (elementAtId, loggedIn, fetch) => (
    (dispatch, getState) => {
        dispatch(addToCart(elementAtId));
        if (loggedIn) {
            const { elements, savedCartObj } = getState();
            cartSetOperationInProgress(true, dispatch);
            return cartSave(elements, savedCartObj, fetch).then((updatedSavedCartObj) => {
                cartSetOperationInProgress(false, dispatch);
                cartCacheSaved(updatedSavedCartObj, dispatch);
                return updatedSavedCartObj;
            });
        }
        return null;
    }
);


/**
 * Redux action creator to add multiple elements to the cart.
 * @param {array} elementAtIds `@ids` of elements being added to cart
 * @return {object} Redux action object
 */
export const addMultipleToCart = elementAtIds => (
    { type: ADD_MULTIPLE_TO_CART, elementAtIds }
);


/**
 * Redux thunk action creator to add multiple elements to the cart and save this change to the
 * logged-in user's cart object in the database.
 * @param {array} elementAtIds `@ids` of elements being added to cart
 * @param {bool} loggedIn True if user has logged in.
 * @param {function} fetch fetch function from <App> context
 * @return {object} Promise from saving the cart; null not logged in
 */
export const addMultipleToCartAndSave = (elementAtIds, loggedIn, fetch) => (
    (dispatch, getState) => {
        dispatch(addMultipleToCart(elementAtIds));
        if (loggedIn) {
            const { elements, savedCartObj } = getState();
            cartSetOperationInProgress(true, dispatch);
            return cartSave(elements, savedCartObj, fetch).then((updatedSavedCartObj) => {
                cartSetOperationInProgress(false, dispatch);
                cartCacheSaved(updatedSavedCartObj, dispatch);
                return updatedSavedCartObj;
            });
        }
        return null;
    }
);


/**
 * Redux action creator to remove an element from the cart.
 * @param {string} elementAtId `@id` of element to remove from the cart
 * @return {object} Redux action object
 */
export const removeFromCart = elementAtId => (
    { type: REMOVE_FROM_CART, elementAtId }
);


/**
 * Redux thunk action creator to remove an element from the cart and save this change to the
 * logged-in user's cart object in the database.
 * @param {string} elementAtId `@id` of object being added to cart
 * @param {bool} loggedIn True if user has logged in.
 * @param {function} fetch fetch function from <App> context
 * @return {object} Promise from saving the cart; null not logged in
 */
export const removeFromCartAndSave = (elementAtId, loggedIn, fetch) => (
    (dispatch, getState) => {
        dispatch(removeFromCart(elementAtId));
        if (loggedIn) {
            const { elements, savedCartObj } = getState();
            cartSetOperationInProgress(true, dispatch);
            return cartSave(elements, savedCartObj, fetch).then((updatedSavedCartObj) => {
                cartSetOperationInProgress(false, dispatch);
                cartCacheSaved(updatedSavedCartObj, dispatch);
                return updatedSavedCartObj;
            });
        }
        return Promise.resolve(null);
    }
);


/**
 * Redux action creator to remove multiple elements from the cart.
 * @param {array} elementAtIds `@ids` of elements to remove from the cart
 * @return {object} Redux action object
 */
export const removeMultipleFromCart = elementAtIds => (
    { type: REMOVE_MULTIPLE_FROM_CART, elementAtIds }
);


/**
 * Redux thunk action creator to remove multiple elements from the cart and save this change to the
 * database.
 * @param {array} elementAtIds `@ids` of elements to remove from the cart
 * @param {bool} loggedIn True if user has logged in
 * @param {function} fetch fetch function from <App> context
 * @return {object} Promise from saving the cart; null if not logged in
 */
export const removeMultipleFromCartAndSave = (elementAtIds, loggedIn, fetch) => (
    (dispatch, getState) => {
        dispatch(removeMultipleFromCart(elementAtIds));
        if (loggedIn) {
            const { elements, savedCartObj } = getState();
            cartSetOperationInProgress(true, dispatch);
            return cartSave(elements, savedCartObj, fetch).then((updatedSavedCartObj) => {
                cartSetOperationInProgress(false, dispatch);
                cartCacheSaved(updatedSavedCartObj, dispatch);
                return updatedSavedCartObj;
            });
        }
        return Promise.resolve(null);
    }
);


/**
 * Redux action creator to replace all items in the cart with another set of items.
 * @param {array} elementAtIds `@ids` of elements to set the cart to
 * @return {object} Redux action object
 */
export const replaceCart = elementAtIds => (
    { type: REPLACE_CART, elementAtIds }
);


/**
 * Redux action creator to cache a saved cart object into the cart store.
 * @param {object} savedCartObj Cart object as saved to the database
 * @return {object} Redux action object
 */
export const cacheSavedCart = savedCartObj => (
    { type: CACHE_SAVED_CART, savedCartObj }
);


/**
 * Redux action creator to indicate that a cart operation is currently in progress.
 * @param {bool} inProgress True to indicate cart operation in progress; false when done
 * @return {object} Redux action object
 */
export const cartOperationInProgress = inProgress => (
    { type: CART_OPERATION_IN_PROGRESS, inProgress }
);


/**
 * Redux action creator to set the name of the cart.
 * @param {string} name Name to set cart to
 * @return {object} Redux action object
 */
export const setCartName = name => (
    { type: SET_NAME, name }
);


/**
 * Redux action creator to set the identifier of the cart.
 * @param {string} identifier Identifier to set cart to
 * @return {object} Redux action object
 */
export const setCartIdentifier = identifier => (
    { type: SET_IDENTIFIER, identifier }
);


/**
 * Redux action creator to set the current cart. This sets the current cart in the Redux store
 * only -- this does not affect the cart settings in localstorage.
 * @param {string} current @id of cart to set as current
 * @return {object} Redux action object
 */
export const setCurrentCart = current => (
    { type: SET_CURRENT, current }
);


/**
 * Redux action creator to set the status of the cart.
 * @param {string} status New status for cart
 * @return {object} Redux action object
 */
export const setCartStatus = status => (
    { type: SET_STATUS, status }
);


/**
 * Redux thunk action creator to set the name and/or identifier of a cart both in the Redux store
 * and the cart's database object.
 * @param {string} {name} Name to assign to cart (optional)
 * @param {string} {identifier} Identifier (URI) to assign to cart (optional)
 * @param {object} cart Cart object being updated
 * @param {object} user Current user object, often from `session` React context variable
 * @param {func} fetch System fetch function
 * @return {Promise} Resolves to the updated cart object
 */
export const setCartNameIdentifierAndSave = ({ name, identifier }, cart, user, fetch) => (
    dispatch => (
        new Promise((resolve, reject) => {
            const nameIdentifierSetList = { name };

            // Determine whether the cart identifer needs to be set or removed from the cart
            // object entirely.
            let identifierRemovalList;
            if (identifier) {
                nameIdentifierSetList.identifier = identifier;
                identifierRemovalList = null;
            } else {
                identifierRemovalList = ['identifier'];
            }

            // Attempt to update the cart database object.
            cartSetOperationInProgress(true, dispatch);
            return cartPatch(cart['@id'], nameIdentifierSetList, identifierRemovalList, fetch).then((updatedSavedCartObj) => {
                // We know the update of the cart object in the database succeeded, so update the
                // cart Redux store as well.
                cartSetOperationInProgress(false, dispatch);
                const currentCartAtId = cartGetSettings(user).current;

                // If we updated the current cart, re-cache the cart object.
                if (updatedSavedCartObj['@id'] === currentCartAtId) {
                    dispatch(cacheSavedCart(updatedSavedCartObj));
                }

                // Update the name and identifier in the cart store.
                if (name) {
                    dispatch(setCartName(name));
                }
                dispatch(setCartIdentifier(identifier || null));

                // The current cart settings track the current cart's identifier, so that needs to
                // be updated if the identifer for the current cart gets updated.
                if (cart['@id'] !== updatedSavedCartObj['@id']) {
                    // At this point we know the identifier changed, but we don't know if that
                    // affects the current cart.
                    if (cart['@id'] === currentCartAtId) {
                        // The identifier changed AND it affects the current cart, so update the
                        // current cart settings and cart Redux store with the new identifier.
                        cartSetSettingsCurrent(user, updatedSavedCartObj['@id']);
                        dispatch(setCurrentCart(updatedSavedCartObj['@id']));
                    }
                }
                resolve(updatedSavedCartObj);
            }, (err) => {
                reject(err);
            });
        })
    )
);
