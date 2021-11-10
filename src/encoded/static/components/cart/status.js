// node_modules
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
// libs
import { uc } from '../../libs/constants';
// libs/ui
import BooleanToggle from '../../libs/ui/boolean-toggle';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';
// components
import Status from '../status';
// local
import { setCartStatusAndSave, setDescriptionAndSave } from './actions';
import { CartDescriptionDisplay, CartDescriptionEditorContent, sanitizeDescription, getCartDescriptionInfo } from './description';
import { getReadOnlyState } from './util';


/**
 *  Display the displayed cart's status property.
 */
export const CartStatus = ({ cart }) => (
    cart && cart.status
        ?
            <div className="cart-title-status">
                <Status item={cart} badgeSize="small" />
            </div>
        : null
);

CartStatus.propTypes = {
    /** Cart whose status we display */
    cart: PropTypes.object,
};

CartStatus.defaultProps = {
    cart: {},
};


/**
 * Displays the toggle switch that allows the user to choose whether the cart has the 'listed' or
 * 'unlisted' status.
 */
const CartListingToggleComponent = ({ cart, setStatus }) => {
    /**
     * Called when the user clicks the listing toggle switch.
     */
    const onSwitchListed = () => {
        setStatus(cart.status === 'listed' ? 'unlisted' : 'listed', cart);
    };

    return (
        <div className="listing-toggle">
            <BooleanToggle
                id="listing-toggle"
                state={cart.status === 'listed'}
                title="Listed"
                voice="Listed on cart listing"
                disabled={!cart.description}
                triggerHandler={onSwitchListed}
                options={{
                    cssSwitch: 'listing-toggle__switch',
                    cssTitle: 'listing-toggle__title',
                }}
            />
        </div>
    );
};

CartListingToggleComponent.propTypes = {
    /** Cart whose listing status gets changed */
    cart: PropTypes.object.isRequired,
    /** Called when the user changes the listed status of a cart */
    setStatus: PropTypes.func.isRequired,
};

CartListingToggleComponent.mapDispatchToProps = (dispatch, ownProps) => ({
    setStatus: (status, cart) => dispatch(
        setCartStatusAndSave(
            status,
            cart,
            ownProps.sessionProperties && ownProps.sessionProperties.user,
            ownProps.fetch
        )
    ),
});

const CartListingToggleInternal = connect(null, CartListingToggleComponent.mapDispatchToProps)(CartListingToggleComponent);

const CartListingToggle = ({ cart }, reactContext) => (
    <CartListingToggleInternal cart={cart} sessionProperties={reactContext.session_properties} fetch={reactContext.fetch} />
);

CartListingToggle.propTypes = {
    /** Cart object as it exists in the database */
    cart: PropTypes.object.isRequired,
};

CartListingToggle.contextTypes = {
    session_properties: PropTypes.object,
    fetch: PropTypes.func,
};


/**
 * Contains the content to manage the listing of a cart, including the listing toggle switch and
 * cart description.
 */
export const CartListingConfigContent = ({ cart, editedDescription, onChangeDescription, onSaveDescriptionClick }) => {
    /** Current states of the Save Description button */
    const {
        descriptionSaveButtonLabel,
        isDescriptionSaveButtonDisabled,
        isDescriptionEdited,
    } = getCartDescriptionInfo(cart, editedDescription);
    const readOnlyState = getReadOnlyState(cart);

    return (
        <>
            {readOnlyState.any
                ? <CartDescriptionDisplay description={editedDescription} />
                : (
                    <>
                        <p id="listing-description">
                            Your cart appears on the public <strong>Listed carts</strong> page by enabling
                            the <strong>Listed</strong> switch below. You must supply a description for
                            your cart to list it. This description also appears with this cart on
                            the <strong>Listed carts</strong> page. You can format the text with Markdown
                            syntax.
                        </p>
                        <CartDescriptionEditorContent
                            editedDescription={editedDescription}
                            savedDescription={cart.description || ''}
                            isDescriptionEdited={isDescriptionEdited}
                            onChangeDescription={onChangeDescription}
                        />
                        <div className="listing-config-description-save">
                            <button
                                type="button"
                                disabled={isDescriptionSaveButtonDisabled}
                                className="btn btn-info btn-sm"
                                onClick={onSaveDescriptionClick}
                            >
                                {descriptionSaveButtonLabel}
                            </button>
                        </div>
                        <CartListingToggle cart={cart} />
                    </>
                )
            }
        </>
    );
};

CartListingConfigContent.propTypes = {
    /** Cart object whose listing state we alter */
    cart: PropTypes.object.isRequired,
    /** Current contents of the description text area */
    editedDescription: PropTypes.string.isRequired,
    /** Called when the user changes the contents of the description text area */
    onChangeDescription: PropTypes.func.isRequired,
    /** Called when the user clicks the Save Description button */
    onSaveDescriptionClick: PropTypes.func.isRequired,
};


