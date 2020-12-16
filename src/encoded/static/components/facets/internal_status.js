import React from 'react';
import PropTypes from 'prop-types';
import { DefaultFacet } from './defaults';
import FacetRegistry from './registry';


/**
 * The Internal Status facet only displays with an admin login. Its display gets supressed with the
 * null output from this component otherwise.
 */
const InternalStatusFacet = ({ facet, results, mode, relevantFilters, pathname, queryString, isExpanded, handleExpanderClick, handleKeyDown }, reactContext) => (
    <React.Fragment>
        {reactContext.session_properties && reactContext.session_properties.admin ?
            <DefaultFacet
                facet={facet}
                results={results}
                mode={mode}
                relevantFilters={relevantFilters}
                pathname={pathname}
                queryString={queryString}
                isExpanded={isExpanded}
                handleExpanderClick={handleExpanderClick}
                handleKeyDown={handleKeyDown}
            />
        : null}
    </React.Fragment>
);

InternalStatusFacet.propTypes = {
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
    /** True if facet is expanded */
    isExpanded: PropTypes.bool,
    /** Expand or collapse facet */
    handleExpanderClick: PropTypes.func,
    /** Handles key-press and toggling facet */
    handleKeyDown: PropTypes.func,
};

InternalStatusFacet.defaultProps = {
    mode: '',
    queryString: '',
    isExpanded: false,
    handleExpanderClick: () => {},
    handleKeyDown: () => {},
};

InternalStatusFacet.contextTypes = {
    session_properties: PropTypes.object,
};

FacetRegistry.Facet.register('internal_status', InternalStatusFacet);
