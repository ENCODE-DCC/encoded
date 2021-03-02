import {
    useEffect,
    useState,
    useRef,
} from 'react';
import PropTypes from 'prop-types';
import {
    FetchedData,
    Param,
} from '../fetched';
import debounce from '../top_hits/debounce';
import GeneSearchInput from './input';
import GeneSearchResults from './results';
import { GENE_SEARCH_URL } from './constants';


export const makeSearchUrl = (searchTerm, assembly) => (
    `${GENE_SEARCH_URL}` +
    `&searchTerm=${searchTerm}` +
    `&locations.assembly=${assembly}`
);


/**
* Renders input and results for gene lookup.
*/
const Search = (props) => {
    const [input, setInput] = useState('');
    const [showResults, setShowResults] = useState(false);
    const [debouncedInput, setDebouncedInput] = useState('');
    const [debounceTimer, setDebounceTimer] = useState(null);
    const debounceTime = 200;
    const inputBox = useRef(null);

    /**
    * We want to be able to clear the input and results
    * on clicks and different assemblies.
    */
    const clearInputAndHideResults = () => {
        setInput('');
        setDebouncedInput('');
        setShowResults(false);
    };

    /**
    * If the assembly changes from genome browser
    * we should clear input and results.
    */
    useEffect(() => {
        clearInputAndHideResults();
    }, [props.assembly]);

    /**
    * Instead of debouncing the request in the FetchedData/Param
    * components we debounce the searchTerm that is passed to it.
    */
    const handleInputChange = (e) => {
        const { value } = e.target;
        setInput(value);
        setDebounceTimer(
            debounce(
                () => {
                    setDebouncedInput(value);
                },
                debounceTime,
                debounceTimer
            )
        );
        setShowResults(true);
    };

    /**
    * We handle hiding results and focusing on input box here, and let
    * parent take care of scrolling to gene location.
    */
    const handleClick = (gene) => {
        clearInputAndHideResults();
        setInput(gene.asString());
        inputBox.current.focus();
        props.handleClick(gene);
    };

    return (
        <div className="searchform">
            <GeneSearchInput
                ref={inputBox}
                input={input}
                onChange={handleInputChange}
            />
            {
                (showResults && debouncedInput.length > 0) ?
                <FetchedData loadingComplete>
                    <Param
                        name="rawResults"
                        url={makeSearchUrl(debouncedInput, props.assembly)}
                        type="json"
                        allowMultipleRequest
                    />
                    <GeneSearchResults
                        searchTerm={debouncedInput}
                        handleClick={handleClick}
                    />
                </FetchedData>
                : null
            }
        </div>
    );
};


Search.propTypes = {
    assembly: PropTypes.string.isRequired,
    handleClick: PropTypes.func.isRequired,
};


export default Search;
