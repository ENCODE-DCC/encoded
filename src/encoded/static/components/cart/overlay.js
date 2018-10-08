import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';


// Button to add the current object to the cart, or to remove it.
const CartOverlayComponent = ({ cart, savedElements, current }) => {
    const inCart = cart.indexOf(current) > -1;
    const saved = savedElements.indexOf(current) > -1;

    return inCart !== saved ? <div className="result-item__cart-overlay" /> : null;
};

CartOverlayComponent.propTypes = {
    cart: PropTypes.array, // Current contensts of cart
    savedElements: PropTypes.array, // Elements already saved to user cart
    current: PropTypes.string.isRequired, // @id of current object being added
};

CartOverlayComponent.defaultProps = {
    cart: [],
    savedElements: [],
};

const mapStateToProps = (state, ownProps) => ({
    cart: state.cart,
    savedElements: (state.savedCartObj && state.savedCartObj.elements) || [],
    current: ownProps.current['@id'],
});

const CartOverlay = connect(mapStateToProps)(CartOverlayComponent);

export default CartOverlay;
