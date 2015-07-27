"use strict";
// Use this module when you have a form with input fields and an optional submit button.
// It supplies an Input component used for all types of form fields (e.g. text fields,
// drop-downs, etc.). The component that includes the form must also include the InputMixin
// mixin that handles standard form things like saving and retrieving form values, and
// handling validation errors.

var React = require('react');
var _ = require('underscore');


// Surround Input elements with the Form element
var Form = module.exports.Form = React.createClass({
    // Add 'id' property to any Input elements. Make it a copy of the Input's ref. Run through all children
    // of the form, and any children of those children, recursively.
    createInputRefs: function(children) {
        var processedChildren = React.Children.map(children, child => {
            var props = {};

            // Copy ref to new id property.
            if (child.ref) {
                props.id = child.ref;
            }

            // If the current child has children, process them recursively and assign the result to the new children property
            if (child.props && child.props.children) {
                props.children = this.createInputRefs(child.props.children);
            }

            // If we made new properties, clone the child and assign the properties to the clone
            return Object.keys(props).length ? React.cloneElement(child, props) : child;
        });
        return processedChildren;
    },

    render: function() {
        // Before rendering, copy any refs on any elements in the form to each element's id property
        var children = this.createInputRefs(this.props.children);
        return (
            <form onSubmit={this.props.submitHandler} className={this.props.formClassName}>
                {children}
            </form>
        );
    }
});


var FormMixin = module.exports.FormMixin = {
    formValues: {},

    // Do not call; called by React.
    getInitialState: function() {
        return {formErrors: {}};
    },

    // Retrieves the saved value of the Input with the given 'ref' value. saveFormValue
    // must already have been called with this Input's value.
    getFormValue: function(ref) {
        return this.formValues[ref];
    },

    // Retrieves the saved value of the Input with the given 'ref' value, and the Input
    // value must be numeric. If the Input had no entered value at all, the empty string is
    // returned. If the Input had an entered value but it wasn't numeric, null is returned.
    // If the Input had a proper numberic value, a Javascript 'number' type is returned
    // with the entered value.
    getFormValueNumber: function(ref) {
        var value = this.getFormValue(ref);
        if (value) {
            var numericValue = value.match(/^\s*(\d*)\s*$/);
            if (numericValue) {
                return parseInt(numericValue[1], 10);
            }
            return null;
        }
        return '';
    },

    // Normally used after the submit button is clicked. Call this to save the value
    // from the Input with the given 'ref' value and the value itself. This does
    // NOT modify the form input values; it just saves them for later processing.
    saveFormValue: function(ref, value) {
        this.formValues[ref] = value;
    },

    // Call this to avoid calling 'saveFormValue' for every form item. It goes through all the
    // form items with refs (should be all of them) and saves a formValue property with the
    // corresponding value from the DOM.
    saveAllFormValues: function() {
        if (this.refs && Object.keys(this.refs).length) {
            Object.keys(this.refs).map(ref => {
                this.saveFormValue(ref, this.refs[ref].getValue());
            });
        }
    },

    // Get the saved form error for the Input with the given 'ref' value.
    getFormError: function(ref) {
        return this.state.formErrors[ref];
    },

    // Save a form error for the given Input's 'ref' value for later retrieval with getFormError.
    // The message that should be displayed to the user is passed in 'msg'.
    setFormErrors: function(ref, msg) {
        var formErrors = this.state.formErrors;
        formErrors[ref] = msg;
        this.setState({formErrors: formErrors});
    },

    // Clear error state from the Input with the given 'ref' value. This should be passed to
    // Input components in the 'clearError' property so that it can be called when an Input's
    // value changes.
    clrFormErrors: function(ref) {
        var errors = this.state.formErrors;
        errors[ref] = '';
        this.setState({formErrors: errors});
    },

    // Return true if the form's current state shows any Input errors. Return false if no
    // errors are indicated. This should be called in the render function so that the submit
    // form function will have had a chance to record any errors.
    anyFormErrors: function() {
        var formErrors = Object.keys(this.state.formErrors);

        if (formErrors.length) {
            return _(formErrors).any(errKey => {
                return this.state.formErrors[errKey];
            });
        }
        return false;
    },

    // Do form validation on the required fields. Each field checked must have a unique ref,
    // and the boolean 'required' field set if it's required. All the Input's values must
    // already have been collected with saveFormValue. Returns true if all required fields
    // have values, or false if any do not. It also sets any empty required Inputs error
    // to the 'Required' message so it's displayed on the next render.
    validateDefault: function() {
        var valid = true;
        Object.keys(this.refs).forEach(ref => {
            if (this.refs[ref].props.required && !this.getFormValue(ref)) {
                // Required field has no value. Set error state to render
                // error, and remember to return false.
                this.setFormErrors(ref, 'Required');
                valid = false;
            } else if (this.refs[ref].props.format === 'number') {
                // Validate that format="number" fields have a valid number in them
                if (this.getFormValueNumber(ref) === null) {
                    this.setFormErrors(ref, 'Number only');
                    valid = false;
                }
            }
        });
        return valid;
    }
};


