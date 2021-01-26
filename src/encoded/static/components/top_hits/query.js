import {
    TOP_HITS_URL,
    TOP_HITS_PARAMS,
} from './constants';


/**
* Encapsulates all the functionality for querying the top hits endpoint
* and returning parsed results.
*/


// We just want the actual properties in a document.
const parseHits = hits => (
    hits.map(
        hit => hit._source.embedded
    )
);


/**
* Must reach into the aggregation and pull out results
* for every bucket (object type). These get mapped to a
* list that includes the type name, the total number of results
* of that type, and the formatted top hits of that type.
*/
const parseResults = results => (
    results.aggregations.types.types.buckets.map(
        result => (
            {
                key: result.key,
                count: result.doc_count,
                hits: parseHits(result.top_hits.hits.hits),
            }
        )
    )
);


const fetchAndParseTopHits = url => (
    fetch(
        url,
        {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        }
    ).then(
        response => (response.ok ? response.json() : [])
    ).then(
        results => parseResults(results)
    )
);


/**
* Allows you to pass in a user searchTerm and get back
* a list of formatted top hits by type:
*     const topHitsQuery = new Query('a549');
*     const results = topHitsQuery.getResults().
*/
class Query {
    constructor(searchTerm) {
        this.searchTerm = searchTerm;
    }

    makeTopHitsUrl() {
        return `${TOP_HITS_URL}?searchTerm=${this.searchTerm}${TOP_HITS_PARAMS}`;
    }

    getResults() {
        return fetchAndParseTopHits(
            this.makeTopHitsUrl()
        );
    }
}


export default Query;
