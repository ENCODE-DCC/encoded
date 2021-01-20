import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';


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
// {this.state.displayModal ? <Modal>{child components}</Modal> : null}
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


export class ModalHeader extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.closeModal = this.closeModal.bind(this);
    }

    closeModal() {
        // Call close button's existing close handler if it had one first.
        if (this.chainedCloseModal) {
            this.chainedCloseModal();
        }

        // Now call the standard close handler.
        this.props.c_closeModal();
    }

    render() {
        const { title, closeModal, addCss, labelId } = this.props;
        let titleRender = null;

        // Handle the string and React component cases for the title
        if (title) {
            titleRender = typeof title === 'string' ? <h2>{title}</h2> : <div>{title}</div>;
        }

        // Chain in the given closeBtn function if given
        if (typeof closeModal === 'function') {
            this.chainedCloseModal = closeModal;
        }

        return (
            <div className={`modal__header${addCss ? ` ${addCss}` : ''}`} id={labelId}>
                {titleRender ? <div className="modal__header-title">{titleRender}</div> : null}
                {this.props.children}
                {closeModal ? <button type="button" className="modal__header-close" aria-label="Close" onClick={this.closeModal}><span aria-hidden="true">&times;</span></button> : null}
            </div>
        );
    }
}

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
    children: PropTypes.node,
    c_closeModal: PropTypes.func, // Auto-added
};

ModalHeader.defaultProps = {
    addCss: '',
    title: null,
    closeModal: null,
    labelId: '',
    children: null,
    c_closeModal: null,
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


export class ModalFooter extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.closeModal = this.closeModal.bind(this);
        this.submitModal = this.submitModal.bind(this);
    }

    closeModal() {
        // Call close button's existing close handler if it had one first.
        if (this.chainedCloseModal) {
            this.chainedCloseModal();
        }

        // Now call the standard close handler.
        this.props.c_closeModal();
    }

    submitModal() {
        const { submitBtn, dontClose } = this.props;
        if (typeof submitBtn === 'function') {
            submitBtn();
        }
        if (!dontClose) {
            this.closeModal();
        }
    }

    render() {
        const { submitBtn, submitTitle, addCss, cancelTitle } = this.props;
        let { closeModal } = this.props;
        let submitBtnComponent = null;
        let closeBtnComponent = null;

        // Make a Submit button component -- either the given one or a default one that calls the
        // given function. Note: if you pass `null` in the submitBtn property, this component
        // thinks that's a function because of an old Javascript characteristic.
        if (submitBtn) {
            submitBtnComponent = (typeof submitBtn === 'object') ? submitBtn : <button type="button" className="btn btn-info" onClick={this.submitModal}>{submitTitle}</button>;
        }

        // If the given closeModal property is a component, make sure it calls the close function
        // when it gets clicked.
        if (typeof closeModal === 'object') {
            // If the close button had a click handler, save it so we can call it before calling
            // the standard one.
            if (closeModal.props.onClick) {
                this.chainedCloseModal = closeModal.props.onClick;
            }
            closeModal = React.cloneElement(closeModal, { onClick: this.closeModal });
        } else if (typeof closeModal === 'function') {
            this.chainedCloseModal = closeModal;
        }

        // Make a Cancel button component -- either the given one, a default one that calls the
        // given function, or a default one that calls the default function. Note: if you pass
        // `null` in the closeModal property, this component thinks that's a function because of an
        // old Javascript characteristic.
        if (closeModal) {
            const closeBtnFunc = (typeof closeModal === 'function') ? closeModal : (typeof closeModal === 'boolean' ? this.props.c_closeModal : null);
            closeBtnComponent = (typeof closeModal === 'object') ? closeModal : <button type="button" className="btn btn-default" onClick={closeBtnFunc} id={this.props.closeId}>{cancelTitle}</button>;
        }

        return (
            <div className={`modal__footer${addCss ? ` ${addCss}` : ''}`}>
                {this.props.children ? this.props.children : null}
                {submitBtnComponent || closeBtnComponent ?
                    <div className="modal__footer-controls">
                        {closeBtnComponent}
                        {submitBtnComponent}
                    </div>
                : null}
            </div>
        );
    }
}

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
    c_closeModal: PropTypes.func, // Auto-add
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
    c_closeModal: null,
    children: null,
};


/**
 * Renders the modal without conditions -- conditions need to be handled outside this component.
 */
export class ModalElement extends React.Component {
    constructor(props) {
        super(props);
        this.handleTab = this.handleTab.bind(this);
        this.modalEl = document.createElement('div');
        this.focusableElements = null;
    }

