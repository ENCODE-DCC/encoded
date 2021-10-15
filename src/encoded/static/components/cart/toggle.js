/**
 * Renders and handles a button to toggle items in/out of the cart.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';
import { svgIcon } from '../../libs/svg-icons';
import { uc } from '../../libs/constants';
import {
    addMultipleToCartAndSave,
    addToCartAndSave,
    removeFromCartAndSave,
    removeMultipleFromCartAndSave,
    triggerAlert,
} from './actions';
import CartLoggedOutWarning, { useLoggedOutWarning } from './loggedout_warning';
import CartMaxElementsWarning from './max_elements_warning';
import { allowedDatasetTypes, CART_MAX_ELEMENTS, DEFAULT_FILE_VIEW_NAME } from './util';
import { atIdToType, hasType, truncateString } from '../globals';


/**
 * Present an alert when the user tries to remove a series object from the cart to indicate that
 * this also removes its related datasets from the cart.
 */
const SeriesRemovalWarning = ({ onCloseWarning }) => {
    /** Ref to the Close button so we can focus it on mount */
    const closeButton = React.useRef(null);

    /**
     * Called when the user closes the warning alert to not take action.
     */
    const onCloseWithoutAction = () => {
        onCloseWarning(false);
    };

    React.useEffect(() => {
        // Focus the Close button on mount.
        closeButton.current.focus();
    }, []);

    return (
        <Modal closeModal={onCloseWithoutAction}>
            <ModalHeader title="Remove series from cart" closeModal={onCloseWithoutAction} />
            <ModalBody>
                Removing a series object from the cart also removes the displayed additional
                datasets from the cart. This action is not reversible.
            </ModalBody>
            <ModalFooter
                closeModal={<button type="button" ref={closeButton} className="btn btn-info" onClick={onCloseWithoutAction}>Cancel</button>}
                submitBtn={<button type="button" className="btn btn-info" onClick={() => onCloseWarning(true)}>Remove series and related datasets</button>}
            />
        </Modal>
    );
};

SeriesRemovalWarning.propTypes = {
    /** Called when the user closes the warning either to confirm or cancel the removal */
    onCloseWarning: PropTypes.func.isRequired,
};


/**
 * Initiates the immediate removal of a series object and its related datasets from the cart.
 * @param {object} seriesElement Series object to remove from the cart
 * @param {function} removeSeriesDatasets Function to remove the series and its datasets from the cart
 * @returns {Promise} Promise that resolves when the series and its datasets are removed from the cart
 */
const removeSeries = async (seriesElement, removeSeriesDatasets) => {
    const seriesAndRelatedDatasetPaths = [seriesElement].concat(seriesElement.related_datasets);
    return removeSeriesDatasets(seriesAndRelatedDatasetPaths);
};


/**
 * Renders and controls the individual cart toggle icons.
 */
