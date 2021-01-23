import React from 'react';
import PropTypes from 'prop-types';
import Input from './input';
import Results from './results';


const Form = props => (
    <div className="top-hits-search__input">
        <div className="top-hits-search__input-field">
            <form action="/search/">
                <Input input={props.input} onChange={props.handleInputChange} />
            </form>
            {!!props.results.length && <Results input={props.input} results={props.results} />}
        </div>
    </div>
);

Form.propTypes = {
    input: PropTypes.string.isRequired,
    handleInputChange: PropTypes.func.isRequired,
    results: PropTypes.array.isRequired,
};


export default Form;
