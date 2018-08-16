/**
 * Redux and thunk functions to interact with the cart in the Redux store.
 */
import cartCacheSaved from './cache_saved';
import cartSave from './save';
import cartSetOperationInProgress from './in_progress';


// Action creators to use with Redux store.dispatch().
export const ADD_TO_CART = 'ADD_TO_CART';
export const ADD_MULTIPLE_TO_CART = 'ADD_MULTIPLE_TO_CART';
export const REMOVE_FROM_CART = 'REMOVE_FROM_CART';
export const REMOVE_MULTIPLE_FROM_CART = 'REMOVE_MULTIPLE_FROM_CART';
export const CACHE_SAVED_CART = 'CACHE_SAVED_CART';
export const CART_OPERATION_IN_PROGRESS = 'CART_OPERATION_IN_PROGRESS';
export const NO_ACTION = 'NO_ACTION';


/**
 * Redux action to add an element to the cart.
 * @param {string} elementAtId `@id` of element being added to cart
 * @return {object} Redux action object
 */
export const addToCart = elementAtId => (
    { type: ADD_TO_CART, elementAtId }
);


/**
 * Redux thunk action to add an element to the cart and save this change to the logged-in user's
 * cart object in the database.
 * @param {string} elementAtId `@id` of element being added to cart
 * @param {object} user User object from <App> session_properties
 * @param {function} fetch fetch function from <App> context
 * @return {object} Promise from saving the cart; null if not logged in
 */
export const addToCartAndSave = (elementAtId, user, fetch) => (
    (dispatch, getState) => {
        dispatch(addToCart(elementAtId));
        if (user) {
            const { cart, savedCartObj } = getState();
            cartSetOperationInProgress(true, dispatch);
            return cartSave(cart, savedCartObj, user, fetch).then((updatedSavedCartObj) => {
                cartSetOperationInProgress(false, dispatch);
                cartCacheSaved(updatedSavedCartObj, dispatch);
                return updatedSavedCartObj;
            });
        }
        return null;
    }
);


/**
 * Redux action to add multiple elements to the cart.
 * @param {array} elementAtIds `@ids` of elements being added to cart
 * @return {object} Redux action object
 */
export const addMultipleToCart = elementAtIds => (
    { type: ADD_MULTIPLE_TO_CART, elementAtIds }
);


/**
 * Redux thunk action to add multiple elements to the cart and save this change to the logged-in
 * user's cart object in the database.
 * @param {array} elementAtIds `@ids` of elements being added to cart
 * @param {object} user User object from <App> session_properties
 * @param {function} fetch fetch function from <App> context
 * @return {object} Promise from saving the cart; null not logged in
 */
export const addMultipleToCartAndSave = (elementAtIds, user, fetch) => (
    (dispatch, getState) => {
        dispatch(addMultipleToCart(elementAtIds));
        if (user) {
            const { cart, savedCartObj } = getState();
            cartSetOperationInProgress(true, dispatch);
            return cartSave(cart, savedCartObj, user, fetch).then((updatedSavedCartObj) => {
                cartSetOperationInProgress(false, dispatch);
                cartCacheSaved(updatedSavedCartObj, dispatch);
                return updatedSavedCartObj;
            });
        }
        return null;
    }
);


/**
 * Redux action to remove an element from the cart.
 * @param {string} elementAtId `@id` of element to remove from the cart
 * @return {object} Redux action object
 */
export const removeFromCart = elementAtId => (
    { type: REMOVE_FROM_CART, elementAtId }
);


/**
 * Redux thunk action to remove an element from the cart and save this change to the logged-in
 * user's cart object in the database.
 * @param {string} elementAtId `@id` of object being added to cart
 * @param {object} user User object from <App> session_properties
 * @param {function} fetch fetch function from <App> context
 * @return {object} Promise from saving the cart; null not logged in
 */
export const removeFromCartAndSave = (elementAtId, user, fetch) => (
    (dispatch, getState) => {
        dispatch(removeFromCart(elementAtId));
        if (user) {
            const { cart, savedCartObj } = getState();
            cartSetOperationInProgress(true, dispatch);
            return cartSave(cart, savedCartObj, user, fetch).then((updatedSavedCartObj) => {
                cartSetOperationInProgress(false, dispatch);
                cartCacheSaved(updatedSavedCartObj, dispatch);
                return updatedSavedCartObj;
            });
        }
        return Promise.resolve(null);
    }
);


/**
 * Redux action to remove multiple elements from the cart.
 * @param {array} elementAtIds `@ids` of elements to remove from the cart
 * @return {object} Redux action object
 */
export const removeMultipleFromCart = elementAtIds => (
    { type: REMOVE_MULTIPLE_FROM_CART, elementAtIds }
);


/**
 * Redux thunk action to remove multiple elements from the cart and save this change to the
 * database.
 * @param {array} elementAtIds `@ids` of elements to remove from the cart
 * @param {object} user User object from <App> session_properties
 * @param {function} fetch fetch function from <App> context
 * @return {object} Promise from saving the cart; null if not logged in
 */
export const removeMultipleFromCartAndSave = (elementAtIds, user, fetch) => (
    (dispatch, getState) => {
        dispatch(removeMultipleFromCart(elementAtIds));
        if (user) {
            const { cart, savedCartObj } = getState();
            cartSetOperationInProgress(true, dispatch);
            return cartSave(cart, savedCartObj, user, fetch).then((updatedSavedCartObj) => {
                cartSetOperationInProgress(false, dispatch);
                cartCacheSaved(updatedSavedCartObj, dispatch);
                return updatedSavedCartObj;
            });
        }
        return Promise.resolve(null);
    }
);


/**
 * Redux action to cache a saved cart object into the cart store.
 * @param {object} savedCartObj Cart object as saved to the database
 * @return {object} Redux action object
 */
export const cacheSavedCart = savedCartObj => (
    { type: CACHE_SAVED_CART, savedCartObj }
);


/**
 * Redux action to indicate that a cart operation is currently in progress.
 * @param {bool} inProgress True to indicate cart operation in progress; false when done
 * @return {object} Redux action object
 */
export const cartOperationInProgress = inProgress => (
    { type: CART_OPERATION_IN_PROGRESS, inProgress }
);
