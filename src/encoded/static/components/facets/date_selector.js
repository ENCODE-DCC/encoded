import React from 'react';
import PropTypes from 'prop-types';
import { DefaultDateSelectorFacet } from './defaults';
import FacetRegistry from './registry';


/**
 * Handles the facet to control submission and release dates.
 */
const DateReleasedFacet = ({ facet, results, mode, relevantFilters, pathname, queryString }) => (
    <DefaultDateSelectorFacet
        facet={facet}
        results={results}
        mode={mode}
        relevantFilters={relevantFilters}
        pathname={pathname}
        queryString={queryString}
    />
);

DateReleasedFacet.propTypes = {
    /** Relevant `facet` object from `facets` array in `results` */
    facet: PropTypes.object.isRequired,
    /** Complete search-results object */
    results: PropTypes.object.isRequired,
    /** Facet display mode */
    mode: PropTypes.string,
    /** Filters relevant to the current facet */
    relevantFilters: PropTypes.array.isRequired,
    /** Search results path without query-string portion */
    pathname: PropTypes.string.isRequired,
    /** Query-string portion of current URL without initial ? */
    queryString: PropTypes.string,
};

DateReleasedFacet.defaultProps = {
    mode: '',
    queryString: '',
};


FacetRegistry.Facet.register('date_released', DateReleasedFacet);
FacetRegistry.Facet.register('date_submitted', DateReleasedFacet);
