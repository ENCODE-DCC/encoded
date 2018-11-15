/**
 * Renders and handles a button to toggle items in/out of the cart.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { svgIcon } from '../../libs/svg-icons';
import { addToCartAndSave, removeFromCartAndSave } from './actions';
import { CART_MAXIMUM_ELEMENTS_LOGGEDOUT } from './util';


class CartToggleComponent extends React.Component {
    constructor() {
        super();
        this.handleClick = this.handleClick.bind(this);
    }

    /**
     * Called when user clicks a toggle button. Depending on whether the element is already in the
     * cart, call the Redux action either to remove from or add to the cart.
     */
    handleClick() {
        const { cart, elementAtId, onRemoveFromCartClick, onAddToCartClick } = this.props;
        const onClick = (cart.indexOf(elementAtId) !== -1) ? onRemoveFromCartClick : onAddToCartClick;
        onClick();
    }

    render() {
        const { cart, elementAtId, loggedIn, inProgress } = this.props;
        const inCart = cart.indexOf(elementAtId) > -1;
        const cartAtLimit = !loggedIn && cart.length >= CART_MAXIMUM_ELEMENTS_LOGGEDOUT;
        const inCartToolTip = inCart ? 'Remove item from cart' : 'Add item to cart';
        const inProgressToolTip = inProgress ? 'Cart operation in progress' : '';
        const cartAtLimitToolTip = cartAtLimit ? `Cart can contain a maximum of ${CART_MAXIMUM_ELEMENTS_LOGGEDOUT} items` : '';

        // "name" attribute needed for BDD test targeting.
        return (
            <button
                className={`cart__toggle${inCart ? ' cart__toggle--in-cart' : ''}`}
                onClick={this.handleClick}
                disabled={inProgress || (!loggedIn && !inCart && cartAtLimit)}
                title={cartAtLimitToolTip || inProgressToolTip || inCartToolTip}
                aria-pressed={inCart}
                aria-label={cartAtLimitToolTip || inProgressToolTip || inCartToolTip}
                name={elementAtId}
            >
                {svgIcon('cart')}
            </button>
        );
    }
}

CartToggleComponent.propTypes = {
    /** Current contents of cart; array of @ids */
    cart: PropTypes.array,
    /** @id of element being added to cart */
    elementAtId: PropTypes.string.isRequired,
    /** Function to call to add `elementAtId` to cart */
    onAddToCartClick: PropTypes.func.isRequired,
    /** Function to call to remove `elementAtId` from cart  */
    onRemoveFromCartClick: PropTypes.func.isRequired,
    /** True if user is logged in */
    loggedIn: PropTypes.bool,
    /** True if cart operation is in progress */
    inProgress: PropTypes.bool,
};

CartToggleComponent.defaultProps = {
    cart: [],
    loggedIn: false,
    inProgress: false,
};

const mapStateToProps = (state, ownProps) => ({
    cart: state.cart,
    inProgress: state.inProgress,
    elementAtId: ownProps.element['@id'],
    loggedIn: ownProps.loggedIn,
});

const mapDispatchToProps = (dispatch, ownProps) => ({
    onAddToCartClick: () => dispatch(addToCartAndSave(ownProps.element['@id'], ownProps.sessionProperties.user, ownProps.loggedIn, ownProps.fetch)),
    onRemoveFromCartClick: () => dispatch(removeFromCartAndSave(ownProps.element['@id'], ownProps.sessionProperties.user, ownProps.loggedIn, ownProps.fetch)),
});

const CartToggleInternal = connect(mapStateToProps, mapDispatchToProps)(CartToggleComponent);


const CartToggle = (props, reactContext) => (
    <CartToggleInternal
        element={props.element}
        loggedIn={!!(reactContext.session && reactContext.session['auth.userid'])}
        sessionProperties={reactContext.session_properties}
        fetch={reactContext.fetch}
    />
);

CartToggle.propTypes = {
    /** Object being added */
    element: PropTypes.object.isRequired,
};

CartToggle.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
    fetch: PropTypes.func,
};

export default CartToggle;
