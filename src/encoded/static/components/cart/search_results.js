import React from 'react';
import PropTypes from 'prop-types';
import { hasType } from '../globals';
import { Listing } from '../search';
import * as constants from './constants';
import CartViewContext from './context';
import SeriesManagerActuator from './series';


/**
 * List of search results for the cart series and dataset views.
 */
export const CartResultTableList = ({ results, cartControls }) => {
    const { allSeriesInCart } = React.useContext(CartViewContext);
    return (
        <ul className="result-table" id="result-table">
            {results.length > 0 ?
                results.map((result) => {
                    // Determine if a dataset should have no cart controls even with `cartControls`
                    // true.
                    let seriesOfDataset;
                    const isSeries = hasType(result, 'Series');
                    const isSeriesDataset = result._relatedSeries;
                    if (isSeries) {
                        // Search result is a series object. Display its series manager actuator.
                        seriesOfDataset = [result];
                    } else if (isSeriesDataset) {
                        // Search result it a related dataset to a series. Find each of the related
                        // series that exist in the cart to display their series manager actuators.
                        seriesOfDataset = result._relatedSeries.map((seriesPath) => (
                            allSeriesInCart.find((seriesInCart) => seriesPath === seriesInCart['@id'])
                        )).filter((series) => series);
                    }

                    return (
                        <li key={result['@id']} className="result-item__wrapper">
                            {Listing({ context: result, cartControls: !(isSeries || isSeriesDataset) && cartControls, mode: 'cart-view' })}
                            {(isSeries || isSeriesDataset) && (
                                <>
                                    {seriesOfDataset.map((singleSeriesOfDataset) => (
                                        <SeriesManagerActuator key={singleSeriesOfDataset['@id']} singleSeries={singleSeriesOfDataset} />
                                    ))}
                                </>
                            )}
                        </li>
                    );
                })
            : null}
        </ul>
    );
};

CartResultTableList.propTypes = {
    /** Array of search results to display */
    results: PropTypes.array.isRequired,
    /** True if items should display with cart controls */
    cartControls: PropTypes.bool,
};

CartResultTableList.defaultProps = {
    cartControls: false,
};


/**
 * Display a page of cart contents within the cart display.
 */
export const CartSearchResults = ({ elements, currentPage, cartControls, loading }) => {
    if (elements.length > 0) {
        const pageStartIndex = currentPage * constants.PAGE_ELEMENT_COUNT;
        const currentPageElements = elements.slice(pageStartIndex, pageStartIndex + constants.PAGE_ELEMENT_COUNT);
        return (
            <div className="cart-search-results">
                <CartResultTableList results={currentPageElements} cartControls={cartControls} />
            </div>
        );
    }

    // No elements and the page isn't currently loading, so indicate no datasets to view.
    if (!loading) {
        return <div className="nav result-table cart__empty-message">No visible datasets on this page.</div>;
    }

    // Page is currently loading, so don't display anything for now.
    return <div className="nav result-table cart__empty-message">Page currently loading&hellip;</div>;
};

CartSearchResults.propTypes = {
    /** Array of cart items */
    elements: PropTypes.array,
    /** Page of results to display */
    currentPage: PropTypes.number,
    /** True if displaying an active cart */
    cartControls: PropTypes.bool,
    /** True if cart currently loading on page */
    loading: PropTypes.bool.isRequired,
};

CartSearchResults.defaultProps = {
    elements: [],
    currentPage: 0,
    cartControls: false,
};
