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


export const makeCollectionUrl = (searchUrl, searchTerm) => `${searchUrl}&searchTerm=${searchTerm}`;


export const fetchTotalResultsFromCollection = (url) => (
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
        (results) => results.total
    )
);


export const getHitsFromCollections = (collections, searchTerm) => (
    collections.map(
        (collection) => (
            {
                total: fetchTotalResultsFromCollection(
                    makeCollectionUrl(
                        collection.searchUrl,
                        searchTerm,
                    )
                ),
                ...collection,
            }
        )
    )
);


export const getCountFromCollectionsHits = (hits) => (
    hits.reduce(
        (accumulator, {total}) => accumulator + total, 0
    )
);


class CollectionsQuery {
    constructor(searchTerm) {
        this.searchTerm = searchTerm;
        this.collections = COLLECTIONS;
    }

    getCollectionsWithResults() {
        let hits = getHitsFromCollections(this.collections, this.searchTerm);
        return [
            {
                key: COLLECTIONS_KEY,
                count: getCountFromCollectionsHits(hits),
                hits: hits,
            }
        ];
    }

    getResults() {
        return this.getCollectionsWithResults();
    }
}


export const getTopHitsQuery = (searchTerm) => (
    new Query(searchTerm)
);


export const getCollectionsQuery = (searchTerm) => (
    new CollectionsQuery(searchTerm)
);


class TopHitsAndCollectionQuery {
    constructor(searchTerm) {
        this.searchTerm = searchTerm;
        this.topHitsQuery = getTopHitsQuery(searchTerm);
        this.collectionsQuery = getCollectionsQuery(searchTerm);
    }

    getResults() {
        return (
            this.collectionsQuery.getResults() +
            this.topHitsQuery.getResults()
        );
    }
}


export default Query;
