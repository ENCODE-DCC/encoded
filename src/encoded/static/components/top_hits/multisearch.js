import { cloneElement, useState } from 'react';
import PropTypes from 'prop-types';
import debounce from './debounce';
import {
    MultiResultsNavBarForm,
} from './multiform';
import {
    queries
} from './constants';


const MultiSearch = ({ children }) => {
    const [input, setInput] = useState('');
    const [results, setResults] = useState({});
    const [debounceTimer, setDebounceTimer] = useState(null);
    const debounceTime = 200;

    const makeSearchAndSetResults = (searchTerm) => {
        const results = queries.map(
            ([name, Query]) => {
                const query = new Query(searchTerm);
                return query.getResults().then(
                    (result) => ({[name]: result})
                );
            }
        );
        Promise.all(results).then(
            (results) => Object.assign({}, ...results)
        ).then(
            (results) => setResults(results)
        );
    };

    const debouncedMakeSearchAndSetResults = (searchTerm) => {
        setDebounceTimer(
            debounce(
                () => {
                    makeSearchAndSetResults(searchTerm);
                },
                debounceTime,
                debounceTimer
            )
        );
    };

    const handleInputChange = (e) => {
        const { value } = e.target;
        setInput(value);
        debouncedMakeSearchAndSetResults(value);
    };

    const handleClickAway = () => {
        setResults({});
    };

    return (
        <>
            {
                cloneElement(
                    children,
                    {
                        input,
                        handleInputChange,
                        handleClickAway,
                        results,
                    }
                )
            }
        </>
    );
};


MultiSearch.contextTypes = {
    fetch: PropTypes.func,
};


MultiSearch.propTypes = {
    children: PropTypes.element.isRequired,
};


export const NavBarMultiSearch = () => (
    <li className="navbar__item navbar__item--search">
        <MultiSearch>
            <MultiResultsNavBarForm />
        </MultiSearch>
    </li>
);

