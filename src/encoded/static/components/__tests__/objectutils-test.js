import React from 'react';
import { mount } from 'enzyme';

// Import test component and data.
import { InternalTags } from '../objectutils';


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
            <InternalTags context={context} />
        );
    });

    test('generates two links', () => {
        const internalTagLinks = wrapper.find('a');
        expect(internalTagLinks).toHaveLength(2);
    });


    test('generates the right images in each link', () => {
        const uris = testTags.map(tag => `/static/img/tag-${tag}.png`);
        wrapper.find('a').forEach((link, i) => {
            const image = link.find('img');
            expect(image).toHaveLength(1);
            expect(image.prop('src')).toEqual(uris[i]);
            expect(image.prop('alt')).toContain(testTags[i]);
        });
    });
});
