import {
    TOP_HITS_URL,
    TOP_HITS_PARAMS,
} from './constants';


const parseHits = hits => (
    hits.map(
        hit => hit._source.embedded
    )
);


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