// Handles most form inputs, like text fields and dropdowns. The different Bootstrap styles of
// inputs can be handled through the labelClassName, groupClassName, and wrapperClassName properties.
var Input = module.exports.Input = React.createClass({
    propTypes: {
        type: React.PropTypes.string.isRequired, // Type of input
        label: React.PropTypes.oneOfType([
            React.PropTypes.string,
            React.PropTypes.object
        ]), // <label> for input; string or another React component
        placeholder: React.PropTypes.string, // <input> placeholder text
        error: React.PropTypes.string, // Error message to display below input
        labelClassName: React.PropTypes.string, // CSS classes to add to labels
        groupClassName: React.PropTypes.string, // CSS classes to add to control groups (label/input wrapper div)
        wrapperClassName: React.PropTypes.string, // CSS classes to add to wrapper div around inputs
        inputClassName: React.PropTypes.string, // CSS classes to add to input elements themselves
        rows: React.PropTypes.string, // Number of rows in textarea
        value: React.PropTypes.string, // Value to pre-fill input with
        defaultValue: React.PropTypes.string, // Default value for <select>
        required: React.PropTypes.bool, // T to make this a required field
        cancelHandler: React.PropTypes.func // Called to handle cancel button click
    },

    getInitialState: function() {
        return {value: this.props.value};
    },

    // Get the text the user entered from the text-type field. Meant to be called from
    // parent components.
    getValue: function() {
        if (this.props.type === 'text' || this.props.type === 'email' || this.props.type === 'textarea') {
            return React.findDOMNode(this.refs.input).value;
        } else if (this.props.type === 'select') {
            return this.getSelectedOption();
        }
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
            return selectedOptionNode.getAttribute('value') || selectedOptionNode.innerHTML;
        }

        // Nothing selected
        return '';
    },

    // Called when any input's value changes from user input
    handleChange: function(e) {
        this.setState({value: e.target.value});
        if (this.props.clearError) {
            this.props.clearError();
        }
    },

    render: function() {
        var input, inputClasses;
        var groupClassName = 'form-group' + this.props.groupClassName ? ' ' + this.props.groupClassName : '';

        switch (this.props.type) {
            case 'text':
            case 'email':
                inputClasses = 'form-control' + (this.props.error ? ' error' : '') + (this.props.inputClassName ? ' ' + this.props.inputClassName : '');
                var innerInput = (
                    <span>
                        <input className={inputClasses} type={this.props.type} id={this.props.id} name={this.props.id} placeholder={this.props.placeholder} ref="input" value={this.state.value} onChange={this.handleChange} />
                        <div className="form-error">{this.props.error ? <span>{this.props.error}</span> : <span>&nbsp;</span>}</div>
                    </span>
                );
                input = (
                    <div className={this.props.groupClassName}>
                        {this.props.label ? <label htmlFor={this.props.id} className={this.props.labelClassName}><span>{this.props.label}{this.props.required ? ' *' : ''}</span></label> : null}
                        {this.props.wrapperClassName ? <div className={this.props.wrapperClassName}>{innerInput}</div> : <span>{innerInput}</span>}
                    </div>
                );
                break;

            case 'select':
                input = (
                    <div className={this.props.groupClassName}>
                        {this.props.label ? <label htmlFor={this.props.id} className={this.props.labelClassName}><span>{this.props.label}{this.props.required ? ' *' : ''}</span></label> : null}
                        <div className={this.props.wrapperClassName}>
                            <select className="form-control" ref="input" onChange={this.props.clearError} defaultValue={this.props.value ? this.props.value : this.props.defaultValue}>
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
                            <textarea className={inputClasses} id={this.props.id} name={this.props.id} ref="input" defaultValue={this.props.value} placeholder={this.props.placeholder} onChange={this.props.clearError} rows={this.props.rows} />
                            <div className="form-error">{this.props.error ? <span>{this.props.error}</span> : <span>&nbsp;</span>}</div>
                        </div>
                    </div>
                );
                break;

            case 'text-range':
                input = (
                    <div className={this.props.groupClassName}>
                        {this.props.label ? <label className={this.props.labelClassName}><span>{this.props.label}{this.props.required ? ' *' : ''}</span></label> : null}
                        <div className={this.props.wrapperClassName}>
                            {this.props.children}
                        </div>
                    </div>
                );
                break;

            case 'submit':
                var title = this.props.title ? this.props.title : 'Submit';
                inputClasses = 'btn' + (this.props.inputClassName ? ' ' + this.props.inputClassName : '');
                input = (
                    <input className={inputClasses} type={this.props.type} value={title} onClick={this.props.submitHandler} />
                );
                break;

            case 'cancel':
                title = this.props.title ? this.props.title : 'Cancel';
                inputClasses = 'btn' + (this.props.inputClassName ? ' ' + this.props.inputClassName : '');
                input = (
                    <button className={inputClasses} onClick={this.props.cancelHandler}>{title}</button>
                );
                break;

            default:
                break;
        }

        return <span>{input}</span>;
    }
});
