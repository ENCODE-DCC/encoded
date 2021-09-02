/**
 * Component to allow the user to clear all contents from the cart, saving this emptied cart if
 * you're logged in.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';
import { clearCartAndSave } from './actions';


/**
 * Display the modal dialog to confirm a user wants to clear their current cart.
 */
class CartClearModalComponent extends React.Component {
    constructor() {
        super();
        this.handleConfirmClearClick = this.handleConfirmClearClick.bind(this);
    }

    /**
     * Called when a user clicks the modal button to confirm clearing the cart.
     */
    handleConfirmClearClick() {
        const { onClearCartClick, closeClickHandler } = this.props;
        onClearCartClick();
        closeClickHandler();
    }

    render() {
        const { cartName, closeClickHandler, inProgress } = this.props;
        return (
            <Modal labelId="clear-cart-label" descriptionId="clear-cart-description" focusId="clear-cart-close">
                <ModalHeader labelId="clear-cart-label" title={`Clear entire cart contents${cartName ? `: ${cartName}` : ''}`} closeModal={closeClickHandler} />
                <ModalBody>
                    <p id="clear-cart-description">Clearing the cart is not reversible.</p>
                </ModalBody>
                <ModalFooter
                    closeModal={<button type="button" id="clear-cart-close" onClick={closeClickHandler} className="btn btn-default">Cancel</button>}
                    submitBtn={<button type="button" onClick={this.handleConfirmClearClick} disabled={inProgress} className="btn btn-danger" id="clear-cart-submit">Clear</button>}
                    dontClose
                />
            </Modal>
        );
    }
}

CartClearModalComponent.propTypes = {
    /** Name of current cart */
    cartName: PropTypes.string,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool,
    /** Function to call to close the Clear Cart modal */
    closeClickHandler: PropTypes.func.isRequired,
    /** Function to call to clear the cart from the Redux store */
    onClearCartClick: PropTypes.func.isRequired,
};

CartClearModalComponent.defaultProps = {
    cartName: '',
    inProgress: false,
};

CartClearModalComponent.mapStateToProps = (state) => ({
    cartName: state.savedCartObj && state.savedCartObj.name,
    inProgress: state.inProgress,
});

CartClearModalComponent.mapDispatchToProps = (dispatch, ownProps) => ({
    onClearCartClick: () => dispatch(clearCartAndSave(ownProps.fetch)),
});

const CartClearModalInternal = connect(CartClearModalComponent.mapStateToProps, CartClearModalComponent.mapDispatchToProps)(CartClearModalComponent);

export const CartClearModal = ({ closeClickHandler }, { fetch }) => (
    <CartClearModalInternal closeClickHandler={closeClickHandler} fetch={fetch} />
);

CartClearModal.propTypes = {
    /** Function to call to close the Cart Clear modal */
    closeClickHandler: PropTypes.func.isRequired,
};

CartClearModal.contextTypes = {
    fetch: PropTypes.func,
};


/**
 * Display an actuator button to clear the current cart, and handle the resulting warning modal.
 */
class CartClearButtonComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            /** True if modal about clearing the cart is visible */
            modalOpen: false,
        };
        this.handleClearCartClick = this.handleClearCartClick.bind(this);
        this.handleCloseClick = this.handleCloseClick.bind(this);
    }

    /**
     * Handle a click in the Clear Cart button by showing the confirmation modal.
     */
    handleClearCartClick() {
        this.setState({ modalOpen: true });
    }

    /**
     * Handle a click for closing the modal without doing anything.
     */
    handleCloseClick() {
        this.setState({ modalOpen: false });
    }

    render() {
        const { elements, inProgress } = this.props;
        if (elements.length > 0 && !this.props.locked) {
            return (
                <div className="cart-tools-extras__button">
                    <button type="button" disabled={inProgress} onClick={this.handleClearCartClick} id="clear-cart-actuator" className="btn btn-danger btn-sm btn-inline">Clear cart</button>
                    {this.state.modalOpen ?
                        <CartClearModal closeClickHandler={this.handleCloseClick} />
                    : null}
                </div>
            );
        }
        return null;
    }
}

CartClearButtonComponent.propTypes = {
    /** Current contents of cart */
    elements: PropTypes.array,
    /** True if cart updating operation is in progress */
    inProgress: PropTypes.bool,
    /** True if cart is locked */
    locked: PropTypes.bool,
};

CartClearButtonComponent.defaultProps = {
    elements: [],
    inProgress: false,
    locked: false,
};

CartClearButtonComponent.mapStateToProps = (state) => ({
    elements: state.elements,
    inProgress: state.inProgress,
    locked: state.locked,
});
const CartClearButton = connect(CartClearButtonComponent.mapStateToProps)(CartClearButtonComponent);

export default CartClearButton;
