import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';
import { triggerAlert } from './actions';
import { CART_MAX_ELEMENTS } from './util';


/**
 * Display a modal warning the user that they cannot add any more elements to the cart because
 * they've hit the maximum allowed number of elements in a cart.
 */
const CartMaxElementsWarningComponent = ({ closeMaxElementsWarning }) => {
    /** Ref to the submit button so we can focus it on mount */
    const submitButton = React.useRef(null);

    /**
     * Called when the use clicks the modal's Close button.
     */
    const handleClose = () => {
        closeMaxElementsWarning();
    };

    React.useEffect(() => {
        // The submit button has the title "Close" in this case.
        submitButton.current.focus();
    }, []);

    return (
        <Modal closeModal={handleClose}>
            <ModalHeader title="Cart maximum size" closeModal={handleClose} />
            <ModalBody>
                Carts can hold a maximum of {CART_MAX_ELEMENTS} datasets.
            </ModalBody>
            <ModalFooter submitBtn={<button ref={submitButton} onClick={handleClose} className="btn btn-info">Close</button>} />
        </Modal>
    );
};

CartMaxElementsWarningComponent.propTypes = {
    closeMaxElementsWarning: PropTypes.func.isRequired,
};

CartMaxElementsWarningComponent.mapDispatchToProps = dispatch => ({
    closeMaxElementsWarning: () => dispatch(triggerAlert(null)),
});

const CartMaxElementsWarning = connect(null, CartMaxElementsWarningComponent.mapDispatchToProps)(CartMaxElementsWarningComponent);

export default CartMaxElementsWarning;
