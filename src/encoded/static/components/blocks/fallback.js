'use strict';
var React = require('react');
var form = require('../form');
var globals = require('../globals');
var item = require('../item');

var FallbackBlockView = React.createClass({
    render: function() {
        var Panel = item.Panel;
        return (
            <div>
            <h2>{this.props.blocktype.label}</h2>
                <Panel context={this.props.value} />
            </div>
        );
    }
});

var JSONInput = React.createClass({

    getInitialState: function() {
        return { value: JSON.stringify(this.props.value, null, 4), error: false };
    },

    render: function() {
        return <div className={"rf-Field" + (this.state.error ? " rf-Field--invalid" : '')}>
            <textarea rows="10" value={this.state.value} onChange={this.handleChange} />
        </div>;
    },

    handleChange: function(e) {
        var value = e.target.value;
        this.setState({ value: value });
        var error = false;
        try {
            value = JSON.parse(value);
        } catch (e) {
            error = true;
        }
        this.setState({ error });
        if (!error) {
            this.props.onChange(value);
        }
    }
});

var fallbackSchema = {
    type: 'object',
    formInput: <JSONInput />
}

var FallbackBlockEdit = module.exports.FallbackBlockEdit = React.createClass({
    render: function() {
        var {schema, value, ...props} = this.props;
        return <form.Field
            schema={schema || fallbackSchema} value={value} updateChild={this.update} />;
    },

    update: function(name, value) {
        this.props.onChange(value);
    }
});

// Use this as a fallback for any block we haven't registered
globals.blocks.fallback = function (obj) {
    return {
        label: obj['@type'].join(','),
        schema: fallbackSchema,
        view: FallbackBlockView
    };
};
