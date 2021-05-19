import { useEffect } from 'react';
import PropTypes from 'prop-types';
import {
    Title,
    Item,
} from '../links';
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


const Results = ({ input, results, handleClickAway }) => {
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
    input: PropTypes.string.isRequired,
    results: PropTypes.array.isRequired,
    handleClickAway: PropTypes.func.isRequired,
};


export default Results;
