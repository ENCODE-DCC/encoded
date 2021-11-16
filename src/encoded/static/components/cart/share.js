/**
 * Components to display the Share Cart modal.
 */

// node_modules
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import url from 'url';
// libs/ui
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';
// components
import { useMount } from '../hooks';
import { CopyButton } from '../objectutils';
// local
import { setDescriptionAndSave } from './actions';
import { sanitizeDescription } from './description';
import { CartListingConfigContent } from './status';


/**
 * Internal component to display and process the modal used to share a cart URL. The copyable cart
 * URL gets placed into a read-only <input> element.
 */
const CartShareComponent = ({ userCart, locationHref, closeShareCart, inProgress, setDescription }) => {
    /** Current contents of the description text area */
    const [editedDescription, setEditedDescription] = React.useState(userCart.description || '');
    /** Modal Visit Shareable Cart button */
    const submitRef = React.useRef(null);

    // Generate the shared cart URL.
    const parsedUrl = url.parse(locationHref);
    Object.assign(parsedUrl, {
        pathname: userCart['@id'],
        search: '',
        query: '',
    });
    const shareableUrl = url.format(parsedUrl);

    /**
     * Called when the user changes the contents of the description text area.
     * @param {string} value Contents of description text area
     */
    const onChangeDescription = (value) => {
        setEditedDescription(value);
    };

    /**
     * Called when the user clicks the Save Description button.
     */
    const onSaveDescriptionClick = () => {
        // Strip the description of anything dangerous, save it to the cart object in the database
        // and then update the edit field with the sanitized description.
        const descriptionToSave = sanitizeDescription(editedDescription);
        setDescription(descriptionToSave, userCart);
        setEditedDescription(descriptionToSave);
    };

    useMount(() => {
        // Focus on the Visit Shareable Cart button on mount.
        submitRef.current.focus();
    });

    return (
        <Modal closeModal={closeShareCart} labelId="share-cart-label" descriptionId="share-cart-description" focusId="share-cart-close" widthClass="sm">
            <ModalHeader title={`Share cart: ${userCart.name}`} labelId="share-cart-label" closeModal={closeShareCart} />
            <ModalBody>
                <div id="share-cart-description" role="document">
                    <p>
                        Copy the URL below to share with other people. Some items might not appear
                        for all people depending on whether they have logged in or not.
                    </p>
                </div>
                <div className="cart__share-url">
                    <input type="text" aria-label="Shareable cart URL" value={shareableUrl} readOnly />
                    <CopyButton label="Copy shared cart URL" copyText={shareableUrl} css="btn-sm cart__share-button" />
                </div>
                <CartListingConfigContent
                    cart={userCart}
                    editedDescription={editedDescription}
                    onChangeDescription={onChangeDescription}
                    onSaveDescriptionClick={onSaveDescriptionClick}
                />
            </ModalBody>
            <ModalFooter
                closeModal={closeShareCart}
                cancelTitle="Close"
                submitBtn={<a data-bypass="true" ref={submitRef} disabled={inProgress} target="_self" className="btn btn-info" href={shareableUrl}>Visit shareable cart</a>}
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
    /** Called to set an edited description */
    setDescription: PropTypes.func.isRequired,
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

const mapDispatchToProps = (dispatch, ownProps) => ({
    setDescription: (description, cart) => dispatch(
        setDescriptionAndSave(
            description,
            cart,
            ownProps.sessionProperties && ownProps.sessionProperties.user,
            ownProps.fetch,
        )
    ),
});

const CartShareInternal = connect(mapStateToProps, mapDispatchToProps)(CartShareComponent);


/**
 * Public wrapper component to receive React <App> context and pass them as props to
 * CartShareInternal.
 */
const CartShare = ({ userCart, closeShareCart }, reactContext) => (
    <CartShareInternal
        userCart={userCart}
        closeShareCart={closeShareCart}
        locationHref={reactContext.location_href}
        sessionProperties={reactContext.session_properties}
        fetch={reactContext.fetch}
    />
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
    fetch: PropTypes.func,
    session_properties: PropTypes.object,
};

export default CartShare;
