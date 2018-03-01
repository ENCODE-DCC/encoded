import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { removeMultipleFromCartAndSave } from './actions';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/bootstrap/modal';


// Renders a button that allows the user to clear the entire cart contents.
class CartClearComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            /** True if modal about clearing the cart is visible */
            modalOpen: false,
        };
        this.handleClearCartClick = this.handleClearCartClick.bind(this);
        this.handleConfirmClearClick = this.handleConfirmClearClick.bind(this);
        this.handleCloseClick = this.handleCloseClick.bind(this);
    }

    /**
     * Handle a click in the Clear Cart button by showing the confirmation modal.
     */
    handleClearCartClick() {
        this.setState({ modalOpen: true });
    }

    /**
     * Handle a click on the button in the modal confirming clearing the cart.
     */
    handleConfirmClearClick() {
        this.props.onClearCartClick(this.props.cart).then(() => {
            this.setState({ modalOpen: false });
        });
    }

    /**
     * Handle a click for closing the modal without doing anything.
     */
    handleCloseClick() {
        if (!this.state.inProgress) {
            this.setState({ modalOpen: false });
        }
    }

    render() {
        const { cart, inProgress } = this.props;
        if (cart.length > 0) {
            return (
                <span>
                    <button disabled={inProgress} onClick={this.handleClearCartClick} className="btn btn-info btn-sm">Clear cart</button>
                    {this.state.modalOpen ?
                        <Modal>
                            <ModalHeader title="Clear entire cart contents" closeModal={this.handleCloseClick} />
                            <ModalBody>
                                <p>Clearing the cart is not undoable.</p>
                            </ModalBody>
                            <ModalFooter
                                closeModal={<button onClick={this.handleCloseClick} className="btn btn-info">Close</button>}
                                submitBtn={this.handleConfirmClearClick}
                                submitTitle="Clear cart"
                                dontClose
                            />
                        </Modal>
                    : null}
                </span>
            );
        }
        return null;
    }
}

CartClearComponent.propTypes = {
    /** Current contents of cart */
    cart: PropTypes.array,
    /** True if cart updating operation is in progress */
    inProgress: PropTypes.bool,
    /** Function called to remove all elements */
    onClearCartClick: PropTypes.func.isRequired,
};

CartClearComponent.defaultProps = {
    cart: [],
    inProgress: false,
};

const mapStateToProps = (state, ownProps) => ({
    cart: state.cart,
    inProgress: state.inProgress,
    user: ownProps.sessionProperties,
});
const mapDispatchToProps = (dispatch, ownProps) => ({
    onClearCartClick: elementAtIds => dispatch(removeMultipleFromCartAndSave(elementAtIds, ownProps.sessionProperties.user, ownProps.fetch)),
});

const CartClearInternal = connect(mapStateToProps, mapDispatchToProps)(CartClearComponent);

const CartClear = (props, reactContext) => (
    <CartClearInternal sessionProperties={reactContext.session_properties} fetch={reactContext.fetch} />
);

CartClear.contextTypes = {
    session_properties: PropTypes.object,
    fetch: PropTypes.func,
};

export default CartClear;
