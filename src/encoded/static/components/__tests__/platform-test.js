'use strict';

jest.autoMockOff();

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');
jest.dontMock('underscore');

describe('Platform', function() {
    var TestUtils;
    var platformPanel;
    var defTerms;
    var defDescs;

    beforeEach(function() {
        var React = require('react');
        var Panel = require('../platform').Panel;
        TestUtils = require('react/lib/ReactTestUtils');

        // Set up context object to be rendered
        var context = require('../testdata/platform');

        // Render platform panel into jsnode
        platformPanel = TestUtils.renderIntoDocument(
            <Panel context={context} />
        );

        // Get the <dt> and <dd> terms needed for all tests
        defTerms = TestUtils.scryRenderedDOMComponentsWithTag(platformPanel, 'dt');
        defDescs = TestUtils.scryRenderedDOMComponentsWithTag(platformPanel, 'dd');
    });

    it('has three <dt> and <dd> elements', function() {
        expect(defTerms.length).toEqual(3);
        expect(defDescs.length).toEqual(3);
    });

    describe('External References (third key-value) Item', function() {
        var defDescNode, unorderedList, listItems, anchors;

        beforeEach(function() {
            defDescNode = defDescs[2].getDOMNode();
            unorderedList = defDescNode.childNodes[0];
            listItems = unorderedList.childNodes;
            anchors = unorderedList.getElementsByTagName('a');
        });

        it('has an unordered list with three items', function() {
            expect(defDescNode.hasChildNodes()).toBeTruthy();
            expect(defDescNode.childNodes.length).toEqual(1);
            expect(unorderedList.hasChildNodes()).toBeTruthy();
            expect(unorderedList.childNodes.length).toEqual(3);
        });

        it('has proper link text', function() {
            expect(listItems[0].textContent).toEqual('UCSC-ENCODE-cv:Illumina_HiSeq_2000');
            expect(listItems[1].textContent).toEqual('GEO:GPL11154');
            expect(listItems[2].textContent).toEqual('GEO:GPL13112');
        });

        it('has links to the proper places', function() {
            expect(listItems[0].hasChildNodes()).toBeTruthy();
            expect(listItems[0].childNodes.length).toEqual(1);
            expect(listItems[1].hasChildNodes()).toBeTruthy();
            expect(listItems[1].childNodes.length).toEqual(1);
            expect(anchors[0].getAttribute('href')).toEqual('http://genome.cse.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&term="Illumina_HiSeq_2000"');
            expect(anchors[1].getAttribute('href')).toEqual('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL11154');
        });
    });
});
