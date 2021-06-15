/**
 * Small, general components and functions needed by other cart modules.
 */

import _ from 'underscore';
import url from 'url';


/**
 * Maximum number of items allowed in a cart.
 */
export const CART_MAX_ELEMENTS = 8000;


/**
 * List of dataset types allowed in carts. Maps from collection names to corresponding data:
 *     title: Displayable title for the type
 *     type: Object @type, i.e. RHS of "type=<dataset type>" in a query string
 */
export const allowedDatasetTypes = {
    experiments: { title: 'Experiments', type: 'Experiment' },
    annotations: { title: 'Annotations', type: 'Annotation' },
    'functional-characterization-experiments': { title: 'Functional characterizations', type: 'FunctionalCharacterizationExperiment' },
};

/**
 * The default dataset type for All Datasets. The object matches the real dataset types in
 * `allowedDatasetTypes` but without a type.
 */
export const defaultDatasetType = {
    all: { title: 'All dataset types' },
};


/**
 * Get a mutable array of dataset types allowed in carts, i.e. an array of types on the right-
 * hand side of "type=<dataset type>" in a query string.
 * @return {array} Copy of `allowedCartTypes` global
 */
export const cartGetAllowedTypes = () => (
    Object.keys(allowedDatasetTypes).map((datasetType) => allowedDatasetTypes[datasetType].type)
);


/**
 * Get a mutable array of object path types allowed in carts, i.e. the part in an object path:
 * /{object path type}/{accession}/ e.g. /experiments/ENCSR000AAA/
 * @return {array} Copy of `allowedCartTypes` global
 */
export const cartGetAllowedObjectPathTypes = () => (
    Object.keys(allowedDatasetTypes)
);


/**
 * Given an array of search-result filters, determine if these filters could potentially lead to
 * search results containing object types allowed in carts, including:
 *  - type=<allowed cart type> included in filters or...
 *  - No "type" filters at all
 * @param {array} resultFilters Search results filter object
 * @return {bool} True if filters might allow for allowed object types in result.
 */
export const isAllowedElementsPossible = (resultFilters) => {
    let typeFilterExists = false;
    const allowedTypes = cartGetAllowedTypes();
    const allowedFilters = resultFilters.filter((resultFilter) => {
        if (resultFilter.field === 'type') {
            typeFilterExists = true;
            return allowedTypes.indexOf(resultFilter.term) >= 0;
        }
        return false;
    });
    return allowedFilters.length > 0 || !typeFilterExists;
};


/**
 * Return a new array containing the merged contents of two carts with no duplicates. Contains odd
 * ES6 syntax to merge, clone, and de-dupe arrays in one operation.
 * https://stackoverflow.com/questions/1584370/how-to-merge-two-arrays-in-javascript-and-de-duplicate-items#answer-38940354
 * @param {array} cart0AtIds Array of @ids in one cart
 * @param {array} cart1AtIds Array of @ids to merge with `cart0AtIds`
 */
export const mergeCarts = (cart0AtIds, cart1AtIds) => (
    [...new Set([...cart0AtIds, ...cart1AtIds])]
);


/**
 * Determine whether the given search results is for a cart search or not.
 * @param {object} context Search-results object
 *
 * @return {boolean} True if search results are for a cart search.
 */
const cartSearchPaths = ['/cart-search/', '/cart-matrix/', '/cart-report/'];
export const getIsCartSearch = (context) => {
    const pathName = url.parse(context['@id']).pathname;
    return cartSearchPaths.includes(pathName);
};

/**
 * Get array of @types of objects that exist in the given cart search results.
 * @param {object} context /cart-search/ results
 *
 * @return {array} @types of all elements in the cart search results, de-duped.
 */
export const getCartSearchTypes = (context) => (
    _.uniq(context['@graph'].map((result) => result['@type'][0]))
);


/**
 * Extract the file @ids of the analyses selected by the given analysis titles.
 * @param {array} availableAnalyses Compiled analysis objects.
 * @param {array} analysisTitles Titles of analyses from which to extract file @ids.
 *
 * @return {array} Combined @ids of selected analysis files.
 */
export const getAnalysesFileIds = (availableAnalyses, analysisTitles = []) => {
    const selectedFileIds = availableAnalyses.reduce((fileIds, analysis) => {
        if (analysisTitles.length === 0 || analysisTitles.includes(analysis.title)) {
            return fileIds.concat(analysis.files);
        }
        return fileIds;
    }, []);
    return _.uniq(selectedFileIds);
};


/**
 * Extract the value of an object property based on a dotted-notation field,
 * e.g. { a: 1, b: { c: 5 }} you could retrieve the 5 by passing 'b.c' in `field`.
 * Based on https://stackoverflow.com/questions/6393943/convert-javascript-string-in-dot-notation-into-an-object-reference#answer-6394168
 * @param {object} object Object containing the value you want to extract.
 * @param {string} field  Dotted notation for the property to extract.
 *
 * @return {value} Whatever value the dotted notation specifies, or undefined.
 */
export const getObjectFieldValue = (object, field) => {
    const parts = field.split('.');
    if (parts.length === 1) {
        return object[field];
    }
    const value = parts.reduce((partObject, part) => partObject && partObject[part], object);
    if (Array.isArray(value)) {
        return value.length > 0 ? value : undefined;
    }
    return value;
};
