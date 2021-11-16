// node_modules
import React from 'react';
import marked from 'marked';
import PropTypes from 'prop-types';
import { sanitize } from 'dompurify';
import { connect } from 'react-redux';
// libs
import { svgIcon } from '../../libs/svg-icons';
// libs/ui
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';
// components
import { TextAreaCounter } from '../objectutils';
// local
import { setDescriptionAndSave } from './actions';
import { getReadOnlyState } from './util';


// Maximum number of characters allowed in the description in Javascript.
const MAX_DESCRIPTION_LENGTH = 1000;


/**
 * Sanitize the given description to strip it of anything that could cause an XSS attack, as well
 * as preceding and trailing spaces as required by the cart schema.
 * @param {string} description Description entered by the user
 * @returns {string} `description` but sanitized and with preceding/trailing spaces removed
 */
export const sanitizeDescription = (description) => sanitize(description).trim();


/**
 * Calculates the enabled/disabled state of the button to save a description and the label that
 * should appear in the button given the current saved state of the description.
 * @param {object} cart Saved cart object
 * @param {string} editedDescription Description as entered by the user before sanitizing
 * @returns See return statement
 */
export const getCartDescriptionInfo = (cart, editedDescription) => {
    const isDescriptionEdited = editedDescription !== (cart.description || '');
    const descriptionSaveButtonLabel = isDescriptionEdited ? 'Save description' : 'Saved';
    const isDescriptionEmpty = sanitizeDescription(editedDescription) === '';
    const isDescriptionSaveButtonDisabled = !isDescriptionEdited || (cart.status === 'listed' && isDescriptionEmpty);
    return {
        // Label that should appear in the Save Description button
        descriptionSaveButtonLabel,
        // True if Save Description button should appear disabled
        isDescriptionSaveButtonDisabled,
        // True if the description has been changed from the saved version
        isDescriptionEdited,
    };
};


export const CartDescriptionEditorContent = ({
    editedDescription,
    savedDescription,
    isDescriptionEdited,
    onChangeDescription,
}) => {
    /**
     * Called when the users wants to reset the text area to the saved description.
     */
    const onResetDescription = () => {
        onChangeDescription(savedDescription);
    };

    return (
        <div className="cart-description-editor">
            <textarea
                id="text-editing-area"
                value={editedDescription}
                maxLength={MAX_DESCRIPTION_LENGTH}
                rows="12"
                name="cart-description-text-area"
                onChange={(e) => onChangeDescription(e.target.value)}
                className="cart-description__editor"
            />
            <div className="cart-description-editor__tools">
                <button type="button" disabled={!isDescriptionEdited} className="btn btn-sm btn-danger" onClick={onResetDescription}>
                    Revert to saved description
                </button>
                <TextAreaCounter value={editedDescription} maxLength={MAX_DESCRIPTION_LENGTH} />
            </div>
        </div>
    );
};

CartDescriptionEditorContent.propTypes = {
    /** Holds current edited description */
    editedDescription: PropTypes.string,
    /** Description as currently saved in the cart object */
    savedDescription: PropTypes.string,
    /** True if user has edited the description */
    isDescriptionEdited: PropTypes.bool.isRequired,
    /** Called as the user edits the description */
    onChangeDescription: PropTypes.func.isRequired,
};

CartDescriptionEditorContent.defaultProps = {
    editedDescription: '',
    savedDescription: '',
};


/**
 * Displays the formatted cart description.
 */
export const CartDescriptionDisplay = ({ description }) => {
    /** Description cleaned of any dangerous HTML/Javascript */
    const [sanitizedDescription, setSanitizedDescription] = React.useState(description);

    React.useEffect(() => {
        // Must have a DOM to sanitize the description.
        setSanitizedDescription(marked(sanitizeDescription(description || '')));
    }, [description]);

    if (sanitizedDescription) {
        return (
            <div className="cart-description">
                <div dangerouslySetInnerHTML={{ __html: sanitizedDescription }} />
            </div>
        );
    }
    return null;
};

CartDescriptionDisplay.propTypes = {
    description: PropTypes.string,
};

CartDescriptionDisplay.defaultProps = {
    description: '_No description',
};


/**
 * Displays the cart description editor modal and its controls.
 */