const CartToggleComponent = ({
    elements,
    targetElement,
    savedCartObj,
    displayName,
    css,
    onRemoveFromCartClick,
    onAddToCartClick,
    addSeriesDatasets,
    removeSeriesDatasets,
    removeConfirmation,
    loggedIn,
    inProgress,
    showMaxElementsWarning,
}) => {
    /** Get hooks for the logged-out warning modal */
    const [loggedOutWarningStates, loggedOutWarningActions] = useLoggedOutWarning(false);

    React.useEffect(() => {
        if (removeConfirmation.isRemoveConfirmed) {
            // Combine the series path with the paths of its related datasets and remove them all
            // from the cart.
            removeSeries(targetElement, removeSeriesDatasets).then(() => {
                if (removeConfirmation.onCompleteRemoveSeries) {
                    removeConfirmation.onCompleteRemoveSeries();
                }
            });
        }
    }, [removeConfirmation.isRemoveConfirmed]);

    /**
     * Called when user clicks a toggle button. Depending on whether the element is already in the
     * cart, call the Redux action either to remove from or add to the cart.
     */
    const handleClick = () => {
        if (loggedIn) {
            if (elements.indexOf(targetElement['@id']) === -1) {
                // Toggling an element on (adding to cart) so first make sure we don't exceed the
                // maximum number of elements in the cart with the addition.
                if (savedCartObj.elements.length + 1 > CART_MAX_ELEMENTS) {
                    showMaxElementsWarning();
                } else {
                    if (hasType(targetElement, 'Series')) {
                        // Extract allowed child datasets from the series and add them to the cart.
                        const relatedDatasetPaths = targetElement.related_datasets
                            .map((relatedDataset) => relatedDataset['@id'])
                            .filter((path) => allowedDatasetTypes[atIdToType(path)]);
                        const seriesAndRelatedDatasetPaths = [targetElement['@id']].concat(relatedDatasetPaths);
                        addSeriesDatasets(seriesAndRelatedDatasetPaths);
                    }
                    onAddToCartClick();
                }
            } else if (hasType(targetElement, 'Series')) {
                // Indicate that the user has requested removing a series object from the cart and
                // therefore we need some user action.
                if (removeConfirmation.immediate) {
                    removeSeries(targetElement, removeSeriesDatasets);
                } else if (removeConfirmation.requestRemove) {
                    removeConfirmation.requestRemove();
                }
            } else {
                // Toggling a single element off (removing from cart).
                onRemoveFromCartClick();
            }
        } else {
            loggedOutWarningActions.setIsWarningVisible(true);
        }
    };

    const inCart = elements.indexOf(targetElement['@id']) > -1;
    const cartName = (savedCartObj && Object.keys(savedCartObj).length > 0 ? savedCartObj.name : '');
    const inCartToolTip = `${inCart ? 'Remove item from cart' : 'Add item to cart'}${cartName ? ` ${uc.ldquo}${cartName}${uc.rdquo}` : ''}`;
    const inProgressToolTip = inProgress ? 'Cart operation in progress' : '';
    const locked = savedCartObj && Object.keys(savedCartObj).length > 0 ? savedCartObj.locked : false;
    const lockedToolTip = locked ? `Cart ${uc.ldquo}${cartName}${uc.rdquo} locked` : '';

    // "name" attribute needed for BDD test targeting.
    return (
        <div className={`cart-toggle${inCart ? ' cart-toggle--in-cart' : ''}${css ? ` ${css}` : ''}`}>
            {displayName && savedCartObj && savedCartObj.name ? <div className="cart-toggle__name">{truncateString(savedCartObj.name, 22)}</div> : null}
            <button
                type="button"
                onClick={handleClick}
                disabled={inProgress || locked}
                title={inProgressToolTip || lockedToolTip || inCartToolTip}
                aria-pressed={inCart}
                aria-label={inProgressToolTip || lockedToolTip || inCartToolTip}
                name={targetElement['@id']}
            >
                {svgIcon('cart', inProgress || locked ? { fill: '#a0a0a0', stroke: '#a0a0a0' } : null)}
            </button>
            {loggedOutWarningStates.isWarningVisible ? <CartLoggedOutWarning closeModalHandler={loggedOutWarningActions.handleCloseWarning} /> : null}
        </div>
    );
};

