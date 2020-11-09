/**
 * Renders and handles a button to toggle items in/out of the cart.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { svgIcon } from '../../libs/svg-icons';
import { addToCartAndSave, removeFromCartAndSave } from './actions';
import { truncateString } from '../globals';
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
        const { elements, elementAtId, onRemoveFromCartClick, onAddToCartClick } = this.props;
        const onClick = (elements.indexOf(elementAtId) !== -1) ? onRemoveFromCartClick : onAddToCartClick;
        onClick();
    }

    render() {
        const { elements, elementAtId, savedCartObj, displayName, css, loggedIn, inProgress } = this.props;
        const inCart = elements.indexOf(elementAtId) > -1;
        const cartName = (savedCartObj && Object.keys(savedCartObj).length > 0 ? savedCartObj.name : '');
        const cartAtLimit = !loggedIn && elements.length >= CART_MAXIMUM_ELEMENTS_LOGGEDOUT;
        const inCartToolTip = `${inCart ? 'Remove item from cart' : 'Add item to cart'}${cartName ? `: ${cartName}` : ''}`;
        const inProgressToolTip = inProgress ? 'Cart operation in progress' : '';
        const cartAtLimitToolTip = cartAtLimit ? `Cart can contain a maximum of ${CART_MAXIMUM_ELEMENTS_LOGGEDOUT} items` : '';
        const locked = savedCartObj && Object.keys(savedCartObj).length > 0 ? savedCartObj.locked : false;

        // "name" attribute needed for BDD test targeting.
        return (
            <div className={`cart-toggle${inCart ? ' cart-toggle--in-cart' : ''}${css ? ` ${css}` : ''}`}>
                {displayName && savedCartObj && savedCartObj.name ? <div className="cart-toggle__name">{truncateString(savedCartObj.name, 22)}</div> : null}
                <button
                    onClick={this.handleClick}
                    disabled={inProgress || locked || (!loggedIn && !inCart && cartAtLimit)}
                    title={cartAtLimitToolTip || inProgressToolTip || inCartToolTip}
                    aria-pressed={inCart}
                    aria-label={cartAtLimitToolTip || inProgressToolTip || inCartToolTip}
                    name={elementAtId}
                >
                    {svgIcon('cart')}
                </button>
            </div>
        );
    }
}

CartToggleComponent.propTypes = {
    /** Current contents of cart; array of @ids */
    elements: PropTypes.array,
    /** Current cart saved object */
    savedCartObj: PropTypes.object,
    /** @id of element being added to cart */
    elementAtId: PropTypes.string.isRequired,
    /** True to display cart name */
    displayName: PropTypes.bool.isRequired,
    /** CSS to add to toggle */
    css: PropTypes.string.isRequired,
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
    elements: [],
    savedCartObj: null,
    loggedIn: false,
    inProgress: false,
};

const mapStateToProps = (state, ownProps) => ({
    elements: state.elements,
    savedCartObj: state.savedCartObj,
    displayName: ownProps.displayName,
    inProgress: state.inProgress,
    elementAtId: ownProps.element['@id'],
    css: ownProps.css,
    loggedIn: ownProps.loggedIn,
});

const mapDispatchToProps = (dispatch, ownProps) => ({
    onAddToCartClick: () => dispatch(addToCartAndSave(ownProps.element['@id'], ownProps.loggedIn, ownProps.fetch)),
    onRemoveFromCartClick: () => dispatch(removeFromCartAndSave(ownProps.element['@id'], ownProps.loggedIn, ownProps.fetch)),
});

const CartToggleInternal = connect(mapStateToProps, mapDispatchToProps)(CartToggleComponent);


const CartToggle = (props, reactContext) => (
    <CartToggleInternal
        element={props.element}
        displayName={props.displayName}
        css={props.css}
        loggedIn={!!(reactContext.session && reactContext.session['auth.userid'])}
        fetch={reactContext.fetch}
    />
);

CartToggle.propTypes = {
    /** Object being added */
    element: PropTypes.object.isRequired,
    /** True to show cart name next to toggle */
    displayName: PropTypes.bool,
    /** CSS to add to toggle */
    css: PropTypes.string,
};

CartToggle.defaultProps = {
    displayName: false,
    css: '',
};

CartToggle.contextTypes = {
    session: PropTypes.object,
    fetch: PropTypes.func,
};

export default CartToggle;
