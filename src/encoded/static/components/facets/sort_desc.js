import PropTypes from 'prop-types';
import _ from 'underscore';
import { FacetFunctionRegistry } from './registry';


/**
 * Render terms sorted by key in descending order.
 */
const SortDecs = (terms) => _.sortBy(terms, 'key').reverse();

SortDecs.propTypes = {
    terms: PropTypes.object.isRequired,
};


FacetFunctionRegistry.sortTerms.register('publication_year', SortDecs);

