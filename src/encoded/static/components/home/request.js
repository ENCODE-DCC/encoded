// node_modules
import _ from 'underscore';
// top_hits
import { CollectionsQuery, getHitsFromCollections } from '../top_hits/query';
// components
import { postUri, requestUri } from '../objectutils';
// local
import {
    SCREEN_SUGGESTIONS_URL,
    HOME_COLLECTIONS,
    MAX_TYPE_HITS_TYPES,
    TYPE_QUERY_URI,
} from './constants';


/**
 * Used to search a larger set of collections from the standard set. We do this specifically for
 * the home page.
 */
class HomeCollectionsQuery extends CollectionsQuery {
    getResults() {
        return getHitsFromCollections(this.searchTerm, HOME_COLLECTIONS);
    }
}


/**
 * Query the SCREEN server for a list of suggestions for the given search term.
 * @param {string} searchTerm - Term to search for SCREEN suggestions
 * @returns {Promise} - Array of suggested search terms; empty array if none
 */
export const requestScreenSuggestions = (searchTerm) => (
    postUri(SCREEN_SUGGESTIONS_URL, { userQuery: searchTerm }).then((results) => (
        results.length
            ? _.chain(results.map((term) => term.trim())).uniq().compact().value()
            : []
    ))
);


/**
 * Compose a homepage type query for the given search term.
 * @returns {string} - The URI for the homepage type-search query
 */
const composeTypeQuery = (searchTerm) => `${TYPE_QUERY_URI}&searchTerm=${searchTerm}`;


/**
 * Used to retrieve the hit counts for types relevant to a search term.
 * @param {string} searchTerm - Term to search for types
 */
class TypeQuery {
    constructor(searchTerm) {
        this._searchTerm = searchTerm;
    }

    async getResults() {
        const typeResults = await requestUri(composeTypeQuery(this._searchTerm));
        if (typeResults.facets) {
            const typeFacet = typeResults.facets.find((facet) => facet.field === 'type');
            return typeFacet?.terms || [];
        }
        return [];
    }
}


/**
 * Send requests to the server for the given search term and return a promise with a list of the
 * relevant collection titles and the number of hits for each object type.
 * @param {string} searchTerm - Term to search for relevant collections
 * @returns {Promise} - Promise resolving to an object with collection titles and counts.
 * collectionTitles:
 * {
 *     [collectionTitles]: corresponding hit count
 *     ...
 * }
 *
 * typeHits:
 * [
 *     key: object type
 *     doc_count: number of hits
 * ]
 */
export const requestCollectionsAndTypeHits = async (searchTerm) => {
    // Query the collections as well as the top hits for the user's search term.
    const collectionsQuery = new HomeCollectionsQuery(searchTerm);
    const typeQuery = new TypeQuery(searchTerm);
    const [collectionResults, typeHits] = await Promise.all([
        collectionsQuery.getResults(),
        typeQuery.getResults(),
    ]);

    // Extract the collection titles into an object keyed by collection title, each with its
    // corresponding hit count.
    const collectionTitles = {};
    const collectionHits = collectionResults.find((hit) => hit.key === 'DataCollection');
    if (collectionHits?.hits.length > 0) {
        collectionHits.hits.forEach((hit) => {
            collectionTitles[hit.title] = hit.total;
        });
    }

    return { collectionTitles, typeHits: typeHits.slice(0, MAX_TYPE_HITS_TYPES) };
};
