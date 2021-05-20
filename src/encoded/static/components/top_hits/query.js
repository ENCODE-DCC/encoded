import {
    COLLECTIONS,
    COLLECTIONS_KEY,
    TOP_HITS_URL,
    TOP_HITS_PARAMS,
} from './constants';


/**
* Encapsulates all the functionality for querying the top hits endpoint
* and returning parsed results.
*/


/**
* We just want the actual properties in a document.
* @param {array} hits - The raw hits pulled from Elasticsearch results.
* @return {array} Parsed hits that only include properties of interest.
*/
export const parseHits = (hits) => (
    hits.map(
        (hit) => hit._source.embedded
    )
);


/**
* Must reach into the aggregation and pull out results
* for every bucket (object type). These get mapped to a
* list of objects that includes the type name, the total
* number of results of that type, and the formatted
* top hits of that type.
* @param {object} results - Raw top hit results from Elasticsearch.
* @return {array} Parsed top hits.
*/
export const parseResults = (results) => (
    results.aggregations.types.types.buckets.map(
        (result) => (
            {
                key: result.key,
                count: result.doc_count,
                hits: parseHits(result.top_hits.hits.hits),
            }
        )
    )
);


/**
* Queries top hits endpoint and parses raw results.
* @param {string} url - The URL defining raw hits endpoint and specified fields to return.
* @return {array} The parsed top hits in [{key: string, count: number, hits: array}, ...] format.
*/
export const fetchAndParseTopHits = (url) => (
    fetch(
        url,
        {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        }
    ).then(
        (response) => (response.ok ? response.json() : [])
    ).then(
        (results) => parseResults(results)
    )
);


/**
* Allows you to pass in a user searchTerm and get back
* a list of formatted top hits by type:
* >>> const topHitsQuery = new Query('a549');
* >>> const results = topHitsQuery.getResults();
*/
class Query {
    constructor(searchTerm) {
        this.searchTerm = searchTerm;
    }

    /**
    * @return {string} The generated query URL including endpoint and fields to return.
    */
    makeTopHitsUrl() {
        return `${TOP_HITS_URL}?searchTerm=${this.searchTerm}${TOP_HITS_PARAMS}`;
    }

    /**
    * @return {array} The parsed top hits in [{key: string, count: number, hits: array}, ...] format.
    */
    getResults() {
        return fetchAndParseTopHits(
            this.makeTopHitsUrl()
        );
    }
}


/**
* Functionality for treating the multiple data collection URLs as one query. We search over all
* of the URLs with the given user searchTerm and see if they have any results. We format data
* collections with results in way that can be rendered by dropdown component.
*/


/**
* Generates URL for searching data collection with specific user search term.
* @param {string} searchUrl - The search URL for a specific data collection.
* @param {string} searchTerm - The user search term.
* @return {string} The generated query URL for a collection.
*/
export const makeCollectionUrl = (searchUrl, searchTerm) => `${searchUrl}&searchTerm=${searchTerm}`;


/**
* Adds the total to a collection item.
* @param {number} total - The total hits in a collection that match a given search term.
* @param {object} collection - The collection item (defined by title, searchUrl, @id, @type fields).
* @return {object} Collection item with total.
*/
export const addTotalToCollection = (total, collection) => (
    {
        total,
        ...collection,
    }
);


/**
* Queries a data collection URL and returns the collection item with its total results.
* @param {object} collection - The collection item (defined by title, searchUrl, @id, @type fields).
* @param {string} searchTerm - The user search term.
* @return {object} Collection item with total results.
*/
export const fetchTotalResultsFromCollection = (collection, searchTerm) => (
    fetch(
        makeCollectionUrl(collection.searchUrl, searchTerm),
        {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        }
    ).then(
        (response) => (response.ok ? response.json() : { total: 0 })
    ).then(
        (result) => addTotalToCollection(result.total, collection)
    )
);


/**
* Only keep collections with results.
* @param {array[object]} collections - An array of collection items.
* @return {array[object]} Filtered array of collection items.
*/
export const filterCollectionsWithNoResults = (collections) => (
    collections.filter(
        ({ total }) => total > 0
    )
);


/**
* Return all the data collections with results as array of hits.
* @param {array[object]} collections - Filtered array of collection items.
* @return {array[object]} Result format that can be rendered by dropdown.
*/
export const formatCollections = (collections) => {
    if (collections.length > 0) {
        return [
            {
                key: COLLECTIONS_KEY,
                hits: collections,
            },
        ];
    }
    return collections;
};


/**
* Get results from all of the data collections for a given search term, filter collections
* with no results, and format the collections in a way that can be rendered by dropdown.
* @param {string} searchTerm - The user search term.
* @return {array[object]} Formatted collection results.
*/
export const getHitsFromCollections = (searchTerm) => (
    Promise.all(
        COLLECTIONS.map(
            (collection) => fetchTotalResultsFromCollection(collection, searchTerm)
        )
    ).then(
        (collections) => filterCollectionsWithNoResults(collections)
    ).then(
        (collections) => formatCollections(collections)
    )
);


/**
* Allows you to pass in a user searchTerm and get back
* a list of formatted data collection hits.
* >>> const collectionsQuery = new CollectionsQuery('a549');
* >>> const results = collectionsQuery.getResults();
*/
export class CollectionsQuery {
    constructor(searchTerm) {
        this.searchTerm = searchTerm;
    }

    getResults() {
        return getHitsFromCollections(this.searchTerm);
    }
}


export default Query;
