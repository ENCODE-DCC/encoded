import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import { keyCode } from '../constants';


// Display a modal dialog box that blocks all other page input until the user dismisses it. The
// typical format looks like:
//
// <Modal actuator={JSX component to actuate the modal}>
//     <ModalHeader>
//         <content in addition to title and close button>
//     </ModalHeader>
//     <ModalBody>
//         <content of modal dialog body>
//     </ModalBody>
//     <ModalFooter>
//         <content of modal footer>
//     </ModalFooter>
// </Modal>
//
// Generally you place this anywhere you want to see the actuator rendered. When you click the
// actuator (often a button), the modal appears, e.g.:
//
// <div>
//     <Modal actuator={<button className="btn btn-info">Open Modal</button>}>
//         ...
//
// The resulting HTML becomes:
//
// <div>
//     <button class="btn btn-info">Open Modal</button>
//         ...
//
//
// ...where the <Modal> component automatically adds a click handler to this button to make the
// modal appear.
//
// This is *one* of two ways to use this modal component. The two ways are:
//
// 1. Plug-and-play mode: The modal component handles opening and closing itself in reaction to a
//    click on an actuator component (usually a button). I demonstrated this case above.
//
// 2. Self-management mode: The component using the modal component handles opening and closing the
//    modal.
//
// In the second case, the parent component supplies no actuator property to <Modal>. Instead, it
// either renders the modal to display it opened, or doesn't to hide it. That typically looks
// something like:
//
// {this.state.displayModal && <Modal>{child components}</Modal>}
//
// <Modal> usage details:
// actuator: Component that opens the modal. You don't normally need a click handler for this
//           component because <Modal> attaches a default click handler that simply opens the
//           modal. The existence or absence of this property determines whether you're using
//           plug-and-play mode or self-management mode. Supply `actuator` to use plug-and-play
//           mode. Don't supply `actuator` to use self-management mode.
// closeModal: Supply a function to close the modal for self-management mode. This function
//             normally sets a state that decides whether to render the modal or not. Provide this
//             function so that <Modal> knows what to call when the user types the ESC key. For
//             closing the modal with a button in the modal's footer (typically), supply a click
//             handler for the close button to close the modal.
//
// <ModalHeader> usage details:
// title: Title to display in the header. You can pass this as a string or a React component (e.g.
//        if you need a link within the title string).
// closeModal: As a boolean, this displays the standard close button (an "x") in the header with
//             the standard close handler. You can also pass a function to use as a click handler
//             on this button to close the modal for self-management mode..
//
// <ModalBody> takes no properties. All it does is render a wrapper <div> for Bootstrap modal
// bodies.
//
// <ModalFooter> usage details:
// submitBtn: Pass a React component to render as the submit button. You can also supply a function
//            that gets used as a click handler for a standard Submit button.
// closeModal: Pass True to get a standard "Cancel" button that simply closes the modal in
//             plug-and-play mode. You can also pass a function that gets used as the click handler
//             for the standard cancel button that gets called before closing the modal. Finally, you
//             can pass a React component that handles the closing of the modal in self-management
//             mode.
// dontClose: Supply this as a boolean to prevent the submit button from closing the modal. Of
//            course you'll need to provide some other way to close the modal.
//
// The method of rendering the modal to a div inserted to a specific <div> in <body> rather than
// into the React virtual DOM comes from:
// http://jamesknelson.com/rendering-react-components-to-the-document-body/


