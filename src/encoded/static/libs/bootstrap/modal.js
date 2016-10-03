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


module.exports.ModalMixin = {
    childContextTypes: {
        Modal_modalOpen: React.PropTypes.bool, // T if modal is visible
        Modal_openModal: React.PropTypes.func, // Function to open the modal
        Modal_cancelBtnDefault: React.PropTypes.func, // Default function to close the modal
    },

    // Retrieve current React context
    getChildContext: function() {
        return {
            Modal_modalOpen: this.state.Modal_modalOpen,
            Modal_openModal: this.Modal_openModal,
            Modal_cancelBtnDefault: this.Modal_cancelBtnDefault
        };
    },

    getInitialState: function() {
        return {
            Modal_modalOpen: false // T if the modal and blocking backdrop are visible
        };
    },

    // Open the modal
    Modal_openModal: function() {
        this.setState({Modal_modalOpen: true});

        // Add class to body element to make modal-backdrop div visible
        document.body.classList.add('modal-open');
    },

    // Default function to close the modal without doing anything.
    Modal_cancelBtnDefault: function() {
        this.setState({Modal_modalOpen: false});

        // Remove class from body element to make modal-backdrop div visible
        document.body.classList.remove('modal-open');
    },
};


var Modal = module.exports.Modal = React.createClass({
    propTypes: {
        actuator: React.PropTypes.object.isRequired // Component (usually a button) that makes the modal appear
    },

    contextTypes: {
        Modal_modalOpen: React.PropTypes.bool, // Is the modal open or not? Owned by ModalMixin
        Modal_openModal: React.PropTypes.func, // Function to call to open the modal. Owned by ModalMixin
        Modal_cancelBtnDefault: React.PropTypes.func // Function to call to close the modal. Owned by ModalMixin
    },

    componentDidMount: function() {
        // Modal HTML gets injected at the end of <body> so the backdrop overlay works, even with other
        // fixed elements on the page.
        this.modalEl = document.createElement('div');
        document.body.appendChild(this.modalEl);
        this.renderModal();

        // Have ESC key press close the modal.
        document.addEventListener('keydown', this.handleEsc.bind(this), false);
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
        if (this.context.Modal_modalOpen && e.keyCode === 27) {
            this.context.Modal_cancelBtnDefault();
        }
    },

    // Render the modal JSX into the element this component appended to the <body> element. that
    // lets us properly render the fixed-position backdrop so that it overlays the fixed-position
    // navigation bar.
    renderModal: function() {
        React.render(
            <div>
                {this.context.Modal_modalOpen ?
                    <div>
                        <div className="modal" style={{display: "block"}}>
                            <div className="modal-dialog">
                                <div className="modal-content">
                                    {this.props.children}
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
        let actuator = cloneWithProps(this.props.actuator, {onClick: this.context.Modal_openModal});

        return <span>{actuator}</span>;
    }
});


var ModalHeader = module.exports.ModalHeader = React.createClass({
    propTypes: {
        title: React.PropTypes.oneOfType([
            React.PropTypes.string, // String to display as an <h4> title
            React.PropTypes.object // React component to display for the title 
        ]),
        cancelBtn: React.PropTypes.bool // True to display the close button in the header
    },

    contextTypes: {
        Modal_cancelBtnDefault: React.PropTypes.func // Function to call to close the modal. Owned by ModalMixin
    },

    render: function() {
        let {title, cancelBtn} = this.props;
        let titleRender = null;

        // Handle the string and React component cases for the title
        if (title) {
            titleRender = typeof title === 'string' ? <h4>{title}</h4> : <div>{title}</div>;
        }

        return (
            <div className="modal-header">
                {cancelBtn ? <button type="button" className="close" aria-label="Close" onClick={this.context.Modal_cancelBtnDefault}><span aria-hidden="true">&times;</span></button> : null}
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
        cancelBtn: React.PropTypes.oneOfType([
            React.PropTypes.bool, // Use default-rendered Cancel button that closes the modal
            React.PropTypes.object, // Cancel button is a React component; just render it
            React.PropTypes.func // Function to call when default-rendered Cancel button clicked
        ])
    },

    contextTypes: {
        Modal_cancelBtnDefault: React.PropTypes.func // Function to call to close the modal. Owned by ModalMixin
    },

    render: function() {
        let {submitBtn, cancelBtn} = this.props;
        let submitBtnComponent = null;
        let cancelBtnComponent = null;

        // Make a Submit button component -- either the given one or a default one that calls the
        // given function. Note: if you pass `null` in the submitBtn property, this component
        // thinks that's a function because of an old Javascript characteristic.
        if (submitBtn) {
            submitBtnComponent = (typeof submitBtn === 'object') ? submitBtn : <button className="btn btn-info" onClick={submitBtn}>Submit</button>;
        }

        // Make a Cancel button component -- either the given one, a default one that calls the
        // given function, or a default one that calls the default function. Note: if you pass
        // `null` in the cancelBtn property, this component thinks that's a function because of an
        // old Javascript characteristic.
        if (cancelBtn) {
            let cancelBtnFunc = (typeof cancelBtn === 'function') ? cancelBtn : (typeof cancelBtn === 'boolean' ? this.context.Modal_cancelBtnDefault : null);
            cancelBtnComponent = (typeof cancelBtn === 'object') ? cancelBtn : <button className="btn btn-info" onClick={cancelBtnFunc}>Cancel</button>;
        }

        return (
            <div className="modal-footer">
                {this.props.children ? this.props.children : null}
                {submitBtnComponent || cancelBtnComponent ?
                    <div className="modal-footer-controls">
                        {cancelBtnComponent}
                        {submitBtnComponent}
                    </div>
                : null}
                {this.props.children}
            </div>
        );
    }
});
