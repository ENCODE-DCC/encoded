import React from 'react';
import PropTypes from 'prop-types';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/bootstrap/modal';


/** List of object @type allowed in the cart. */
const allowedTypes = [
    'Experiment',
];
/** Maximum number of elements allowed in cart while not logged in */
export const CART_MAXIMUM_ELEMENTS_LOGGEDOUT = 4000;


/**
 * Displays a modal to tell the logged-out user that there are too many datasets than can be added
 */
export const MaximumElementsLoggedoutModal = ({ closeClickHandler }) => (
    <Modal>
        <ModalHeader title="Too many experiments selected" closeModal={closeClickHandler} />
        <ModalBody>
            <p>You can add a maximum of {CART_MAXIMUM_ELEMENTS_LOGGEDOUT} experiments to a cart if you have not logged in.</p>
        </ModalBody>
        <ModalFooter closeModal={closeClickHandler} />
    </Modal>
);

MaximumElementsLoggedoutModal.propTypes = {
    /** Callback to close the modal */
    closeClickHandler: PropTypes.func.isRequired,
};


/**
 * Given an array of search results filters, return an array with any "type" filters for types not
 * qualified for a cart filtered out. If no "type" filters exist after this, then return an empty
 * array, as we need at least one qualifying "type" filter to add anything to the cart.
 * @param {array} resultFilters Object with types to be filtered
 * @return {array} All `items` with types in `allowedTypes`
 */
const getAllowedResultFilters = (resultFilters) => {
    const allowedFilters = resultFilters.filter(resultFilter => resultFilter.field !== 'type' || allowedTypes.indexOf(resultFilter.term) >= 0);
    return allowedFilters.some(filter => filter.field === 'type') ? allowedFilters : [];
};

export default getAllowedResultFilters;
