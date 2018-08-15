import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/bootstrap/modal';
import { addMultipleToCart } from './actions';


class CartMergeSharedComponent extends React.Component {
    constructor() {
        super();
        this.handleClick = this.handleClick.bind(this);
    }

    handleClick() {
        this.props.onMergeCartClick(this.props.sharedCartObj.items);
    }

    render() {
        const { sharedCartObj, savedCartObj } = this.props;

        if (sharedCartObj.items && (sharedCartObj.items.length > 0 && sharedCartObj['@id'] !== savedCartObj['@id'])) {
            return (
                <Modal actuator={<button className="btn btn-info btn-sm">Add to my cart</button>}>
                    <ModalHeader title="Add shared cart items to my cart" closeModal />
                    <ModalBody>
                        <p>Add the contents of this shared cart to your cart. Any items already in your cart won&rsquo;t be affected.</p>
                    </ModalBody>
                    <ModalFooter
                        closeModal={<button className="btn btn-info">Close</button>}
                        submitBtn={this.handleClick}
                        submitTitle="Add items to my cart"
                    />
                </Modal>
            );
        }
        return null;
    }
}

CartMergeSharedComponent.propTypes = {
    sharedCartObj: PropTypes.object, // Shared cart object
    savedCartObj: PropTypes.object, // Current user's saved cart object
    onMergeCartClick: PropTypes.func.isRequired, // Called to merge shared cart with own cart
};

CartMergeSharedComponent.defaultProps = {
    sharedCartObj: {},
    savedCartObj: null,
};

const mapStateToProps = (state, ownProps) => ({ cart: state.cart, savedCartObj: state.savedCartObj, sharedCartObj: ownProps.sharedCartObj });
const mapDispatchToProps = dispatch => ({
    onMergeCartClick: itemAtIds => dispatch(addMultipleToCart(itemAtIds)),
});

const CartMergeShared = connect(mapStateToProps, mapDispatchToProps)(CartMergeSharedComponent);

export default CartMergeShared;
