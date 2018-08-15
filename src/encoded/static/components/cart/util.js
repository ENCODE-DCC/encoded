// List of object @type allowed in the cart.
const allowedTypes = [
    'Experiment',
];


/**
 * Given an array of search results filters, return an array with any "type" filters for types not
 * qualified for a cart filtered out. If no "type" filters exist after this, then return an empty
 * array, as we need at least one qualifying "type" filter to add anything to the cart.
 *
 * @param {array} items - Object with types to be filtered
 * @return {array} - All `items` with types in `allowedTypes`
 */
const getAllowedResultFilters = (resultFilters) => {
    const allowedFilters = resultFilters.filter(resultFilter => resultFilter.field !== 'type' || allowedTypes.indexOf(resultFilter.term) >= 0);
    return allowedFilters.some(filter => filter.field === 'type') ? allowedFilters : [];
};

export default getAllowedResultFilters;
