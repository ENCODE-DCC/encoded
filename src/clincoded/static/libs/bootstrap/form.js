"use strict";
var React = require('react');


var Input = module.exports.Input = React.createClass({
    propTypes: {
        type: React.PropTypes.string.isRequired, // Type of input
        id: React.PropTypes.string.isRequired, // Unique ID of input
        ref: React.PropTypes.string, // To access this input from JS
        label: React.PropTypes.oneOfType([
            React.PropTypes.string,
            React.PropTypes.object
        ]), // <label> for input; string or another React component
        labelClassName: React.PropTypes.string, // CSS classes to add to labels
        groupClassName: React.PropTypes.string, // CSS classes to add to control groups (label/input wrapper div)
        wrapperClassName: React.PropTypes.string, // CSS classes to add to wrapper div around inputs
        value: React.PropTypes.string // Value to pre-fill input with
    },

    render: function() {
        var input;
        var groupClassName = 'form-group' + this.props.groupClassName ? ' ' + this.props.groupClassName : '';

        switch (this.props.type) {
            case 'text':
            case 'email':
                input = (
                    <div className={this.props.groupClassName}>
                        {this.props.label ? <label htmlFor={this.props.id} className={this.props.labelClassName}>{this.props.label}</label> : null}
                        <div className={this.props.wrapperClassName}>
                            <input className="form-control" type={this.props.type} id={this.props.id} ref={this.props.ref} value={this.props.value} />
                        </div>
                    </div>
                );
                break;

            case 'select':
                input = (
                    <div className={this.props.groupClassName}>
                        {this.props.label ? <label htmlFor={this.props.id} className={this.props.labelClassName}>{this.props.label}</label> : null}
                        <div className={this.props.wrapperClassName}>
                            <select className="form-control">
                                {this.props.children}
                            </select>
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
