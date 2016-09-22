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


module.exports.ModalMixin = {
    childContextTypes: {
        modalOpen: React.PropTypes.bool, // T if modal is visible
        alertOpen: React.PropTypes.object, // List of open alerts
        openModal: React.PropTypes.func, // Function to open the modal
        closeModal: React.PropTypes.func // Function to close the modal
    },

    // Retrieve current React context
    getChildContext: function() {
        return {
            modalOpen: this.state.modalOpen,
            alertOpen: this.state.alertOpen,
            openModal: this.openModal,
            closeModal: this.closeModal
        };
    },

    getInitialState: function() {
        return {
            modalOpen: false, // T if the model and blocking backdrop are visible
            alertOpen: {} // Tracks the open state of each alert
        };
    },

    // Open the modal
    openModal: function() {
        this.setState({modalOpen: true});

        // Add class to body element to make modal-backdrop div visible
        document.body.classList.add('modal-open');
    },

    // Close the modal
    closeModal: function() {
        this.setState({modalOpen: false});

        // Remove class from body element to make modal-backdrop div visible
        document.body.classList.remove('modal-open');
    },

    // Open an alert with the ID given in 'alert'
    openAlert: function(alert) {
        var currOpenStates = this.state.alertOpen;
        currOpenStates[alert] = true;
        this.setState({alertOpen: currOpenStates});
    },

    // Close the alert with the ID given in 'alert'
    closeAlert: function(alert) {
        var currOpenStates = this.state.alertOpen;
        currOpenStates[alert] = false;
        this.setState({alertOpen: currOpenStates});
    }
};


var Modal = module.exports.Modal = React.createClass({
    propTypes: {
        title: React.PropTypes.string.isRequired, // Title in modal's header
        wrapperClassName: React.PropTypes.string, // CSS classes for modal trigger wrapper
        modalClass: React.PropTypes.string, // CSS class for modal header
    },

    contextTypes: {
        openModal: React.PropTypes.func, // Function to open the modal
        modalOpen: React.PropTypes.bool // T if modal is visible
    },

    getInitialState: function() {
        return {
            modal: null
        };
    },

    handleClick: function(el) {
        this.setState({modal: el});
        this.context.openModal();
    },

    render: function() {
        // Get child nodes and assign the Modal click handler to open the model when the child is clicked
        var children = React.Children.map(this.props.children, child => {
            if (child.props.modal) {
                // Child has "modal" prop; assign Modal click handler to child and pass it the child’s modal property.
                // Modifying child React components requires modifying a clone, so...
                var clone = cloneWithProps(child, {onClick: this.handleClick.bind(this, child.props.modal)});
                return clone;
            }

            // Child doesn't have a "modal" prop; don't bother modifying (cloning with props) it
            return child;
        });

        // Use or make OK button title
        var btnOkTitle = this.props.btnOk ? this.props.btnOk : 'OK';

        return (
            <div className={this.props.wrapperClassName}>
                {children}
                {this.context.modalOpen ?
                    <div>
                        <div className="modal" style={{display: 'block'}}>
                            <div className="modal-dialog">
                                <div className="modal-content">
                                    <div className={"modal-header " + this.props.modalClass}>
                                        <h4 className="modal-title">{this.props.title}</h4>
                                    </div>
                                    {this.state.modal}
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


var Alert = module.exports.Alert = React.createClass({
    propTypes: {
        content: React.PropTypes.object.isRequired, // Content of alert
        wrapperClassName: React.PropTypes.string // CSS classes for modal trigger wrapper
    },

    contextTypes: {
        alertOpen: React.PropTypes.object // List of visible alerts
    },

    render: function() {
        return (
            <div className={this.props.wrapperClassName}>
                {this.context.alertOpen[this.props.id] ?
                    <div>
                        <div className="modal" style={{display: 'block'}}>
                            <div className="modal-dialog">
                                <div className="modal-content">
                                    {this.props.content}
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
