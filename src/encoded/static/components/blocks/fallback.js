import React from 'react';
import PropTypes from 'prop-types';
import { Field } from '../form';
import * as globals from '../globals';
import { Panel } from '../item';


const FallbackBlockView = (props) => (
    <div>
        <h2>{props.blocktype.label}</h2>
        <Panel context={props.value} />
    </div>
);

FallbackBlockView.propTypes = {
    blocktype: PropTypes.object.isRequired,
    value: PropTypes.any,
};

FallbackBlockView.defaultProps = {
    value: null,
};


class JSONInput extends React.Component {
    constructor(props) {
        super(props);

        // Set initial React component state.
        this.state = {
            value: JSON.stringify(this.props.value, null, 4),
            error: false,
        };

        // Bind this to non-React components.
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(event) {
        let value = event.target.value;
        this.setState({ value });
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
    }

    render() {
        return (
            <div className={`rf-Field${this.state.error ? ' rf-Field--invalid' : ''}`}>
                <textarea rows="10" value={this.state.value} onChange={this.handleChange} />
            </div>
        );
    }
}

JSONInput.propTypes = {
    value: PropTypes.any,
    onChange: PropTypes.func,
};

JSONInput.defaultProps = {
    value: null,
    onChange: null,
};


const fallbackSchema = {
    type: 'object',
    formInput: <JSONInput />,
};


export default class FallbackBlockEdit extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.update = this.update.bind(this);
    }

    update(name, value) {
        this.props.onChange(value);
    }

    render() {
        const { schema, value } = this.props;
        return (<Field
            schema={schema || fallbackSchema} value={value} updateChild={this.update}
        />);
    }
}

FallbackBlockEdit.propTypes = {
    schema: PropTypes.object,
    value: PropTypes.any,
    onChange: PropTypes.func.isRequired,
};

FallbackBlockEdit.defaultProps = {
    schema: null,
    value: null,
};

// Use this as a fallback for any block we haven't registered
globals.blocks.fallback = function fallback(obj) {
    return {
        label: obj['@type'].join(','),
        schema: fallbackSchema,
        view: FallbackBlockView,
    };
};
