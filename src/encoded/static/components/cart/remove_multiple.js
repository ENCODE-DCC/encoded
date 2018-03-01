// Components and functions to modify the cart.
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { removeMultipleFromCart } from './actions';


// Button to remove mutliple elements from the cart.
const CartRemoveAllComponent = ({ cart, elements, onClick }) => {
    const disabled = elements.every(element => cart.indexOf(element['@id']) === -1);
    return <button className="btn btn-info btn-sm" disabled={disabled} onClick={onClick}>Remove all</button>;
};

CartRemoveAllComponent.propTypes = {
    cart: PropTypes.array, // Current contents of cart
    elements: PropTypes.array.isRequired, // List of @ids of the elements to add
    onClick: PropTypes.func.isRequired, // Function to call when Remove All clicked
};

CartRemoveAllComponent.defaultProps = {
    cart: [],
};

const mapStateToProps = (state, ownProps) => ({ cart: state.cart, elements: ownProps.elements });
const mapDispatchToProps = (dispatch, ownProps) => (
    {
        onClick: () => {
            const elementAtIds = ownProps.elements.map(element => element['@id']);
            return dispatch(removeMultipleFromCart(elementAtIds));
        },
    }
);

const CartRemoveAll = connect(mapStateToProps, mapDispatchToProps)(CartRemoveAllComponent);
export default CartRemoveAll;
