// Components to display the status of the cart.
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import url from 'url';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/bootstrap/modal';


// Button to add the current object to the cart, or to remove it.
const CartShareComponent = ({ cart, userCart, closeShareCart }, reactContext) => {
    const parsedUrl = url.parse(reactContext.location_href);
    parsedUrl.pathname = userCart['@id'];
    parsedUrl.search = '';
    parsedUrl.query = '';
    const sharableUrl = url.format(parsedUrl);
    return (
        cart.length > 0 ?
            <Modal>
                <ModalHeader title="Share cart" closeModal />
                <ModalBody>
                    <p>
                        Copy the URL below to share with other people. Some items might not appear
                        for all people depending on whether they have logged in or not.
                    </p>
                    <code>{sharableUrl}</code>
                </ModalBody>
                <ModalFooter
                    closeModal={closeShareCart}
                    submitBtn={<a data-bypass="true" target="_self" className="btn btn-info" href={sharableUrl}>Visit sharable cart</a>}
                />
            </Modal>
        : null
    );
};

CartShareComponent.propTypes = {
    cart: PropTypes.array, // Cart contents
    userCart: PropTypes.object, // Logged-in users's cart object
    closeShareCart: PropTypes.func.isRequired, // Function to close the modal
};

CartShareComponent.defaultProps = {
    cart: [],
    userCart: {},
};

CartShareComponent.contextTypes = {
    location_href: PropTypes.string, // URL of this experiment page, including query string stuff
};


const mapStateToProps = (state, ownProps) => ({
    cart: state.cart,
    userCart: ownProps.userCart,
    closeShareCart: ownProps.closeShareCart,
});

const CartShare = connect(mapStateToProps)(CartShareComponent);
export default CartShare;
