import React from 'react';
import PropTypes from 'prop-types';


/**
* Controlled input box that accepts user's query
* and triggers onChange callback.
*/
const Input = React.forwardRef((props, ref) => (
    <input
        id="gene"
        autoComplete="off"
        aria-label="search for gene name"
        placeholder="Enter gene name here"
        value={props.input}
        onChange={props.onChange}
        ref={ref}
    />
));


Input.propTypes = {
    input: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
};


export default Input;