    componentDidMount() {
        // Modal HTML gets injected at the end of <body> so the backdrop overlay works, even with other
        // fixed elements on the page. The "modal-root" div is defined in app.js at the end of the
        // <body> section.
        const modalRoot = document.getElementById('modal-root');
        modalRoot.appendChild(this.modalEl);

        // Focus screen reader on the given element if specified.
        if (this.props.focusId) {
            const focusElement = document.getElementById(this.props.focusId);
            if (focusElement) {
                focusElement.focus();
            }
        }

        // Attach tab-key listener.
        document.addEventListener('keydown', this.handleTab, false);

        // Collect all the focusable elements.
        this.focusableElements = this.modalEl.querySelectorAll('a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select');
    }

    componentWillUnmount() {
        const modalRoot = document.getElementById('modal-root');
        modalRoot.removeChild(this.modalEl);
        document.removeEventListener('keydown', this.handleTab, false);
        this.focusableElements = null;
    }

    /**
     * Handle key presses while the modal is open, but only handle and consume TAB key presses
     * setting focus to the next or previous elements within the modal, depending on whether the
     * shift key is held down at the time.
     * @param {object} e React synthetic event
     */
    handleTab(e) {
        if (e.keyCode === 9 && this.focusableElements) {
            const firstFocusableElement = this.focusableElements[0];
            const lastFocusableElement = this.focusableElements[this.focusableElements.length - 1];
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
    }

    render() {
        return ReactDOM.createPortal(
            <div>
                <div className="modal" style={{ display: 'block' }}>
                    <div className={`modal-dialog${this.props.addClasses ? ` ${this.props.addClasses}` : ''}`} role="alertdialog" aria-modal="true" aria-labelledby={this.props.labelId} aria-describedby={this.props.descriptionId}>
                        <div className="modal-content">
                            {this.props.modalChildren}
                        </div>
                    </div>
                </div>
                <div className="modal-backdrop in" />
            </div>,
            this.modalEl
        );
    }
}

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


export class Modal extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            modalOpen: false, // True if modal is visible. Ignored if no actuator given
        };
        this.handleKey = this.handleKey.bind(this);
        this.openModal = this.openModal.bind(this);
        this.closeModal = this.closeModal.bind(this);
    }

    componentDidMount() {
        // Have ESC key press close the modal.
        document.addEventListener('keydown', this.handleKey, false);
    }

    componentWillUnmount() {
        document.removeEventListener('keydown', this.handleKey, false);
    }

    // Called when the user presses the ESC key.
    handleKey(e) {
        if (!this.props.actuator || this.state.modalOpen) {
            if (e.keyCode === 27) {
                // User typed ESC.
                if (this.props.closeModal) {
                    this.props.closeModal();
                } else {
                    this.closeModal();
                }
            } else if (e.keyCode === 13) {
                // User typed RETURN.
                if (this.props.submitModal) {
                    this.props.submitModal();
                }
            }
        }
    }

    // Open the modal
    openModal() {
        this.setState({ modalOpen: true });
    }

    // Default function to close the modal without doing anything.
    closeModal() {
        this.setState({ modalOpen: false });
    }

    render() {
        // We don't require/allow a click handler for the actuator, so we attach the built-in one
        // here. You can't add attributes to an existing component in React, but React has no issue
        // adding attributes while cloning a component.
        const actuator = this.props.actuator ? React.cloneElement(this.props.actuator, { onClick: this.openModal }) : null;

        // Pass important Modal states and functions to child objects without the parent component
        // needing to do it explicitly.
        const modalChildren = React.Children.map(this.props.children, (child) => {
            if (child.type === ModalHeader || child.type === ModalBody || child.type === ModalFooter) {
                return React.cloneElement(child, { c_closeModal: this.closeModal, c_modalOpen: this.state.modalOpen });
            }
            return child;
        });

        return (
            <>
                {actuator ? <>{actuator}</> : null}
                {!this.props.actuator || this.state.modalOpen ?
                    <ModalElement
                        modalChildren={modalChildren}
                        descriptionId={this.props.descriptionId}
                        addClasses={this.props.addClasses}
                        labelId={this.props.labelId}
                        focusId={this.props.focusId}
                    />
                : null}
            </>
        );
    }
}

Modal.propTypes = {
    actuator: PropTypes.object, // Component (usually a button) that makes the modal appear
    closeModal: PropTypes.func, // Called to close the modal if an actuator isn't provided
    submitModal: PropTypes.func, // Called to close the modal with a submit
    addClasses: PropTypes.string, // CSS classes to add to the default
    labelId: PropTypes.string, // id of modal label element
    descriptionId: PropTypes.string, // id of modal description element
    focusId: PropTypes.string, // id of first focusable element
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
