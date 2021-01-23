import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import {
    Title,
    Item,
} from './links';


const makeTitle = result => `${result.key} (${result.count})`;


export const Items = ({ items }) => (
    <ul>
        {
            items.map(
                item => (
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


const Results = ({ input, results, handleClickAway }) => {
    const resultsRef = useRef(null);

    useEffect(
        () => {
            const handleClickOutside = (e) => {
                if (resultsRef.current && !resultsRef.current.contains(e.target)) {
                    handleClickAway();
                }
            };
            document.addEventListener('click', handleClickOutside, true);
            return () => {
                document.removeEventListener('click', handleClickOutside, true);
            };
        },
        [handleClickAway]
    );

    return (
        <div className="top-hits-search__suggested-results" ref={resultsRef}>
            {
                results.map(
                    result => (
                        <Section
                            key={result.key}
                            title={makeTitle(result)}
                            href={`/search/?type=${result.key}&searchTerm=${input}`}
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
