import PropTypes from 'prop-types';
import FacetRegistry from './registry';
import Status from '../status';


/**
 * Displays status terms with matching status icons.
 */
const StatusTermName = ({ term }) => (
    <div className="facet-term__status-wrapper">
        <Status item={term.key} badgeSize="small" css="facet-term__status" noLabel />
        <div className="facet-term__status-label">{term.key}</div>
    </div>
);

StatusTermName.propTypes = {
    /** facet.terms object for the term we're rendering */
    term: PropTypes.object.isRequired,
};


FacetRegistry.TermName.register('lot_reviews.status', StatusTermName);
FacetRegistry.TermName.register('status', StatusTermName);
