import React from 'react';
import PropTypes from 'prop-types';
import { DefaultFacet } from './defaults';
import FacetRegistry from './registry';


/**
 * The type facet renders like the default facet, but often gets hidden unless conditions allow for
 * its display.
 */
const TypeFacet = ({ facet, results, mode, relevantFilters, pathname, queryString, expandedFacets, setExpandFacets }) => {
    // Get "normal" facets, meaning non-audit facets.
    const nonAuditFacets = results.facets.filter(resultFacets => resultFacets.field.substring(0, 6) !== 'audit.');

    // Determine whether the type facet should be hidden or not.
    let hideTypes;
    if (mode === 'picker') {
        // The edit forms item picker (search results in an edit item) shows the Types facet.
        hideTypes = false;
    } else {
        // Hide the types facet if one "type=" term exists in the URL. and it's not the only
        // facet.
        hideTypes = results.filters.filter(filter => filter.field === 'type').length === 1 && nonAuditFacets.length > 1;
    }

    if (!hideTypes) {
        return (
            <DefaultFacet
                facet={facet}
                results={results}
                mode={mode}
                relevantFilters={relevantFilters}
                pathname={pathname}
                queryString={queryString}
                allowNegation={false}
                expandedFacets={expandedFacets}
                setExpandFacets={setExpandFacets}
            />
        );
    }

    // For the common case where the type facet should be hidden.
    return null;
};

TypeFacet.propTypes = {
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

TypeFacet.defaultProps = {
    mode: '',
    queryString: '',
    expandedFacets: new Set([]),
    setExpandFacets: () => {},
};

FacetRegistry.Facet.register('type', TypeFacet);
