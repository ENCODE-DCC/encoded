import React from 'react';
import { mount } from 'enzyme';
import _ from 'underscore';

// Import test component and data.
import Software from '../software';
import context from '../testdata/software';


describe('Software', () => {
    describe('Software object with no references', () => {
        let software;
        let summary;

        beforeAll(() => {
            software = mount(
                <Software context={context} />
            );

            summary = software.find('.key-value');
        });

        it('has a title with link to software source', () => {
            const item = summary.find('[data-test="title"]');
            const itemDescription = item.find('dd');
            const anchor = itemDescription.find('a');
            expect(itemDescription.text()).toEqual('HaploReg');
            expect(anchor.prop('href')).toEqual('http://www.broadinstitute.org/mammals/haploreg/haploreg.php');
        });

        it('has a good description, software type, and used for', () => {
            let item = summary.find('[data-test="description"]');
            let itemDescription = item.find('dd');
            expect(itemDescription.text()).toContain('Explores annotations of the noncoding genome');

            item = summary.find('[data-test="type"]');
            itemDescription = item.find('dd');
            expect(itemDescription.text()).toEqual('database, variant annotation');

            item = summary.find('[data-test="purpose"]');
            itemDescription = item.find('dd');
            expect(itemDescription.text()).toEqual('community resource');
        });
    });

    describe('Software object with a single reference', () => {
        let software;
        let summary;

        beforeAll(() => {
            const contextRef = _.clone(context);
            contextRef.references = [require('../testdata/publication/publication')];
            contextRef.references[0].identifiers = ['PMID:19352372', 'PMCID:PMC3062402'];

            software = mount(
                <Software context={contextRef} />
            );

            summary = software.find('.key-value');
        });

        it('has two references with proper links', () => {
            const item = summary.find('[data-test="references"]');
            const itemDescription = item.find('dd');
            const ul = itemDescription.find('ul');
            const lis = ul.find('li');
            expect(lis).toHaveLength(2);

            let anchor = lis.at(0).find('a');
            expect(anchor.at(0).text()).toEqual('PMID:19352372');
            expect(anchor.at(0).prop('href')).toEqual('/publications/52e85c70-fe2d-11e3-9191-0800200c9a66/');

            anchor = lis.at(1).find('a');
            expect(anchor.at(0).text()).toEqual('PMCID:PMC3062402');
            expect(anchor.at(0).prop('href')).toEqual('/publications/52e85c70-fe2d-11e3-9191-0800200c9a66/');
        });
    });
});
