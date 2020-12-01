/**
 * Components to display the Share Cart modal.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import url from 'url';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';


/**
 * Internal component to display and process the modal used to share a cart URL. The copyable cart
 * URL gets placed into a read-only <input> element.
 */
class CartShareComponent extends React.Component {
    constructor() {
        super();
        this.copyUrl = this.copyUrl.bind(this);
    }

    /**
     * Called when the user clicks the Copy button to copy the URL to the clipboard.
     */
    copyUrl() {
        // Gewt the URL text <input> element in the DOM and select all of the text in it to copy to
        // the user's clipboard.
        // https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Interact_with_the_clipboard#Using_execCommand()
        this.cartUrlBox.select();

        // Execute copy command. Firefox can throw errors on rare occasion. As this is so unusual,
        // we just show a console warning in that case.
        try {
            document.execCommand('copy');
        } catch (err) {
            console.warn('Text copy failed.');
        }

        // Remove the selection after copying.
        this.cartUrlBox.setSelectionRange(0, 0);
    }

    render() {
        const { userCart, locationHref, closeShareCart, disableFooterSubmitBtn } = this.props;

        // Generate the shared cart URL.
        const parsedUrl = url.parse(locationHref);
        Object.assign(parsedUrl, {
            pathname: userCart['@id'],
            search: '',
            query: '',
        });
        const sharableUrl = url.format(parsedUrl);

        return (
            <Modal closeModal={closeShareCart} labelId="share-cart-label" descriptionId="share-cart-description" focusId="share-cart-close">
                <ModalHeader title={`Share cart: ${userCart.name}`} labelId="share-cart-label" closeModal={closeShareCart} />
                <ModalBody>
                    <p id="share-cart-description" role="document">
                        Copy the URL below to share with other people. Some items might not appear
                        for all people depending on whether they have logged in or not.
                    </p>
                    <div className="cart__share-url">
                        <input ref={(input) => { this.cartUrlBox = input; }} type="text" aria-label="Sharable cart URL" value={sharableUrl} readOnly />
                        <button id="cart-share-url-trigger" aria-label="Copy shared cart URL" onClick={this.copyUrl} className="btn btn-sm"><i className="icon icon-clipboard" />&nbsp;Copy</button>
                    </div>
                </ModalBody>
                <ModalFooter
                    closeModal={closeShareCart}
                    cancelTitle="Close"
                    submitBtn={<a data-bypass="true" disabled={disableFooterSubmitBtn} target="_self" className="btn btn-info" href={sharableUrl}>Visit sharable cart</a>}
                    closeId="share-cart-close"
                />
            </Modal>
        );
    }
}

CartShareComponent.propTypes = {
    /** Logged-in users's cart object */
    userCart: PropTypes.object.isRequired,
    /** location_href from <App> context */
    locationHref: PropTypes.string,
    /** Function to close the modal */
    closeShareCart: PropTypes.func.isRequired,
    /** Disable element if set to true */
    disableFooterSubmitBtn: PropTypes.bool,
};

CartShareComponent.defaultProps = {
    locationHref: '',
    disableFooterSubmitBtn: false,
};

const mapStateToProps = (state, ownProps) => ({
    userCart: ownProps.userCart,
    locationHref: ownProps.locationHref,
    closeShareCart: ownProps.closeShareCart,
});

const CartShareInternal = connect(mapStateToProps)(CartShareComponent);


/**
 * Public wrapper component to receive React <App> context and pass them as props to
 * CartShareInternal.
 */
const CartShare = ({ userCart, closeShareCart, disableFooterSubmitBtn }, reactContext) => (
    <CartShareInternal userCart={userCart} closeShareCart={closeShareCart} disableFooterSubmitBtn={disableFooterSubmitBtn} locationHref={reactContext.location_href} />
);

CartShare.propTypes = {
    /** Logged-in users's cart object */
    userCart: PropTypes.object,
    /** Function to close the modal */
    closeShareCart: PropTypes.func.isRequired,
    /** Disable footer submit button if true */
    disableFooterSubmitBtn: PropTypes.bool,
};

CartShare.defaultProps = {
    userCart: {},
    disableFooterSubmitBtn: false,
};

CartShare.contextTypes = {
    location_href: PropTypes.string,
};

export default CartShare;
