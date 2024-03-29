import { useEffect } from 'react';
import PropTypes from 'prop-types';
import {
    Items,
} from '../results';


export const Section = ({ items }) => (
    <>
        <Items
            items={items}
        />
    </>
);


Section.propTypes = {
    items: PropTypes.array.isRequired,
};


/**
* Results are mapped to sections. We add an event listener
* to detect when the user clicks away from the dropdown list
* so we can close it.
*/
const Results = ({ results, handleClickAway }) => {
    useEffect(
        () => {
            document.addEventListener('click', handleClickAway, true);
            return () => {
                document.removeEventListener('click', handleClickAway, true);
            };
        },
        [handleClickAway]
    );
    return (
        <div className="multisearch__results">
            {
                results.map(
                    (result) => (
                        <Section
                            key={result.key}
                            items={result.hits}
                        />
                    )
                )
            }
        </div>
    );
};


Results.propTypes = {
    results: PropTypes.array.isRequired,
    handleClickAway: PropTypes.func.isRequired,
};


export default Results;
