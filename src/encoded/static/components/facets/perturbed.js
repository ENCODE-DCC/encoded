import React from 'react';
import PropTypes from 'prop-types';
import FacetRegistry from './registry';

/**
 * This module handles the “perturbed” boolean facet, needed because the values of the facet terms
 * aren't human readable and have to be mapped to human-readable forms, and because we didn't want
 * this facet to be the typical boolean radio buttons.
 */

const perturbedTerms = ['not perturbed', 'perturbed'];


/**
 * Perturbed terms have a value either 0 or 1. Map them to human-readable names.
 */
const PerturbedTermName = ({ term }) => {
    let mappedTerm;
    if (term.key === 0 || term.key === 1) {
        mappedTerm = perturbedTerms[term.key];
    } else {
        // Likely will never happen.
        mappedTerm = 'unknown';
    }
    return <span>{mappedTerm}</span>;
};

PerturbedTermName.propTypes = {
    /** facet.terms object for the term we're mapping */
    term: PropTypes.object.isRequired,
};


/**
 * Maps the "perturbed" "0" and "1" values from the search result filters to human-readable
 * strings for the "Selected filters" links.
 */
const PerturbedSelectedTermName = ({ filter }) => (
    <span>{perturbedTerms[filter.term]}</span>
);

PerturbedSelectedTermName.propTypes = {
    /** facet.filters object for the selected term we're mapping */
    filter: PropTypes.object.isRequired,
};


FacetRegistry.TermName.register('replicates.library.biosample.perturbed', PerturbedTermName);
FacetRegistry.TermName.register('perturbed', PerturbedTermName);
FacetRegistry.SelectedTermName.register('replicates.library.biosample.perturbed', PerturbedSelectedTermName);
FacetRegistry.SelectedTermName.register('perturbed', PerturbedSelectedTermName);
