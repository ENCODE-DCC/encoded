import React from 'react';
import PropTypes from 'prop-types';


const Input = props => (
    <input
        type="text"
        autoComplete="off"
        name="searchTerm"
        placeholder="Search for top hits by type"
        value={props.input}
        onChange={props.onChange}
    />
);


Input.propTypes = {
    input: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
};


export default Input;
