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
export class Query {
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


export const addTotalToCollection = (total, collection) => (
    {
        total,
        ...collection
    }
);


export const filterCollectionsWithNoResults = (collections) => (
    collections.filter(
        ({total}) => total > 0
    )
);


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
        (response) => (response.ok ? response.json() : {total: 0})
    ).then(
        (result) => addTotalToCollection(result.total, collection)
    )
);


export const getHitsFromCollections = (collections, searchTerm) => (
    Promise.all(
        collections.map(
            (collection) => fetchTotalResultsFromCollection(collection, searchTerm)
        )
    ).then(
        (collections) => filterCollectionsWithNoResults(collections)
    )
);


export const getCountFromCollectionsHits = (hits) => (
    hits.reduce(
        (accumulator, {total}) => accumulator + total, 0
    )
);


export const getCollectionLink = () => `/help/project-overview/`;


export class CollectionsQuery {
    constructor(searchTerm) {
        this.searchTerm = searchTerm;
        this.collections = COLLECTIONS;
    }

    getCollectionsWithResults() {
        return getHitsFromCollections(
            this.collections,
            this.searchTerm
        ).then(
            (hits) => (
                [
                    {
                        key: COLLECTIONS_KEY,
                        count: getCountFromCollectionsHits(hits),
                        hits: hits,
                        href: getCollectionLink()
                    }
                ]
            )
        ).then(
            (results) => results.filter(
                ({count}) => count > 0
            )
        );
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


export const flattenArrays = (arrays) => (
    arrays.reduce((a, b) => a.concat(b), [])
);


export const sortResultsByCount = (results) => (
    results.sort((a, b) => b.count - a.count)
);


class TopHitsAndCollectionsQuery {
    constructor(searchTerm) {
        this.searchTerm = searchTerm;
    }

    getQueries() {
        return [
            getCollectionsQuery(this.searchTerm),
            getTopHitsQuery(this.searchTerm),
        ];
    }

    getResults() {
        let queries = this.getQueries();
        return Promise.all(
            queries.map(
                (query) => query.getResults()
            )
        ).then(
            (results) =>  flattenArrays(results)
        ).then(
            (results) => sortResultsByCount(results)
        );
    }
}


export default TopHitsAndCollectionsQuery;
