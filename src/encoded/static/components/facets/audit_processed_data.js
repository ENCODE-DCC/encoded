import PropTypes from 'prop-types';
import QueryString from '../../libs/query_string';
import { SpecialFacetRegistry } from './registry';


/**
 * Special facet to display a dropdown to select between having the search result query string
 * contain "audit.WARNING.category!=lacking processed data" and without that term at all.
 */
const AuditProcessedData = ({ results, queryString }, reactContext) => {
    /**
     * Called when the user changes the dropdown to a new value.
     */
    const handleChange = (event) => {
        const query = new QueryString(queryString);
        if (event.target.value === 'all-data') {
            // "All data" selected. Clear out any audit.WARNING.category from the query string.
            query.deleteKeyValue('audit.WARNING.category');
        } else {
            // "Processed data" selected. Replace any audit.WARNING.category in the query string
            // with audit.WARNING.category!=lacking+processed+data.
            query.replaceKeyValue('audit.WARNING.category', 'lacking processed data', true);
        }
        const href = `?${query.format()}`;
        reactContext.navigate(href, { noscroll: true });
    };

    // Make sure a single type=FunctionalCharacterization experiment exists, or display no facet.
    const fccTypeFilters = results.filters.filter((filter) => filter.field === 'type' && filter.term === 'FunctionalCharacterizationExperiment');
    if (fccTypeFilters.length === 1) {
        // Determine the state of the switch from the query string, and save it so that
        // `handleSwitch` doesn't have to do this same calculation later.
        const query = new QueryString(queryString);
        const auditWarningValues = query.getKeyValues('audit.WARNING.category', true);
        const dataSelection = (auditWarningValues.length === 1 && auditWarningValues[0] === 'lacking processed data') ? 'processed-data' : 'all-data';

        return (
            <div className="facet facet--audit-warning">
                <select value={dataSelection} onChange={handleChange}>
                    <option value="processed-data">With processed data</option>
                    <option value="all-data">All data</option>
                </select>
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
