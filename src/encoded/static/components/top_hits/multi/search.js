import { cloneElement, useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import debounce from '../debounce';
import NavBarForm from './form';
import QUERIES from './constants';


/**
* MultiSearch version of search-as-you-type dropdown. The list of
* queries defined in constants is used to get results from different
* endpoints (e.g. top hits endpoint, data collections endpoint). The
* results from a specific endpoint are rendered in sections in the
* dropdown using the associated custom results component.
*/
const Search = ({ children }) => {
    // User input.
    const [input, setInput] = useState('');
    // Reference to latest input for use in callback.
    const inputRef = useRef();
    // Update reference with latest input value.
    useEffect(() => {
        inputRef.current = input;
    }, [input]);
    // All results are stored by endpoint key in same object.
    const [results, setResults] = useState({});
    // Store the debounce timer so we can reset it
    // after every keystroke.
    const [debounceTimer, setDebounceTimer] = useState(null);
    // Wait this long after last user input making queries.
    const debounceTime = 200;

    // Compare searchTerm from query with latest user input.
    const queryResultsAreFromLatestSearchTerm = (searchTerm) => (
        searchTerm === inputRef.current
    );

    // Only set results from the latest query.
    const maybeSetResults = (queryResults, searchTerm) => {
        if (queryResultsAreFromLatestSearchTerm(searchTerm)) {
            setResults(queryResults);
        }
    };

    // Iterate over all the Query objects and get the results from each.
    // Wait for all results to return, collapse into single object, then
    // update component state.
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
            (queryResults) => maybeSetResults(queryResults, searchTerm)
        );
    };

    // Avoid querying endpoints until user stops typing.
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

    // Pass down to input component as callback to
    // update input and get query results as user types.
    const handleInputChange = (e) => {
        const { value } = e.target;
        setInput(value);
        debouncedMakeSearchAndSetResults(value);
    };

    // Pass down to dropdown component as callback to
    // clear the results when user clicks somewhere else
    // on screen.
    const handleClickAway = () => {
        setResults({});
    };

    // This passes down props to custom Form.
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
