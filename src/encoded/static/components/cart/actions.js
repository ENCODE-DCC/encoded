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

export const addToCart = current => (
    { type: ADD_TO_CART, current }
);

/**
 * Redux thunk action to not only add an element to the cart, but also to save this change to the
 * database.
 * @param {string} current - @id of object being added to cart
 * @param {object} user - User object from <App> session_properties
 * @param {function} fetch - fetch function from <App>
 * @return {object} - Promise from saving the cart; null if error or not logged in
 */
export const addToCartAndSave = (current, user, fetch) => (
    (dispatch, getState) => {
        dispatch(addToCart(current));
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

export const addMultipleToCart = elements => (
    { type: ADD_MULTIPLE_TO_CART, elements }
);

export const addMultipleToCartAndSave = (elements, user, fetch) => (
    (dispatch, getState) => {
        dispatch(addMultipleToCart(elements));
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

export const removeFromCart = current => (
    { type: REMOVE_FROM_CART, current }
);

/**
 * Redux thunk action to not only remove an element from the cart, but also to save this change to
 * the database.
 * @param {string} current - @id of object being added to cart
 * @param {object} user - User object from <App> session_properties
 * @param {function} fetch - fetch function from <App>
 * @return {object} - Promise from saving the cart; null if error or not logged in
 */
export const removeFromCartAndSave = (current, user, fetch) => (
    (dispatch, getState) => {
        dispatch(removeFromCart(current));
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

export const removeMultipleFromCart = elements => (
    { type: REMOVE_MULTIPLE_FROM_CART, elements }
);

export const removeMultipleFromCartAndSave = (elements, user, fetch) => (
    (dispatch, getState) => {
        dispatch(removeMultipleFromCart(elements));
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

export const cacheSavedCart = cartObj => (
    { type: CACHE_SAVED_CART, cartObj }
);

export const cartOperationInProgress = inProgress => (
    { type: CART_OPERATION_IN_PROGRESS, inProgress }
);
