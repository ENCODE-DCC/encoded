import React from 'react';
import { mount } from 'enzyme';

// Import test component and data.
import Platform from '../platform';
import context from '../testdata/platform';


describe('Platform', () => {
    let platformPanel;
    let defTerms;
    let defDescs;

    beforeAll(() => {
        // Render platform panel into jsnode
        platformPanel = mount(
            <Platform context={context} />
        );

        // Get the <dt> and <dd> terms needed for all tests
        defTerms = platformPanel.find('dt');
        defDescs = platformPanel.find('dd');
    });

    test('has three <dt> and <dd> elements', () => {
        expect(defTerms).toHaveLength(3);
        expect(defDescs).toHaveLength(3);
    });

    describe('External References (third key-value) Item', () => {
        let defDescNode;
        let unorderedList;
        let listItems;
        let anchors;

        beforeAll(() => {
            defDescNode = defDescs.at(2);
            unorderedList = defDescNode.childAt(0);
            listItems = unorderedList.children();
            anchors = unorderedList.find('a');
        });

        test('has an unordered list with three items', () => {
            expect(defDescNode.children().exists()).toBeTruthy();
            expect(defDescNode.children()).toHaveLength(1);
            expect(unorderedList.children().exists()).toBeTruthy();
            expect(unorderedList.children()).toHaveLength(3);
        });

        test('has proper link text', () => {
            expect(listItems.at(0).text()).toEqual('UCSC-ENCODE-cv:Illumina_HiSeq_2000');
            expect(listItems.at(1).text()).toEqual('GEO:GPL11154');
            expect(listItems.at(2).text()).toEqual('GEO:GPL13112');
        });

        test('has links to the proper places', () => {
            expect(listItems.at(0).children().exists()).toBeTruthy();
            expect(listItems.at(0).children()).toHaveLength(1);
            expect(listItems.at(1).children().exists()).toBeTruthy();
            expect(listItems.at(1).children()).toHaveLength(1);
            expect(anchors.at(0).prop('href')).toEqual('http://genome.cse.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&term="Illumina_HiSeq_2000"');
            expect(anchors.at(1).prop('href')).toEqual('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL11154');
        });
    });
});
