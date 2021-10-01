import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';
import * as Pager from '../../libs/ui/pager';
import { useMount } from '../hooks';
import { Listing } from '../search';
import { cartManualSetOperationInProgress } from './actions';
import * as constants from './constants';
import CartViewContext from './context';
import { calcTotalPageCount, getSeriesDatasets, isObligateSeries } from './util';


/**
 * Display a confirmation modal for removing a series object from the cart. This modal doesn't use
 * the standard Modal mechanism because nested modals get awkward.
 */
const CartSeriesConfirmation = ({ requestRemoveConfirmation }) => {
    const closeButton = React.useRef();

    React.useEffect(() => {
        // Focus the close button when the modal is opened.
        closeButton.current.focus();
    });

    return (
        <div className="cart-series-confirmation">
            <div className="cart-series-confirmation__controls">
                <button
                    type="button"
                    className="btn btn-sm btn-danger cart-series-confirmation__button cart-series-confirmation__button--confirm"
                    onClick={() => requestRemoveConfirmation(true)}
                >
                    Remove series and datasets
                </button>
                <button
                    id="care-series-confirmation-close"
                    type="button"
                    className="btn btn-sm cart-series-confirmation__button cart-series-confirmation__button--cancel"
                    onClick={() => requestRemoveConfirmation(false)}
                    ref={closeButton}
                >
                    Cancel
                </button>
            </div>
            <div className="cart-series-confirmation__help">
                Removing a series object also removes its datasets from the cart. This action is
                not reversible.
            </div>
        </div>
    );
};

CartSeriesConfirmation.propTypes = {
    /** Called when the user confirms or cancels removing a series object */
    requestRemoveConfirmation: PropTypes.func.isRequired,
};


/**
 * Displays the modal unconditionally that lets you manage a series object in the cart.
 */
const ManageSeriesModalComponent = ({ series, onCloseModalClick, setCartInProgress }) => {
    /** True if the user has requested removing a series object, but not yet confirmed */
    const [isRemoveRequested, setIsRemoveRequested] = React.useState(false);
    /** True if the user has confirmed removing the series object from the cart */
    const [isRemoveConfirmed, setIsRemoveConfirmed] = React.useState(false);
    /** Get all datasets currently in the cart to filter against `series` related_datasets */
    const { allDatasetsInCart, setManagedSeries } = React.useContext(CartViewContext);
    /** Current displayed page of related datasets */
    const [currentPage, setCurrentPage] = React.useState(0);

    // Get the datasets that are part of the series.
    const seriesDatasets = getSeriesDatasets(series, allDatasetsInCart);
    const totalPageCount = calcTotalPageCount(seriesDatasets.length, constants.SERIES_MANAGER_DATASET_COUNT);
    const pageStartIndex = currentPage * constants.SERIES_MANAGER_DATASET_COUNT;
    const currentPageElements = seriesDatasets.slice(pageStartIndex, pageStartIndex + constants.SERIES_MANAGER_DATASET_COUNT);

    // Give a different hint on removing datasets depending on whether the series is obligatory.
    const datasetRemovalNote = isObligateSeries(series)
        ? 'Remove the series to remove these datasets from the cart.'
        : 'Remove independently of the series, or remove all by removing the series';


    /**
     * Called when the user confirms closing the modal without taking action.
     */
    const onClose = () => {
        setCartInProgress(false);
        onCloseModalClick();
    };

    /**
     * Called when the user clicks the "Remove series and datasets" button. Sets new properties to
     * pass to `Listing` to trigger the removal of the series and its datasets.
     * @param {boolean} isConfirmed True if the user confirms removing the series object
     */
    const requestRemoveConfirmation = (isConfirmed) => {
        setIsRemoveRequested(false);
        if (isConfirmed) {
            setIsRemoveConfirmed(true);
        }
        setCartInProgress(false);
    };

    /**
     * Called when the user clicks the cart icon in the series management modal to request to
     * remove the series object from the cart.
     */
    const requestRemove = () => {
        setCartInProgress(true);
        setIsRemoveRequested(true);
    };

    /**
     * Called when removing the series object from the cart has completed.
     */
    const onCompleteRemoveSeries = () => {
        setManagedSeries(null);
    };

    useMount(() => (
        // Clicking a link in the modal to the series or related dataset pages also sets the cart
        // to not-in-progress.
        () => {
            setCartInProgress(false);
        }
    ));

    React.useEffect(() => {
        // Reset the current page when the user removes enough related datasets from the cart that
        // the current page is beyond the new last page.
        if (currentPage > totalPageCount - 1) {
            setCurrentPage(totalPageCount - 1);
        }
    });

    return (
        <Modal focusId="manage-series-close" closeModal={onClose}>
            <ModalHeader title="Manage series" closeModal={onClose} />
            <ModalBody addCss="manage-series">
                <div className="manage-series__header">
                    <h2>Series</h2>
                </div>
                <ul className="result-table result-table--manage-series">
                    <li className="result-item__wrapper">
                        {Listing({
                            context: series,
                            cartControls: true,
                            mode: 'cart-view',
                            removeConfirmation: {
                                requestRemove,
                                requestRemoveConfirmation,
                                isRemoveConfirmed,
                                onCompleteRemoveSeries,
                            },
                        })}
                        {isRemoveRequested && <div className="manage-series__cover" />}
                    </li>
                </ul>
                {seriesDatasets.length > 0 && (
                    <>
                        <div className="manage-series__header">
                            <div className="manage-series__header-title">
                                <h2>Additional datasets</h2>
                                <div className="manage-series__removal-note">{datasetRemovalNote}</div>
                            </div>
                            <div className="manage-series__header-pagination">
                                {totalPageCount > 1 &&
                                    <Pager.Simple total={totalPageCount} current={currentPage} updateCurrentPage={setCurrentPage} />
                                }
                            </div>
                        </div>
                        <ul className="result-table result-table">
                            {currentPageElements.map((dataset) => (
                                <li key={dataset['@id']} className="result-item__wrapper">
                                    {Listing({
                                        context: dataset,
                                        cartControls: !isObligateSeries(series),
                                        mode: 'cart-view',
                                        removeConfirmation: {
                                            requestRemove,
                                            requestRemoveConfirmation,
                                            isRemoveConfirmed,
                                        },
                                    })}
                                    {isRemoveRequested && <div className="manage-series__cover" />}
                                </li>
                            ))}
                        </ul>
                    </>
                )}
                {isRemoveRequested && (
                    <>
                        <div className="manage-series__cover" />
                        <CartSeriesConfirmation requestRemoveConfirmation={requestRemoveConfirmation} />
                    </>
                )}
            </ModalBody>
            <ModalFooter
                closeModal={
                    <button
                        type="button"
                        id="manage-series-close"
                        onClick={onClose}
                    >
                        Close
                    </button>
                }
            />
        </Modal>
    );
};