/**
 * Displays the modal so the user can choose to list a cart or not, and to update the description
 * of the cart.
 */
const ListingConfigModal = ({ cart, onSetDescription, onClose }) => {
    /** Current contents of the description text area */
    const [editedDescription, setEditedDescription] = React.useState(cart.description || '');
    const isDescriptionEdited = editedDescription !== cart.description;

    // Compose the note next to the modal Close button.
    let note = '';
    let isNoteError = false;
    if (!cart.description) {
        note = 'Cart must have a saved description to list it';
        isNoteError = true;
    } else {
        note = cart.status === 'listed' ? `Cart listed as ${uc.ldquo}${cart.name}${uc.rdquo}` : 'Cart unlisted';
        isNoteError = false;
    }

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
        onSetDescription(descriptionToSave);
        setEditedDescription(descriptionToSave);
    };

    return (
        <Modal labelId="description-editor" descriptionId="description-editor-description" focusId="text-editing-area" closeModal={onClose} widthClass="sm">
            <ModalHeader labelId="description-editor" closeModal={onClose} title={`Edit cart description: ${cart.name}`} />
            <ModalBody addCss="cart-description-editor">
                <CartListingConfigContent
                    cart={cart}
                    editedDescription={editedDescription}
                    onChangeDescription={onChangeDescription}
                    onSaveDescriptionClick={onSaveDescriptionClick}
                />
            </ModalBody>
            <ModalFooter>
                <div className={`listing-note${isNoteError ? ' listing-note--error' : ''}`}>
                    {note}
                </div>
                <button type="button" className="btn btn-default" onClick={onClose}>Close{isDescriptionEdited ? ' without saving description' : ''}</button>
            </ModalFooter>
        </Modal>
    );
};

ListingConfigModal.propTypes = {
    /** Cart object whose listing state we alter */
    cart: PropTypes.object.isRequired,
    /** Called when the user chooses to save the new description */
    onSetDescription: PropTypes.func.isRequired,
    /** Called when the user closes the modal */
    onClose: PropTypes.func.isRequired,
};


/**
 * Renders a toggle to make the cart status 'listed' or 'unlisted'.
 */
const CartListingAgentActuatorComponent = ({
    cart,
    inProgress,
    disabled,
    setDescription,
}) => {
    /** True if listing agent modal visible */
    const [listingConfigVisible, setListingConfigVisible] = React.useState(false);

    /**
     * Called when the user clicks the button to view the listing configuration modal.
     */
    const onClickManageListing = () => {
        setListingConfigVisible(true);
    };

    /**
     * Called when the user closes the modal.
     */
    const onClose = () => {
        setListingConfigVisible(false);
    };

    /**
     * Called when the user saves the edited description. This closes the editor modal and
     * sanitizes the Markdown before saving it to the cart object.
     * @param {string} description Edited description.
     */
    const onSetDescription = (description) => {
        setDescription(sanitizeDescription(description), cart);
    };

    return (
        <div className="listing-agent-actuator">
            <button type="button" className="btn btn-info btn-sm btn-inline" disabled={inProgress || disabled} onClick={onClickManageListing}>
                {`${cart.status === 'unlisted' ? 'List' : 'Unlist'} cart`}
            </button>
            {listingConfigVisible &&
                <ListingConfigModal cart={cart} onSetDescription={onSetDescription} onClose={onClose} />
            }
        </div>
    );
};

CartListingAgentActuatorComponent.propTypes = {
    /** Cart as it exists in the database */
    cart: PropTypes.object.isRequired,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
    /** True if the listing agent actuator should be disabled */
    disabled: PropTypes.bool.isRequired,
    /** Called to set an edited description */
    setDescription: PropTypes.func.isRequired,
};

CartListingAgentActuatorComponent.mapDispatchToProps = (dispatch, ownProps) => ({
    setDescription: (description, cart) => dispatch(
        setDescriptionAndSave(
            description,
            cart,
            ownProps.sessionProperties && ownProps.sessionProperties.user,
            ownProps.fetch,
        )
    ),
});

const CartListingAgentActuatorInternal = connect(null, CartListingAgentActuatorComponent.mapDispatchToProps)(CartListingAgentActuatorComponent);

export const CartListingAgentActuator = ({ cart, inProgress, disabled }, reactContext) => (
    <CartListingAgentActuatorInternal cart={cart} inProgress={inProgress} disabled={disabled} sessionProperties={reactContext.session_properties} fetch={reactContext.fetch} />
);

CartListingAgentActuator.propTypes = {
    /** Cart as it exists in the database */
    cart: PropTypes.object.isRequired,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
    /** True if the listing agent actuator should be disabled */
    disabled: PropTypes.bool.isRequired,
};

CartListingAgentActuator.contextTypes = {
    fetch: PropTypes.func,
    session_properties: PropTypes.object,
};
