import React from 'react';
import PropTypes from 'prop-types';
import { DefaultExistsFacet } from './defaults';
import FacetRegistry from './registry';


/**
 * Facet renderer for "exists" facets.
 */
const ExistsFacet = ({ facet, results, mode, relevantFilters, pathname, queryString, expandedFacets, setExpandFacets }) => (
    <DefaultExistsFacet
        facet={facet}
        results={results}
        mode={mode}
        relevantFilters={relevantFilters}
        pathname={pathname}
        queryString={queryString}
        expandedFacets={expandedFacets}
        setExpandFacets={setExpandFacets}
    />
);

ExistsFacet.propTypes = {
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
    /** List of expand facet */
    expandedFacets: PropTypes.instanceOf(Set),
    /** toogles facets */
    setExpandFacets: PropTypes.func,
};

ExistsFacet.defaultProps = {
    mode: '',
    queryString: '',
    expandedFacets: new Set([]),
    setExpandFacets: () => {},
};

FacetRegistry.Facet.register('datasets.accession', ExistsFacet);
FacetRegistry.Facet.register('nih_institutional_certification', ExistsFacet);
