"use strict";
var React = require('react');
var _ = require('underscore');


var InputMixin = module.exports.InputMixin = {
    getInitialState: function() {
        return {formErrors: {}};
    },

    getFormErrors: function() {
        return this.state.formErrors;
    },

    // Set form errors without affecting ones already set
    setFormErrors: function(id, msg) {
        var formErrors = this.state.formErrors;
        formErrors[id] = msg;
        this.setState({formErrors: formErrors});
    },

    // Clear error state from an input with 'id' as its Input id.
    // This is called by Input components when their contents change.
    clrFormErrors: function(id) {
        var errors = this.state.formErrors;
        errors[id] = '';
        this.setState({formErrors: errors});
    }
};


// Handles most form inputs, like text fields and dropdowns. The different Bootstrap styles of
// inputs can be handled through the labelClassName, groupClassName, and wrapperClassName properties.
var Input = module.exports.Input = React.createClass({
    propTypes: {
        type: React.PropTypes.string.isRequired, // Type of input
        id: React.PropTypes.string.isRequired, // Unique ID of input
        label: React.PropTypes.oneOfType([
            React.PropTypes.string,
            React.PropTypes.object
        ]), // <label> for input; string or another React component
        error: React.PropTypes.string, // Error message to display below input
        labelClassName: React.PropTypes.string, // CSS classes to add to labels
        groupClassName: React.PropTypes.string, // CSS classes to add to control groups (label/input wrapper div)
        wrapperClassName: React.PropTypes.string, // CSS classes to add to wrapper div around inputs
        inputClassName: React.PropTypes.string, // CSS classes to add to input elements themselves
        rows: React.PropTypes.string, // Number of rows in textarea
        value: React.PropTypes.string, // Value to pre-fill input with
        required: React.PropTypes.bool // T to make this a required field
    },

    // Get the text the user entered from the text-type field. Meant to be called from
    // parent components.
    getValue: function() {
        return React.findDOMNode(this.refs.input).value;
    },

    // Get the selected option from a <select> list
    getSelectedOption: function() {
        var optionNodes = this.refs.input.getDOMNode().getElementsByTagName('option');

        // Get the DOM node for the selected <option>
        var selectedOptionNode = _(optionNodes).find(function(option) {
            return option.selected;
        });

        // Get the selected options value, or its text if it has no value
        if (selectedOptionNode) {
            return selectedOptionNode.getAttribute('value') || selectedOptionNode.innerHtml;
        }

        // Nothing selected
        return '';
    },

    render: function() {
        var input, inputClasses;
        var groupClassName = 'form-group' + this.props.groupClassName ? ' ' + this.props.groupClassName : '';

        switch (this.props.type) {
            case 'text':
            case 'email':
                inputClasses = 'form-control' + (this.props.error ? ' error' : '') + (this.props.inputClassName ? ' ' + this.props.inputClassName : '');
                input = (
                    <div className={this.props.groupClassName}>
                        {this.props.label ? <label htmlFor={this.props.id} className={this.props.labelClassName}><span>{this.props.label}{this.props.required ? ' *' : ''}</span></label> : null}
                        <div className={this.props.wrapperClassName}>
                            <input className={inputClasses} type={this.props.type} id={this.props.id} ref="input" value={this.props.value} onChange={this.props.clearError} />
                            <div className="form-error">{this.props.error ? <span>{this.props.error}</span> : <span>&nbsp;</span>}</div>
                        </div>
                    </div>
                );
                break;

            case 'select':
                input = (
                    <div className={this.props.groupClassName}>
                        {this.props.label ? <label htmlFor={this.props.id} className={this.props.labelClassName}><span>{this.props.label}{this.props.required ? ' *' : ''}</span></label> : null}
                        <div className={this.props.wrapperClassName}>
                            <select className="form-control" ref="input">
                                {this.props.children}
                            </select>
                            <div className="form-error">{this.props.error ? <span>{this.props.error}</span> : <span>&nbsp;</span>}</div>
                        </div>
                    </div>
                );
                break;

            case 'textarea':
                inputClasses = 'form-control' + (this.props.error ? ' error' : '') + (this.props.inputClassName ? ' ' + this.props.inputClassName : '');
                input = (
                    <div className={this.props.groupClassName}>
                        {this.props.label ? <label htmlFor={this.props.id} className={this.props.labelClassName}><span>{this.props.label}{this.props.required ? ' *' : ''}</span></label> : null}
                        <div className={this.props.wrapperClassName}>
                            <textarea className={inputClasses} id={this.props.id} ref="input" value={this.props.value} onChange={this.props.clearError} rows={this.props.rows} />
                            <div className="form-error">{this.props.error ? <span>{this.props.error}</span> : <span>&nbsp;</span>}</div>
                        </div>
                    </div>
                );
                break;

            case 'submit':
                var title = this.props.value ? this.props.value : 'Submit';
                input = (
                    <div className={this.props.groupClassName}>
                        <div className={this.props.wrapperClassName}>
                            <input className="btn btn-primary" type={this.props.type} value={title} onClick={this.props.submitHandler} />
                        </div>
                    </div>
                );
                break;

            default:
                break;
        }

        return <div>{input}</div>;
    }
});
