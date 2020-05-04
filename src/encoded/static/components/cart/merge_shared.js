/**
 * Button to add shared cart elements to the user's cart. The merging doesn't happen until the user
 * confirms the action in a modal presented here.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';
import { addMultipleToCartAndSave } from './actions';
import { MaximumElementsLoggedoutModal, CART_MAXIMUM_ELEMENTS_LOGGEDOUT } from './util';


class CartMergeSharedComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            /** True if modal for merging a shared cart displayed */
            mergeCartDisplayed: false,
            /** True if shared cart has more than maximum number of elements while not logged in */
            overMaximumError: false,
        };
        this.handleMergeButtonClick = this.handleMergeButtonClick.bind(this);
        this.handleMergeModalClose = this.handleMergeModalClose.bind(this);
        this.handleErrorModalClose = this.handleErrorModalClose.bind(this);
        this.handleClick = this.handleClick.bind(this);
    }

    /**
     * Called when the user requests merging the shared cart into their own, resulting in a modal
     * for the user to confirm this action, or a modal to indicate this would result in more items
     * in a logged-out user's cart than allowed.
     */
    handleMergeButtonClick() {
        const { viewableDatasets, loggedIn } = this.props;
        if (loggedIn || viewableDatasets.length <= CART_MAXIMUM_ELEMENTS_LOGGEDOUT) {
            this.setState({ mergeCartDisplayed: true });
        } else {
            this.setState({ overMaximumError: true });
        }
    }

    /**
     * Called when the user wants to close the modal for confirming they want to merge carts.
     */
    handleMergeModalClose() {
        this.setState({ mergeCartDisplayed: false });
    }

    /**
     * Called when the user want to close the modal warning that merging carts would result in more
     * items in their cart than allowed for logged-out users.
     */
    handleErrorModalClose() {
        this.setState({ overMaximumError: false });
    }

    /**
     * Called when the user confirms they want to merge the shared cart into their own.
     */
    handleClick() {
        this.props.onMergeCartClick(this.props.viewableDatasets);
    }

    render() {
        const { sharedCartObj, savedCartObj, viewableDatasets } = this.props;

        // Show the "Add to current cart" button if the shared cart has elements and we're not looking
        // at our own shared cart.
        if ((viewableDatasets && viewableDatasets.length > 0) && (sharedCartObj['@id'] !== savedCartObj['@id'])) {
            const cartName = (savedCartObj && Object.keys(savedCartObj).length > 0 ? savedCartObj.name : '');
            return (
                <span>
                    <button className="btn btn-info btn-sm" disabled={this.props.inProgress} onClick={this.handleMergeButtonClick}>Add to current cart</button>
                    {this.state.mergeCartDisplayed ?
                        <Modal labelId="merge-cart-label" descriptionId="merge-cart-description" focusId="merge-cart-close">
                            <ModalHeader labelId="merge-cart-label" title={`Add items to cart: ${cartName || ''}`} closeModal />
                            <ModalBody>
                                <p id="merge-cart-description">
                                    Any items already in {cartName ? <span>&ldquo;{cartName}&rdquo;</span> : <span>your cart</span>} won&rsquo;t be affected
                                    and won&rsquo;t be duplicated.
                                </p>
                            </ModalBody>
                            <ModalFooter
                                closeModal={<button id="merge-cart-close" className="btn btn-info" onClick={this.handleMergeModalClose}>Close</button>}
                                submitBtn={this.handleClick}
                                submitTitle="Add items to current cart"
                            />
                        </Modal>
                    : null}
                    {this.state.overMaximumError ?
                        <MaximumElementsLoggedoutModal closeClickHandler={this.handleErrorModalClose} />
                    : null}
                </span>
            );
        }

        return null;
    }
}

CartMergeSharedComponent.propTypes = {
    /** Shared cart object */
    sharedCartObj: PropTypes.object,
    /** Current user's saved cart object */
    savedCartObj: PropTypes.object,
    /** Viewable cart element @ids */
    viewableDatasets: PropTypes.array,
    /** Called to merge shared cart with own cart */
    onMergeCartClick: PropTypes.func.isRequired,
    /** True if cart updating operation is in progress */
    inProgress: PropTypes.bool.isRequired,
    /** True if user is logged in */
    loggedIn: PropTypes.bool,
};

CartMergeSharedComponent.defaultProps = {
    sharedCartObj: {},
    savedCartObj: null,
    viewableDatasets: null,
    loggedIn: false,
};

const mapStateToProps = (state, ownProps) => ({
    elements: state.elements,
    savedCartObj: state.savedCartObj,
    inProgress: state.inProgress,
    sharedCartObj: ownProps.sharedCartObj,
    viewableDatasets: ownProps.viewableDatasets,
    adminUser: ownProps.adminUser,
});

const mapDispatchToProps = (dispatch, ownProps) => ({
    onMergeCartClick: elementAtIds => dispatch(addMultipleToCartAndSave(elementAtIds, ownProps.loggedIn, ownProps.fetch)),
});

const CartMergeSharedInternal = connect(mapStateToProps, mapDispatchToProps)(CartMergeSharedComponent);


/**
 * Wrapper component to receive React <App> context and pass them to <CartMergeSharedInternal>.
 */
const CartMergeShared = ({ sharedCartObj, viewableDatasets }, reactContext) => (
    <CartMergeSharedInternal
        sharedCartObj={sharedCartObj}
        viewableDatasets={viewableDatasets}
        loggedIn={!!(reactContext.session && reactContext.session['auth.userid'])}
        sessionProperties={reactContext.session_properties}
        fetch={reactContext.fetch}
    />
);

CartMergeShared.propTypes = {
    /** Shared cart object */
    sharedCartObj: PropTypes.object.isRequired,
    /** Viewable cart element @ids */
    viewableDatasets: PropTypes.array,
};

CartMergeShared.defaultProps = {
    viewableDatasets: null,
};

CartMergeShared.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
    fetch: PropTypes.func,
};

export default CartMergeShared;
