import { useState } from 'react';
import PropTypes from 'prop-types';


/**
* Controlled input box that accepts user's query
* and triggers onChange callback.
*/
export const Input = (props) => {
    const [isSelected, setIsSelected] = useState(false);
    return (
        <input
            type="text"
            className={isSelected ? 'selected' : null}
            autoComplete="off"
            name="searchTerm"
            placeholder="Search..."
            value={props.input}
            onChange={props.onChange}
            onFocus={() => setIsSelected(true)}
            onBlur={() => setIsSelected(props.input.length > 0)}
        />
    );
};


Input.propTypes = {
    input: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
};


/**
* This adds a search icon to input form for use in nav bar.
*/
export const InputWithIcon = (props) => (
    <>
        <Input {...props} />
        <button type="submit" className="search-button">
            <i className="icon icon-search" />
            <span className="sr-only">Search</span>
        </button>
    </>
);


InputWithIcon.propTypes = {
    input: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
};
