import { useEffect } from 'react';
import PropTypes from 'prop-types';
import {
    Title,
    Item,
} from './links';


/**
* Components for rendering results. Results are grouped in sections.
* A Section has a Title that displays the type (e.g. Experiment, File)
* and number of results with that type, as well as the top Items
* in that Section.
*/


/**
* @param {object} result - The result object containing key and count properties.
* @return {string} The generated result title.
*/
export const makeTitle = (result) => `${result.key} (${result.count})`;


export const makeLink = (result, input) => {
    return result.href || `/search/?type=${result.key}&searchTerm=${input}`;
};


// Items are mapped to an Item component.
export const Items = ({ items }) => (
    <ul>
        {
            items.map(
                (item) => (
                    <Item
                        key={item['@id']}
                        item={item}
                        href={item['@id']}
                    />
                )
            )
        }
    </ul>
);


Items.propTypes = {
    items: PropTypes.array.isRequired,
};


export const Section = ({ title, href, items }) => (
    <>
        <Title value={title} href={href} />
        <Items
            items={items}
        />
    </>
);


Section.propTypes = {
    title: PropTypes.string.isRequired,
    href: PropTypes.string.isRequired,
    items: PropTypes.array.isRequired,
};


/**
* Results are mapped to sections. We add an event listener
* to detect when the user clicks away from the dropdown list
* so we can close it.
*/
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
        <div className="top-hits-search__results">
            {
                results.map(
                    (result) => (
                        <Section
                            key={result.key}
                            title={makeTitle(result)}
                            href={makeLink(result, input)}
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


export const CollectionSection = ({ items }) => (
    <>
        <Items
            items={items}
        />
    </>
);


Section.propTypes = {
    items: PropTypes.array.isRequired,
};


export const CollectionResults = ({ input, results, handleClickAway }) => {
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
        <div className="top-hits-search__results">
            {
                results.map(
                    (result) => (
                        <CollectionSection
                            key={result.key}
                            items={result.hits}
                        />
                    )
                )
            }
        </div>
    );
};


CollectionResults.propTypes = {
    input: PropTypes.string.isRequired,
    results: PropTypes.array.isRequired,
    handleClickAway: PropTypes.func.isRequired,
};