export const ModalHeader = ({ title, closeModal, addCss, labelId, focusClose, children, cCloseModal }) => {
    /** Holds ref of header close box */
    const closeRef = React.useRef(null);

    const internalCloseModal = () => {
        // Call directly given close handler.
        if (typeof closeModal === 'function') {
            closeModal();
        }

        // Now call the standard close handler.
        cCloseModal();
    };

    // Handle the string and React component cases for the title
    let titleRender = null;
    if (title) {
        titleRender = typeof title === 'string' ? <h2>{title}</h2> : <div>{title}</div>;
    }

    React.useEffect(() => {
        // If requested, set keyboard focus to the header bar close button.
        if (focusClose) {
            closeRef.current.focus();
        }
    }, []);

    return (
        <div className={`modal__header${addCss ? ` ${addCss}` : ''}`} id={labelId}>
            {titleRender && <div className="modal__header-title">{titleRender}</div>}
            {children}
            {closeModal && (
                <button type="button" className="modal__header-close" name="close-modal" aria-label="Close" onClick={internalCloseModal} ref={closeRef}>
                    <span aria-hidden="true">&times;</span>
                </button>
            )}
        </div>
    );
};

ModalHeader.propTypes = {
    addCss: PropTypes.string, // CSS classes to add to modal header
    title: PropTypes.oneOfType([
        PropTypes.string, // String to display as an <h4> title
        PropTypes.object, // React component to display for the title
    ]),
    closeModal: PropTypes.oneOfType([
        PropTypes.bool, // True to display the close button in the header with the built-in handler
        PropTypes.func, // If not using an actuator on <Modal>, provide a function to close the modal
    ]),
    labelId: PropTypes.string, // id of header element to match aria-labelledby in modal title
    focusClose: PropTypes.bool, // True to automatically set keyboard focus on the close icon
    children: PropTypes.node,
    cCloseModal: PropTypes.func, // Auto-added
};

ModalHeader.defaultProps = {
    addCss: '',
    title: null,
    closeModal: null,
    labelId: '',
    focusClose: false,
    children: null,
    cCloseModal: null,
};


export const ModalBody = (props) => (
    <div className={`modal__body${props.addCss ? ` ${props.addCss}` : ''}`}>
        {props.children}
    </div>
);

ModalBody.propTypes = {
    addCss: PropTypes.string,
    children: PropTypes.node,
};

ModalBody.defaultProps = {
    addCss: '',
    children: null,
};


export const ModalFooter = ({
    submitBtn,
    submitTitle,
    cancelTitle,
    addCss,
    closeModal,
    dontClose,
    closeId,
    cCloseModal,
    children,
}) => {
    const chainedCloseModal = React.useRef(null);

    const internalCloseModal = () => {
        // Call close button's existing close handler if it had one first.
        if (chainedCloseModal.current) {
            chainedCloseModal.current();
        }

        // Now call the standard close handler.
        cCloseModal();
    };

    const submitModal = (e) => {
        e.stopPropagation();

        if (typeof submitBtn === 'function') {
            submitBtn();
        }
        if (!dontClose) {
            internalCloseModal();
        }
    };

    let submitBtnComponent = null;
    let closeBtnComponent = null;

    // Make a Submit button component -- either the given one or a default one that calls the
    // given function. Note: if you pass `null` in the submitBtn property, this component
    // thinks that's a function because of an old Javascript characteristic.
    if (submitBtn) {
        submitBtnComponent = (typeof submitBtn === 'object') ? submitBtn : <button type="button" className="btn btn-info" onClick={submitModal}>{submitTitle}</button>;
    }

    // If the given closeModal property is a component, make sure it calls the close function
    // when it gets clicked.
    if (typeof closeModal === 'object') {
        // If the close button had a click handler, save it so we can call it before calling
        // the standard one.
        if (closeModal.props.onClick) {
            chainedCloseModal.current = closeModal.props.onClick;
        }
        closeModal = React.cloneElement(closeModal, { onClick: internalCloseModal });
    } else if (typeof closeModal === 'function') {
        chainedCloseModal.current = closeModal;
    }

    // Make a Cancel button component -- either the given one, a default one that calls the
    // given function, or a default one that calls the default function. Note: if you pass
    // `null` in the closeModal property, this component thinks that's a function because of an
    // old Javascript characteristic.
    if (closeModal) {
        const closeBtnFunc = (typeof closeModal === 'function') ? closeModal : (typeof closeModal === 'boolean' ? cCloseModal : null);
        closeBtnComponent = (typeof closeModal === 'object') ? closeModal : <button type="button" className="btn btn-default" onClick={closeBtnFunc} id={closeId}>{cancelTitle}</button>;
    }

    return (
        <div className={`modal__footer${addCss ? ` ${addCss}` : ''}`}>
            {children}
            {(submitBtnComponent || closeBtnComponent) && (
                <div className="modal__footer-controls">
                    {closeBtnComponent}
                    {submitBtnComponent}
                </div>
            )}
        </div>
    );
};

