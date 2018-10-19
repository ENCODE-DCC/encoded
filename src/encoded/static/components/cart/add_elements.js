import { addMultipleToCart } from './actions';


/**
 * Add encode item @ids to the store.
 * @param {array} elements Array of @ids to add to the cart
 * @param {func} dispatch Redux dispatch function for the cart store
 */
const cartAddElements = (elements, dispatch) => {
    dispatch(addMultipleToCart(elements));
};

export default cartAddElements;
