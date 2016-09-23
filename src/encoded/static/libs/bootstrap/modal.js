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


var Modal = module.exports.Modal = React.createClass({
    propTypes: {
        modalOpen: React.PropTypes.bool, // True if modal is open
        closeModal: React.PropTypes.func, // Callback to parent function when modal is closed
        wrapperClassName: React.PropTypes.string, // CSS classes for modal trigger wrapper
        modalClass: React.PropTypes.string, // CSS class for modal header
    },

    render: function() {
        let {modalOpen, wrapperClassName, modalClass, title} = this.props;

        return (
            <div>
                {modalOpen ?
                    <div className={wrapperClassName}>
                        <div className="modal" style={{display: 'block'}}>
                            <div className="modal-dialog">
                                <div className="modal-content">
                                    {this.props.children}
                                </div>
                            </div>
                        </div>
                        <div className="modal-backdrop in"></div>
                    </div>
                : null}
            </div>
        );
    }
});


var ModalHeader = module.exports.ModalHeader = React.createClass({
    render: function() {
        return (
            <div className="modal-header">
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
    render: function() {
        return (
            <div className="modal-footer">
                {this.props.children}
            </div>
        );
    }
});
