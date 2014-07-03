/** @jsx React.DOM */
'use strict';

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');
jest.dontMock('underscore');

jest.dontMock('../platform.js');
jest.dontMock('../globals.js');
jest.dontMock('../dbxref.js');
jest.dontMock('../../libs/registry.js');

describe('platform', function() {
    it('shows proper text and links', function() {
        var React = require('react');
        var Panel = require('../platform.js').Panel;
        var TestUtils = require('react/lib/ReactTestUtils');

        // Set up context object
        var context = {
            url: 'http://www3.appliedbiosystems.com/cms/groups/mcb_marketing/documents/generaldocuments/cms_072050.pdf',
            title: 'Applied Biosystems SOLiD System 3 Plus',
            term_id: 'OBI:0000000',
            dbxrefs: ['UCSC-ENCODE-cv:AB_SOLiD_3.5', 'GEO:GPL9442']
        };

        // Render a platform panel in the document
        var platformPanel = <Panel context={context} />;
        TestUtils.renderIntoDocument(platformPanel);

        // Verify we have three <dt> and <dd> elements
        var defTerms = TestUtils.scryRenderedDOMComponentsWithTag(platformPanel, 'dt');
        expect(defTerms.length).toEqual(3);
        var defDescs = TestUtils.scryRenderedDOMComponentsWithTag(platformPanel, 'dd');
        expect(defDescs.length).toEqual(3);

        // Verify the first <dd> (Platform name) has a link to www3.appliedbiosystems.com
        var defDescNode = defDescs[0].getDOMNode();
        expect(defDescNode.hasChildNodes()).toEqual(true);
        expect(defDescNode.childNodes.length).toEqual(1);
        var anchor = defDescNode.childNodes[0];
        expect(anchor.getAttribute('href')).toEqual('http://www3.appliedbiosystems.com/cms/groups/mcb_marketing/documents/generaldocuments/cms_072050.pdf');

        // Verify the third <dd> (dbxrefs) has an unordered list with two items
        defDescNode = defDescs[2].getDOMNode();
        expect(defDescNode.hasChildNodes()).toEqual(true);
        expect(defDescNode.childNodes.length).toEqual(1);
        var unordered = defDescNode.childNodes[0];
        expect(unordered.hasChildNodes()).toEqual(true);
        expect(unordered.childNodes.length).toEqual(2);

        // Make sure the two items got the proper text
        var listItem = unordered.childNodes;
        expect(listItem[0].textContent).toEqual('UCSC-ENCODE-cv:AB_SOLiD_3.5');
        expect(listItem[1].textContent).toEqual('GEO:GPL9442');

        // Make sure the two items contain links to the proper places
        expect(listItem[0].hasChildNodes()).toEqual(true);
        expect(listItem[0].childNodes.length).toEqual(1);
        expect(listItem[1].hasChildNodes()).toEqual(true);
        expect(listItem[1].childNodes.length).toEqual(1);
        anchor = listItem[0].childNodes[0];
        expect(anchor.getAttribute('href')).toEqual('http://genome.cse.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&term="AB_SOLiD_3.5"');
        anchor = listItem[1].childNodes[0];
        expect(anchor.getAttribute('href')).toEqual('http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL9442');
    });
});
