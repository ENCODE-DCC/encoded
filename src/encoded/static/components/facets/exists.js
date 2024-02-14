import PropTypes from 'prop-types';
import { DefaultExistsFacet, DefaultExistsBinaryFacet } from './defaults';
import FacetRegistry from './registry';


/**
 * Facet renderer for "exists" facets.
 */
const ExistsFacet = ({ facet, results, mode, relevantFilters, pathname, queryString, forceDisplay }) => (
    <DefaultExistsFacet
        facet={facet}
        results={results}
        mode={mode}
        relevantFilters={relevantFilters}
        pathname={pathname}
        queryString={queryString}
        forceDisplay={forceDisplay}
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
    /** True to force facet to display in cases it would normally be hidden */
    forceDisplay: PropTypes.bool,
};

ExistsFacet.defaultProps = {
    mode: '',
    queryString: '',
    forceDisplay: false,
};

FacetRegistry.Facet.register('datasets', ExistsFacet);
FacetRegistry.Facet.register('publication_data', ExistsFacet);
FacetRegistry.Facet.register('nih_institutional_certification', ExistsFacet);

/**
 * Facet renderer for "exists" facets.
*/
const ExistsBooleanFacet = ({
    facet,
    results,
    mode,
    relevantFilters,
    pathname,
    isExpanded,
    handleExpanderClick,
    handleKeyDown,
    isExpandable,
    queryString,
    forceDisplay,
}) => (
    <DefaultExistsBinaryFacet
        facet={facet}
        results={results}
        mode={mode}
        relevantFilters={relevantFilters}
        pathname={pathname}
        isExpanded={isExpanded}
        handleExpanderClick={handleExpanderClick}
        handleKeyDown={handleKeyDown}
        isExpandable={isExpandable}
        queryString={queryString}
        forceDisplay={forceDisplay}
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
    /** True if facet is to be expanded */
    isExpanded: PropTypes.bool,
    /** Expand or collapse facet */
    handleExpanderClick: PropTypes.func,
    /** Handles key-press and toggling facet */
    handleKeyDown: PropTypes.func,
    /** True if expandable, false otherwise */
    isExpandable: PropTypes.bool,
    /** True to force facet to display in cases it would normally be hidden */
    forceDisplay: PropTypes.bool,
    /** Query-string portion of current URL without initial ? */
    queryString: PropTypes.string,
};

ExistsBooleanFacet.defaultProps = {
    mode: '',
    isExpanded: false,
    handleExpanderClick: () => {},
    handleKeyDown: () => {},
    isExpandable: true,
    forceDisplay: false,
    queryString: '',
};

FacetRegistry.Facet.register('control_type', ExistsBooleanFacet);
