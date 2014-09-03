/** @jsx React.DOM */
'use strict';

jest.autoMockOff();

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');
jest.dontMock('underscore');

describe('Software', function() {
    var React, TestUtils, Software, publication, context, _;

    beforeEach(function() {
        React = require('react');
        TestUtils = require('react/lib/ReactTestUtils');
        _ = require('underscore');

        // Set up context object to be rendered
        Software = require('../software').Software;
        context = require('../testdata/software');
    });

    describe('Software object with no references', function() {
        var software, summary;

        beforeEach(function() {
            software = TestUtils.renderIntoDocument(
                <Software context={context} />
            );

            summary = TestUtils.scryRenderedDOMComponentsWithClass(software, 'key-value');
        });

        it('has a title with link to software source', function() {
            var item = summary[0].getDOMNode().querySelector('[data-test="title"]');
            var itemDescription = item.getElementsByTagName('dd')[0];
            var anchor = itemDescription.getElementsByTagName('a')[0];
            expect(itemDescription.textContent).toEqual('HaploReg');
            expect(anchor.getAttribute('href')).toEqual('http://www.broadinstitute.org/mammals/haploreg/haploreg.php');
        });

        it('has a good description, software type, and used for', function() {
            var item = summary[0].getDOMNode().querySelector('[data-test="description"]');
            var itemDescription = item.getElementsByTagName('dd')[0];
            expect(itemDescription.textContent).toContain('Explores annotations of the noncoding genome');

            item = summary[0].getDOMNode().querySelector('[data-test="type"]');
            itemDescription = item.getElementsByTagName('dd')[0];
            expect(itemDescription.textContent).toEqual('database, variant annotation');

            item = summary[0].getDOMNode().querySelector('[data-test="purpose"]');
            itemDescription = item.getElementsByTagName('dd')[0];
            expect(itemDescription.textContent).toEqual('community resource');
        });
    });

    describe('Software object with a single reference', function() {
        var software, summary;

        beforeEach(function() {
            var context_ref = _.clone(context);
            context_ref.references = [require('../testdata/publication')];
            context_ref.references[0].references = ['PMID:19352372', 'PMCID:PMC3062402'];

            software = TestUtils.renderIntoDocument(
                <Software context={context_ref} />
            );

            summary = TestUtils.scryRenderedDOMComponentsWithClass(software, 'key-value');
        });

        it('has two references with proper links', function() {
            var item = summary[0].getDOMNode().querySelector('[data-test="references"]');
            var itemDescription = item.getElementsByTagName('dd')[0];
            var ul = itemDescription.getElementsByTagName('ul')[0];
            var lis = ul.getElementsByTagName('li');
            expect(lis.length).toEqual(2);

            var anchor = lis[0].getElementsByTagName('a')[0];
            expect(anchor.textContent).toEqual('PMID:19352372');
            expect(anchor.getAttribute('href')).toEqual('http://www.ncbi.nlm.nih.gov/pubmed/?term=19352372');

            anchor = lis[1].getElementsByTagName('a')[0];
            expect(anchor.textContent).toEqual('PMCID:PMC3062402');
            expect(anchor.getAttribute('href')).toEqual('http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3062402');
        });
    });
});
