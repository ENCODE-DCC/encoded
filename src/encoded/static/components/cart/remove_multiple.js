// Components and functions to modify the cart.
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { removeMultipleFromCart } from './actions';


// Button to remove mutliple items from the cart..
const CartRemoveAllComponent = ({ cart, items, onClick }) => {
    const disabled = items.every(item => cart.indexOf(item['@id']) === -1);
    return <button className="btn btn-info btn-sm" disabled={disabled} onClick={onClick}>Remove all</button>;
};

CartRemoveAllComponent.propTypes = {
    cart: PropTypes.array, // Current contents of cart
    items: PropTypes.array.isRequired, // List of @ids of the items to add
    onClick: PropTypes.func.isRequired, // Function to call when Remove All clicked
};

CartRemoveAllComponent.defaultProps = {
    cart: [],
};

const mapStateToProps = (state, ownProps) => ({ cart: state.cart, items: ownProps.items });
const mapDispatchToProps = (dispatch, ownProps) => (
    {
        onClick: () => {
            const itemAtIds = ownProps.items.map(item => item['@id']);
            return dispatch(removeMultipleFromCart(itemAtIds));
        },
    }
);

const CartRemoveAll = connect(mapStateToProps, mapDispatchToProps)(CartRemoveAllComponent);
export default CartRemoveAll;
