"use strict";
var React = require('react');
var _ = require('underscore');


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
        value: React.PropTypes.string // Value to pre-fill input with
    },

    getValue: function() {
        return React.findDOMNode(this.refs.input).value;
    },

    getSelectedOption: function() {
        var optionNodes = this.refs.input.getDOMNode().getElementsByTagName('option');

        var selectedOptionNode = _(optionNodes).find(function(option) {
            return option.selected;
        });

        if (selectedOptionNode) {
            return selectedOptionNode.getAttribute('value') || selectedOptionNode.innerHtml;
        }
        return '';
    },

    render: function() {
        var input, inputClasses;
        var groupClassName = 'form-group' + this.props.groupClassName ? ' ' + this.props.groupClassName : '';

        switch (this.props.type) {
            case 'text':
            case 'email':
                inputClasses = 'form-control' + (this.props.error ? ' error' : '');
                input = (
                    <div className={this.props.groupClassName}>
                        {this.props.label ? <label htmlFor={this.props.id} className={this.props.labelClassName}>{this.props.label}</label> : null}
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
                        {this.props.label ? <label htmlFor={this.props.id} className={this.props.labelClassName}>{this.props.label}</label> : null}
                        <div className={this.props.wrapperClassName}>
                            <select className="form-control" ref="input">
                                {this.props.children}
                            </select>
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
