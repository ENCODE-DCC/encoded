import {
    CollectionsQuery,
    makeCollectionUrl,
    addTotalToCollection,
    fetchTotalResultsFromCollection,
    filterCollectionsWithNoResults,
    formatCollections,
} from '../../query';


const collections = [
    {
        title: 'abc 123',
        searchUrl: '/abc/?format=json',
        '@id': '123',
        '@type': 'CollectionType',
    },
];


const collectionsWithTotals = [
    {
        title: 'abc 123',
        searchUrl: 'abc',
        '@id': '123',
        '@type': 'CollectionType',
        total: 4,
    },
    {
        title: 'xyz 456',
        searchUrl: 'xyz',
        '@id': '456',
        '@type': 'CollectionType',
        total: 6,
    },
    {
        title: 'def 789',
        searchUrl: 'def',
        '@id': '789',
        '@type': 'CollectionType',
        total: 0,
    },
];


const rawResults = {
    total: 44,
};


describe('CollectionsQuery', () => {
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
    describe('makeCollectionUrl', () => {
        test('appends searchTerm to collection url', () => {
            expect(
                makeCollectionUrl(collections[0].searchUrl, 'a549')
            ).toEqual(
                '/abc/?format=json&searchTerm=a549'
            );
        });
    });
    describe('addTotalToCollection', () => {
        test('returns collection with total', () => {
            expect(addTotalToCollection(5, collections[0])).toEqual(
                {
                    title: 'abc 123',
                    searchUrl: '/abc/?format=json',
                    '@id': '123',
                    '@type': 'CollectionType',
                    total: 5,
                }
            );
        });
    });
    describe('fetchTotalResultsFromCollection', () => {
        test('gets results and adds total to collection', () => {
            fetchTotalResultsFromCollection(
                collections[0],
                'a549',
            ).then(
                (result) => (
                    expect(result).toEqual(
                        {
                            title: 'abc 123',
                            searchUrl: '/abc/?format=json',
                            '@id': '123',
                            '@type': 'CollectionType',
                            total: 44,
                        }
                    )
                )
            );
        });
    });
    describe('filterCollectionsWithNoResults', () => {
        test('removes collections with zero results', () => {
            expect(
                filterCollectionsWithNoResults(collectionsWithTotals)
            ).toEqual(
                [
                    {
                        title: 'abc 123',
                        searchUrl: 'abc',
                        '@id': '123',
                        '@type': 'CollectionType',
                        total: 4,
                    },
                    {
                        title: 'xyz 456',
                        searchUrl: 'xyz',
                        '@id': '456',
                        '@type': 'CollectionType',
                        total: 6,
                    },
                ]
            );
        });
    });
    describe('formatCollections', () => {
        test('returns collections as hits', () => {
            expect(
                formatCollections(collectionsWithTotals)
            ).toEqual(
                [
                    {
                        key: 'DataCollection',
                        hits: collectionsWithTotals,
                    },
                ],
            );
        });
    });
    describe('CollectionsQuery class', () => {
        test('getResults', () => {
            const collectionsQuery = new CollectionsQuery('a549');
            collectionsQuery.getResults().then(
                (results) => expect(results[0].hits.length).toEqual(5)
            );
        });
    });
});