CartToggleComponent.propTypes = {
    /** Current contents of cart; array of @ids */
    elements: PropTypes.array,
    /** Current cart saved object */
    savedCartObj: PropTypes.object,
    /** @id of element being added or removed */
    targetElement: PropTypes.object.isRequired,
    /** True to display cart name */
    displayName: PropTypes.bool.isRequired,
    /** CSS to add to toggle */
    css: PropTypes.string.isRequired,
    /** Function to call to add `elementAtId` to cart */
    onAddToCartClick: PropTypes.func.isRequired,
    /** Function to call to remove `elementAtId` from cart  */
    onRemoveFromCartClick: PropTypes.func.isRequired,
    /** Function to add a series's related datasets to the cart */
    addSeriesDatasets: PropTypes.func.isRequired,
    /** Function to remove a series's related datasets from the cart */
    removeSeriesDatasets: PropTypes.func.isRequired,
    /** Needed for series removals that require user confirmation */
    removeConfirmation: PropTypes.shape({
        /** Called by cart toggle when the user requests removing a series object from the cart */
        requestRemove: PropTypes.func,
        /** Called when the user confirms removing a series object from the cart */
        requestRemoveConfirmation: PropTypes.func,
        /** True if the user has confirmed they want to remove the series object from the cart */
        isRemoveConfirmed: PropTypes.bool,
        /** Called once removing a series object from the cart has completed */
        onCompleteRemoveSeries: PropTypes.func,
        /** True to remove series and its related datasets without a confirmation modal */
        immediate: PropTypes.bool,
    }),
    /** True if user is logged in */
    loggedIn: PropTypes.bool,
    /** True if cart operation is in progress */
    inProgress: PropTypes.bool,
    /** Call to show the max elements warning alert */
    showMaxElementsWarning: PropTypes.func.isRequired,
};

CartToggleComponent.defaultProps = {
    elements: [],
    savedCartObj: null,
    removeConfirmation: {},
    loggedIn: false,
    inProgress: false,
};

const mapStateToProps = (state, ownProps) => ({
    elements: state.elements,
    savedCartObj: state.savedCartObj,
    displayName: ownProps.displayName,
    inProgress: state.inProgress,
    targetElement: ownProps.element,
    css: ownProps.css,
    loggedIn: ownProps.loggedIn,
});

const mapDispatchToProps = (dispatch, ownProps) => ({
    onAddToCartClick: () => dispatch(addToCartAndSave(ownProps.element['@id'], ownProps.fetch)),
    onRemoveFromCartClick: () => dispatch(removeFromCartAndSave(ownProps.element, ownProps.fileViewTitle, ownProps.fetch)),
    addSeriesDatasets: (elementsForCart) => dispatch(addMultipleToCartAndSave(elementsForCart, ownProps.fetch)),
    removeSeriesDatasets: (elementsForCart) => dispatch(removeMultipleFromCartAndSave(elementsForCart, ownProps.fileViewTitle, ownProps.fetch)),
    showMaxElementsWarning: () => dispatch(triggerAlert(<CartMaxElementsWarning />)),
});

const CartToggleInternal = connect(mapStateToProps, mapDispatchToProps)(CartToggleComponent);


const CartToggle = (props, reactContext) => (
    <CartToggleInternal
        element={props.element}
        displayName={props.displayName}
        fileViewTitle={DEFAULT_FILE_VIEW_NAME}
        css={props.css}
        removeConfirmation={props.removeConfirmation}
        loggedIn={!!(reactContext.session && reactContext.session['auth.userid'])}
        fetch={reactContext.fetch}
    />
);

CartToggle.propTypes = {
    /** Object being added */
    element: PropTypes.object.isRequired,
    /** True to show cart name next to toggle */
    displayName: PropTypes.bool,
    /** Needed for series removals that require user confirmation */
    removeConfirmation: PropTypes.shape({
        /** Called by cart toggle when the user requests removing a series object from the cart */
        requestRemove: PropTypes.func,
        /** Called when the user confirms removing a series object from the cart */
        requestRemoveConfirmation: PropTypes.func,
        /** True if the user has confirmed they want to remove the series object from the cart */
        isRemoveConfirmed: PropTypes.bool,
    }),
    /** CSS to add to toggle */
    css: PropTypes.string,
};

CartToggle.defaultProps = {
    displayName: false,
    removeConfirmation: {},
    css: '',
};

CartToggle.contextTypes = {
    session: PropTypes.object,
    fetch: PropTypes.func,
};

export default CartToggle;
