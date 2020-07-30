import React from 'react';
import { mount } from 'enzyme';
import _ from 'underscore';

// Import test component and data.
import { SearchControls } from '../search';
import context from '../testdata/experiment-search';


describe('View controls for search with Experiments', () => {
    describe('Minimal Experiment', () => {
        let searchControls;

        beforeAll(() => {
            const contextResults = _.clone(context);
            searchControls = mount(
                <SearchControls context={contextResults} />,
                { context: { location_href: '/search/?type=Experiment' } }
            );
        });

        test('has proper view control buttons', () => {
            const viewControls = searchControls.find('.btn-attached');
            const links = viewControls.find('a');
            expect(links).toHaveLength(2);
            expect(links.at(0).prop('href')).toEqual('/report/?type=Experiment&status=released&assay_slims=DNA+accessibility');
            expect(links.at(1).prop('href')).toEqual('/matrix/?type=Experiment&status=released&assay_slims=DNA+accessibility');
        });

        test('has Download, Visualize, and JSON buttons', () => {
            const buttons = searchControls.find('button');
            expect(buttons).toHaveLength(3);
            expect(buttons.at(0).text()).toEqual('Download');
            expect(buttons.at(1).text()).toEqual('Visualize');
            expect(buttons.at(2).text()).toEqual('{ ; }');
        });
    });
});