ModalFooter.propTypes = {
    submitBtn: PropTypes.oneOfType([
        PropTypes.object, // Submit button is a React component; just render it
        PropTypes.func, // Function to call when default-rendered Submit button clicked
    ]),
    submitTitle: PropTypes.string, // Title for default submit button
    cancelTitle: PropTypes.string, // Title for default cancel button
    addCss: PropTypes.string, // CSS classes to add to modal footer
    closeModal: PropTypes.oneOfType([
        PropTypes.bool, // Use default-rendered Cancel button that closes the modal
        PropTypes.object, // Cancel button is a React component; just render it
        PropTypes.func, // Function to call when default-rendered Cancel button clicked
    ]),
    dontClose: PropTypes.bool, // True to *not* close the modal when the user clicks Submit
    closeId: PropTypes.string, // id to assign to default Close button
    cCloseModal: PropTypes.func, // Auto-add
    children: PropTypes.node,
};

ModalFooter.defaultProps = {
    submitBtn: null,
    submitTitle: 'Submit',
    cancelTitle: 'Cancel',
    addCss: '',
    closeModal: undefined,
    dontClose: false,
    closeId: '',
    cCloseModal: null,
    children: null,
};


/**
 * Renders the modal without conditions -- conditions need to be handled outside this component.
 */
const ModalElement = ({
    modalChildren,
    descriptionId,
    addClasses,
    focusId,
    labelId,
}) => {
    const modalEl = React.useRef(null);
    const focusableElements = React.useRef(null);

    /**
     * Retrieve the current <div> DOM node for the modal. Lazily create this node if needed.
     * @returns {DOM node} Injected DOM node reference for modal
     */
    const getModalEl = () => {
        if (modalEl.current === null) {
            modalEl.current = document.createElement('div');
        }
        return modalEl.current;
    };

    /**
     * Handle key presses while the modal is open, but only handle and consume TAB key presses
     * setting focus to the next or previous elements within the modal, depending on whether the
     * shift key is held down at the time.
     * @param {object} e React synthetic event
     */
    const handleTab = (e) => {
        if (e.keyCode === keyCode.TAB && focusableElements) {
            const firstFocusableElement = focusableElements[0];
            const lastFocusableElement = focusableElements[focusableElements.length - 1];
            if (e.shiftKey) {
                if (document.activeElement === firstFocusableElement) {
                    lastFocusableElement.focus();
                    e.preventDefault();
                }
            } else if (document.activeElement === lastFocusableElement) {
                firstFocusableElement.focus();
                e.preventDefault();
            }
        }
    };

    React.useEffect(() => {
        // Modal HTML gets injected at the end of <body> so the backdrop overlay works, even with other
        // fixed elements on the page. The "modal-root" div is defined in app.js at the end of the
        // <body> section.
        const modalRoot = document.getElementById('modal-root');
        modalRoot.appendChild(getModalEl());

        // Focus screen reader on the given element if specified.
        if (focusId) {
            const focusElement = document.getElementById(focusId);
            if (focusElement) {
                focusElement.focus();
            }
        }

        // Attach tab-key listener.
        document.addEventListener('keydown', handleTab, false);

        // Collect all the focusable elements.
        focusableElements.current = getModalEl().querySelectorAll('a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select');

        // When unmounting...
        return () => {
            const modalRootForUnmount = document.getElementById('modal-root');
            modalRootForUnmount.removeChild(getModalEl());
            document.removeEventListener('keydown', handleTab, false);
            focusableElements.current = null;
        };
    }, [focusId]);

    return ReactDOM.createPortal(
        <div>
            <div className="modal" style={{ display: 'block' }}>
                <div className={`modal-dialog${addClasses ? ` ${addClasses}` : ''}`} role="alertdialog" aria-modal="true" aria-labelledby={labelId} aria-describedby={descriptionId}>
                    <div className="modal-content">
                        {modalChildren}
                    </div>
                </div>
            </div>
            <div className="modal-backdrop in" />
        </div>,
        getModalEl()
    );
};

