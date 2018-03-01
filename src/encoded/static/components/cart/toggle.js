// Components and functions to modify the cart.
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { svgIcon } from '../../libs/svg-icons';
import { addToCartAndSave, removeFromCartAndSave } from './actions';
import { CART_MAXIMUM_ELEMENTS_LOGGEDOUT } from './util';


/**
 * Button to add a search-result item to the cart, or to remove it. Disable for items not in the
 * cart if the user's not logged in and the number of items in the cart is the maximum allowed for
 * not-logged-in users.
 */
class CartToggleComponent extends React.Component {
    constructor(props) {
        super(props);
        this.handleClick = this.handleClick.bind(this);
    }

    /**
     * Called when user clicks cart button on search result pages. Depending on whether the item is
     * already in the cart, call either the Redux action to remove from or add to the cart.
     */
    handleClick() {
        const { cart, current, onRemoveFromCartClick, onAddToCartClick } = this.props;
        const onClick = (cart.indexOf(current) > -1) ? onRemoveFromCartClick : onAddToCartClick;
        onClick();
    }

    render() {
        const { cart, inProgress, current, loggedIn } = this.props;
        const inCart = cart.indexOf(current) > -1;
        const toolTip = inCart ? 'Remove item from cart' : 'Add item to cart';

        return (
            <div className="cart__toggle">
                <div className={`cart__checkbox${inCart ? ' cart__checkbox--in-cart' : ''}`}>
                    <button
                        onClick={this.handleClick}
                        disabled={inProgress || (!loggedIn && !inCart && cart.length >= CART_MAXIMUM_ELEMENTS_LOGGEDOUT)}
                        title={toolTip}
                        aria-pressed={inCart}
                        aria-label={toolTip}
                    >
                        {svgIcon('cart')}
                    </button>
                </div>
            </div>
        );
    }
}

CartToggleComponent.propTypes = {
    /** Current contents of cart */
    cart: PropTypes.array,
    /** True if cart operation is in progress */
    inProgress: PropTypes.bool,
    /** @id of current object being added */
    current: PropTypes.string.isRequired,
    /** Function to call when Add item to Cart clicked */
    onAddToCartClick: PropTypes.func.isRequired,
    /** Function to call when Remove item from Cart clicked */
    onRemoveFromCartClick: PropTypes.func.isRequired,
    /** True if user is logged in */
    loggedIn: PropTypes.bool,
};

CartToggleComponent.defaultProps = {
    cart: [],
    inProgress: false,
    loggedIn: false,
};

const mapStateToProps = (state, ownProps) => ({
    cart: state.cart,
    inProgress: state.inProgress,
    current: ownProps.current['@id'],
    loggedIn: ownProps.loggedIn,
});

const mapDispatchToProps = (dispatch, ownProps) => ({
    onAddToCartClick: () => dispatch(addToCartAndSave(ownProps.current['@id'], ownProps.sessionProperties.user, ownProps.fetch)),
    onRemoveFromCartClick: () => dispatch(removeFromCartAndSave(ownProps.current['@id'], ownProps.sessionProperties.user, ownProps.fetch)),
});

const CartToggleInternal = connect(mapStateToProps, mapDispatchToProps)(CartToggleComponent);


/**
 * Wrapper component that subscribes to React context properties reliably, and passes them to a
 * Redux component as regular props.
 */
const CartToggle = (props, reactContext) => (
    <CartToggleInternal
        current={props.current}
        loggedIn={!!(reactContext.session && reactContext.session['auth.userid'])}
        sessionProperties={reactContext.session_properties}
        fetch={reactContext.fetch}
    />
);

CartToggle.propTypes = {
    /** @id of current object being added */
    current: PropTypes.object.isRequired,
};

CartToggle.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
    fetch: PropTypes.func,
};

export default CartToggle;
