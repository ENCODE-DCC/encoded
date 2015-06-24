"use strict";
var React = require('react');


var Input = module.exports.Input = React.createClass({
    propTypes: {
        type: React.PropTypes.string.isRequired, // Type of input
        id: React.PropTypes.string.isRequired, // Unique ID of input
        ref: React.PropTypes.string, // To access this input from JS
        label: React.PropTypes.string, // Label for input
        value: React.PropTypes.string // Value to pre-fill input with
    },

    render: function() {
        var input;

        switch (this.props.type) {
            case "text":
                input = (
                    <div className="form-group">
                        {this.props.label ? <label for={this.props.id}>{this.props.label}</label> : null}
                        <input className="form-control" type={this.props.type} id={this.props.id} ref={this.props.ref} value={this.props.value} />
                    </div>
                );
                break;
            default:
                break;
        }

        return <div>{input}</div>;
    }
});
