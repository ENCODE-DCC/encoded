// Components and functions to modify the cart.
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { addToCartAndSave, removeFromCartAndSave } from './actions';
import { CART_MAXIMUM_ELEMENTS_LOGGEDOUT } from './util';


/**
 * Button to add the current object to the cart, or to remove it. Disable for items not in the cart
 * if the user's not logged in and the number of items in the cart is the maximum allowed for not-
 * logged-in users.
 */
const CartControlComponent = ({ cart, inProgress, current, loggedIn, onAddToCartClick, onRemoveFromCartClick }) => {
    const inCart = cart.indexOf(current) > -1;
    return (
        inCart ?
            <button
                disabled={inProgress}
                className="btn btn-info btn-sm cart__control-button--inline"
                onClick={onRemoveFromCartClick}
                aria-label="Remove item from cart"
            >
                Remove from cart
            </button>
        :
            <button
                disabled={inProgress || (!loggedIn && cart.length >= CART_MAXIMUM_ELEMENTS_LOGGEDOUT)}
                className="btn btn-info btn-sm cart__control-button--inline"
                onClick={onAddToCartClick}
                aria-label="Add item to cart"
            >
                Add to cart
            </button>
    );
};

CartControlComponent.propTypes = {
    /** Current contents of cart */
    cart: PropTypes.array,
    /** True if cart updating operation is in progress */
    inProgress: PropTypes.bool,
    /** @id of current object being added */
    current: PropTypes.string.isRequired,
    /** True if user is logged in */
    loggedIn: PropTypes.bool,
    /** Function to call when Add to Cart clicked */
    onAddToCartClick: PropTypes.func.isRequired,
    /** Function to call when Remove from Cart clicked */
    onRemoveFromCartClick: PropTypes.func.isRequired,
};

CartControlComponent.defaultProps = {
    cart: [],
    inProgress: false,
    loggedIn: false,
};

const mapStateToProps = (state, ownProps) => ({ cart: state.cart, inProgress: state.inProgress, current: ownProps.current['@id'] });
const mapDispatchToProps = (dispatch, ownProps) => (
    {
        onAddToCartClick: () => dispatch(addToCartAndSave(ownProps.current['@id'], ownProps.sessionProperties.user, ownProps.fetch)),
        onRemoveFromCartClick: () => dispatch(removeFromCartAndSave(ownProps.current['@id'], ownProps.sessionProperties.user, ownProps.fetch)),
    }
);

const CartControlInternal = connect(mapStateToProps, mapDispatchToProps)(CartControlComponent);


/**
 * Wrapper component that subscribes to React context properties reliably, and passes them to a
 * Redux component as regular props.
 */
const CartControl = (props, reactContext) => (
    <CartControlInternal
        current={props.current}
        loggedIn={!!(reactContext.session && reactContext.session['auth.userid'])}
        sessionProperties={reactContext.session_properties}
        fetch={reactContext.fetch}
    />
);

CartControl.propTypes = {
    /** @id of current object being added */
    current: PropTypes.object.isRequired,
};

CartControl.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
    fetch: PropTypes.func,
};

export default CartControl;
