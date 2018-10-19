/**
 * Functions to remove multiple elements from the in-memory cart.
 */
import { removeMultipleFromCart } from './actions';


/**
 * Remove encode item @ids from the cart in the Redux store.
 * @param {array} elementAtIds Array of @ids to remove from the cart
 * @param {func} dispatch Redux dispatch function for the cart store
 */
const cartRemoveElements = (elementAtIds, dispatch) => {
    dispatch(removeMultipleFromCart(elementAtIds));
};

export default cartRemoveElements;
