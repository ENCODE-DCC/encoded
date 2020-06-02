/**
 * Components to display the Share Cart modal.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import url from 'url';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/bootstrap/modal';


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
        const { userCart, locationHref, closeShareCart } = this.props;

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
                <ModalHeader title={`Share cohort: ${userCart.name}`} labelId="share-cart-label" closeModal={closeShareCart} />
                <ModalBody>
                    <p id="share-cart-description" role="document">
                        Copy the URL below to share with other people. Some items might not appear
                        for all people depending on whether they have logged in or not.
                    </p>
                    <div className="cart__share-url">
                        <input ref={(input) => { this.cartUrlBox = input; }} type="text" aria-label="Sharable cart URL" value={sharableUrl} readOnly />
                        <button id="cart-share-url-trigger" aria-label="Copy shared cart URL" onClick={this.copyUrl} className="btn btn-info btn-sm"><i className="icon icon-clipboard" />&nbsp;Copy</button>
                    </div>
                </ModalBody>
                <ModalFooter
                    closeModal={closeShareCart}
                    cancelTitle="Close"
                    submitBtn={<a data-bypass="true" target="_self" className="btn btn-info" href={sharableUrl}>Visit sharable cohort</a>}
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
};

CartShareComponent.defaultProps = {
    locationHref: '',
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
const CartShare = ({ userCart, closeShareCart }, reactContext) => (
    <CartShareInternal userCart={userCart} closeShareCart={closeShareCart} locationHref={reactContext.location_href} />
);

CartShare.propTypes = {
    /** Logged-in users's cart object */
    userCart: PropTypes.object,
    /** Function to close the modal */
    closeShareCart: PropTypes.func.isRequired,
};

CartShare.defaultProps = {
    userCart: {},
};

CartShare.contextTypes = {
    location_href: PropTypes.string,
};

export default CartShare;
