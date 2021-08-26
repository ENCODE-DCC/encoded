/**
 * Displays a button to remove a specific set of datasets from the cart.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';
import { removeMultipleFromCartAndSave } from './actions';
import { DEFAULT_FILE_VIEW_NAME } from './util';


/**
 * Display the modal dialog to confirm a user wants to remove the selected datasets from their
 * cart, and initiate that action if they do.
 */
const CartRemoveElementsModalComponent = ({ elements, closeClickHandler, removeMultipleItems, loggedIn, inProgress }) => {
    /**
     * Called when a user clicks the modal button to confirm removing the selected elements from the
     * cart.
     */
    const handleConfirmRemoveClick = () => {
        if (loggedIn && elements.length > 0) {
            removeMultipleItems(elements);
            closeClickHandler();
        }
    };

    return (
        <Modal labelId="label-remove-selected" descriptionId="description-remove-selected" focusId="close-remove-items">
            <ModalHeader labelId="label-remove-selected" title="Remove selected datasets from cart" closeModal={closeClickHandler} />
            <ModalBody>
                <p id="description-remove-selected">
                    Remove the {elements.length} currently selected datasets from the cart. Series
                    datasets remain in the cart and can only be removed as a part of a series. This
                    action is not reversible.
                </p>
            </ModalBody>
            <ModalFooter
                closeModal={<button type="button" id="close-remove-items" onClick={closeClickHandler} className="btn btn-default">Cancel</button>}
                submitBtn={<button type="button" onClick={handleConfirmRemoveClick} disabled={inProgress} className="btn btn-danger" id="submit-remote-selected">Remove selected</button>}
                dontClose
            />
        </Modal>
    );
};

CartRemoveElementsModalComponent.propTypes = {
    /** Items in the current cart */
    elements: PropTypes.array.isRequired,
    /** Function to call to close the Clear Cart modal */
    closeClickHandler: PropTypes.func.isRequired,
    /** True if user has logged in */
    loggedIn: PropTypes.bool.isRequired,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
    /** Function to call to clear the selected datasets from the Redux store */
    removeMultipleItems: PropTypes.func.isRequired,
};

CartRemoveElementsModalComponent.mapStateToProps = (state, ownProps) => ({
    elements: ownProps.elements,
    closeClickHandler: ownProps.closeClickHandler,
    loggedIn: ownProps.loggedIn,
    inProgress: state.inProgress,
});

CartRemoveElementsModalComponent.mapDispatchToProps = (dispatch, ownProps) => ({
    removeMultipleItems: (elements) => dispatch(removeMultipleFromCartAndSave(elements, ownProps.fileViewTitle, ownProps.fetch)),
});

const CartRemoveElementsModalInternal = connect(CartRemoveElementsModalComponent.mapStateToProps, CartRemoveElementsModalComponent.mapDispatchToProps)(CartRemoveElementsModalComponent);

export const CartRemoveElementsModal = ({ elements, closeClickHandler }, reactContext) => (
    <CartRemoveElementsModalInternal
        elements={elements}
        closeClickHandler={closeClickHandler}
        fileViewTitle={DEFAULT_FILE_VIEW_NAME}
        loggedIn={!!(reactContext.session && reactContext.session['auth.userid'])}
        fetch={reactContext.fetch}
    />
);

CartRemoveElementsModal.propTypes = {
    /** Currently selected datasets to remove from cart as array of @ids */
    elements: PropTypes.array.isRequired,
    /** Function to call to close the Cart Clear modal */
    closeClickHandler: PropTypes.func.isRequired,
};

CartRemoveElementsModal.contextTypes = {
    fetch: PropTypes.func,
    session: PropTypes.object,
};


/**
 * Renders a button to remove all the given datasets from the current cart.
 */
const CartRemoveElementsComponent = ({
    elements,
    loading,
    savedCartObj,
    inProgress,
}) => {
    /** True if the alert modal is visible */
    const [isModalVisible, setIsModalVisible] = React.useState(false);

    // Filter the given elements so we only remove datasets not within a series.
    const nonSeriesDatasets = elements.filter((element) => !element._relatedSeries);

    /**
     * Handle a click in the actuator button to open the alert modal.
     */
    const handleOpenClick = () => {
        setIsModalVisible(true);
    };

    /**
     * Handle a click for closing the modal without doing anything.
     */
    const handleCloseClick = () => {
        setIsModalVisible(false);
    };

    return (
        <div className="remove-multiple-control">
            <button
                type="button"
                disabled={nonSeriesDatasets.length === 0 || loading || inProgress || (savedCartObj && savedCartObj.locked)}
                className="btn btn-info btn-sm"
                onClick={handleOpenClick}
            >
                Remove selected items from cart
            </button>
            <div className="remove-multiple-control__note">
                Any datasets belonging to a series remain after removing the selected items from the cart.
            </div>
            {isModalVisible
                ? <CartRemoveElementsModal elements={nonSeriesDatasets} closeClickHandler={handleCloseClick} />
                : null}
        </div>
    );
};

CartRemoveElementsComponent.propTypes = {
    /** Currently selected datasets to remove from cart as array of @ids */
    elements: PropTypes.array.isRequired,
    /** True if cart currently loading on the page */
    loading: PropTypes.bool.isRequired,
    /** Current cart saved object */
    savedCartObj: PropTypes.object,
    /** True if cart updating operation is in progress */
    inProgress: PropTypes.bool.isRequired,
};

CartRemoveElementsComponent.defaultProps = {
    savedCartObj: null,
};

CartRemoveElementsComponent.mapStateToProps = (state, ownProps) => ({
    elements: ownProps.elements,
    loading: ownProps.loading,
    savedCartObj: state.savedCartObj,
    inProgress: state.inProgress,
});

const CartRemoveElementsInternal = connect(CartRemoveElementsComponent.mapStateToProps)(CartRemoveElementsComponent);


// Public component used to bind to context properties.
const CartRemoveElements = ({ elements, loading }, reactContext) => (
    <CartRemoveElementsInternal elements={elements} loading={loading} fetch={reactContext.fetch} />
);

CartRemoveElements.propTypes = {
    /** Elements to remove from the cart as array of @ids */
    elements: PropTypes.array,
    /** True if cart currently loading on the page */
    loading: PropTypes.bool,
};

CartRemoveElements.defaultProps = {
    elements: [],
    loading: false,
};

CartRemoveElements.contextTypes = {
    fetch: PropTypes.func,
};

export default CartRemoveElements;
