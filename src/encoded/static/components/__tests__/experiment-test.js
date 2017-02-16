
'use strict';

jest.autoMockOff();

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');
jest.dontMock('underscore');


describe('Experiment Page', function() {
    var React, TestUtils, Experiment, FetchContext, context, _;

    beforeEach(function() {
        React = require('react');
        TestUtils = require('react/lib/ReactTestUtils');
        _ = require('underscore');

        Experiment = require('../experiment').Experiment;
        context = require('../testdata/experiment');

        FetchContext = {
            fetch: function(url, options) {
                return Promise.resolve({json: () => ({'@graph': []})});
            }
        };
    });

    describe('Minimal Experiment', function() {
        var experiment, summary, defTerms, defDescs;

        beforeEach(function() {
            context.references = [require('../testdata/publication/PMID16395128'), require('../testdata/publication/PMID23000965')];
            experiment = React.withContext(FetchContext, function() {
                return TestUtils.renderIntoDocument(
                    <Experiment context={context} />
                );
            });

            summary = TestUtils.scryRenderedDOMComponentsWithClass(experiment, 'data-display');
            defTerms = summary[0].getDOMNode().getElementsByTagName('dt');
            defDescs = summary[0].getDOMNode().getElementsByTagName('dd');
        });

        it('has proper links in dbxrefs key-value', function() {
            var item = summary[0].getDOMNode().querySelector('[data-test="external-resources"]');
            var desc = item.getElementsByTagName('dd')[0];
            var dbxrefs = desc.getElementsByTagName('a');
            expect(dbxrefs.length).toEqual(2);
            expect(dbxrefs[0].getAttribute('href')).toEqual('http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=hg19&hgt_mdbVal1=wgEncodeEH003317');
            expect(dbxrefs[1].getAttribute('href')).toEqual('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM1010811');
        });

        it('has proper release date', function() {
            var item = summary[0].getDOMNode().querySelector('[data-test="date-released"]');
            var desc = item.getElementsByTagName('dd')[0];
            expect(desc.textContent).toEqual('2011-10-29');
        });

        it('has one experiment status element in header', function() {
            var statusList = TestUtils.findRenderedDOMComponentWithClass(experiment, 'status-list').getDOMNode();
            expect(statusList.hasChildNodes()).toBeTruthy();
            expect(statusList.childNodes.length).toEqual(1);
        });
    });

    describe('Document Panel', function() {
        var experiment, doc;

        beforeEach(function() {
            require('../biosample.js').Document;
            var context_doc = _.clone(context);
            context_doc.documents = [require('../testdata/document/myerschipseq')];
            experiment = React.withContext(FetchContext, function() {
                return TestUtils.renderIntoDocument(
                    <Experiment context={context_doc} />
                );
            });
            doc = TestUtils.findRenderedDOMComponentWithClass(experiment, 'type-Document').getDOMNode();;
        });

        it('has one document panel with a PDF image anchor', function() {
            var figures = doc.getElementsByTagName('figure');
            expect(figures.length).toEqual(1);
            var anchors = figures[0].getElementsByClassName('file-pdf');
            expect(anchors.length).toEqual(1);
        });

        it('has a single proper download link', function() {
            var url = require('url');

            var dlBar = doc.getElementsByClassName('document__file');
            expect(dlBar.length).toEqual(1);
            var anchors = dlBar[0].getElementsByTagName('a');
            expect(anchors.length).toEqual(2);
            expect(url.parse(anchors[0].getAttribute('href')).pathname).toEqual('/documents/df9dd0ec-c1cf-4391-a745-a933ab1af7a7/@@download/attachment/Myers_Lab_ChIP-seq_Protocol_v042211.pdf');
        });

        it('has two key-value pairs, and proper DL link', function() {
            var trigger = doc.getElementsByClassName('document__file-detail-switch');
            TestUtils.Simulate.click(trigger[0]);

            var docKeyValue = doc.getElementsByClassName('key-value-doc');
            expect(docKeyValue.length).toEqual(1);
            var defTerms = docKeyValue[0].getElementsByTagName('dt');
            expect(defTerms.length).toEqual(3);
            var defDescs = docKeyValue[0].getElementsByTagName('dd');
            expect(defDescs.length).toEqual(3);
        });
    });

    describe('Document Panel References', function() {
        var experiment, doc;

        beforeEach(function() {
            require('../biosample.js').Document;
            var context_doc = _.clone(context);
            context_doc.documents = [require('../testdata/document/wgEncodeSydhHist-refs')];
            experiment = React.withContext(FetchContext, function() {
                return TestUtils.renderIntoDocument(
                    <Experiment context={context_doc} />
                );
            });
            doc = TestUtils.findRenderedDOMComponentWithClass(experiment, 'type-Document').getDOMNode();
        });

        it('has five key-value pairs, and two good references links', function() {
            var url = require('url');
            var docKeyValue = doc.getElementsByClassName('key-value-doc');
            expect(docKeyValue.length).toEqual(1);
            var defTerms = docKeyValue[0].getElementsByTagName('dt');
            expect(defTerms.length).toEqual(3);
            var defDescs = docKeyValue[0].getElementsByTagName('dd');
            expect(defDescs.length).toEqual(3);
        });
    });

    describe('Replicate Panels', function() {
        var experiment, replicates, summary;

        beforeEach(function() {
            var context_rep = _.clone(context);
            context_rep.replicates = [require('../testdata/replicate/human'), require('../testdata/replicate/mouse')];
            context_rep.replicates[0].library = require('../testdata/library/sid38806');
            context_rep.replicates[1].library = require('../testdata/library/sid38807');
            context_rep.files = [require('../testdata/file/fastq')];
            experiment = React.withContext(FetchContext, function() {
                return TestUtils.renderIntoDocument(
                    <Experiment context={context_rep} />
                );
            });
            summary = TestUtils.scryRenderedDOMComponentsWithClass(experiment, 'data-display');
        });

        it('has proper treatment', function() {
            var item = summary[0].getDOMNode().querySelector('[data-test="treatments"]');
            var desc = item.getElementsByTagName('dd')[0];
            expect(desc.textContent).toEqual('97.2 nM doxycycline hyclate (CHEBI:34730) for 6 hour [1-1]');
        });

        it('has proper strand specificity', function() {
            var item = summary[0].getDOMNode().querySelector('[data-test="strandspecificity"]');
            var desc = item.getElementsByTagName('dd')[0];
            expect(desc.textContent).toEqual('Strand-specific');
        });

        it('has proper spikeins', function() {
            var item = summary[0].getDOMNode().querySelector('[data-test="spikeins"]');
            var desc = item.getElementsByTagName('dd')[0];
            expect(desc.textContent).toEqual('ENCSR000AJW [1-1]');
        });
    });

    describe('Alternate accession display', function() {
        var experiment, alt;

        beforeEach(function() {
            var context_alt = _.clone(context);
            context_alt.alternate_accessions = ["ENCSR000ACT", "ENCSR999NOF"];
            experiment = React.withContext(FetchContext, function() {
                return TestUtils.renderIntoDocument(
                    <Experiment context={context_alt} />
                );
            });
            alt = TestUtils.findRenderedDOMComponentWithClass(experiment, 'repl-acc');
        });

        it('displays two alternate accessions', function() {
            expect(alt.getDOMNode().textContent).toEqual('Replaces ENCSR000ACT, ENCSR999NOF');
        });
    });
});
