import PropTypes from 'prop-types';
import { geneFactory } from './gene';


export const HighlightedText = (props) => (
    <span className="matching-text">
        {props.value}
    </span>
);


HighlightedText.propTypes = { value: PropTypes.string.isRequired };


export const NormalText = (props) => (
    <>
        {props.value}
    </>
);


NormalText.propTypes = { value: PropTypes.string.isRequired };


/**
* This maps a string partitioned by whether or not it matches
* a user's searchTerm to display components.
*/
export const matchingOrNotToComponent = {
    match: HighlightedText,
    mismatch: NormalText,
};


/**
* This creates a gene object from a gene search result and maps a display
* value to components that highlight the value or not depending on if it
* matches the user's searchTerm. The gene object is passed to the caller to
* use when the component is clicked.
*/
export const Result = ({ item, searchTerm, handleClick }) => {
    const gene = geneFactory(item, searchTerm);
    return (
        <li>
            <button
                type="button"
                tabIndex="0"
                onClick={() => handleClick(gene)}
            >
                {
                    gene.asMatchingOrNot().map(
                        ([key, value], i) => {
                            const Component = matchingOrNotToComponent[key];
                            // Trying to make unique key here since it's possible to have
                            // duplicate values, e.g. all of the matching tokens.
                            return <Component key={`${value}-${searchTerm}-${i}`} value={value} />;
                        }
                    )
                }
            </button>
        </li>
    );
};


Result.propTypes = {
    item: PropTypes.object.isRequired,
    searchTerm: PropTypes.string.isRequired,
    handleClick: PropTypes.func.isRequired,
};


export const shouldShowSearchResults = (searchTerm, results) => (
    searchTerm &&
    searchTerm.length > 0 &&
    results &&
    results.length > 0
);


/**
* Pulls gene search results from sibling Param (rawResults) and
* parent FetchedData component and maps to a Result.
*/
const Results = ({ searchTerm, rawResults, handleClick }) => {
    const results = rawResults['@graph'] || [];
    return (
        shouldShowSearchResults(searchTerm, results) ?
            (
                <ul className="adv-search-autocomplete">
                    {
                        results.map(
                            (item) => (
                                <Result
                                    key={item['@id']}
                                    searchTerm={searchTerm}
                                    item={item}
                                    handleClick={handleClick}
                                />
                            )
                        )
                    }
                </ul>
            ) :
            null
    );
};


Results.propTypes = {
    searchTerm: PropTypes.string,
    rawResults: PropTypes.object,
    handleClick: PropTypes.func.isRequired,
};


Results.defaultProps = {
    rawResults: {}, // Looks required, but because it's built from <Param>, it can fail type checks.
    searchTerm: '',
};


export default Results;
