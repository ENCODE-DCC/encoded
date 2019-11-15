import React from 'react';
import PropTypes from 'prop-types';
import { DefaultExistsFacet } from './defaults';
import FacetRegistry from './registry';


/**
 * The nih_institutional_certification facet field renders an "exists" facet.
 */
const NihInstitutionalCertificationFacet = ({ facet, results, mode, relevantFilters, pathname, queryString }) => (
    <DefaultExistsFacet
        facet={facet}
        results={results}
        mode={mode}
        relevantFilters={relevantFilters}
        pathname={pathname}
        queryString={queryString}
    />
);

NihInstitutionalCertificationFacet.propTypes = {
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

NihInstitutionalCertificationFacet.defaultProps = {
    mode: '',
    queryString: '',
};

FacetRegistry.Facet.register('nih_institutional_certification', NihInstitutionalCertificationFacet);
