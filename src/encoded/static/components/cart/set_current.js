import { setCurrentCart } from './actions';


/**
 * Set the current cart to the given @id.
 * @param {string} current @id of the cart to set as the current cart
 * @param {func} dispatch Redux dispatch function for the cart store
 */
const cartSetCurrent = (current, dispatch) => {
    dispatch(setCurrentCart(current));
};

export default cartSetCurrent;
