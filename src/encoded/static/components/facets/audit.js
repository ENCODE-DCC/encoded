import PropTypes from 'prop-types';
import FacetRegistry from './registry';


/**
 * Render titles with icons for all audit-facet types.
 */
const AuditTitle = ({ facet }) => {
    let titleComponent = null;

    // Get the human-readable part of the audit facet title.
    const titleParts = facet.title.split(': ');

    // Get the non-human-readable part so we can generate a corresponding CSS class name.
    const fieldParts = facet.field.match(/^audit.(.+).category$/i);
    if (fieldParts && fieldParts.length === 2 && titleParts) {
        // We got something that looks like an audit title. Generate a CSS class name for
        // the corresponding audit icon, and generate the title.
        const iconClass = `icon audit-activeicon-${fieldParts[1].toLowerCase()}`;
        titleComponent = <h5>{titleParts[0]}: <i className={iconClass} /></h5>;
    } else {
        // Something about the audit facet title doesn't match expectations, so just
        // display the given non-human-readable audit title.
        titleComponent = <h5>{facet.title}</h5>;
    }
    return titleComponent;
};

AuditTitle.propTypes = {
    /** results.facets object for the facet whose term we're rendering */
    facet: PropTypes.object.isRequired,
};


FacetRegistry.Title.register('audit.ERROR.category', AuditTitle);
FacetRegistry.Title.register('audit.NOT_COMPLIANT.category', AuditTitle);
FacetRegistry.Title.register('audit.WARNING.category', AuditTitle);
FacetRegistry.Title.register('audit.INTERNAL_ACTION.category', AuditTitle);
