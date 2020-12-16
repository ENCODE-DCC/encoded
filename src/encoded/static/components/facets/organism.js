import React from 'react';
import PropTypes from 'prop-types';
import FacetRegistry from './registry';


/**
 * Organism scientific names appear italic. The rest of the facet term works and appears normally.
 */
const OrganismTermName = ({ term }) => (
    <i>{term.key}</i>
);

OrganismTermName.propTypes = {
    /** facet.terms object for the term we're rendering */
    term: PropTypes.object.isRequired,
};


FacetRegistry.TermName.register('replicates.library.biosample.donor.organism.scientific_name', OrganismTermName);
FacetRegistry.TermName.register('organism.scientific_name', OrganismTermName);
FacetRegistry.TermName.register('target.organism.scientific_name', OrganismTermName);
FacetRegistry.TermName.register('targets.organism.scientific_name', OrganismTermName);
