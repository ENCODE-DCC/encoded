import {
    TOP_HITS_URL,
    TOP_HITS_PARAMS
} from './constants';


export default class Query {
    constructor(searchTerm) {
        this.searchTerm = searchTerm;
    }

    parseHits(hits) {
        return hits.map(
            (hit) => hit._source.embedded
        );
    }

    parseResults(results) {
        return results.aggregations.types.types.buckets.map(
            (result) => (
                {
                    key: result.key,
                    count: result.doc_count,
                    hits: this.parseHits(result.top_hits.hits.hits)
                }
            )
        );
    }

    makeTopHitsUrl() {
        return `${TOP_HITS_URL}?searchTerm=${this.searchTerm}${TOP_HITS_PARAMS}`;
    }

    fetchAndParseTopHits(url) {
        return fetch(
            url,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            }
        ).then(
            response => (response.ok ? response.json() : [])
        ).then(
            results => {
                return this.parseResults(results);
            }
        );
    }

    getResults() {
        return this.fetchAndParseTopHits(
            this.makeTopHitsUrl()
        );
    }
}
