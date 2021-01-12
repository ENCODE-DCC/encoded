import React from 'react';
import PropTypes from 'prop-types';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';


/**
 * Display a modal warning the user that they need to log in to use carts.
 */
const CartLoggedOutWarning = ({ closeModalHandler }) => {
    /** Ref to the submit button so we can focus it on mount */
    const submitButton = React.useRef(null);

    /**
     * Called when the use clicks the modal's login button. Just close the modal because <App>
     * handles the login.
     */
    const handleSubmit = () => {
        closeModalHandler();
    };

    React.useEffect(() => {
        submitButton.current.focus();
    }, []);

    return (
        <Modal closeModal={closeModalHandler}>
            <ModalHeader title="Sign in to create and modify carts" closeModal={closeModalHandler} />
            <ModalBody>
                Carts can hold groups of Experiments, Annotations, and/or Functional
                Characterization datasets. Please sign in (or create account) to use this feature.
            </ModalBody>
            <ModalFooter
                closeModal={closeModalHandler}
                cancelTitle={'Close'}
                submitBtn={<button ref={submitButton} data-trigger="login" onClick={handleSubmit} className="btn btn-info">Sign in / Create account</button>}
            />
        </Modal>
    );
};

CartLoggedOutWarning.propTypes = {
    /** Function to call to close the warning modal */
    closeModalHandler: PropTypes.func.isRequired,
};

export default CartLoggedOutWarning;


/**
 * Custom hook to handle warnings to log in before using carts.
 * @param {bool} visible True to make the modal visible initially
 *
 * @return {array} States and actions for logged-out warning
 * state.isWarningVisible {bool} True if the warning modal is visible
 * actions.setIsWarningVisible Pass True to make the warning modal visible
 * actions.handleCloseWarning Call to close the warning modal
 */
export const useLoggedOutWarning = (visible) => {
    const [isWarningVisible, setIsWarningVisible] = React.useState(visible);

    /**
     * Called when the user requests to close the warning modal.
     */
    const handleCloseWarning = () => {
        setIsWarningVisible(false);
    };

    return [
        // states
        {
            isWarningVisible,
        },
        // actions
        {
            setIsWarningVisible,
            handleCloseWarning,
        },
    ];
};
