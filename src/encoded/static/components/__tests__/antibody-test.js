'use strict';

jest.autoMockOff();

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');

describe('Antibody', function() {
    var React, TestUtils, Antibody, context;

    beforeEach(function() {
        React = require('react');
        Antibody = require('../antibody').Lot;
        TestUtils = require('react/lib/ReactTestUtils');

        // Set up context object to be rendered
        context = require('../testdata/antibody/ENCAB000AUZ');
        context.host_organism = require('../testdata/organism/rabbit');
        context.source = require('../testdata/source/aviva');
        context.characterizations = [require('../testdata/characterization/antibody-367a6fdd0cef')];
        context.characterizations[0].submitted_by = require('../testdata/submitter');
        context.characterizations[0].documents = [require('../testdata/document/antibodyStandards')];
        context.characterizations[0].lab = require('../testdata/lab');
        context.characterizations[0].award = require('../testdata/award');
        context.characterizations[0].target = require('../testdata/target/HNRNPA1-human');
        context.characterizations[0].target.organism = require('../testdata/organism/human');
        context.lot_reviews = [require('../testdata/lot_review/EFO-0002791')];
        context.lot_reviews[0].organisms = [require('../testdata/organism/human')];
        context.lot_reviews[0].targets = [require('../testdata/target/HNRNPA1-human')];
        context.lot_reviews[0].targets[0].organisms = [require('../testdata/organism/human')];
    });

    describe('Typical antibody', function() {
        var antibody;

        beforeEach(function() {
            var Context = {
              fetch: function(url, options) {
                return Promise.resolve({json: () => ({'@graph': []})});
              }
            };

            // Render antibody into jsnode
            antibody = React.withContext(Context, function() {
                return TestUtils.renderIntoDocument(
                    <Antibody context={context} />
                );
            });
        });

        it('has a good header', function() {
            var headerLine = TestUtils.findRenderedDOMComponentWithTag(antibody, 'h2').getDOMNode();
            expect(headerLine.textContent).toEqual('ENCAB000AUZ');
            headerLine = headerLine.nextSibling;
            expect(headerLine.textContent).toEqual('Antibody against Homo sapiens HNRNPA1');
        });

        it('has a good status panel', function() {
            var panel = TestUtils.findRenderedDOMComponentWithClass(antibody, 'type-antibody-status').getDOMNode();
            var row = panel.getElementsByClassName('status-organism-row');
            var element = row[0].getElementsByClassName('status-awaiting-lab-characterization');
            expect(element.length).toEqual(1);
            element = element[0].nextSibling;
            expect(element.textContent).toEqual('awaiting lab characterization');
            element = row[0].getElementsByClassName('status-organism');
            expect(element[0].textContent).toEqual('Homo sapiens');
            element = row[0].getElementsByClassName('status-terms');
            expect(element[0].textContent).toEqual('HeLa-S3');
        });

        it('has a good summary panel', function() {
            var panel = TestUtils.findRenderedDOMComponentWithClass(antibody, 'data-display').getDOMNode();

            var item = panel.querySelector('[data-test="source"]');
            var itemDescription = item.getElementsByTagName('dd')[0];
            var anchor = itemDescription.getElementsByTagName('a')[0];
            expect(itemDescription.textContent).toEqual('Aviva');
            expect(anchor.getAttribute('href')).toEqual('http://www.avivasysbio.com');

            item = panel.querySelector('[data-test="productid"]');
            itemDescription = item.getElementsByTagName('dd')[0];
            anchor = itemDescription.getElementsByTagName('a')[0];
            expect(itemDescription.textContent).toEqual('ARP40383_T100');
            expect(anchor.getAttribute('href')).toEqual('http://www.avivasysbio.com/anti-hnrpa1-antibody-n-terminal-region-arp40383-t100.html');

            item = panel.querySelector('[data-test="lotid"]');
            itemDescription = item.getElementsByTagName('dd')[0];
            expect(itemDescription.textContent).toEqual('QC9473-091124');

            item = panel.querySelector('[data-test="targets"]');
            itemDescription = item.getElementsByTagName('dd')[0];
            anchor = itemDescription.getElementsByTagName('a')[0];
            expect(itemDescription.textContent).toEqual('HNRNPA1 (Homo sapiens)');
            expect(anchor.getAttribute('href')).toEqual('/targets/HNRNPA1-human/');

            item = panel.querySelector('[data-test="host"]');
            itemDescription = item.getElementsByTagName('dd')[0];
            expect(itemDescription.textContent).toEqual('rabbit');

            item = panel.querySelector('[data-test="clonality"]');
            itemDescription = item.getElementsByTagName('dd')[0];
            expect(itemDescription.textContent).toEqual('polyclonal');

            item = panel.querySelector('[data-test="isotype"]');
            itemDescription = item.getElementsByTagName('dd')[0];
            expect(itemDescription.textContent).toEqual('IgG');

            item = panel.querySelector('[data-test="antigensequence"]');
            itemDescription = item.getElementsByTagName('dd')[0];
            expect(itemDescription.textContent).toEqual('MSKSESPKEPEQLRKLFIGGLSFETTDESLRSHFEQWGTLTDCVVMRDPN');
        });
    });
});
