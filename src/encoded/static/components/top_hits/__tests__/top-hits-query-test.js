import Query,
{
    parseHits,
    parseResults,
    fetchAndParseTopHits,
} from '../query';


const rawHits = [
    {
        _index: 'experiment',
        _type: 'experiment',
        _id: 'fe9fe0cb-b859-461c-8d0f-4fa5f8e9377f',
        _score: 4.5483103,
        _source: {
            embedded: {
                '@type': [
                    'Experiment',
                    'Dataset',
                    'Item',
                ],
                accession: 'ENCSR003SER',
                '@id': '/experiments/ENCSR003SER/',
                status: 'released',
            },
        },
    },
];


const rawResults = {
    _shards: {
        total: 535,
        successful: 535,
        skipped: 0,
        failed: 0,
    },
    aggregations: {
        types: {
            doc_count: 13,
            types: {
                doc_count_error_upper_bound: 0,
                sum_other_doc_count: 0,
                buckets: [
                    {
                        key: 'Experiment',
                        doc_count: 6,
                        max_score: {
                            value: 4.548310279846191,
                        },
                        top_hits: {
                            hits: {
                                total: 6,
                                max_score: 4.5483103,
                                hits: [
                                    {
                                        _index: 'experiment',
                                        _type: 'experiment',
                                        _id: 'fe9fe0cb-b859-461c-8d0f-4fa5f8e9377f',
                                        _score: 4.5483103,
                                        _source: {
                                            embedded: {
                                                '@type': [
                                                    'Experiment',
                                                    'Dataset',
                                                    'Item',
                                                ],
                                                accession: 'ENCSR003SER',
                                                '@id': '/experiments/ENCSR003SER/',
                                                status: 'released',
                                            },
                                        },
                                    },
                                    {
                                        _index: 'experiment',
                                        _type: 'experiment',
                                        _id: 'e162561a-08c0-463c-93d8-c4f924584e13',
                                        _score: 3.2180696,
                                        _source: {
                                            embedded: {
                                                '@type': [
                                                    'Experiment',
                                                    'Dataset',
                                                    'Item',
                                                ],
                                                accession: 'ENCSR001CTL',
                                                '@id': '/experiments/ENCSR001CTL/',
                                                status: 'released',
                                            },
                                        },
                                    },
                                    {
                                        _index: 'experiment',
                                        _type: 'experiment',
                                        _id: '4cead359-10e9-49a8-9d20-f05b2499b919',
                                        _score: 3.207864,
                                        _source: {
                                            embedded: {
                                                '@type': [
                                                    'Experiment',
                                                    'Dataset',
                                                    'Item',
                                                ],
                                                accession: 'ENCSR001SER',
                                                '@id': '/experiments/ENCSR001SER/',
                                                status: 'released',
                                            },
                                        },
                                    },
                                ],
                            },
                        },
                    },
                    {
                        key: 'Page',
                        doc_count: 3,
                        max_score: {
                            value: 3.030086040496826,
                        },
                        top_hits: {
                            hits: {
                                total: 3,
                                max_score: 3.030086,
                                hits: [
                                    {
                                        _index: 'page',
                                        _type: 'page',
                                        _id: '4677b033-b52b-4a46-a8b8-38a60dc9cd84',
                                        _score: 3.030086,
                                        _source: {
                                            embedded: {
                                                '@type': [
                                                    'Page',
                                                    'Item',
                                                ],
                                                '@id': '/latest-ggr-release-reddy-lab/',
                                                status: 'released',
                                            },
                                        },
                                    },
                                    {
                                        _index: 'page',
                                        _type: 'page',
                                        _id: '6d24ad59-2247-4e5e-8e00-2fe0b6ecfad8',
                                        _score: 2.788453,
                                        _source: {
                                            embedded: {
                                                '@type': [
                                                    'Page',
                                                    'Item',
                                                ],
                                                '@id': '/2016-12-20-new-chipseq-data/',
                                                status: 'released',
                                            },
                                        },
                                    },
                                ],
                            },
                        },
                    },
                ],
            },
        },
    },
    num_reduce_phases: 2,
    timed_out: false,
    took: 58,
};


const parsedResults = [
    {
        count: 6,
        hits: [
            {
                '@id': '/experiments/ENCSR003SER/',
                '@type': ['Experiment', 'Dataset', 'Item'],
                accession: 'ENCSR003SER',
                status: 'released',
            },
            {
                '@id': '/experiments/ENCSR001CTL/',
                '@type': ['Experiment', 'Dataset', 'Item'],
                accession: 'ENCSR001CTL',
                status: 'released',
            },
            {
                '@id': '/experiments/ENCSR001SER/',
                '@type': ['Experiment', 'Dataset', 'Item'],
                accession: 'ENCSR001SER',
                status: 'released',
            },
        ],
        key: 'Experiment',
    },
    {
        count: 3,
        hits: [
            {
                '@id': '/latest-ggr-release-reddy-lab/',
                '@type': ['Page', 'Item'],
                status: 'released',
            },
            {
                '@id': '/2016-12-20-new-chipseq-data/',
                '@type': ['Page', 'Item'],
                status: 'released',
            },
        ],
        key: 'Page',
    },
];


describe('Query', () => {
    beforeEach(() => {
        global.fetch = jest.fn(
            () => (
                Promise.resolve(
                    {
                        ok: true,
                        headers: {
                            get: () => null,
                        },
                        json: () => rawResults,
                    }
                )
            )
        );
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    describe('parseHits', () => {
        test('returns embedded source', () => {
            expect(parseHits(rawHits)).toEqual(
                [
                    {
                        '@type': [
                            'Experiment',
                            'Dataset',
                            'Item',
                        ],
                        accession: 'ENCSR003SER',
                        '@id': '/experiments/ENCSR003SER/',
                        status: 'released',
                    },
                ]
            );
        });
    });
    describe('parseResults', () => {
        test('returns parsed results', () => {
            expect(
                parseResults(rawResults)
            ).toEqual(parsedResults);
        });
    });
    describe('fetchAndParseTopHits', () => {
        test('results fetched and parsed', () => {
            fetchAndParseTopHits('abc').then(
                (results) => expect(results).toEqual(parsedResults)
            );
        });
    });
    describe('Query class', () => {
        test('makeTopHitsUrl', () => {
            const query = new Query('a549');
            expect(
                query.makeTopHitsUrl()
            ).toEqual(
                (
                    '/top-hits-raw/?searchTerm=a549&field=description&field=accession&field=external_accession' +
                    '&field=title&field=summary&field=biosample_summary&field=assay_term_name&field=file_type' +
                    '&field=status&field=antigen_description&field=target.label&field=targets.label' +
                    '&field=assay_title&field=output_type&field=replicates.library.biosample.organism.scientific_name' +
                    '&field=organism.scientific_name&field=term_name&field=biosample_ontology.term_name' +
                    '&field=classification&field=document_type&field=attachment.download&field=lot_id' +
                    '&field=product_id&field=annotation_type&field=news_excerpt&field=abstract&field=authors' +
                    '&field=label&field=symbol&field=name&field=category&field=purpose&field=method' +
                    '&field=institute_name&field=assay_term_names&field=strain_name&field=genotype&format=json'
                )
            );
        });
        test('getResults', () => {
            const query = new Query('a549');
            query.getResults().then(
                (results) => expect(results).toEqual(parsedResults)
            );
        });
    });
});
