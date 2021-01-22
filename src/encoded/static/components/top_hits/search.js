import * as globals from '../globals';
import React, {useState} from 'react';
import PropTypes from 'prop-types';
import debounce from './debounce';
import Form from './form';
import Query from './query';


const Search = (props) => {
    const [input, setInput] = useState('');
    const [results, setResults] = useState([]);
    const [displayResults, setDisplayResults] = useState(true);
    const [debounceTimer, setDebounceTimer] = useState(null);
    const debounceTime = 200;

    const makeSearchAndSetResults = (searchTerm) => {
        const topHitsQuery = new Query(searchTerm);
        topHitsQuery.getResults().then(
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
        const value = e.target.value;
        setInput(value);
        debouncedMakeSearchAndSetResults(e.target.value);
    };

    return (
        <Form
          input={input}
          handleInputChange={handleInputChange}
          results={results}
        />
    );
};


Search.contextTypes = {
    fetch: PropTypes.func
};


globals.contentViews.register(Search, 'TopHitsSearch');
