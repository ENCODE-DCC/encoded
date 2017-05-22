const React = require('react');
import PropTypes from 'prop-types';
import createReactClass from 'create-react-class';
const form = require('../form');
const globals = require('../globals');
const item = require('../item');

const FallbackBlockView = createReactClass({
    propTypes: {
        blocktype: PropTypes.object,
        value: PropTypes.any,
    },

    render() {
        const Panel = item.Panel;
        return (
            <div>
            <h2>{this.props.blocktype.label}</h2>
                <Panel context={this.props.value} />
            </div>
        );
    },
});

const JSONInput = createReactClass({

    propTypes: {
        value: PropTypes.any,
        onChange: PropTypes.func,
    },

    getInitialState() {
        return { value: JSON.stringify(this.props.value, null, 4), error: false };
    },

    handleChange(event) {
        let value = event.target.value;
        this.setState({ value: value });
        let error = false;
        try {
            value = JSON.parse(value);
        } catch (e) {
            error = true;
        }
        this.setState({ error });
        if (!error) {
            this.props.onChange(value);
        }
    },

    render() {
        return (
            <div className={`rf-Field${this.state.error ? ' rf-Field--invalid' : ''}`}>
                <textarea rows="10" value={this.state.value} onChange={this.handleChange} />
            </div>
        );
    },
});

const fallbackSchema = {
    type: 'object',
    formInput: <JSONInput />,
};

module.exports.FallbackBlockEdit = createReactClass({
    propTypes: {
        schema: PropTypes.object,
        value: PropTypes.any,
        onChange: PropTypes.func,
    },

    update(name, value) {
        this.props.onChange(value);
    },

    render() {
        const { schema, value } = this.props;
        return (<form.Field
            schema={schema || fallbackSchema} value={value} updateChild={this.update}
        />);
    },
});

// Use this as a fallback for any block we haven't registered
globals.blocks.fallback = function (obj) {
    return {
        label: obj['@type'].join(','),
        schema: fallbackSchema,
        view: FallbackBlockView,
    };
};
