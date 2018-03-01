// Components to display the status of the cart.
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import url from 'url';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/bootstrap/modal';


/**
 * onClick callback to copy the text in the <input> field with id `cart-share-url-text` to the
 * system clipboard.
 */
const copyUrl = () => {
    // Find the URL text in the DOM and select all of the text in it.
    // https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Interact_with_the_clipboard#Using_execCommand()
    const cartUrlElement = document.getElementById('cart-share-url-text');
    cartUrlElement.select();

    // Execute copy command. Firefix can throw errors on rare occasion. As this is so unusual,
    // we just show a console warning in that case.
    try {
        document.execCommand('copy');
    } catch (err) {
        console.warn('Text copy failed.');
    }

    // Remove the selection after copying.
    cartUrlElement.setSelectionRange(0, 0);
};


/**
 * Button to add the current object to the cart, or to remove it.
 */
const CartShareComponent = ({ cart, userCart, closeShareCart }, reactContext) => {
    if (cart.length > 0) {
        const parsedUrl = url.parse(reactContext.location_href);
        parsedUrl.pathname = userCart['@id'];
        parsedUrl.search = '';
        parsedUrl.query = '';
        const sharableUrl = url.format(parsedUrl);
        return (
            <Modal closeModal={closeShareCart} labelId="share-cart-label" descriptionId="share-cart-description" focusId="share-cart-close">
                <ModalHeader title="Share cart" labelId="share-cart-label" closeModal={closeShareCart} />
                <ModalBody>
                    <p id="share-cart-description" role="document">
                        Copy the URL below to share with other people. Some items might not appear
                        for all people depending on whether they have logged in or not.
                    </p>
                    <div className="cart__share-url">
                        <input id="cart-share-url-text" type="text" aria-label="Sharable cart URL" value={sharableUrl} readOnly />
                        <button id="cart-share-url-trigger" aria-label="Copy shared cart URL" onClick={copyUrl} className="btn btn-info btn-sm"><i className="icon icon-clipboard" />&nbsp;Copy</button>
                    </div>
                </ModalBody>
                <ModalFooter
                    closeModal={closeShareCart}
                    cancelTitle="Close"
                    submitBtn={<a data-bypass="true" target="_self" className="btn btn-info" href={sharableUrl}>Visit sharable cart</a>}
                    closeId="share-cart-close"
                />
            </Modal>
        );
    }
    return null;
};

CartShareComponent.propTypes = {
    /** Cart contents */
    cart: PropTypes.array,
    /** Logged-in users's cart object */
    userCart: PropTypes.object,
    /** Function to close the modal */
    closeShareCart: PropTypes.func.isRequired,
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
