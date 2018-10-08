import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/bootstrap/modal';
import { addMultipleToCart } from './actions';
import { MaximumElementsLoggedoutModal, CART_MAXIMUM_ELEMENTS_LOGGEDOUT } from './util';


/**
 * Button to add shared cart elements to the local cart.
 */
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
        this.handleClick = this.handleClick.bind(this);
        this.handleErrorModalClose = this.handleErrorModalClose.bind(this);
    }

    handleMergeButtonClick() {
        const { viewableElements, loggedIn } = this.props;
        if (loggedIn || viewableElements.length <= CART_MAXIMUM_ELEMENTS_LOGGEDOUT) {
            this.setState({ mergeCartDisplayed: true });
        } else {
            this.setState({ overMaximumError: true });
        }
    }

    handleMergeModalClose() {
        this.setState({ mergeCartDisplayed: false });
    }

    handleClick() {
        this.props.onMergeCartClick(this.props.viewableElements);
    }

    handleErrorModalClose() {
        this.setState({ overMaximumError: false });
    }

    render() {
        const { sharedCartObj, savedCartObj, viewableElements, inProgress } = this.props;

        // Show the "Add to my cart" button if the shared cart has elements and we're not looking
        // at our own shared cart.
        if ((viewableElements && viewableElements.length > 0) && (sharedCartObj['@id'] !== savedCartObj['@id'])) {
            return (
                <span>
                    <button className="btn btn-info btn-sm" disabled={inProgress} onClick={this.handleMergeButtonClick}>Add to my cart</button>
                    {this.state.mergeCartDisplayed ?
                        <Modal>
                            <ModalHeader title="Add shared cart items to my cart" closeModal />
                            <ModalBody>
                                <p>Add the contents of this shared cart to your cart. Any items already in your cart won&rsquo;t be affected.</p>
                            </ModalBody>
                            <ModalFooter
                                closeModal={<button className="btn btn-info" onClick={this.handleMergeModalClose}>Close</button>}
                                submitBtn={this.handleClick}
                                submitTitle="Add items to my cart"
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
    viewableElements: PropTypes.array,
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
    viewableElements: null,
    loggedIn: false,
};

const mapStateToProps = (state, ownProps) => ({
    cart: state.cart,
    savedCartObj: state.savedCartObj,
    inProgress: state.inProgress,
    sharedCartObj: ownProps.sharedCartObj,
    viewableElements: ownProps.viewableElements,
    loggedIn: ownProps.loggedIn,
});

const mapDispatchToProps = dispatch => ({
    onMergeCartClick: elementAtIds => dispatch(addMultipleToCart(elementAtIds)),
});

const CartMergeSharedInternal = connect(mapStateToProps, mapDispatchToProps)(CartMergeSharedComponent);

const CartMergeShared = (props, reactContext) => {
    const loggedIn = !!(reactContext.session && reactContext.session['auth.userid']);
    return <CartMergeSharedInternal sharedCartObj={props.sharedCartObj} viewableElements={props.viewableElements} loggedIn={loggedIn} />;
};

CartMergeShared.propTypes = {
    /** Shared cart object */
    sharedCartObj: PropTypes.object.isRequired,
    /** Viewable cart element @ids */
    viewableElements: PropTypes.array,
};

CartMergeShared.defaultProps = {
    viewableElements: null,
};

CartMergeShared.contextTypes = {
    session: PropTypes.object,
};

export default CartMergeShared;
