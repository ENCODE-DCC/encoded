import PropTypes from 'prop-types';
import { DefaultExistsFacet, DefaultExistsBinaryFacet } from './defaults';
import FacetRegistry from './registry';


/**
 * Facet renderer for "exists" facets.
 */
const ExistsFacet = ({ facet, results, mode, relevantFilters, pathname, queryString }) => (
    <DefaultExistsFacet
        facet={facet}
        results={results}
        mode={mode}
        relevantFilters={relevantFilters}
        pathname={pathname}
        queryString={queryString}
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
};

ExistsFacet.defaultProps = {
    mode: '',
    queryString: '',
};

FacetRegistry.Facet.register('datasets', ExistsFacet);
FacetRegistry.Facet.register('publication_data', ExistsFacet);
FacetRegistry.Facet.register('nih_institutional_certification', ExistsFacet);

/**
 * Facet renderer for "exists" facets.
*/
const ExistsBooleanFacet = ({ facet, results, mode, relevantFilters, pathname, queryString }) => (
    <DefaultExistsBinaryFacet
        facet={facet}
        results={results}
        mode={mode}
        relevantFilters={relevantFilters}
        pathname={pathname}
        queryString={queryString}
        defaultValue="yes"
    />
);

ExistsBooleanFacet.propTypes = {
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

ExistsBooleanFacet.defaultProps = {
    mode: '',
    queryString: '',
};

FacetRegistry.Facet.register('control_type', ExistsBooleanFacet);
