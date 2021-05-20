import { cloneElement, useState } from 'react';
import PropTypes from 'prop-types';
import debounce from '../debounce';
import NavBarForm from './form';
import QUERIES from './constants';


const Search = ({ children }) => {
    const [input, setInput] = useState('');
    const [results, setResults] = useState({});
    const [debounceTimer, setDebounceTimer] = useState(null);
    const debounceTime = 200;

    const makeSearchAndSetResults = (searchTerm) => {
        const queries = QUERIES.map(
            ([name, Query]) => {
                const query = new Query(searchTerm);
                return query.getResults().then(
                    (result) => ({ [name]: result })
                );
            }
        );
        Promise.all(queries).then(
            (queryResults) => Object.assign({}, ...queryResults)
        ).then(
            (queryResults) => setResults(queryResults)
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


Search.contextTypes = {
    fetch: PropTypes.func,
};


Search.propTypes = {
    children: PropTypes.element.isRequired,
};


const NavBarMultiSearch = () => (
    <li className="navbar__item navbar__item--search">
        <Search>
            <NavBarForm />
        </Search>
    </li>
);


export default NavBarMultiSearch;
