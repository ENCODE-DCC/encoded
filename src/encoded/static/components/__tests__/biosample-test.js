import { collectChildren } from '../biosample';


const biosample = {
    '@id': '/biosamples/ENCBS000AAA/',
    parent_of: [
        {
            '@id': '/biosamples/ENCBS000AAB/',
            parent_of: [],
        },
        {
            '@id': '/biosamples/ENCBS000AAC/',
            parent_of: [
                {
                    '@id': '/biosamples/ENCBS000AAD/',
                    parent_of: [],
                },
                {
                    '@id': '/biosamples/ENCBS000AAE/',
                    parent_of: [
                        {
                            '@id': '/biosamples/ENCBS000AAF/',
                            parent_of: [],
                        },
                    ],
                },
            ],
        },
    ],
};

describe('Utility functions', () => {
    test('collectChildren generates correct tree structure', () => {
        collectChildren(biosample.parent_of).then((tree) => {
            console.dir(JSON.stringify(tree, null, 2));
            // Top level has expected properties.
            expect(tree.children).toBeDefined();
            expect(tree.hierarchy).toBeDefined();
            expect(tree.children.length).toEqual(2);
            expect(Object.keys(tree.hierarchy).length).toEqual(2);

            // Second level has expected properties.
            expect(tree.hierarchy['/biosamples/ENCBS000AAB/']).toBeDefined();
            expect(Object.keys(tree.hierarchy['/biosamples/ENCBS000AAB/']).length).toEqual(0);

            const level2AAC = tree.hierarchy['/biosamples/ENCBS000AAC/'];
            expect(level2AAC).toBeDefined();
            expect(level2AAC.children).toBeDefined();
            expect(level2AAC.hierarchy).toBeDefined();
            expect(level2AAC.children.length).toEqual(2);
            expect(Object.keys(level2AAC.hierarchy).length).toEqual(2);

            // Third level has expected properties.
            expect(Object.keys(level2AAC.hierarchy['/biosamples/ENCBS000AAD/']).length).toEqual(0);

            const level3AAE = level2AAC.hierarchy['/biosamples/ENCBS000AAE/'];
            expect(level3AAE).toBeDefined();
            expect(level3AAE.children).toBeDefined();
            expect(level3AAE.hierarchy).toBeDefined();
            expect(level3AAE.children.length).toEqual(1);
            expect(Object.keys(level3AAE.hierarchy).length).toEqual(1);
        });
    });
});
