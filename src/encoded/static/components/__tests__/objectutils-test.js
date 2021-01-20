import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';

// Import test component and data.
import { InternalTags, internalTagsMap } from '../objectutils';

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
        const uris = testTags.map((tag) => `/static/img/${internalTagsMap[tag]}`);
        wrapper.find('a').forEach((link, i) => {
            const image = link.find('img');
            expect(image).toHaveLength(1);
            expect(image.prop('src')).toEqual(uris[i]);
            expect(image.prop('alt')).toContain(testTags[i]);
        });
    });
});
