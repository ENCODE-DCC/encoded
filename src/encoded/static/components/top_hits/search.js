import { cloneElement, useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import debounce from './debounce';
import {
    NavBarForm,
    PageForm,
} from './form';
import Query from './query';


/**
* Main entrypoint to search-as-you-type component. Debounced user input
* is sent to the top hits API which returns the top matching documents grouped
* by type (e.g. File, Experiment, etc.). Results are rendered in a dropdown
* component that allows the user to go directly to that document when clicked,
* or to be redirected to the search results for all matching documents of a
* specific type. Hitting enter will redirect the user to the normal search
* page with the current input as a query, and clicking anywhere else on the
* page besides the dropdown will hide the results.
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
    // Search results that get rendered.
    const [results, setResults] = useState([]);
    // Store the debounce timer so we can reset it
    // after every keystroke.
    const [debounceTimer, setDebounceTimer] = useState(null);
    // Wait this long after last user input before querying
    // the top hits API.
    const debounceTime = 200;

    // Compare searchTerm from query with latest user input.
    const queryResultsAreFromLatestSearchTerm = (searchTerm) => (
        searchTerm === inputRef.current
    );

    // Only set results from the latest query.
    const maybeSetResults = (topHits, searchTerm) => {
        if (queryResultsAreFromLatestSearchTerm(searchTerm)) {
            setResults(topHits);
        }
    };

    // Pass user input (searchTerm) to top hits API
    // and store the returned results. Avoid setting
    // results if they are from a stale request.
    const makeSearchAndSetResults = (searchTerm) => {
        const topHitsQuery = new Query(searchTerm);
        topHitsQuery.getResults().then(
            (topHits) => maybeSetResults(topHits, searchTerm)
        );
    };

    // Wrap the top hits query in a debounced function to
    // avoid querying the endpoint until user stops typing.
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
    // update input and make debounced top hits query
    // as user types.
    const handleInputChange = (e) => {
        const { value } = e.target;
        setInput(value);
        debouncedMakeSearchAndSetResults(value);
    };

    // Pass down to dropdown component as callback to
    // clear the results when user clicks somewhere else
    // on screen.
    const handleClickAway = () => {
        setResults([]);
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


export const NavBarSearch = () => (
    <li className="navbar__item navbar__item--search">
        <Search>
            <NavBarForm />
        </Search>
    </li>
);


export const PageSearch = () => (
    <Search>
        <PageForm />
    </Search>
);
