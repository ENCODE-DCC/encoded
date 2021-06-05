import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';
import { act } from 'react-dom/test-utils';

import NavBarMultiSearch from '../search';


const rawResults1 = {
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


const rawResults2 = {
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
                        key: 'File',
                        doc_count: 1,
                        max_score: {
                            value: 4.548310279846191,
                        },
                        top_hits: {
                            hits: {
                                total: 1,
                                max_score: 4.5483103,
                                hits: [
                                    {
                                        _index: 'file',
                                        _type: 'file',
                                        _id: 'fe9fe0cb-b859-461c-8d0f-4fa5f8e9377f',
                                        _score: 4.5483103,
                                        _source: {
                                            embedded: {
                                                '@type': [
                                                    'File',
                                                    'Item',
                                                ],
                                                accession: 'ENCFF000ABC',
                                                '@id': '/files/ENCFF000ABC/',
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


// Search for H takes 1050ms to return H, search for HBB takes 550ms.
const getDelayedResultsForUrl = async (url) => {
    if (url.includes('?searchTerm=H&')) {
        return new Promise(
            (resolve) => setTimeout(() => resolve(rawResults1), 1000)
        );
    }
    if (url.includes('?searchTerm=HBB&')) {
        return new Promise(
            (resolve) => setTimeout(() => resolve(rawResults2), 500)
        );
    }
    if (url.includes('&internal_tags=ENTEx&limit=0&format=json&searchTerm=HBB')) {
        return new Promise(
            (resolve) => setTimeout(() => resolve({ total: 2 }), 550)
        );
    }
    if (url.includes('&internal_tags=ENTEx&limit=0&format=json&searchTerm=H')) {
        return new Promise(
            (resolve) => setTimeout(() => resolve({ total: 44 }), 1050)
        );
    }
    return new Promise(
        (resolve) => setTimeout(() => resolve({}), 0)
    );
};


// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


describe('NavBarMultiSearch', () => {
    beforeEach(() => {
        jest.useFakeTimers();
        global.fetch = jest.fn(
            (url) => (
                Promise.resolve(
                    {
                        ok: true,
                        headers: {
                            get: () => null,
                        },
                        json: () => getDelayedResultsForUrl(url),
                    }
                )
            )
        );
    });
    afterEach(() => {
        jest.clearAllMocks();
    });
    test('NavBarMultiSearch renders', () => {
        const search = mount(
            <NavBarMultiSearch />
        );
        expect(search.find('NavBarForm')).toHaveLength(1);
        expect(search.find('i')).toHaveLength(1);
    });
    test('Multisearch component updates asynchronously on input', async () => {
        const search = mount(
            <NavBarMultiSearch />
        );
        // User types in H.
        search.find('input').simulate(
            'change',
            {
                target: {
                    value: 'H',
                },
            }
        );
        // H shows in input box.
        expect(search.find('Input').prop('input')).toEqual('H');
        // No results yet.
        expect(search.find('Results')).toHaveLength(0);
        // Wait debounce time.
        await act(async () => {
            jest.advanceTimersByTime(200);
        });
        search.update();
        // Wait half of search request time.
        await act(async () => {
            jest.advanceTimersByTime(525);
        });
        search.update();
        // No results yet.
        expect(search.find('Results')).toHaveLength(0);
        // Wait rest of response time for H results.
        await act(async () => {
            jest.advanceTimersByTime(525);
        });
        search.update();
        // Top hits and data collection results should show.
        expect(search.find('Results')).toHaveLength(2);
        expect(search.find('Section')).toHaveLength(3);
        expect(search.find('Item')).toHaveLength(6);
        expect(search.find('i')).toHaveLength(1);
    });
    test('Multisearch ignores results from stale H request', async () => {
        const search = mount(
            <NavBarMultiSearch />
        );
        // User types in H.
        search.find('input').simulate(
            'change',
            {
                target: {
                    value: 'H',
                },
            }
        );
        // H shows in input box.
        expect(search.find('Input').prop('input')).toEqual('H');
        // No results yet.
        expect(search.find('Results')).toHaveLength(0);
        // Wait debounce time.
        await act(async () => {
            jest.advanceTimersByTime(200);
        });
        search.update();
        // User types in HBB.
        search.find('input').simulate(
            'change',
            {
                target: {
                    value: 'HBB',
                },
            }
        );
        // Wait debounce time.
        await act(async () => {
            jest.advanceTimersByTime(200);
        });
        search.update();
        // Wait for all results to come back.
        await act(async () => {
            jest.runAllTimers();
        });
        search.update();
        // HBB top hits and data collection results should show.
        expect(search.find('Results')).toHaveLength(2);
        expect(search.find('Section')).toHaveLength(2);
        expect(search.find('Item')).toHaveLength(2);
        expect(search.find('i')).toHaveLength(1);
    });
});
