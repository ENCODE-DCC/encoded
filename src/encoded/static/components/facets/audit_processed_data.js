import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import QueryString from '../../libs/query_string';
import BooleanSwitch from '../../libs/ui/boolean-switch';
import { SpecialFacetRegistry } from './registry';


/**
 * Special facet to display a switch to select between having the search result query string
 * contain: "audit.WARNING.category!=lacking processed data" and without that term at all, with the
 * boolean switch component showing the "on" state with the former and the "off" state with the
 * latter.
 */
const AuditProcessedData = ({ facet, results, mode, pathname, queryString, isExpanded, handleExpanderClick, handleKeyDown, isExpandable }, reactContext) => {
    /** Keeps track of the switch state for `handleSwitch` */
    const switchState = React.useRef(false);

    /**
     * Called when the user clicks the term to flip the switch and modify the query string
     * accordingly.
     */
    const handleSwitch = () => {
        const parsedUrl = url.parse(results['@id']);
        const query = new QueryString(parsedUrl.query);
        if (switchState.current) {
            query.deleteKeyValue('audit.WARNING.category');
        } else {
            query.replaceKeyValue('audit.WARNING.category', 'lacking processed data', true);
        }
        const href = `?${query.format()}`;
        reactContext.navigate(href, { noscroll: true });
    };

    // Make sure a single type=FunctionalCharacterization experiment exists, or display no facet.
    const fccTypeFilters = results.filters.filter(filter => filter.field === 'type' && filter.term === 'FunctionalCharacterizationExperiment');
    if (fccTypeFilters.length === 1) {
        // Determine the state of the switch from the query string, and save it so that
        // `handleSwitch` doesn't have to do this same calculation later.
        const parsedUrl = url.parse(results['@id']);
        const query = new QueryString(parsedUrl.query);
        const auditWarningValues = query.getKeyValues('audit.WARNING.category', true);
        switchState.current = auditWarningValues.length === 1 && auditWarningValues[0] === 'lacking processed data';

        // Retrieve reference to the registered facet title component for this facet.
        const TitleComponent = SpecialFacetRegistry.Title.lookup();

        return (
            <div className="facet facet--audit-warning">
                <div
                    className="facet__expander--header"
                    tabIndex="0"
                    role="button"
                    aria-label="audit.WARNING.category"
                    aria-pressed={isExpanded}
                    onClick={e => handleExpanderClick(e, isExpanded, facet.field)}
                    onKeyDown={e => handleKeyDown(e, isExpanded, facet.field)}
                >
                    <TitleComponent facet={facet} results={results} mode={mode} pathname={pathname} queryString={queryString} />
                    {isExpandable ? <i className={`facet-chevron icon icon-chevron-${isExpanded ? 'up' : 'down'}`} /> : null}
                </div>
                <div className={`facet-content facet-${(isExpanded || !isExpandable) ? 'open' : 'close'}`}>
                    <BooleanSwitch id="facet-audit-warning" state={switchState.current} title="with processed data" triggerHandler={handleSwitch} />
                </div>
            </div>
        );
    }
    return null;
};

AuditProcessedData.propTypes = {
    /** Relevant `facet` object from `facets` array in `results` */
    facet: PropTypes.object.isRequired,
    /** Complete search-results object */
    results: PropTypes.object.isRequired,
    /** Facet display mode */
    mode: PropTypes.string,
    /** Search results path without query-string portion */
    pathname: PropTypes.string.isRequired,
    /** Query-string portion of current URL without initial ? */
    queryString: PropTypes.string,
    /** True if facet is to be expanded */
    isExpanded: PropTypes.bool,
    /** Expand or collapse facet */
    handleExpanderClick: PropTypes.func,
    /** Handles key-press and toggling facet */
    handleKeyDown: PropTypes.func,
    /** True if expandable, false otherwise */
    isExpandable: PropTypes.bool,
};

AuditProcessedData.defaultProps = {
    mode: '',
    queryString: '',
    isExpanded: false,
    handleExpanderClick: () => {},
    handleKeyDown: () => {},
    isExpandable: true,
};

AuditProcessedData.contextTypes = {
    navigate: PropTypes.func,
};


SpecialFacetRegistry.Facet.register('audit.WARNING.category', AuditProcessedData, 'Processed data', true);
