'use strict';
var React = require('react');
var cloneWithProps = require('react/lib/cloneWithProps');


// Display a modal dialog box that blocks all other page input until it's dismissed.
// Use it as a wrapper around a button or link that actuates it, like:
// <Modal title="My Modal" btnOk="OK" btnCancel="Cancel">
//     <button modal={<ModalContent />}>Open Modal</button>
// </Modal>
// The button or link to actuate the modal must have "modal" property that references the
// React component that renders the content of the modal.
// You must pass a "title" property to the Modal component. You can also pass btnOk which
// specifies the text of the button to confirm and dismiss the modal, and it defaults to "OK".
// You can pass btnCancel which specifies the text of the button to cancel and dismiss the
// modal. If you don't pass this property, no Cancel button is displayed.

// The method of rendering the modal to a div appended to <body> rather than into the React virtual
// DOM comes from: http://jamesknelson.com/rendering-react-components-to-the-document-body/


var Modal = module.exports.Modal = React.createClass({
    propTypes: {
        actuator: React.PropTypes.object, // Component (usually a button) that makes the modal appear
        closeModal: React.PropTypes.func // Called to close the modal if an actuator isn't provided'
    },

    getInitialState: function() {
        return {
            modalOpen: false // True if modal is visible. Ignored if no actuator given
        }
    },

    componentDidMount: function() {
        // Modal HTML gets injected at the end of <body> so the backdrop overlay works, even with other
        // fixed elements on the page.
        this.modalEl = document.createElement('div');
        document.body.appendChild(this.modalEl);
        this.renderModal();

        // Have ESC key press close the modal.
        document.addEventListener('keydown', this.handleEsc, false);
    },

    componentWillUnmount: function() {
        React.unmountComponentAtNode(this.modalEl);
        document.body.removeChild(this.modalEl);
        document.removeEventListener('keydown', this.handleEsc, false);
    },

    componentDidUpdate: function() {
        this.renderModal();
    },

    // Called when the user presses the ESC key.
    handleEsc: function(e) {
        if ((!this.props.actuator || this.state.modalOpen) && e.keyCode === 27) {
            if (this.props.closeModal) {
                this.props.closeModal();
            } else {
                this.closeModal();
            }
        }
    },

    // Open the modal
    openModal: function() {
        this.setState({modalOpen: true});

        // Add class to body element to make modal-backdrop div visible
        document.body.classList.add('modal-open');
    },

    // Default function to close the modal without doing anything.
    closeModal: function() {
        this.setState({modalOpen: false});

        // Remove class from body element to make modal-backdrop div visible
        document.body.classList.remove('modal-open');
    },

    // Render the modal JSX into the element this component appended to the <body> element. that
    // lets us properly render the fixed-position backdrop so that it overlays the fixed-position
    // navigation bar.
    renderModal: function() {
        React.render(
            <div>
                {!this.props.actuator || this.state.modalOpen ?
                    <div>
                        <div className="modal" style={{display: "block"}}>
                            <div className="modal-dialog">
                                <div className="modal-content">
                                    {this.modalChildren}
                                </div>
                            </div>
                        </div>
                        <div className="modal-backdrop in"></div>
                    </div>
                : null}
            </div>,
            this.modalEl
        );
    },

    render: function() {
        // We don't require/allow a click handler for the actuator, so we attach the one from
        // ModalMixin here. You can't add attributes to an existing component in React, but React
        // has no issue adding attributes while cloning a component.
        let actuator = this.props.actuator ? cloneWithProps(this.props.actuator, {onClick: this.openModal}) : null;

        // Pass important Modal states and functions to child objects without the parent component
        // needing to do it explicitly.
        this.modalChildren = React.Children.map(this.props.children, child => {
            if (child.type === ModalHeader.type || child.type === ModalBody.type || child.type === ModalFooter.type) {
                return cloneWithProps(child, {closeModal: this.closeModal, modalOpen: this.state.modalOpen});
            }
            return child;
        });

        return actuator ? <span>{actuator}</span> : null;
    }
});


var ModalHeader = module.exports.ModalHeader = React.createClass({
    propTypes: {
        title: React.PropTypes.oneOfType([
            React.PropTypes.string, // String to display as an <h4> title
            React.PropTypes.object // React component to display for the title 
        ]),
        closeBtn: React.PropTypes.oneOfType([
            React.PropTypes.bool, // True to display the close button in the header with the built-in handler
            React.PropTypes.func // If not using an actuator on <Modal>, provide a function to close the modal
        ])
    },

    render: function() {
        let {title, closeBtn} = this.props;
        let titleRender = null;

        // Handle the string and React component cases for the title
        if (title) {
            titleRender = typeof title === 'string' ? <h4>{title}</h4> : <div>{title}</div>;
        }

        return (
            <div className="modal-header">
                {closeBtn ? <button type="button" className="close" aria-label="Close" onClick={typeof closeBtn === 'function' ? closeBtn : this.props.closeModal}><span aria-hidden="true">&times;</span></button> : null}
                {titleRender ? <div>{titleRender}</div> : null}
                {this.props.children}
            </div>
        );
    }
});


var ModalBody = module.exports.ModalBody = React.createClass({
    render: function() {
        return (
            <div className="modal-body">
                {this.props.children}
            </div>
        );
    }
});


var ModalFooter = module.exports.ModalFooter = React.createClass({
    propTypes: {
        submitBtn: React.PropTypes.oneOfType([
            React.PropTypes.object, // Submit button is a React component; just render it
            React.PropTypes.func // Function to call when default-rendered Submit button clicked
        ]),
        closeBtn: React.PropTypes.oneOfType([
            React.PropTypes.bool, // Use default-rendered Cancel button that closes the modal
            React.PropTypes.object, // Cancel button is a React component; just render it
            React.PropTypes.func // Function to call when default-rendered Cancel button clicked
        ])
    },

    render: function() {
        let {submitBtn, closeBtn} = this.props;
        let submitBtnComponent = null;
        let closeBtnComponent = null;

        // Make a Submit button component -- either the given one or a default one that calls the
        // given function. Note: if you pass `null` in the submitBtn property, this component
        // thinks that's a function because of an old Javascript characteristic.
        if (submitBtn) {
            submitBtnComponent = (typeof submitBtn === 'object') ? submitBtn : <button className="btn btn-info" onClick={submitBtn}>Submit</button>;
        }

        // If the given closeModal property is a component, make sure it calls the close function
        // when it gets clicked.
        if (typeof closeBtn === 'object') {
            closeBtn = cloneWithProps(closeBtn, {onClick: this.props.closeModal});
        }

        // Make a Cancel button component -- either the given one, a default one that calls the
        // given function, or a default one that calls the default function. Note: if you pass
        // `null` in the closeBtn property, this component thinks that's a function because of an
        // old Javascript characteristic.
        if (closeBtn) {
            let closeBtnFunc = (typeof closeBtn === 'function') ? closeBtn : (typeof closeBtn === 'boolean' ? this.props.closeModal : null);
            closeBtnComponent = (typeof closeBtn === 'object') ? closeBtn : <button className="btn btn-info" onClick={closeBtnFunc}>Cancel</button>;
        }

        return (
            <div className="modal-footer">
                {this.props.children ? this.props.children : null}
                {submitBtnComponent || cancelBtnComponent ?
                    <div className="modal-footer-controls">
                        {closeBtnComponent}
                        {submitBtnComponent}
                    </div>
                : null}
                {this.props.children}
            </div>
        );
    }
});
