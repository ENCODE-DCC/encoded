"use strict";
var React = require('react');

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
        title: React.PropTypes.string.isRequired, // Title in modal's header
        btnOk: React.PropTypes.string, // Title of OK button
        btnCancel: React.PropTypes.string // Title of Cancel button
    },

    getInitialState: function() {
        return {
            modal: null,
            visible: false
        };
    },

    handleClick: function(name, e) {
        this.setState({modal: name, visible: true});
    },

    handleBtnOk: function() {
        this.setState({visible: false});
    },

    handleBtnCancel: function() {
        this.setState({visible: false});
    },

    render: function() {
        // Get child nodes and assign the Modal click handler to open the model when the child is clicked
        var children = React.Children.map(this.props.children, function(child) {
            if (child.props.modal) {
                // Child has "modal" prop; assign Modal click handler to child and pass it the child’s modal property.
                // Modifying child React components requires modifying a clone, so...
                var clone = React.cloneElement(child, {onClick: this.handleClick.bind(this, child.props.modal)});
                return clone;
            }

            // Child doesn't have a "modal" prop; don't bother modifying (cloning with props) it
            return child;
        }.bind(this));

        // Use or make OK button title
        var btnOkTitle = this.props.btnOk ? this.props.btnOk : 'OK';

        return (
            <div>
                {children}
                {this.state.visible ?
                    <div>
                        <div className="modal" style={{display: 'block'}}>
                            <div className="modal-dialog">
                                <div className="modal-content">
                                    <div className="modal-header">
                                        <h4 className="modal-title">{this.props.title}</h4>
                                    </div>
                                    {this.state.modal}
                                    <div className='modal-footer'>
                                        {this.props.btnCancel ? <button className="btn btn-default" onClick={this.handleBtnCancel}>{this.props.btnCancel}</button> : null}
                                        <button className="btn btn-primary" onClick={this.handleBtnOk}>{btnOkTitle}</button>
                                    </div>
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

