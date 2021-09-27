import PropTypes from 'prop-types';
import { DefaultDateSelectorFacet } from './defaults';
import FacetRegistry from './registry';


/**
 * Handles the facet to control submission and release dates.
 */
const DateReleasedFacet = ({ facet, results, mode, relevantFilters, pathname, isExpanded, handleExpanderClick, handleKeyDown, isExpandable, queryString }) => (
    <DefaultDateSelectorFacet
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
    /** True if facet is to be expanded */
    isExpanded: PropTypes.bool,
    /** Expand or collapse facet */
    handleExpanderClick: PropTypes.func,
    /** Handles key-press and toggling facet */
    handleKeyDown: PropTypes.func,
    /** True if expandable, false otherwise */
    isExpandable: PropTypes.bool,
    /** Query-string portion of current URL without initial ? */
    queryString: PropTypes.string,
};

DateReleasedFacet.defaultProps = {
    mode: '',
    isExpanded: false,
    handleExpanderClick: () => {},
    handleKeyDown: () => {},
    isExpandable: true,
    queryString: '',
};


FacetRegistry.Facet.register('date_released', DateReleasedFacet);
FacetRegistry.Facet.register('date_submitted', DateReleasedFacet);
