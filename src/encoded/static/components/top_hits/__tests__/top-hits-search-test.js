import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';
import { act } from 'react-dom/test-utils';

import {
    NavBarSearch,
    PageSearch,
} from '../search';


// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


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


describe('Search', () => {
    beforeEach(() => {
        jest.useFakeTimers();
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
    test('NavBarSearch renders', () => {
        const search = mount(
            <NavBarSearch />
        );
        expect(search.find('NavBarForm')).toHaveLength(1);
        expect(search.find('i')).toHaveLength(1);
    });
    test('Ignore stale requests', async () => {
        const search = mount(
            <NavBarSearch />
        );
        search.find('input').simulate(
            'change',
            {
                target: {
                    value: 'A54',
                },
            }
        );
        expect(search.find('Input').prop('input')).toEqual('A54');
        expect(search.find('Results')).toHaveLength(0);
        await act(async () => {
            jest.runAllTimers();
        });
        search.update();
        expect(search.find('Results')).toHaveLength(1);
        expect(search.find('i')).toHaveLength(1);
    });
    test('PageSearch renders', () => {
        const search = mount(
            <PageSearch />
        );
        expect(search.find('PageForm')).toHaveLength(1);
        expect(search.find('i')).toHaveLength(0);
    });
});
