import React from 'react';
import PropTypes from 'prop-types';
import QueryString from '../../libs/query_string';
import BooleanSwitch from '../../libs/ui/boolean-switch';
import { SpecialFacetRegistry } from './registry';


/**
 * Special facet to display a switch to select between having the search result query string
 * contain: "audit.WARNING.category!=lacking processed data" and without that term at all, with the
 * boolean switch component showing the "on" state with the former and the "off" state with the
 * latter.
 */
const AuditProcessedData = ({ results, queryString }, reactContext) => {
    /** Keeps track of the switch state for `handleSwitch` */
    const switchState = React.useRef(false);

    /**
     * Called when the user clicks the term to flip the switch and modify the query string
     * accordingly.
     */
    const handleSwitch = () => {
        const query = new QueryString(queryString);
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
        const query = new QueryString(queryString);
        const auditWarningValues = query.getKeyValues('audit.WARNING.category', true);
        switchState.current = auditWarningValues.length === 1 && auditWarningValues[0] === 'lacking processed data';

        return (
            <div className="facet facet--audit-warning">
                <BooleanSwitch
                    id="facet-audit-warning"
                    state={switchState.current}
                    title={switchState.current ? 'With processed data' : 'All data'}
                    triggerHandler={handleSwitch}
                    options={{ cssTitle: 'facet-audit-switch-title'}}
                />
            </div>
        );
    }
    return null;
};

AuditProcessedData.propTypes = {
    /** Complete search-results object */
    results: PropTypes.object.isRequired,
    /** Query-string portion of current URL without initial ? */
    queryString: PropTypes.string,
};

AuditProcessedData.defaultProps = {
    queryString: '',
};

AuditProcessedData.contextTypes = {
    navigate: PropTypes.func,
};


SpecialFacetRegistry.Facet.register('audit.WARNING.category', AuditProcessedData, 'Processed data', true);