const CartDescriptionEditor = ({ cart, savedDescription, onSetDescription, onClose }) => {
    /** Holds current edited description */
    const [editedDescription, setEditedDescription] = React.useState(savedDescription);
    /** Current states of the Save Description button */
    const { descriptionSaveButtonLabel, isDescriptionSaveButtonDisabled, isDescriptionEdited } = getCartDescriptionInfo(cart, editedDescription);
    const readOnlyState = getReadOnlyState(cart);

    /**
     * Called whenever the user changes the edited description contents.
     * @param {object} event Synthetic event object.
     */
    const onChangeDescription = (content) => {
        setEditedDescription(content);
    };

    return (
        <Modal labelId="description-editor" descriptionId="description-editor-description" focusId="text-editing-area" closeModal={onClose} widthClass="sm">
            <ModalHeader labelId="description-editor" closeModal={onClose} title={`Edit cart description: ${cart.name}`} />
            <ModalBody addCss="cart-description-editor">
                <p id="description-editor-description">
                    This description gets saved with this cart, and appears along with this cart
                    when you list it on the public <strong>Listed carts</strong> page. You can
                    format the text with Markdown syntax.
                </p>
                {cart.status === 'listed' &&
                    <p>This cart is listed and must have a description.</p>
                }
                {readOnlyState.any
                    ? <CartDescriptionDisplay description={savedDescription} />
                    : (
                        <CartDescriptionEditorContent
                            editedDescription={editedDescription}
                            isDescriptionEdited={isDescriptionEdited}
                            savedDescription={savedDescription}
                            onChangeDescription={onChangeDescription}
                        />
                    )
                }
            </ModalBody>
            <ModalFooter
                closeModal={onClose}
                cancelTitle="Close without saving"
                submitBtn={
                    <button
                        type="button"
                        disabled={isDescriptionSaveButtonDisabled}
                        onClick={() => { onSetDescription(editedDescription); }}
                        className="btn btn-info"
                    >
                        {descriptionSaveButtonLabel}
                    </button>
                }
            />
        </Modal>
    );
};

CartDescriptionEditor.propTypes = {
    /** Cart as it exists in the database */
    cart: PropTypes.object.isRequired,
    /** Description as it exists in the cart before editing */
    savedDescription: PropTypes.string.isRequired,
    /** Called when the user chooses to save the new description */
    onSetDescription: PropTypes.func.isRequired,
    /** Called when the user closes the modal without saving */
    onClose: PropTypes.func.isRequired,
};


/**
 * Displays the cart description on the cart-view page. For an editable cart (not a shared cart,
 * nor the active cart that has the released state)
 */
const CartDescriptionComponent = ({ cart, cartType, inProgress, setDescription, isCartReadOnly }) => {
    /** True to show the description editor modal */
    const [isDescriptionEditorVisible, setDescriptionEditorVisible] = React.useState(false);

    /**
     * Called when the user clicks the description edit button.
     */
    const onClickEdit = () => {
        setDescriptionEditorVisible(true);
    };

    /**
     * Called when the user closes the description editor modal without saving.
     */
    const onCloseDescriptionEditor = () => {
        setDescriptionEditorVisible(false);
    };

    /**
     * Called when the user saves the edited description. This closes the editor modal and
     * sanitizes the Markdown before saving it to the cart object.
     * @param {string} description Edited description.
     */
    const onSetDescription = (description) => {
        setDescriptionEditorVisible(false);
        setDescription(sanitizeDescription(description), cart);
    };

    return (
        <div className="cart-view-description">
            <div className={`cart-view-description__display${!isCartReadOnly && cartType === 'ACTIVE' ? ' cart-description__display--active' : ''}`}>
                {!isCartReadOnly && cartType === 'ACTIVE' &&
                    <div className="cart-view-description__edit">
                        <button
                            type="button"
                            aria-label="Edit description"
                            name="edit-description"
                            onClick={onClickEdit}
                            disabled={inProgress}
                            className="cart-view-description__edit-button"
                        >
                            {svgIcon('edit')}
                        </button>
                    </div>
                }
                {cart.description
                    ? <CartDescriptionDisplay description={cart.description} />
                    : <i>No description</i>
                }
            </div>
            {isDescriptionEditorVisible && (
                <CartDescriptionEditor
                    cart={cart}
                    savedDescription={cart.description || ''}
                    onSetDescription={onSetDescription}
                    onClose={onCloseDescriptionEditor}
                />
            )}
        </div>
    );
};

CartDescriptionComponent.propTypes = {
    /** Cart as it exists in the database */
    cart: PropTypes.object.isRequired,
    /** Whether cart is current or shared */
    cartType: PropTypes.oneOf(['ACTIVE', 'OBJECT']).isRequired,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
    /** Called to set an edited description */
    setDescription: PropTypes.func.isRequired,
    /** True if cart is read only */
    isCartReadOnly: PropTypes.bool.isRequired,
};

const mapStateToProps = (state) => ({
    inProgress: state.inProgress,
});

const mapDispatchToProps = (dispatch, ownProps) => ({
    setDescription: (description, cart) => dispatch(
        setDescriptionAndSave(
            description,
            cart,
            ownProps.sessionProperties && ownProps.sessionProperties.user,
            ownProps.fetch
        )
    ),
});

const CartDescriptionInternal = connect(mapStateToProps, mapDispatchToProps)(CartDescriptionComponent);

const CartDescription = ({ cart, cartType, isCartReadOnly }, reactContext) => (
    <CartDescriptionInternal
        cart={cart}
        cartType={cartType}
        isCartReadOnly={isCartReadOnly}
        sessionProperties={reactContext.session_properties}
        fetch={reactContext.fetch}
    />
);

CartDescription.propTypes = {
    /** Current cart object or shared cart object */
    cart: PropTypes.object.isRequired,
    /** Whether cart is current or shared */
    cartType: PropTypes.oneOf(['ACTIVE', 'OBJECT']).isRequired,
    /** True if the cart is read only */
    isCartReadOnly: PropTypes.bool.isRequired,
};

CartDescription.contextTypes = {
    fetch: PropTypes.func,
    session_properties: PropTypes.object,
};

export default CartDescription;
