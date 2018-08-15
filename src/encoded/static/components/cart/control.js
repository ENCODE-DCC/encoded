// Components and functions to modify the cart.
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { addToCartAndSave, addMultipleToCart, removeFromCartAndSave } from './actions';


// Button to add the current object to the cart, or to remove it.
const CartControlComponent = ({ cart, inProgress, current, onAddToCartClick, onRemoveFromCartClick }) => (
    cart.indexOf(current) > -1
        ? <button disabled={inProgress} className="btn btn-info btn-sm cart__control-button--inline" onClick={onRemoveFromCartClick}>Remove from cart</button>
        : <button disabled={inProgress} className="btn btn-info btn-sm cart__control-button--inline" onClick={onAddToCartClick}>Add to cart</button>
);

CartControlComponent.propTypes = {
    /** Current contents of cart */
    cart: PropTypes.array,
    /** True if cart updating operation is in progress */
    inProgress: PropTypes.bool,
    /** @id of current object being added */
    current: PropTypes.string.isRequired,
    /** Function to call when Add to Cart clicked */
    onAddToCartClick: PropTypes.func.isRequired,
    /** Function to call when Remove from Cart clicked */
    onRemoveFromCartClick: PropTypes.func.isRequired,
};

CartControlComponent.defaultProps = {
    cart: [],
    inProgress: false,
};

const mapStateToProps = (state, ownProps) => ({ cart: state.cart, inProgress: state.inProgress, current: ownProps.current['@id'] });
const mapDispatchToProps = (dispatch, ownProps) => (
    {
        onAddToCartClick: () => dispatch(addToCartAndSave(ownProps.current['@id'], ownProps.sessionProperties.user, ownProps.fetch)),
        onRemoveFromCartClick: () => dispatch(removeFromCartAndSave(ownProps.current['@id'], ownProps.sessionProperties.user, ownProps.fetch)),
    }
);

const CartControlInternal = connect(mapStateToProps, mapDispatchToProps)(CartControlComponent);

const CartControl = (props, reactContext) => (
    <CartControlInternal current={props.current} sessionProperties={reactContext.session_properties} fetch={reactContext.fetch} />
);

CartControl.propTypes = {
    current: PropTypes.object.isRequired, // @id of current object being added
};

CartControl.contextTypes = {
    session_properties: PropTypes.object,
    fetch: PropTypes.func,
};

export default CartControl;


/**
 * Add encode item @ids to the store.
 *
 * @param {array} items - Array of @ids to add to the cart
 * @param {func} dispatch - Redux dispatch function for the cart store
 */
const cartAddItems = (items, dispatch) => {
    dispatch(addMultipleToCart(items));
};

export { cartAddItems };
