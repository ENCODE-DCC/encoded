import PropTypes from 'prop-types';
import FacetRegistry from './registry';

/**
 * This module handles the “perturbed” boolean facet, needed to map the 1/0 or true/false term keys
 * to "not perturbed" and "perturbed".
 */

// The facet term key can be true/false or 1/0 with identical results either way.
const perturbedTerms = {
    false: 'not perturbed',
    true: 'perturbed',
    0: 'not perturbed',
    1: 'perturbed',
};


/**
 * Perturbed terms have a key either true/false or 1/0. Map them to human-readable term names.
 */
const PerturbedTermName = ({ term }) => (
    <span>{perturbedTerms[term.key_as_string]}</span>
);

PerturbedTermName.propTypes = {
    /** facet.terms object for the term we're mapping */
    term: PropTypes.object.isRequired,
};


/**
 * Maps the `perturbed` true/false and 0/1 keys from the search result filters to human-readable
 * strings for the "Selected filters" links.
 */
const PerturbedSelectedTermName = ({ filter, alternateTitle }) => (
    <span>{filter ? perturbedTerms[filter.term] : alternateTitle}</span>
);

PerturbedSelectedTermName.propTypes = {
    /** facet.filters object for the selected term we're mapping */
    filter: PropTypes.object,
    /** Title to override the one from `filter` */
    alternateTitle: PropTypes.string,
};

PerturbedSelectedTermName.defaultProps = {
    filter: null,
    alternateTitle: '',
};

FacetRegistry.TermName.register('perturbed', PerturbedTermName);
FacetRegistry.SelectedTermName.register('perturbed', PerturbedSelectedTermName);