ManageSeriesModalComponent.propTypes = {
    /** Series that contains the given datasets */
    series: PropTypes.object.isRequired,
    /** Called when the user closes the modal */
    onCloseModalClick: PropTypes.func.isRequired,
    /** Called to set the in-progress state of the cart when confirming removing the series */
    setCartInProgress: PropTypes.func.isRequired,
};

ManageSeriesModalComponent.mapDispatchToProps = (dispatch) => ({
    setCartInProgress: (isInProgress) => dispatch(cartManualSetOperationInProgress(isInProgress)),
});

export const ManageSeriesModal = connect(null, ManageSeriesModalComponent.mapDispatchToProps)(ManageSeriesModalComponent);


export const useSeriesManager = () => {
    // Series currently appearing in series manager modal.
    const [singleSeries, setSingleSeries] = React.useState(null);

    /**
     * Sets the series and its datasets to manage within the modal that appears when these values get set.
     */
    const setManagedSeries = (series) => {
        setSingleSeries(series);
    };

    /**
     * True if a series and its related datasets have been set for managing.
     */
    const isSeriesManagerOpen = singleSeries;

    return {
        // States
        isSeriesManagerOpen,
        managedSeries: singleSeries,
        // Actions
        setManagedSeries,
    };
};


/**
 * Renders the button that triggers the display of the series management modal.
 */
const SeriesManagerActuator = ({ singleSeries }) => {
    const { setManagedSeries } = React.useContext(CartViewContext);

    return (
        <div className="result-item__controls">
            <button type="button" className="btn btn-info btn-xs" onClick={() => setManagedSeries(singleSeries)}>
                {`Remove series datasets for ${singleSeries.accession}`}
            </button>
        </div>
    );
};

SeriesManagerActuator.propTypes = {
    /** Series that contains the given datasets */
    singleSeries: PropTypes.object.isRequired,
};

export default SeriesManagerActuator;
