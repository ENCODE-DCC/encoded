import { cacheSavedCart } from './actions';


/**
 * Cache the saved cart object to the cart Redux store. This has to be done every time we save an
 * updated cart object to the database.
 *
 * @param {object} cartObj - Saved cart object to be cached
 * @param {func} dispatch - Redux dispatch function for the cart store
 */
const cartCacheSaved = (cartObj, dispatch) => {
    dispatch(cacheSavedCart(cartObj));
};

export default cartCacheSaved;
