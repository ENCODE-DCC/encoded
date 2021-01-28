import { collectChildren } from '../biosample';


const biosample = {
    '@id': '/biosamples/ENCBS000AAA/',
    status: 'released',
    parent_of: [
        {
            '@id': '/biosamples/ENCBS000AAB/',
            status: 'released',
            parent_of: [],
        },
        {
            '@id': '/biosamples/ENCBS000AAC/',
            status: 'released',
            parent_of: [
                {
                    '@id': '/biosamples/ENCBS000AAD/',
                    status: 'released',
                    parent_of: [],
                },
                {
                    '@id': '/biosamples/ENCBS000AAE/',
                    status: 'released',
                    parent_of: [
                        {
                            '@id': '/biosamples/ENCBS000AAF/',
                            status: 'released',
                            parent_of: [],
                        },
                    ],
                },
            ],
        },
    ],
};

describe('Utility functions', () => {
    test('collectChildren generates correct list of biosamples', () => {
        collectChildren(biosample).then((biosamples) => {
            // Top level has expected properties.
            expect(biosamples).toBeDefined();
            expect(biosamples.length).toEqual(5);
        });
    });
});
