/** @jsx React.DOM */
'use strict';

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');
jest.dontMock('underscore');

jest.dontMock('../platform.js');
jest.dontMock('../globals.js');
jest.dontMock('../dbxref.js');
jest.dontMock('../../libs/registry.js');

describe('Platform', function() {
    var TestUtils;
    var platformPanel;
    var defTerms;
    var defDescs;

    beforeEach(function() {
        var React = require('react');
        var Panel = require('../platform.js').Panel;
        TestUtils = require('react/lib/ReactTestUtils');

        // Set up context object to be rendered
        var context = {
            url: 'http://www3.appliedbiosystems.com/cms/groups/mcb_marketing/documents/generaldocuments/cms_072050.pdf',
            title: 'Applied Biosystems SOLiD System 3 Plus',
            term_id: 'OBI:0000000',
            dbxrefs: ['UCSC-ENCODE-cv:AB_SOLiD_3.5', 'GEO:GPL9442']
        };

        // Render platform panel into jsnode
        var platformPanel = <Panel context={context} />;
        TestUtils.renderIntoDocument(platformPanel);

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

        it('has an unordered list with two items', function() {
            expect(defDescNode.hasChildNodes()).toBeTruthy();
            expect(defDescNode.childNodes.length).toEqual(1);
            expect(unorderedList.hasChildNodes()).toBeTruthy();
            expect(unorderedList.childNodes.length).toEqual(2);
        });

        it('has proper link text', function() {
            expect(listItems[0].textContent).toEqual('UCSC-ENCODE-cv:AB_SOLiD_3.5');
            expect(listItems[1].textContent).toEqual('GEO:GPL9442');
        });

        it('has links to the proper places', function() {
            expect(listItems[0].hasChildNodes()).toBeTruthy();
            expect(listItems[0].childNodes.length).toEqual(1);
            expect(listItems[1].hasChildNodes()).toBeTruthy();
            expect(listItems[1].childNodes.length).toEqual(1);
            expect(anchors[0].getAttribute('href')).toEqual('http://genome.cse.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&term="AB_SOLiD_3.5"');
            expect(anchors[1].getAttribute('href')).toEqual('http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL9442');
        });
    });
});
