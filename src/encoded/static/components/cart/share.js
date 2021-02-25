/**
 * Components to display the Share Cart modal.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import url from 'url';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';
import { CopyButton, useMount } from '../objectutils';


/**
 * Internal component to display and process the modal used to share a cart URL. The copyable cart
 * URL gets placed into a read-only <input> element.
 */
const CartShareComponent = ({ userCart, locationHref, closeShareCart, inProgress }) => {
    /** Modal Visit Sharable Cart button */
    const submitRef = React.useRef(null);

    // Generate the shared cart URL.
    const parsedUrl = url.parse(locationHref);
    Object.assign(parsedUrl, {
        pathname: userCart['@id'],
        search: '',
        query: '',
    });
    const sharableUrl = url.format(parsedUrl);

    useMount(() => {
        // Focus on the Visit Sharable Cart button on mount.
        submitRef.current.focus();
    });

    return (
        <Modal closeModal={closeShareCart} labelId="share-cart-label" descriptionId="share-cart-description" focusId="share-cart-close">
            <ModalHeader title={`Share cart: ${userCart.name}`} labelId="share-cart-label" closeModal={closeShareCart} />
            <ModalBody>
                <p id="share-cart-description" role="document">
                    Copy the URL below to share with other people. Some items might not appear
                    for all people depending on whether they have logged in or not.
                </p>
                <div className="cart__share-url">
                    <input type="text" aria-label="Sharable cart URL" value={sharableUrl} readOnly />
                    <CopyButton label="Copy shared cart URL" copyText={sharableUrl} css="btn-sm cart__share-button" />
                </div>
            </ModalBody>
            <ModalFooter
                closeModal={closeShareCart}
                cancelTitle="Close"
                submitBtn={<a data-bypass="true" ref={submitRef} disabled={inProgress} target="_self" className="btn btn-info" href={sharableUrl}>Visit sharable cart</a>}
                closeId="share-cart-close"
            />
        </Modal>
    );
};

CartShareComponent.propTypes = {
    /** Logged-in users's cart object */
    userCart: PropTypes.object.isRequired,
    /** location_href from <App> context */
    locationHref: PropTypes.string,
    /** Function to close the modal */
    closeShareCart: PropTypes.func.isRequired,
    /** True if global cart operation in progress */
    inProgress: PropTypes.bool,
};

CartShareComponent.defaultProps = {
    locationHref: '',
    inProgress: false,
};

const mapStateToProps = (state, ownProps) => ({
    userCart: ownProps.userCart,
    locationHref: ownProps.locationHref,
    inProgress: state.inProgress,
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