ModalElement.propTypes = {
    /** Array of child elements inside the modal */
    modalChildren: PropTypes.array.isRequired,
    /** id of modal description element */
    descriptionId: PropTypes.string,
    /** CSS classes to add to the default */
    addClasses: PropTypes.string,
    /** id of first focusable element */
    focusId: PropTypes.string,
    /** id of modal label element */
    labelId: PropTypes.string,
};

ModalElement.defaultProps = {
    descriptionId: '',
    addClasses: '',
    focusId: '',
    labelId: '',
};


export const Modal = ({
    actuator,
    descriptionId,
    labelId,
    focusId,
    submitModal,
    closeModal,
    addClasses,
    children,
}) => {
    // True if modal is visible. Ignored if no actuator given.
    const [modalOpen, setModalOpen] = React.useState(false);

    // Open the modal
    const openModal = () => {
        setModalOpen(true);
    };

    // Default function to close the modal without doing anything.
    const internalCloseModal = () => {
        setModalOpen(false);
    };

    // Called when the user presses the ESC key.
    const handleKey = (e) => {
        if (!actuator || modalOpen) {
            e.stopPropagation();
            if (e.keyCode === keyCode.ESC) {
                // User typed ESC.
                if (closeModal) {
                    closeModal();
                } else {
                    internalCloseModal();
                }
            } else if (e.keyCode === keyCode.RETURN) {
                // User typed RETURN.
                if (submitModal) {
                    submitModal();
                }
            }
        }
    };

    React.useEffect(() => {
        // Have ESC key press close the modal.
        document.addEventListener('keydown', handleKey, false);

        return () => {
            document.removeEventListener('keydown', handleKey, false);
        };
    }, []);

    // We don't require/allow a click handler for the actuator, so we attach the built-in one
    // here. You can't add attributes to an existing component in React, but React has no issue
    // adding attributes while cloning a component.
    const modalActuator = actuator ? React.cloneElement(actuator, { onClick: openModal }) : null;

    // Pass important Modal states and functions to child objects without the parent component
    // needing to do it explicitly.
    const modalChildren = React.Children.map(children, (child) => {
        if (child.type === ModalHeader || child.type === ModalBody || child.type === ModalFooter) {
            return React.cloneElement(child, { cCloseModal: internalCloseModal, cModalOpen: modalOpen });
        }
        return child;
    });

    return (
        <>
            {modalActuator && <>{modalActuator}</>}
            {(!actuator || modalOpen) &&
                <ModalElement
                    modalChildren={modalChildren}
                    descriptionId={descriptionId}
                    addClasses={addClasses}
                    labelId={labelId}
                    focusId={focusId}
                />
            }
        </>
    );
};

Modal.propTypes = {
    /** Component (usually a button) that makes the modal appear */
    actuator: PropTypes.object,
    /** Called to close the modal if an actuator isn't provided */
    closeModal: PropTypes.func,
    /** Called to close the modal with a submit */
    submitModal: PropTypes.func,
    /** CSS classes to add to the default */
    addClasses: PropTypes.string,
    /** id of modal label element */
    labelId: PropTypes.string,
    /** id of modal description element */
    descriptionId: PropTypes.string,
    /** id of first focusable element */
    focusId: PropTypes.string,
    children: PropTypes.node,
};

Modal.defaultProps = {
    actuator: null,
    closeModal: null,
    submitModal: null,
    addClasses: '',
    labelId: '',
    descriptionId: '',
    focusId: '',
    children: null,
};
