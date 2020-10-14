/**
 * Small, general components and functions needed by other cart modules.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/bootstrap/modal';


/** List of object @type allowed in the cart. */
const allowedCartTypes = [
    'Patient'
];

/** Maximum number of elements allowed in cart while not logged in */
export const CART_MAXIMUM_ELEMENTS_LOGGEDOUT = 4000;


/**
 * Displays a modal to tell the logged-out user that there are too many datasets than can be added.
 */
export const MaximumElementsLoggedoutModal = ({ closeClickHandler }) => (
    <Modal>
        <ModalHeader title="Too many patients selected" closeModal={closeClickHandler} />
        <ModalBody>
            <p>You can add a maximum of {CART_MAXIMUM_ELEMENTS_LOGGEDOUT} patients to a cohort if you have not logged in.</p>
        </ModalBody>
        <ModalFooter closeModal={closeClickHandler} />
    </Modal>
);

MaximumElementsLoggedoutModal.propTypes = {
    /** Callback when user closes the modal */
    closeClickHandler: PropTypes.func.isRequired,
};


/**
 * Given an array of search-result filters, determine if these filters could potentially lead to
 * search results containing object types allowed in carts, including:
 *  - type=<allowed cart type> included in filters or...
 *  - No "type" filters at all
 * @param {array} resultFilters Search results filter object
 * @return {bool} True if filters might allow for allowed object types in result.
 */
export const isAllowedElementsPossible = (resultFilters) => {
    let typeFilterExists = false;
    const allowedFilters = resultFilters.filter((resultFilter) => {
        if (resultFilter.field === 'type') {
            typeFilterExists = true;
            return allowedCartTypes.indexOf(resultFilter.term) >= 0;
        }
        return false;
    });
    return allowedFilters.length > 0 || !typeFilterExists;
};


/**
 * Get a mutatable array of object types allowed in carts.
 * @return {array} Copy of `allowedCartTypes` global
 */
export const getAllowedCartTypes = () => (
    allowedCartTypes.slice(0)
);


/**
 * Return a new array containing the merged contents of two carts with no duplicates. Contains odd
 * ES6 syntax to merge, clone, and dedupe arrays in one operation.
 * https://stackoverflow.com/questions/1584370/how-to-merge-two-arrays-in-javascript-and-de-duplicate-items#answer-38940354
 * @param {array} cart0AtIds Array of @ids in one cart
 * @param {array} cart1AtIds Array of @ids to merge with `cart0AtIds`
 */
export const mergeCarts = (cart0AtIds, cart1AtIds) => (
    [...new Set([...cart0AtIds, ...cart1AtIds])]
);
