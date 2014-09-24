/** @jsx React.DOM */
'use strict';

jest.autoMockOff();

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');
jest.dontMock('underscore');

describe('Publication', function() {
    var React, TestUtils, Panel, publication, context, _;

    beforeEach(function() {
        React = require('react');
        Panel = require('../publication').Panel;
        TestUtils = require('react/lib/ReactTestUtils');
        _ = require('underscore');

        // Set up context object to be rendered
        context = require('../testdata/publication');
    });

    describe('Publication without references', function() {
        var publication;

        beforeEach(function() {
            // Render publication panel into jsnode
            publication = TestUtils.renderIntoDocument(
                <Panel context={context} />
            );
        });

        it('has a good author line', function() {
            var authorLineEl = TestUtils.findRenderedDOMComponentWithClass(publication, 'authors');
            var authors = authorLineEl.getDOMNode();
            expect(authors.textContent).toEqual('ENCODE Project Consortium, Bernstein BE, Birney E, Dunham I, Green ED, Gunter C, Snyder M.');
        });

        it('has a good citation line', function() {
            var journal = TestUtils.findRenderedDOMComponentWithClass(publication, 'journal').getDOMNode();
            expect(journal.textContent).toEqual('Nature. 2012 Sep;489(7414):57-74.');
        });

        it('has a journal name in italics', function() {
            var journal = TestUtils.findRenderedDOMComponentWithClass(publication, 'journal').getDOMNode();
            var italicTexts = journal.getElementsByTagName('i');
            expect(italicTexts.length).toEqual(1);
            expect(italicTexts[0].textContent).toEqual('Nature. ');
        });

        it('has a good abstract with an h2 and a p', function() {
            var abstract = TestUtils.findRenderedDOMComponentWithClass(publication, 'abstract').getDOMNode();
            expect(abstract.getElementsByTagName('*').length).toEqual(2);
            var abstractPart = abstract.getElementsByTagName('h2');
            expect(abstractPart.length).toEqual(1);
            abstractPart = abstract.getElementsByTagName('p');
            expect(abstractPart.length).toEqual(1);
            expect(abstractPart[0].textContent).toContain('The human genome encodes the blueprint of life,');
        });

        it('has a good method summary', function() {
            var pubdata = TestUtils.findRenderedDOMComponentWithClass(publication, 'key-value-left').getDOMNode();
            var item = pubdata.querySelector('[data-test="methodsummary"]');
            var itemDescription = item.getElementsByTagName('dd')[0];
            expect(itemDescription.textContent).toEqual('Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit.');
        });

        it('has good supplemental data links', function() {
            var pubdata = TestUtils.findRenderedDOMComponentWithClass(publication, 'key-value-left').getDOMNode();
            var item = pubdata.querySelector('[data-test="urls"]');
            var itemDescription = item.getElementsByTagName('dd')[0];
            var li = itemDescription.getElementsByTagName('li');
            expect(li.length).toEqual(2);
            expect(li[0].textContent).toEqual('http://www.millipore.com/catalogue/item/05-379#');
            var anchor = li[0].getElementsByTagName('a')[0];
            expect(anchor.getAttribute('href')).toEqual('http://www.millipore.com/catalogue/item/05-379#');
            expect(li[1].textContent).toEqual('http://www.millipore.com/catalogue/item/07-473');
            anchor = li[1].getElementsByTagName('a')[0];
            expect(anchor.getAttribute('href')).toEqual('http://www.millipore.com/catalogue/item/07-473');
        });
    });

    describe('Publication with references', function() {
        var publication;

        beforeEach(function() {
            var context_ref = _.clone(context);
            context_ref.references = ['PMID:19352372', 'PMCID:PMC3062402'];
            publication = TestUtils.renderIntoDocument(
                <Panel context={context_ref} />
            );
        });

        it('has two references', function() {
            var pubdata = TestUtils.findRenderedDOMComponentWithClass(publication, 'key-value-left').getDOMNode();
            var item = pubdata.querySelector('[data-test="references"]');
            var ul = item.getElementsByTagName('ul');
            var li = ul[0].getElementsByTagName('li');
            expect(li.length).toEqual(2);
            var anchor = li[0].getElementsByTagName('a');
            expect(anchor[0].getAttribute('href')).toEqual('http://www.ncbi.nlm.nih.gov/pubmed/?term=19352372');
            anchor = li[1].getElementsByTagName('a');
            expect(anchor[0].getAttribute('href')).toEqual('http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3062402');
        });
    });

    describe('Publication with data_used', function() {
        var publication;

        beforeEach(function() {
            var context_du = _.clone(context);
            context_du.data_used = 'ENCODE main paper';
            publication = TestUtils.renderIntoDocument(
                <Panel context={context_du} />
            );
        });

        it('has a data-used field', function() {
            var references = TestUtils.findRenderedDOMComponentWithClass(publication, 'key-value-left').getDOMNode();
            var dd = references.getElementsByTagName('dd');
            expect(dd[0].textContent).toEqual('ENCODE main paper');
        });
    });

    describe('Publication with datasets', function() {
        var publication;

        beforeEach(function() {
            var context_ds = _.clone(context);
            context_ds.datasets = [require('../testdata/dataset/ENCSR000AJW.js'), require('../testdata/dataset/ENCSR999BLA.js')];
            publication = TestUtils.renderIntoDocument(
                <Panel context={context_ds} />
            );
        });

        it('has two dataset links', function() {
            var pubdata = TestUtils.findRenderedDOMComponentWithClass(publication, 'key-value-left').getDOMNode();
            var item = pubdata.querySelector('[data-test="datasets"]');
            var itemDescription = item.getElementsByTagName('dd')[0];
            var anchors = itemDescription.getElementsByTagName('a');
            expect(anchors.length).toEqual(2);
            expect(anchors[0].getAttribute('href')).toEqual('/datasets/ENCSR000AJW/');
            expect(anchors[0].textContent).toEqual('ENCSR000AJW');
            expect(anchors[1].getAttribute('href')).toEqual('/datasets/ENCSR999BLA/');
            expect(anchors[1].textContent).toEqual('ENCSR999BLA');
        });
    });
});
