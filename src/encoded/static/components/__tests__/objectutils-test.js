import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';

// Import test component and data.
import { InternalTags, internalTagsMap, findRelatedLocation } from '../objectutils';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });

describe('InternalTags', () => {
    let context;
    let wrapper;
    const testTags = ['ENTEx', 'SESCC'];

    beforeAll(() => {
        context = {
            '@type': ['HumanDonor', 'Donor', 'Item'],
            internal_tags: testTags,
        };
        wrapper = mount(
            <InternalTags internalTags={context.internal_tags} objectType={context['@type'][0]} />
        );
    });

    test('generates two links', () => {
        const internalTagLinks = wrapper.find('a');
        expect(internalTagLinks).toHaveLength(2);
    });


    test('generates the right images in each link', () => {
        const uris = testTags.map((tag) => `/static/img/${internalTagsMap[tag].badgeFilename}`);
        wrapper.find('a').forEach((link, i) => {
            const image = link.find('img');
            expect(image).toHaveLength(1);
            expect(image.prop('src')).toEqual(uris[i]);
            expect(image.prop('alt')).toContain(testTags[i]);
        });
    });
});

describe('FindRelatedLocations', () => {
    let context;

    beforeAll(() => {
        context = {
            related_datasets: [
                {
                    elements_references: [
                        {
                            examined_loci: [
                                {
                                    status: 'released',
                                    locations: [
                                        {
                                            assembly: 'GRCh38',
                                            chromosome: 'chrX',
                                            start: 134460165,
                                            end: 134500668,
                                        },
                                        {
                                            assembly: 'hg19',
                                            chromosome: 'chrX',
                                            start: 133594195,
                                            end: 133634698,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        };
    });

    test('finds location from related dataset', () => {
        const defaultLocation = findRelatedLocation(context, 'hg19');
        expect(defaultLocation.chromosome).toEqual('chrX');
        expect(defaultLocation.start).toEqual(133594195);
    });
});
