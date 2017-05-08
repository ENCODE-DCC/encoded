import React from 'react';
import { mount } from 'enzyme';
import _ from 'underscore';

// Import test component and data.
import { Publication } from '../publication';
import context from '../testdata/publication/publication';


describe('Publication', () => {
    describe('Publication without references', () => {
        let publication;

        beforeAll(() => {
            // Render publication panel into jsnode
            publication = mount(
                <Publication context={context} />
            );
        });

        test('has a good author line', () => {
            const authors = publication.find('.authors');
            expect(authors).toHaveLength(1);
            expect(authors.text()).toEqual('ENCODE Project Consortium, Bernstein BE, Birney E, Dunham I, Green ED, Gunter C, Snyder M.');
        });

        test('has a good citation line', () => {
            const journal = publication.find('.journal');
            expect(journal.text()).toEqual('Nature. 2012 Sep;489(7414):57-74.');
        });

        test('has a journal name in italics', () => {
            const journal = publication.find('.journal');
            const italicTexts = journal.find('i');
            expect(italicTexts).toHaveLength(1);
            expect(italicTexts.text()).toEqual('Nature. ');
        });

        test('has a good abstract with an h2 and a p', () => {
            const panel = publication.find('.panel');
            const item = panel.find('[data-test="abstract"]');
            expect(item).toHaveLength(1);
            let abstractPart = item.find('dt');
            expect(abstractPart).toHaveLength(1);
            abstractPart = item.find('dd');
            expect(abstractPart).toHaveLength(1);
            expect(abstractPart.text()).toContain('The human genome encodes the blueprint of life,');
        });
    });

    describe('Publication with references', () => {
        let publication;

        beforeAll(() => {
            // Render publication panel into jsnode
            const contextRef = _.clone(context);
            contextRef.identifiers = ['PMID:19352372', 'PMCID:PMC3062402'];
            publication = mount(
                <Publication context={contextRef} />
            );
        });

        test('has two references', () => {
            const pubdata = publication.find('.key-value');
            const item = pubdata.find('[data-test="references"]');
            const ul = item.find('ul');
            const li = ul.find('li');

            // Should have two <li> within the <ul> for references.
            expect(li).toHaveLength(2);

            // Make sure <a src> is correct for both <li>.
            let anchor = li.at(0).find('a');
            expect(anchor.at(0).prop('href')).toEqual('https://www.ncbi.nlm.nih.gov/pubmed/?term=19352372');
            anchor = li.at(1).find('a');
            expect(anchor.at(0).prop('href')).toEqual('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3062402');
        });
    });

    describe('Publication with data_used', () => {
        let publication;

        beforeAll(() => {
            const contextDu = _.clone(context);
            contextDu.data_used = 'ENCODE main paper';
            publication = mount(
                <Publication context={contextDu} />
            );
        });

        test('has a data-used field', () => {
            const dataused = publication.find('.key-value');
            const item = dataused.find('[data-test="dataused"]');
            const dd = item.find('dd');
            expect(dd.at(0).text()).toEqual('ENCODE main paper');
        });
    });

    describe('Publication with datasets', () => {
        let publication;

        beforeAll(() => {
            const contextDs = _.clone(context);
            contextDs.datasets = [require('../testdata/dataset/ENCSR000AJW.js'), require('../testdata/dataset/ENCSR999BLA.js')];
            publication = mount(
                <Publication context={contextDs} />
            );
        });

        test('has two dataset links', () => {
            const pubdata = publication.find('.key-value');
            const item = pubdata.find('[data-test="datasets"]');
            const itemDescription = item.find('dd');
            const anchors = itemDescription.find('a');
            expect(anchors).toHaveLength(2);
            expect(anchors.at(0).prop('href')).toEqual('/datasets/ENCSR000AJW/');
            expect(anchors.at(0).text()).toEqual('ENCSR000AJW');
            expect(anchors.at(1).prop('href')).toEqual('/datasets/ENCSR999BLA/');
            expect(anchors.at(1).text()).toEqual('ENCSR999BLA');
        });
    });

    describe('Publication with supplementary data', () => {
        let publication;

        beforeAll(() => {
            const contextSd = _.clone(context);
            contextSd.supplementary_data = [require('../testdata/publication/supplementary-data-1.js'), require('../testdata/publication/supplementary-data-2.js')];
            publication = mount(
                <Publication context={contextSd} />
            );
        });

        test('has a supplementary data panel with two items', () => {
            const supdata = publication.find('.type-Publication');
            const item = supdata.find('[data-test="supplementarydata"]');
            const itemSection = item.find('section');
            expect(itemSection).toHaveLength(2);
        });
    });
});
